"""
Universal Task Executor V3.0 - Checkpoint管理器
支持暂停/重启、分层检查点、版本迁移
"""

import os
import json
import logging
import asyncio
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path

from .structures import Checkpoint, CheckpointIndex, Task, TaskBatch, TaskResult

logger = logging.getLogger(__name__)


@dataclass
class ResumeResult:
    """恢复结果"""
    success: bool
    checkpoint: Optional[Checkpoint] = None
    remaining_tasks: List[str] = field(default_factory=list)
    token_remaining: int = 0
    error: Optional[str] = None


@dataclass
class RecoveryResult:
    """自动恢复结果"""
    checkpoint_id: str
    success: bool
    remaining_tasks: int = 0
    token_remaining: int = 0
    error: Optional[str] = None


class CheckpointStorage:
    """Checkpoint存储抽象基类"""
    
    async def save(self, checkpoint: Checkpoint) -> None:
        """保存Checkpoint"""
        raise NotImplementedError()
    
    async def load(self, checkpoint_id: str) -> Optional[Checkpoint]:
        """加载Checkpoint"""
        raise NotImplementedError()
    
    async def delete(self, checkpoint_id: str) -> None:
        """删除Checkpoint"""
        raise NotImplementedError()
    
    async def list_all(self) -> List[Checkpoint]:
        """列出所有Checkpoint"""
        raise NotImplementedError()
    
    async def exists(self, checkpoint_id: str) -> bool:
        """检查Checkpoint是否存在"""
        raise NotImplementedError()


class FileCheckpointStorage(CheckpointStorage):
    """文件存储实现"""
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"FileCheckpointStorage initialized: {base_path}")
    
    def _get_path(self, checkpoint_id: str) -> Path:
        """获取Checkpoint文件路径"""
        return self.base_path / f"{checkpoint_id}.json"
    
    async def save(self, checkpoint: Checkpoint) -> None:
        """保存Checkpoint到文件"""
        path = self._get_path(checkpoint.checkpoint_id)
        try:
            # 同步写入（文件IO不需要async）
            with open(path, "w", encoding="utf-8") as f:
                json.dump(checkpoint.to_dict(), f, indent=2, ensure_ascii=False)
            checkpoint.updated_at = datetime.now()
            logger.debug(f"Checkpoint saved: {checkpoint.checkpoint_id}")
        except Exception as e:
            logger.error(f"Failed to save checkpoint {checkpoint.checkpoint_id}: {e}")
            raise
    
    async def load(self, checkpoint_id: str) -> Optional[Checkpoint]:
        """从文件加载Checkpoint"""
        path = self._get_path(checkpoint_id)
        if not path.exists():
            return None
        
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return Checkpoint.from_dict(data)
        except Exception as e:
            logger.error(f"Failed to load checkpoint {checkpoint_id}: {e}")
            return None
    
    async def delete(self, checkpoint_id: str) -> None:
        """删除Checkpoint文件"""
        path = self._get_path(checkpoint_id)
        if path.exists():
            path.unlink()
            logger.debug(f"Checkpoint deleted: {checkpoint_id}")
    
    async def list_all(self) -> List[Checkpoint]:
        """列出所有Checkpoint"""
        checkpoints = []
        for path in self.base_path.glob("*.json"):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                checkpoints.append(Checkpoint.from_dict(data))
            except Exception as e:
                logger.warning(f"Failed to load checkpoint from {path}: {e}")
        return checkpoints
    
    async def exists(self, checkpoint_id: str) -> bool:
        """检查Checkpoint是否存在"""
        return self._get_path(checkpoint_id).exists()


