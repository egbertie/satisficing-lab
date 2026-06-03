> 生成时间: 2026-04-01 14:13+08:00
> 版本: V1.0
> 来源: 系统生成
> 内化完成时间: 待定

# Universal Task Executor V3.0 - 暂停/重启机制设计

**版本**: 3.0.0  
**设计目标**: 任意时刻可暂停、任意时刻可恢复、支持跨版本恢复  
**核心机制**: 分层Checkpoint + 状态迁移 + 自动恢复

---

## 1. 设计原则

### 1.1 核心目标

| 目标 | 说明 | 实现方式 |
|------|------|----------|
| **随时暂停** | 用户或系统可在任意时刻暂停任务 | 信号机制 + 状态保存 |
| **随时恢复** | 从任意Checkpoint恢复执行 | 状态重构 + 断点续传 |
| **防丢失** | 确保已处理的工作不丢失 | 持久化 + 确认机制 |
| **跨版本** | 支持版本升级后恢复 | 迁移引擎 + 兼容性层 |
| **Token感知** | 恢复时考虑Token预算 | Token状态保存 |

### 1.2 分层策略

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Checkpoint分层策略                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Layer 1: 系统层 (System Checkpoint)                                         │
│  ├── 保存间隔: 每N条记录（可配置）                                            │
│  ├── 触发条件: 自动触发                                                       │
│  ├── 保存内容: 执行状态、Token消耗、任务进度                                   │
│  └── 用途: 系统崩溃恢复、Token耗尽暂停                                        │
│                                                                             │
│  Layer 2: 处理器层 (Handler Checkpoint)                                      │
│  ├── 保存间隔: 处理器决定                                                     │
│  ├── 触发条件: 处理器回调                                                     │
│  ├── 保存内容: 处理器私有状态                                                 │
│  └── 用途: 复杂任务的中间状态恢复                                             │
│                                                                             │
│  Layer 3: 用户层 (User Checkpoint)                                           │
│  ├── 保存间隔: 用户手动触发                                                   │
│  ├── 触发条件: 用户命令                                                       │
│  ├── 保存内容: 完整快照                                                       │
│  └── 用途: 重要里程碑、手动干预点                                             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. 核心组件

### 2.1 Checkpoint管理器

