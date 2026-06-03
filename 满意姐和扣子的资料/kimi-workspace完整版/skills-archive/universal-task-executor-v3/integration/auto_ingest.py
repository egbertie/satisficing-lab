"""
Auto Ingest - 自动入库触发器
集成super-knowledge-ingest Skill到Universal Task Executor V3.0

职责：
1. 每处理完任务自动触发入库
2. 支持配置化入库策略
3. 入库失败自动重试
4. 与TaskEngine生命周期集成
"""

import os
import json
import logging
import asyncio
from typing import Dict, List, Optional, Any, Callable, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum

try:
    from ..core.structures import Task, TaskResult, TaskStatus
except ImportError:
    # 支持直接运行测试
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from core.structures import Task, TaskResult, TaskStatus

from .knowledge_bridge import KnowledgeBridge, IngestResult, BatchIngestResult

logger = logging.getLogger(__name__)


class IngestTrigger(Enum):
    """入库触发时机"""
    TASK_COMPLETE = "task_complete"      # 单个任务完成
    BATCH_COMPLETE = "batch_complete"    # 批次完成
    SCHEDULED = "scheduled"              # 定时触发
    MANUAL = "manual"                    # 手动触发
    ON_FAILURE = "on_failure"            # 失败时触发（用于错误记录）


class IngestStrategy(Enum):
    """入库策略"""
    IMMEDIATE = "immediate"      # 立即入库
    DEFERRED = "deferred"        # 延迟入库（批量）
    SELECTIVE = "selective"      # 选择性入库（按规则）
    DISABLED = "disabled"        # 禁用自动入库


@dataclass
class IngestPolicy:
    """入库策略配置"""
    # 触发时机
    trigger: IngestTrigger = IngestTrigger.TASK_COMPLETE
    
    # 执行策略
    strategy: IngestStrategy = IngestStrategy.IMMEDIATE
    
    # 选择性入库规则（当strategy=SELECTIVE时使用）
    include_categories: List[str] = field(default_factory=lambda: [
        "category_3", "category_4", "category_5", "category_6"
    ])
    exclude_patterns: List[str] = field(default_factory=list)  # 排除的文件模式
    min_file_size: int = 0  # 最小文件大小（字节）
    max_file_size: int = 10 * 1024 * 1024  # 最大文件大小（10MB）
    
    # 延迟入库配置
    deferred_batch_size: int = 10  # 延迟批大小
    deferred_delay_seconds: int = 60  # 延迟等待时间
    
    # 重试配置
    max_retries: int = 3
    retry_backoff: List[int] = field(default_factory=lambda: [1, 2, 4])  # 重试间隔
    
    # Token控制
    max_tokens_per_auto_ingest: int = 10000  # 单次自动入库Token上限
    
    def should_ingest_task(self, task: Task) -> bool:
        """检查任务是否应该入库"""
        if self.strategy == IngestStrategy.DISABLED:
            return False
        
        if task.category not in self.include_categories:
            return False
        
        return True
    
    def should_ingest_file(self, file_path: str) -> bool:
        """检查文件是否应该入库"""
        path = Path(file_path)
        
        # 检查排除模式
        for pattern in self.exclude_patterns:
            if pattern in file_path:
                return False
        
        # 检查文件大小
        if not path.exists():
            return False
        
        size = path.stat().st_size
        if size < self.min_file_size or size > self.max_file_size:
            return False
        
        return True


@dataclass
class IngestRecord:
    """入库记录"""
    record_id: str = field(default_factory=lambda: f"ingest_{datetime.now().strftime('%Y%m%d%H%M%S')}")
    task_id: Optional[str] = None
    trigger: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    
    # 文件信息
    source_files: List[str] = field(default_factory=list)
    ingested_files: List[str] = field(default_factory=list)
    failed_files: List[Dict[str, str]] = field(default_factory=list)
    
    # 结果统计
    success: bool = False
    token_consumed: int = 0
    duration_ms: float = 0
    
    # 重试信息
    retry_count: int = 0
    retry_history: List[Dict] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "record_id": self.record_id,
            "task_id": self.task_id,
            "trigger": self.trigger,
            "timestamp": self.timestamp.isoformat(),
            "source_files": self.source_files,
            "ingested_files": self.ingested_files,
            "failed_files": self.failed_files,
            "success": self.success,
            "token_consumed": self.token_consumed,
            "duration_ms": self.duration_ms,
            "retry_count": self.retry_count,
            "retry_history": self.retry_history,
        }