class CheckpointManager:
    """
    Checkpoint管理器 - 核心组件
    
    职责:
    1. Checkpoint创建和保存
    2. Checkpoint加载和恢复
    3. Checkpoint清理和过期管理
    4. 恢复协调
    5. 每5分钟自动保存
    """
    
    CURRENT_VERSION = "3.0.0"
    CURRENT_SCHEMA_VERSION = 1
    
    def __init__(self, storage: CheckpointStorage = None, 
                 base_path: str = "memory/checkpoints",
                 default_ttl_days: int = 30,
                 auto_save_interval: int = 300):  # 5分钟
        """
        初始化Checkpoint管理器
        
        Args:
            storage: 存储后端，默认使用文件存储
            base_path: 基础路径（用于默认文件存储）
            default_ttl_days: 默认过期天数
            auto_save_interval: 自动保存间隔（秒）
        """
        self.storage = storage or FileCheckpointStorage(base_path)
        self.index = CheckpointIndex()
        self.default_ttl_days = default_ttl_days
        self.auto_save_interval = auto_save_interval
        
        self._active_checkpoints: Dict[str, Checkpoint] = {}
        self._save_hooks: List[Callable[[Checkpoint], None]] = []
        self._auto_save_task: Optional[asyncio.Task] = None
        self._last_auto_save: Optional[datetime] = None
        
        logger.info(f"CheckpointManager initialized: ttl={default_ttl_days}d, "
                   f"auto_save={auto_save_interval}s")
    
    # ─────────────────────────────────────────────────────────────────
    # Checkpoint创建
    # ─────────────────────────────────────────────────────────────────
    
    async def create_checkpoint(
        self,
        task_id: Optional[str] = None,
        batch_id: Optional[str] = None,
        name: Optional[str] = None,
        level: str = "system",  # system/handler/user
        state: Dict[str, Any] = None,
        progress: float = 0.0,
        processed_ids: List[str] = None,
        pending_ids: List[str] = None,
        failed_ids: List[str] = None,
        token_consumed: int = 0,
        handler_state: Dict[str, Any] = None,
    ) -> Checkpoint:
        """
        创建Checkpoint
        
        Args:
            task_id: 关联任务ID
            batch_id: 关联批次ID
            name: 检查点名称
            level: 层级（system/handler/user）
            state: 执行状态
            progress: 进度0-1
            processed_ids: 已处理任务ID列表
            pending_ids: 待处理任务ID列表
            failed_ids: 失败任务ID列表
            token_consumed: 已消耗Token
            handler_state: 处理器私有状态
            
        Returns:
            创建的Checkpoint
        """
        checkpoint = Checkpoint(
            checkpoint_id=self._generate_id(),
            name=name or f"checkpoint_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            task_id=task_id,
            batch_id=batch_id,
            status="active",
            progress=progress,
            execution_state=state or {},
            handler_state=handler_state,
            token_consumed=token_consumed,
            processed_task_ids=processed_ids or [],
            pending_task_ids=pending_ids or [],
            failed_task_ids=failed_ids or [],
            version=self.CURRENT_VERSION,
            schema_version=self.CURRENT_SCHEMA_VERSION,
            expires_at=datetime.now() + timedelta(days=self.default_ttl_days),
        )
        
        # 执行保存钩子
        for hook in self._save_hooks:
            try:
                hook(checkpoint)
            except Exception as e:
                logger.warning(f"Save hook failed: {e}")
        
        # 持久化
        await self.storage.save(checkpoint)
        
        # 更新索引
        self.index.add_checkpoint(checkpoint)
        self._active_checkpoints[checkpoint.checkpoint_id] = checkpoint
        
        logger.info(f"Checkpoint created: {checkpoint.checkpoint_id} "
                   f"(task={task_id}, batch={batch_id}, progress={progress:.1%})")
        
        return checkpoint
    
    async def create_task_checkpoint(
        self,
        task: Task,
        handler_state: Dict[str, Any] = None
    ) -> Checkpoint:
        """为单个任务创建Checkpoint"""
        return await self.create_checkpoint(
            task_id=task.task_id,
            name=f"task_{task.task_id}",
            state={"task": task.to_dict()},
            token_consumed=task.token_consumed,
            handler_state=handler_state
        )
    
    async def create_batch_checkpoint(
        self,
        batch: TaskBatch,
        processed_ids: List[str],
        pending_ids: List[str],
        failed_ids: List[str],
        handler_state: Dict[str, Any] = None
    ) -> Checkpoint:
        """为批次创建Checkpoint"""
        total = len(processed_ids) + len(pending_ids) + len(failed_ids)
        progress = len(processed_ids) / total if total > 0 else 0
        
        return await self.create_checkpoint(
            batch_id=batch.batch_id,
            name=f"batch_{batch.batch_id}",
            progress=progress,
            processed_ids=processed_ids,
            pending_ids=pending_ids,
            failed_ids=failed_ids,
            token_consumed=batch.token_consumed_total,
            handler_state=handler_state
        )
    
    def _generate_id(self) -> str:
        """生成唯一ID"""
        import uuid
        return str(uuid.uuid4())
    
    # ─────────────────────────────────────────────────────────────────
    # Checkpoint恢复
    # ─────────────────────────────────────────────────────────────────
    
    async def resume_from_checkpoint(
        self,
        checkpoint_id: str,
    ) -> ResumeResult:
        """
        从Checkpoint恢复
        
        Args:
            checkpoint_id: 检查点ID
            
        Returns:
            恢复结果
        """
        # 1. 加载Checkpoint
        checkpoint = await self.storage.load(checkpoint_id)
        if not checkpoint:
            return ResumeResult(
                success=False,
                error=f"Checkpoint not found: {checkpoint_id}"
            )
        
        # 2. 检查过期
        if checkpoint.is_expired():
            return ResumeResult(
                success=False,
                error=f"Checkpoint expired: {checkpoint_id}"
            )
        
        # 3. 检查是否可恢复
        if not checkpoint.is_resumable():
            return ResumeResult(
                success=False,
                error=f"Checkpoint not resumable: {checkpoint.status}"
            )
        
        # 4. 版本检查和迁移
        if checkpoint.version != self.CURRENT_VERSION:
            checkpoint = await self._migrate_checkpoint(checkpoint)
        
        # 5. 更新恢复计数
        checkpoint.resume_count += 1
        checkpoint.last_resume_at = datetime.now()
        await self.storage.save(checkpoint)
        
        logger.info(f"Checkpoint resumed: {checkpoint_id} "
                   f"(resume_count={checkpoint.resume_count})")
        
        return ResumeResult(
            success=True,
            checkpoint=checkpoint,
            remaining_tasks=checkpoint.pending_task_ids,
            token_remaining=checkpoint.token_budget_remaining
        )
    
    async def resume_latest(
        self,
        task_id: Optional[str] = None,
        batch_id: Optional[str] = None,
    ) -> Optional[ResumeResult]:
        """恢复最新的Checkpoint"""
        checkpoint = await self._find_latest_checkpoint(task_id, batch_id)
        if not checkpoint:
            return None
        return await self.resume_from_checkpoint(checkpoint.checkpoint_id)
    
    async def _find_latest_checkpoint(
        self,
        task_id: Optional[str] = None,
        batch_id: Optional[str] = None,
    ) -> Optional[Checkpoint]:
        """查找最新的Checkpoint"""
        checkpoints = await self.storage.list_all()
        
        filtered = []
        for cp in checkpoints:
            if task_id and cp.task_id != task_id:
                continue
            if batch_id and cp.batch_id != batch_id:
                continue
            if cp.is_expired():
                continue
            filtered.append(cp)
        
        if not filtered:
            return None
        
        # 按更新时间排序
        filtered.sort(key=lambda x: x.updated_at or x.created_at, reverse=True)
        return filtered[0]
    
    async def list_resumable(
        self,
        category: Optional[str] = None,
    ) -> List[Checkpoint]:
        """
        列出所有可恢复的Checkpoint
        
        Args:
            category: 按类别过滤（可选）
            
        Returns:
            可恢复的Checkpoint列表
        """
        checkpoints = await self.storage.list_all()
        resumable = [cp for cp in checkpoints if cp.is_resumable()]
        
        # 按创建时间排序（最新的在前）
        resumable.sort(key=lambda x: x.created_at, reverse=True)
        
        return resumable
    
    # ─────────────────────────────────────────────────────────────────
    # 状态迁移
    # ─────────────────────────────────────────────────────────────────
    
    async def _migrate_checkpoint(
        self,
        checkpoint: Checkpoint,
        target_version: str = None
    ) -> Checkpoint:
        """
        Checkpoint版本迁移
        
        支持跨版本恢复的关键机制
        """
        target_version = target_version or self.CURRENT_VERSION
        
        if checkpoint.version == target_version:
            return checkpoint
        
        logger.info(f"Migrating checkpoint from {checkpoint.version} to {target_version}")
        
        # 简单的版本迁移逻辑
        # 实际项目中可能需要更复杂的迁移逻辑
        checkpoint.version = target_version
        checkpoint.schema_version = self.CURRENT_SCHEMA_VERSION
        
        # 迁移标记
        if "migrations" not in checkpoint.execution_state:
            checkpoint.execution_state["migrations"] = []
        checkpoint.execution_state["migrations"].append({
            "from_version": checkpoint.version,
            "to_version": target_version,
            "timestamp": datetime.now().isoformat()
        })
        
        return checkpoint
    
    # ─────────────────────────────────────────────────────────────────
    # Checkpoint管理
    # ─────────────────────────────────────────────────────────────────
    
    async def update_checkpoint(
        self,
        checkpoint_id: str,
        progress: float = None,
        status: str = None,
        processed_ids: List[str] = None,
        pending_ids: List[str] = None,
        failed_ids: List[str] = None,
        handler_state: Dict[str, Any] = None,
    ) -> Optional[Checkpoint]:
        """
        更新Checkpoint
        
        Args:
            checkpoint_id: 检查点ID
            progress: 进度0-1
            status: 状态
            processed_ids: 已处理任务ID
            pending_ids: 待处理任务ID
            failed_ids: 失败任务ID
            handler_state: 处理器状态
            
        Returns:
            更新后的Checkpoint
        """
        checkpoint = await self.storage.load(checkpoint_id)
        if not checkpoint:
            logger.warning(f"Checkpoint not found for update: {checkpoint_id}")
            return None
        
        if progress is not None:
            checkpoint.progress = progress
        if status is not None:
            checkpoint.status = status
        if processed_ids is not None:
            checkpoint.processed_task_ids = processed_ids
        if pending_ids is not None:
            checkpoint.pending_task_ids = pending_ids
        if failed_ids is not None:
            checkpoint.failed_task_ids = failed_ids
        if handler_state is not None:
            checkpoint.handler_state = handler_state
        
        checkpoint.updated_at = datetime.now()
        await self.storage.save(checkpoint)
        
        return checkpoint
    
    async def complete_checkpoint(self, checkpoint_id: str) -> bool:
        """标记Checkpoint为已完成"""
        checkpoint = await self.update_checkpoint(
            checkpoint_id,
            status="completed",
            progress=1.0
        )
        if checkpoint:
            logger.info(f"Checkpoint completed: {checkpoint_id}")
            return True
        return False
    
    async def fail_checkpoint(self, checkpoint_id: str, error: str) -> bool:
        """标记Checkpoint为失败"""
        checkpoint = await self.update_checkpoint(
            checkpoint_id,
            status="failed"
        )
        if checkpoint:
            checkpoint.execution_state["error"] = error
            await self.storage.save(checkpoint)
            logger.error(f"Checkpoint failed: {checkpoint_id}, error={error}")
            return True
        return False
    
    # ─────────────────────────────────────────────────────────────────
    # 清理和过期管理
    # ─────────────────────────────────────────────────────────────────
    
    async def cleanup_expired(self) -> int:
        """
        清理过期Checkpoint
        
        Returns:
            清理的数量
        """
        all_checkpoints = await self.storage.list_all()
        expired = [cp for cp in all_checkpoints if cp.is_expired()]
        
        for cp in expired:
            await self.storage.delete(cp.checkpoint_id)
            
        if expired:
            logger.info(f"Cleaned up {len(expired)} expired checkpoints")
        
        return len(expired)
    
    async def cleanup_completed(self, keep_days: int = 7) -> int:
        """
        清理已完成且超过保留期的Checkpoint
        
        Args:
            keep_days: 保留天数
            
        Returns:
            清理的数量
        """
        cutoff = datetime.now() - timedelta(days=keep_days)
        all_checkpoints = await self.storage.list_all()
        
        to_delete = [
            cp for cp in all_checkpoints
            if cp.status == "completed" and cp.updated_at and cp.updated_at < cutoff
        ]
        
        for cp in to_delete:
            await self.storage.delete(cp.checkpoint_id)
        
        if to_delete:
            logger.info(f"Cleaned up {len(to_delete)} completed checkpoints (older than {keep_days} days)")
        
        return len(to_delete)
    
    async def get_stats(self) -> Dict[str, Any]:
        """获取Checkpoint统计"""
        all_checkpoints = await self.storage.list_all()
        
        stats = {
            "total": len(all_checkpoints),
            "active": 0,
            "completed": 0,
            "failed": 0,
            "expired": 0,
            "resumable": 0,
        }
        
        for cp in all_checkpoints:
            if cp.status in stats:
                stats[cp.status] += 1
            if cp.is_expired():
                stats["expired"] += 1
            if cp.is_resumable():
                stats["resumable"] += 1
        
        return stats
    
    # ─────────────────────────────────────────────────────────────────
    # 自动保存
    # ─────────────────────────────────────────────────────────────────
    
    def register_save_hook(self, hook: Callable[[Checkpoint], None]) -> None:
        """注册保存钩子"""
        self._save_hooks.append(hook)
    
    def start_auto_save(self, get_state_callback: Callable[[], Dict[str, Any]]) -> None:
        """
        启动自动保存
        
        Args:
            get_state_callback: 获取当前状态的回调函数
        """
        async def auto_save_loop():
            while True:
                try:
                    await asyncio.sleep(self.auto_save_interval)
                    state = get_state_callback()
                    await self._do_auto_save(state)
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Auto save error: {e}")
        
        self._auto_save_task = asyncio.create_task(auto_save_loop())
        logger.info(f"Auto save started: interval={self.auto_save_interval}s")
    
    async def _do_auto_save(self, state: Dict[str, Any]) -> None:
        """执行自动保存"""
        self._last_auto_save = datetime.now()
        # 创建系统级Checkpoint
        await self.create_checkpoint(
            name=f"auto_save_{self._last_auto_save.strftime('%Y%m%d_%H%M%S')}",
            level="system",
            state=state
        )
        logger.debug(f"Auto save completed: {self._last_auto_save}")
    
    def stop_auto_save(self) -> None:
        """停止自动保存"""
        if self._auto_save_task:
            self._auto_save_task.cancel()
            self._auto_save_task = None
            logger.info("Auto save stopped")
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        self.stop_auto_save()