```python
# checkpoint/manager.py
import asyncio
import json
from typing import Optional, Dict, Any, List, Callable
from datetime import datetime, timedelta
from pathlib import Path

class CheckpointManager:
    """
    Checkpoint管理器 - 核心组件
    
    职责:
    1. Checkpoint创建和保存
    2. Checkpoint加载和恢复
    3. Checkpoint清理和过期管理
    4. 恢复协调
    """
    
    def __init__(self, config: CheckpointConfig):
        self.config = config
        self.storage = self._init_storage(config.storage_type)
        self.index = CheckpointIndex()
        self._active_checkpoints: Dict[str, Checkpoint] = {}
        self._save_hooks: List[Callable] = []
        
    def _init_storage(self, storage_type: str) -> CheckpointStorage:
        """初始化存储后端"""
        if storage_type == "file":
            return FileCheckpointStorage(self.config.path)
        elif storage_type == "redis":
            return RedisCheckpointStorage(self.config.redis_url)
        elif storage_type == "database":
            return DatabaseCheckpointStorage(self.config.db_url)
        else:
            raise ValueError(f"Unknown storage type: {storage_type}")
    
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
    ) -> Checkpoint:
        """创建Checkpoint"""
        
        checkpoint = Checkpoint(
            checkpoint_id=self._generate_id(),
            name=name or f"checkpoint_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            task_id=task_id,
            batch_id=batch_id,
            execution_state=state or {},
            expires_at=datetime.now() + timedelta(days=self.config.ttl_days),
        )
        
        # 执行保存钩子
        for hook in self._save_hooks:
            await hook(checkpoint)
        
        # 持久化
        await self.storage.save(checkpoint)
        
        # 更新索引
        self.index.add_checkpoint(checkpoint)
        self._active_checkpoints[checkpoint.checkpoint_id] = checkpoint
        
        return checkpoint
    
    async def create_periodic_checkpoint(
        self,
        executor_state: ExecutorState,
        force: bool = False
    ) -> Optional[Checkpoint]:
        """
        创建周期性Checkpoint
        
        Args:
            executor_state: 执行器当前状态
            force: 强制创建（忽略间隔检查）
        """
        # 检查间隔
        if not force and not self._should_checkpoint(executor_state):
            return None
            
        checkpoint = await self.create_checkpoint(
            batch_id=executor_state.batch_id,
            name=f"periodic_{executor_state.progress:.0%}",
            level="system",
            state={
                "progress": executor_state.progress,
                "processed_count": len(executor_state.processed_tasks),
                "current_task": executor_state.current_task,
                "token_consumed": executor_state.token_consumed,
            }
        )
        
        # 更新最后检查点时间
        executor_state.last_checkpoint_at = datetime.now()
        
        return checkpoint
    
    def _should_checkpoint(self, state: ExecutorState) -> bool:
        """检查是否应该创建Checkpoint"""
        if state.last_checkpoint_at is None:
            return True
            
        # 基于数量的检查
        if len(state.processed_tasks) - state.last_checkpoint_task_count >= self.config.interval:
            return True
            
        # 基于时间的检查（每5分钟）
        if datetime.now() - state.last_checkpoint_at > timedelta(minutes=5):
            return True
            
        return False
    
    # ─────────────────────────────────────────────────────────────────
    # Checkpoint恢复
    # ─────────────────────────────────────────────────────────────────
    
    async def resume_from_checkpoint(
        self,
        checkpoint_id: str,
        executor: TaskExecutor,
        token_engine: TokenEngine,
    ) -> ResumeResult:
        """
        从Checkpoint恢复执行
        
        这是核心恢复逻辑，支持：
        1. 状态重构
        2. Token预算调整
        3. 任务续传
        4. 版本兼容
        """
        
        # 1. 加载Checkpoint
        checkpoint = await self.storage.load(checkpoint_id)
        if not checkpoint:
            raise CheckpointNotFoundError(f"Checkpoint not found: {checkpoint_id}")
        
        if checkpoint.is_expired():
            raise CheckpointExpiredError(f"Checkpoint expired: {checkpoint_id}")
        
        # 2. 版本检查和迁移
        if checkpoint.version != CURRENT_VERSION:
            checkpoint = await self._migrate_checkpoint(checkpoint)
        
        # 3. 恢复Token状态
        token_engine.budget.consumed = checkpoint.token_consumed
        token_engine.budget.reserved = self._calculate_reserved(checkpoint)
        
        # 4. 重构执行状态
        executor_state = self._reconstruct_state(checkpoint)
        
        # 5. 更新恢复计数
        checkpoint.resume_count += 1
        checkpoint.last_resume_at = datetime.now()
        await self.storage.save(checkpoint)
        
        # 6. 返回恢复结果
        return ResumeResult(
            success=True,
            checkpoint=checkpoint,
            executor_state=executor_state,
            remaining_tasks=checkpoint.pending_task_ids,
            token_remaining=token_engine.budget.available,
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
    
    async def list_resumable(
        self,
        category: Optional[str] = None,
    ) -> List[CheckpointSummary]:
        """列出所有可恢复的Checkpoint"""
        checkpoints = await self.storage.list_all()
        resumable = [cp for cp in checkpoints if cp.is_resumable()]
        
        if category:
            # 根据task_id过滤
            resumable = [cp for cp in resumable 
                        if self._get_task_category(cp.task_id) == category]
        
        return [self._summarize(cp) for cp in resumable]
    
    # ─────────────────────────────────────────────────────────────────
    # 状态迁移
    # ─────────────────────────────────────────────────────────────────
    
    async def _migrate_checkpoint(
        self,
        checkpoint: Checkpoint,
        target_version: str = CURRENT_VERSION
    ) -> Checkpoint:
        """
        Checkpoint版本迁移
        
        支持跨版本恢复的关键机制
        """
        from upgrade.migration_engine import MigrationEngine
        
        engine = MigrationEngine()
        migrated_state = await engine.migrate_checkpoint(
            checkpoint.execution_state,
            target_version
        )
        
        checkpoint.execution_state = migrated_state
        checkpoint.version = target_version
        checkpoint.schema_version = CURRENT_SCHEMA_VERSION
        
        return checkpoint
    
    # ─────────────────────────────────────────────────────────────────
    # 清理和过期管理
    # ─────────────────────────────────────────────────────────────────
    
    async def cleanup_expired(self) -> int:
        """清理过期Checkpoint"""
        all_checkpoints = await self.storage.list_all()
        expired = [cp for cp in all_checkpoints if cp.is_expired()]
        
        for cp in expired:
            await self.storage.delete(cp.checkpoint_id)
            
        return len(expired)
    
    async def cleanup_completed(self, keep_days: int = 7) -> int:
        """清理已完成且超过保留期的Checkpoint"""
        cutoff = datetime.now() - timedelta(days=keep_days)
        all_checkpoints = await self.storage.list_all()
        
        to_delete = [
            cp for cp in all_checkpoints
            if cp.status == "completed" and cp.completed_at and cp.completed_at < cutoff
        ]
        
        for cp in to_delete:
            await self.storage.delete(cp.checkpoint_id)
            
        return len(to_delete)
    
    # ─────────────────────────────────────────────────────────────────
    # 事件处理
    # ─────────────────────────────────────────────────────────────────
    
    def register_save_hook(self, hook: Callable[[Checkpoint], None]):
        """注册保存钩子"""
        self._save_hooks.append(hook)
```