class AutoIngestor:
    """
    自动入库触发器
    
    与TaskEngine集成，自动将任务输出入库到知识库
    """
    
    def __init__(self, 
                 knowledge_bridge: KnowledgeBridge = None,
                 policy: IngestPolicy = None):
        self.bridge = knowledge_bridge or KnowledgeBridge()
        self.policy = policy or IngestPolicy()
        
        # 延迟入库队列
        self._deferred_queue: List[str] = []
        self._deferred_task_id: Optional[str] = None
        self._deferred_timer: Optional[asyncio.Task] = None
        
        # 记录
        self._records: List[IngestRecord] = []
        self._records_file = Path("memory/auto_ingest_records.json")
        self._load_records()
        
        # 统计
        self._stats = {
            "total_triggers": 0,
            "total_files_ingested": 0,
            "total_tokens_consumed": 0,
            "failed_count": 0,
        }
        
        # 回调
        self._on_ingest_complete: Optional[Callable[[IngestRecord], None]] = None
        
    def _load_records(self) -> None:
        """加载历史记录"""
        if self._records_file.exists():
            try:
                with open(self._records_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._records = [IngestRecord(**r) for r in data.get("records", [])]
                logger.info(f"Loaded {len(self._records)} auto-ingest records")
            except Exception as e:
                logger.warning(f"Failed to load records: {e}")
    
    def _save_records(self) -> None:
        """保存记录"""
        self._records_file.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(self._records_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "records": [r.to_dict() for r in self._records[-100:]]  # 保留最近100条
                }, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save records: {e}")
    
    def set_policy(self, policy: IngestPolicy) -> None:
        """设置入库策略"""
        self.policy = policy
        logger.info(f"Auto-ingest policy updated: {policy.strategy.value}")
    
    def on_ingest_complete(self, callback: Callable[[IngestRecord], None]) -> None:
        """注册入库完成回调"""
        self._on_ingest_complete = callback
    
    async def trigger_on_task_complete(self, 
                                       task: Task, 
                                       task_result: TaskResult) -> Optional[IngestRecord]:
        """
        任务完成时触发入库
        
        Args:
            task: 完成的任务
            task_result: 任务执行结果
            
        Returns:
            IngestRecord: 入库记录（如果触发）
        """
        if self.policy.strategy == IngestStrategy.DISABLED:
            return None
        
        if not self.policy.should_ingest_task(task):
            return None
        
        # 检查是否有输出文件
        output_files = self._extract_output_files(task, task_result)
        if not output_files:
            logger.debug(f"No output files to ingest for task {task.task_id}")
            return None
        
        self._stats["total_triggers"] += 1
        
        # 根据策略处理
        if self.policy.strategy == IngestStrategy.IMMEDIATE:
            return await self._ingest_immediate(task.task_id, output_files, IngestTrigger.TASK_COMPLETE)
        
        elif self.policy.strategy == IngestStrategy.DEFERRED:
            return await self._ingest_deferred(task.task_id, output_files)
        
        elif self.policy.strategy == IngestStrategy.SELECTIVE:
            # 选择性过滤
            filtered_files = [f for f in output_files if self.policy.should_ingest_file(f)]
            if filtered_files:
                return await self._ingest_immediate(task.task_id, filtered_files, IngestTrigger.TASK_COMPLETE)
            return None
        
        return None
    
    async def trigger_on_batch_complete(self, 
                                        task_results: List[TaskResult]) -> Optional[IngestRecord]:
        """
        批次完成时触发入库
        
        Args:
            task_results: 批次中所有任务的结果
            
        Returns:
            IngestRecord: 入库记录
        """
        if self.policy.strategy == IngestStrategy.DISABLED:
            return None
        
        # 收集所有输出文件
        all_files: Set[str] = set()
        for result in task_results:
            files = self._extract_output_files_from_result(result)
            all_files.update(files)
        
        if not all_files:
            return None
        
        self._stats["total_triggers"] += 1
        
        return await self._ingest_immediate(
            "batch", 
            list(all_files), 
            IngestTrigger.BATCH_COMPLETE
        )
    
    def trigger_manual(self, file_paths: List[str], task_id: str = None) -> IngestRecord:
        """
        手动触发入库
        
        Args:
            file_paths: 要入库的文件路径
            task_id: 关联的任务ID
            
        Returns:
            IngestRecord: 入库记录
        """
        return asyncio.run(self._ingest_immediate(
            task_id or "manual",
            file_paths,
            IngestTrigger.MANUAL
        ))
    
    async def _ingest_immediate(self, 
                                task_id: str, 
                                file_paths: List[str],
                                trigger: IngestTrigger) -> IngestRecord:
        """
        立即入库
        
        Args:
            task_id: 任务ID
            file_paths: 文件路径列表
            trigger: 触发类型
            
        Returns:
            IngestRecord: 入库记录
        """
        start_time = datetime.now()
        record = IngestRecord(
            task_id=task_id,
            trigger=trigger.value,
            source_files=file_paths,
        )
        
        logger.info(f"Auto-ingest triggered [{trigger.value}]: {len(file_paths)} files for task {task_id}")
        
        # 执行入库（带重试）
        result = await self._ingest_with_retry(file_paths, record)
        
        # 记录结果
        record.duration_ms = (datetime.now() - start_time).total_seconds() * 1000
        record.success = result.success_count > 0 or result.skipped_count > 0
        record.token_consumed = result.token_consumed_total
        
        for r in result.results:
            if r.success and r.output_file:
                record.ingested_files.append(r.output_file)
            elif not r.success:
                record.failed_files.append({
                    "file": r.file_path,
                    "error": r.error or "Unknown error"
                })
        
        # 更新统计
        self._stats["total_files_ingested"] += len(record.ingested_files)
        self._stats["total_tokens_consumed"] += record.token_consumed
        if not record.success:
            self._stats["failed_count"] += 1
        
        # 保存记录
        self._records.append(record)
        self._save_records()
        
        # 触发回调
        if self._on_ingest_complete:
            self._on_ingest_complete(record)
        
        logger.info(f"Auto-ingest completed: {len(record.ingested_files)} success, "
                   f"{len(record.failed_files)} failed, "
                   f"{record.token_consumed} tokens")
        
        return record
    
    async def _ingest_with_retry(self, 
                                  file_paths: List[str],
                                  record: IngestRecord) -> BatchIngestResult:
        """
        带重试的入库
        
        Args:
            file_paths: 文件路径列表
            record: 入库记录（用于更新重试历史）
            
        Returns:
            BatchIngestResult: 入库结果
        """
        retry_count = 0
        last_result = None
        failed_files = file_paths.copy()
        
        while retry_count <= self.policy.max_retries and failed_files:
            # 执行入库
            result = await self.bridge.ingest_batch(failed_files)
            last_result = result
            
            # 检查失败的文件
            new_failed = []
            for r in result.results:
                if not r.success:
                    new_failed.append(r.file_path)
            
            if not new_failed:
                # 全部成功
                break
            
            if retry_count < self.policy.max_retries:
                # 记录重试
                record.retry_history.append({
                    "attempt": retry_count + 1,
                    "failed_count": len(new_failed),
                    "timestamp": datetime.now().isoformat(),
                })
                
                # 等待后重试
                delay = self.policy.retry_backoff[min(retry_count, len(self.policy.retry_backoff) - 1)]
                logger.warning(f"Ingest retry {retry_count + 1}/{self.policy.max_retries}: "
                              f"{len(new_failed)} files failed, waiting {delay}s")
                await asyncio.sleep(delay)
                failed_files = new_failed
            
            retry_count += 1
            record.retry_count = retry_count
        
        return last_result or BatchIngestResult(batch_id="", total_files=0, success_count=0, failed_count=0)
    
    async def _ingest_deferred(self, 
                               task_id: str, 
                               file_paths: List[str]) -> Optional[IngestRecord]:
        """
        延迟入库
        
        将文件加入队列，等待批量处理
        """
        # 如果是新的任务，先处理之前的队列
        if self._deferred_task_id and self._deferred_task_id != task_id:
            if self._deferred_queue:
                # 立即处理之前的队列
                if self._deferred_timer:
                    self._deferred_timer.cancel()
                await self._flush_deferred_queue()
        
        # 添加到队列
        self._deferred_task_id = task_id
        self._deferred_queue.extend(file_paths)
        
        # 如果达到批大小，立即处理
        if len(self._deferred_queue) >= self.policy.deferred_batch_size:
            return await self._flush_deferred_queue()
        
        # 否则启动定时器
        if self._deferred_timer is None or self._deferred_timer.done():
            self._deferred_timer = asyncio.create_task(
                self._deferred_timer_task(task_id)
            )
        
        return None  # 延迟入库不立即返回记录
    
    async def _deferred_timer_task(self, task_id: str) -> None:
        """延迟入库定时器任务"""
        await asyncio.sleep(self.policy.deferred_delay_seconds)
        if self._deferred_queue:
            await self._flush_deferred_queue()
    
    async def _flush_deferred_queue(self) -> Optional[IngestRecord]:
        """刷新延迟队列"""
        if not self._deferred_queue:
            return None
        
        files = self._deferred_queue.copy()
        self._deferred_queue = []
        
        return await self._ingest_immediate(
            self._deferred_task_id or "deferred",
            files,
            IngestTrigger.SCHEDULED
        )
    
    def _extract_output_files(self, task: Task, task_result: TaskResult) -> List[str]:
        """从任务结果中提取输出文件路径"""
        files: List[str] = []
        
        # 从task.extra中获取输出文件
        if task.extra:
            output_files = task.extra.get("output_files", [])
            if isinstance(output_files, list):
                files.extend(output_files)
        
        # 从task_result.output中获取
        if task_result.output:
            # 检查常见的输出字段
            for key in ["output_file", "output_path", "generated_file", "saved_path"]:
                if key in task_result.output:
                    val = task_result.output[key]
                    if isinstance(val, str):
                        files.append(val)
                    elif isinstance(val, list):
                        files.extend(val)
            
            # 检查report中的文件
            if "report" in task_result.output:
                report = task_result.output["report"]
                if isinstance(report, dict):
                    for key in ["files", "attachments", "outputs"]:
                        if key in report:
                            files.extend(report[key])
        
        # 过滤存在的文件
        valid_files = [f for f in files if Path(f).exists()]
        
        # 过滤支持的类型
        valid_files = [f for f in valid_files 
                      if Path(f).suffix.lower() in self.bridge.config.supported_extensions]
        
        return list(set(valid_files))  # 去重
    
    def _extract_output_files_from_result(self, task_result: TaskResult) -> List[str]:
        """从任务结果中提取输出文件路径（简化版）"""
        files: List[str] = []
        
        if task_result.output:
            for key in ["output_file", "output_path", "generated_file", "saved_path", "files"]:
                if key in task_result.output:
                    val = task_result.output[key]
                    if isinstance(val, str):
                        files.append(val)
                    elif isinstance(val, list):
                        files.extend(val)
        
        valid_files = [f for f in files if Path(f).exists()]
        valid_files = [f for f in valid_files 
                      if Path(f).suffix.lower() in self.bridge.config.supported_extensions]
        
        return list(set(valid_files))
    
    async def shutdown(self) -> None:
        """关闭时刷新所有延迟队列"""
        if self._deferred_queue:
            logger.info(f"Flushing {len(self._deferred_queue)} deferred files on shutdown")
            await self._flush_deferred_queue()
        
        if self._deferred_timer and not self._deferred_timer.done():
            self._deferred_timer.cancel()
            try:
                await self._deferred_timer
            except asyncio.CancelledError:
                pass
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            **self._stats,
            "deferred_queue_size": len(self._deferred_queue),
            "policy": {
                "trigger": self.policy.trigger.value,
                "strategy": self.policy.strategy.value,
            },
            "bridge_stats": self.bridge.get_stats(),
        }
    
    def get_records(self, 
                    task_id: Optional[str] = None,
                    limit: int = 50) -> List[IngestRecord]:
        """获取入库记录"""
        records = self._records
        if task_id:
            records = [r for r in records if r.task_id == task_id]
        return records[-limit:]


# 便捷函数
def create_auto_ingestor(policy_config: Dict[str, Any] = None) -> AutoIngestor:
    """创建自动入库触发器"""
    if policy_config:
        # 转换枚举值
        if "trigger" in policy_config:
            policy_config["trigger"] = IngestTrigger(policy_config["trigger"])
        if "strategy" in policy_config:
            policy_config["strategy"] = IngestStrategy(policy_config["strategy"])
        policy = IngestPolicy(**policy_config)
    else:
        policy = IngestPolicy()
    
    return AutoIngestor(policy=policy)