### 2.2 存储抽象

```python
# checkpoint/storage.py
from abc import ABC, abstractmethod

class CheckpointStorage(ABC):
    """Checkpoint存储抽象基类"""
    
    @abstractmethod
    async def save(self, checkpoint: Checkpoint) -> None:
        """保存Checkpoint"""
        pass
    
    @abstractmethod
    async def load(self, checkpoint_id: str) -> Optional[Checkpoint]:
        """加载Checkpoint"""
        pass
    
    @abstractmethod
    async def delete(self, checkpoint_id: str) -> None:
        """删除Checkpoint"""
        pass
    
    @abstractmethod
    async def list_all(self) -> List[Checkpoint]:
        """列出所有Checkpoint"""
        pass

class FileCheckpointStorage(CheckpointStorage):
    """文件存储实现"""
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        
    async def save(self, checkpoint: Checkpoint) -> None:
        path = self.base_path / f"{checkpoint.checkpoint_id}.json"
        async with aiofiles.open(path, "w") as f:
            await f.write(json.dumps(checkpoint.to_dict(), indent=2))
    
    async def load(self, checkpoint_id: str) -> Optional[Checkpoint]:
        path = self.base_path / f"{checkpoint_id}.json"
        if not path.exists():
            return None
        async with aiofiles.open(path) as f:
            data = json.loads(await f.read())
        return Checkpoint.from_dict(data)
    
    async def delete(self, checkpoint_id: str) -> None:
        path = self.base_path / f"{checkpoint_id}.json"
        if path.exists():
            path.unlink()
    
    async def list_all(self) -> List[Checkpoint]:
        checkpoints = []
        for path in self.base_path.glob("*.json"):
            async with aiofiles.open(path) as f:
                data = json.loads(await f.read())
            checkpoints.append(Checkpoint.from_dict(data))
        return checkpoints

class RedisCheckpointStorage(CheckpointStorage):
    """Redis存储实现 - 支持分布式"""
    
    def __init__(self, redis_url: str):
        import aioredis
        self.redis = aioredis.from_url(redis_url)
        self.key_prefix = "checkpoint:"
        
    async def save(self, checkpoint: Checkpoint) -> None:
        key = f"{self.key_prefix}{checkpoint.checkpoint_id}"
        await self.redis.set(
            key, 
            json.dumps(checkpoint.to_dict()),
            ex=int((checkpoint.expires_at - datetime.now()).total_seconds()) if checkpoint.expires_at else None
        )
    
    async def load(self, checkpoint_id: str) -> Optional[Checkpoint]:
        key = f"{self.key_prefix}{checkpoint_id}"
        data = await self.redis.get(key)
        if not data:
            return None
        return Checkpoint.from_dict(json.loads(data))
```

---

## 3. 暂停/恢复流程

### 3.1 暂停流程

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              暂停流程                                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  触发源                                                                       │
│    │                                                                         │
│    ├── 用户命令: `executor.pause()`                                         │
│    ├── 信号: SIGTERM/SIGINT                                                  │
│    ├── Token耗尽: level=L1                                                   │
│    ├── 错误: 连续失败N次                                                      │
│    └── 定时: 执行时间超过阈值                                                  │
│    │                                                                         │
│    ▼                                                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  1. 暂停信号处理                                                     │    │
│  │     - 设置暂停标志位                                                  │    │
│  │     - 通知执行器停止接收新任务                                          │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│    │                                                                         │
│    ▼                                                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  2. 等待当前任务完成                                                  │    │
│  │     - 设置超时(30秒)                                                  │    │
│  │     - 超时后强制终止当前任务                                           │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│    │                                                                         │
│    ▼                                                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  3. 保存Checkpoint                                                   │    │
│  │     - 收集执行状态                                                    │    │
│  │     - 保存Token消耗                                                   │    │
│  │     - 保存处理器私有状态                                               │    │
│  │     - 持久化到存储                                                    │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│    │                                                                         │
│    ▼                                                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  4. 生成暂停报告                                                     │    │
│  │     - 已完成任务数                                                    │    │
│  │     - 待处理任务数                                                    │    │
│  │     - Token消耗情况                                                   │    │
│  │     - 恢复命令                                                        │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│    │                                                                         │
│    ▼                                                                         │
│  完成暂停                                                                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 恢复流程

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              恢复流程                                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  恢复源                                                                       │
│    │                                                                         │
│    ├── 用户命令: `executor.resume(checkpoint_id)`                           │
│    ├── 自动恢复: 系统重启后                                                   │
│    └── Token恢复: 预算补充后                                                  │
│    │                                                                         │
│    ▼                                                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  1. 加载Checkpoint                                                   │    │
│  │     - 验证Checkpoint存在                                              │    │
│  │     - 检查是否过期                                                    │    │
│  │     - 验证完整性                                                      │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│    │                                                                         │
│    ▼                                                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  2. 版本迁移（如果需要）                                                │    │
│  │     - 检查版本兼容性                                                   │    │
│  │     - 执行数据迁移                                                    │    │
│  │     - 更新Schema版本                                                  │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│    │                                                                         │
│    ▼                                                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  3. 重构执行状态                                                      │    │
│  │     - 恢复Token预算                                                   │    │
│  │     - 重建任务队列                                                    │    │
│  │     - 恢复处理器状态                                                  │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│    │                                                                         │
│    ▼                                                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  4. 验证恢复状态                                                      │    │
│  │     - 检查待处理任务是否仍然有效                                         │    │
│  │     - 验证依赖是否满足                                                  │    │
│  │     - 检查外部环境变化                                                  │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│    │                                                                         │
│    ▼                                                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  5. 继续执行                                                         │    │
│  │     - 从断点继续处理任务                                               │    │
│  │     - 更新Checkpoint统计                                               │    │
│  │     - 记录恢复事件                                                    │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│    │                                                                         │
│    ▼                                                                         │
│  恢复完成                                                                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. 处理器集成

### 4.1 处理器Checkpoint接口

```python
# checkpoint/handler_integration.py
class CheckpointableHandler(TaskHandler):
    """
    支持Checkpoint的处理器基类
    
    处理器需要实现以下方法来支持Checkpoint
    """
    
    @abstractmethod
    def get_checkpoint_state(self) -> Dict[str, Any]:
        """
        获取处理器状态用于Checkpoint
        
        返回的状态必须是JSON可序列化的
        """
        pass
    
    @abstractmethod
    def restore_from_checkpoint(self, state: Dict[str, Any]) -> None:
        """
        从Checkpoint状态恢复
        
        恢复后处理器应能从断点继续执行
        """
        pass
    
    def should_checkpoint(self, context: TaskContext) -> bool:
        """
        判断是否应该创建Checkpoint
        
        处理器可以根据自身逻辑决定
        """
        # 默认每5条记录
        return context.processed_count % 5 == 0
```

### 4.2 集成示例

```python
# handlers/audit_handler.py
class AuditHandler(CheckpointableHandler):
    """审计处理器 - 支持Checkpoint"""
    
    def __init__(self):
        self.current_step = 0
        self.processed_records = []
        self.failed_records = []
        self.audit_results = {}
    
    def get_checkpoint_state(self) -> Dict[str, Any]:
        """保存审计进度"""
        return {
            "current_step": self.current_step,
            "processed_records": self.processed_records,
            "failed_records": self.failed_records,
            "audit_results": self.audit_results,
            "step_progress": {
                "step1_classify": self.step1_progress,
                "step2_setup": self.step2_progress,
                # ...其他步骤
            }
        }
    
    def restore_from_checkpoint(self, state: Dict[str, Any]) -> None:
        """恢复审计进度"""
        self.current_step = state["current_step"]
        self.processed_records = state["processed_records"]
        self.failed_records = state["failed_records"]
        self.audit_results = state["audit_results"]
        
        # 恢复各步骤进度
        step_progress = state.get("step_progress", {})
        self.step1_progress = step_progress.get("step1_classify", 0)
        # ...
    
    async def execute(self, context: TaskContext) -> Iterator[TaskResult]:
        """执行审计（支持断点续传）"""
        
        # 如果有Checkpoint状态，恢复
        if context.checkpoint_state:
            self.restore_from_checkpoint(context.checkpoint_state)
            yield TaskResult(
                task_id=context.task_id,
                status="resumed",
                output={"message": f"从步骤{self.current_step}恢复"},
                token_consumed=0,
                time_elapsed=0
            )
        
        # 从当前步骤继续
        steps = [
            self._step1_classify,
            self._step2_setup_dirs,
            self._step3_audit_p0,
            self._step4_audit_p1,
            self._step5_process_p2,
            self._step5_5_blue_army,
            self._step6_fix_issues,
            self._step7_extract_methodology,
            self._step8_generate_report,
            self._step9_user_acceptance,
        ]
        
        for step_index, step_func in enumerate(steps[self.current_step:], start=self.current_step):
            self.current_step = step_index
            
            async for result in step_func(context):
                yield result
                
                # 检查是否需要Checkpoint
                if self.should_checkpoint(context):
                    yield TaskResult(
                        task_id=context.task_id,
                        status="checkpoint",
                        output={"state": self.get_checkpoint_state()},
                        token_consumed=0,
                        time_elapsed=0
                    )
```

---

## 5. 自动恢复机制

### 5.1 系统启动恢复

```python
# checkpoint/auto_recovery.py
class AutoRecovery:
    """自动恢复服务"""
    
    def __init__(self, checkpoint_manager: CheckpointManager):
        self.checkpoint_manager = checkpoint_manager
        self.recovery_handlers: Dict[str, Callable] = {}
    
    async def check_and_recover(self) -> List[RecoveryResult]:
        """
        系统启动时检查并恢复未完成的任务
        
        Returns:
            恢复结果列表
        """
        results = []
        
        # 获取所有可恢复的Checkpoint
        resumable = await self.checkpoint_manager.list_resumable()
        
        for cp_summary in resumable:
            # 检查是否应该自动恢复
            if not self._should_auto_recover(cp_summary):
                continue
            
            try:
                # 执行恢复
                result = await self._recover_checkpoint(cp_summary.checkpoint_id)
                results.append(result)
            except Exception as e:
                results.append(RecoveryResult(
                    checkpoint_id=cp_summary.checkpoint_id,
                    success=False,
                    error=str(e)
                ))
        
        return results
    
    def _should_auto_recover(self, cp: CheckpointSummary) -> bool:
        """判断是否应自动恢复"""
        # P0任务自动恢复
        if cp.priority == "p0":
            return True
        
        # 用户标记为重要
        if cp.tags and "important" in cp.tags:
            return True
        
        # Token充足时恢复
        # (需要检查当前Token预算)
        
        return False
    
    async def _recover_checkpoint(self, checkpoint_id: str) -> RecoveryResult:
        """恢复单个Checkpoint"""
        # 使用CheckpointManager恢复
        resume_result = await self.checkpoint_manager.resume_from_checkpoint(
            checkpoint_id,
            executor=self.executor,
            token_engine=self.token_engine
        )
        
        # 通知用户
        await self._notify_recovery(resume_result)
        
        return RecoveryResult(
            checkpoint_id=checkpoint_id,
            success=True,
            remaining_tasks=len(resume_result.remaining_tasks),
            token_remaining=resume_result.token_remaining
        )
```

---

## 6. 配置示例

```yaml
# config/checkpoint.yaml
checkpoint:
  # 基础配置
  enabled: true
  storage_type: "file"  # file/redis/database
  path: "memory/checkpoints/"
  
  # 创建策略
  interval: 5  # 每5条记录自动创建
  time_interval: 300  # 每5分钟强制创建
  on_error: true  # 出错时自动创建
  on_pause: true  # 暂停时自动创建
  
  # 保留策略
  ttl_days: 30  # 默认保留30天
  keep_completed: 7  # 已完成的保留7天
  max_checkpoints_per_task: 10  # 单任务最大Checkpoint数
  
  # 恢复策略
  auto_recover: true  # 启动时自动恢复
  auto_recover_priority: ["p0", "p1"]  # 自动恢复的优先级
  recover_timeout: 60  # 恢复超时(秒)
  
  # 压缩配置
  compression: true  # 启用压缩
  compression_level: 6  # 压缩级别
  
  # 加密配置（可选）
  encryption: false
  # encryption_key: "${CHECKPOINT_ENCRYPTION_KEY}"
  
  # Redis配置（当storage_type=redis时）
  redis:
    url: "redis://localhost:6379/0"
    key_prefix: "checkpoint:"
    
  # 数据库配置（当storage_type=database时）
  database:
    url: "postgresql://user:pass@localhost/executor"
    table: "checkpoints"
```

---

## 7. CLI命令

```bash
# Checkpoint管理CLI

# 列出所有可恢复的Checkpoint
executor checkpoint list [--category category_6] [--status active]

# 查看Checkpoint详情
executor checkpoint show <checkpoint_id>

# 从指定Checkpoint恢复
executor checkpoint resume <checkpoint_id> [--token-budget 50000]

# 恢复最新的Checkpoint
executor checkpoint resume-latest [--task-id <id>] [--batch-id <id>]

# 删除Checkpoint
executor checkpoint delete <checkpoint_id>

# 清理过期Checkpoint
executor checkpoint cleanup [--expired] [--completed]

# 导出Checkpoint
executor checkpoint export <checkpoint_id> --output checkpoint.json

# 导入Checkpoint
executor checkpoint import checkpoint.json
```

---

## 8. 状态机

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Checkpoint状态机                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│                              ┌──────────┐                                   │
│                              │  CREATE  │                                   │
│                              └────┬─────┘                                   │
│                                   │                                         │
│                                   ▼                                         │
│  ┌─────────┐    pause/resume    ┌──────────┐     complete     ┌──────────┐ │
│  │  PAUSED │◄──────────────────►│  ACTIVE  │───────────────►  │ COMPLETED│ │
│  └─────────┘                    └────┬─────┘                  └──────────┘ │
│                                      │                                      │
│                                      │ fail                                 │
│                                      ▼                                      │
│                                 ┌──────────┐                                │
│                                 │  FAILED  │                                │
│                                 └────┬─────┘                                │
│                                      │                                      │
│                                      │ retry                                │
│                                      ▼                                      │
│                                 ┌──────────┐                                │
│                                 │  ACTIVE  │                                │
│                                 └──────────┘                                │
│                                                                             │
│  所有状态 ──────────────────────► ┌──────────┐                              │
│              expire               │ EXPIRED  │                              │
│                                   └──────────┘                              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

**暂停/重启机制设计完成** | 2026-03-31 | V3.0.0
