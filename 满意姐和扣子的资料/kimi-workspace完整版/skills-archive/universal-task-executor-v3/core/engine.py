"""
Universal Task Executor V3.0 - 任务调度引擎
核心引擎，支持1-6类任务的统一接口、Token优化、暂停/重启
"""

import os
import sys
import json
import time
import logging
import asyncio
from typing import Dict, List, Optional, Any, Callable, Iterator
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from .structures import (
    Task, TaskBatch, TaskStatus, TaskPriority, TaskResult,
    ExecutorConfig, TokenLevel
)
from .token_engine import TokenEngine, TokenAwareScheduler, TokenLevelChangedEvent
from .registry import TaskRegistry, TaskHandler, get_registry
from .checkpoint import CheckpointManager, FileCheckpointStorage, ResumeResult
from .state_manager import StateManager, ExecutorState

logger = logging.getLogger(__name__)


@dataclass
class ExecutionContext:
    """执行上下文"""
    config: ExecutorConfig = field(default_factory=ExecutorConfig)
    checkpoint_id: Optional[str] = None
    resume_from: Optional[str] = None
    
    def __post_init__(self):
        if isinstance(self.config, dict):
            self.config = ExecutorConfig(**self.config)


class TaskEngine:
    """
    任务调度引擎 - Universal Task Executor V3.0 核心
    
    核心特性:
    1. 支持1-6类任务的统一接口
    2. Token档位自动切换 (L1-L5)
    3. 每5分钟自动保存Checkpoint
    4. 可插拔处理器架构
    5. 支持暂停/重启
    """
    
    def __init__(self, config: ExecutorConfig = None, plugin_path: str = None):
        """
        初始化任务引擎
        
        Args:
            config: 执行器配置
            plugin_path: 插件目录路径
        """
        self.config = config or ExecutorConfig()
        self.plugin_path = plugin_path or "plugins/handlers"
        
        # 初始化组件
        self._init_components()
        
        # 处理器缓存
        self._handler_cache: Dict[str, TaskHandler] = {}
        
        # 执行控制
        self._running = False
        self._pause_event = asyncio.Event()
        self._stop_event = asyncio.Event()
        
        # 回调
        self._task_complete_callbacks: List[Callable[[TaskResult], None]] = []
        self._checkpoint_callbacks: List[Callable[[str], None]] = []
        
        logger.info(f"TaskEngine initialized: v{self.config.version}")
    
    def _init_components(self) -> None:
        """初始化核心组件"""
        # Token引擎
        self.token_engine = TokenEngine(
            total_budget=self.config.token_default_budget,
            reserve_ratio=self.config.token_reserve_ratio
        )
        self.token_scheduler = TokenAwareScheduler(self.token_engine)
        
        # 注册Token档位变化观察者
        self.token_engine.add_observer(self._on_token_level_changed)
        
        # 注册表
        self.registry = get_registry(self.plugin_path)
        
        # Checkpoint管理器
        storage_path = self.config.checkpoint_path
        os.makedirs(storage_path, exist_ok=True)
        storage = FileCheckpointStorage(storage_path)
        self.checkpoint_manager = CheckpointManager(
            storage=storage,
            default_ttl_days=self.config.checkpoint_ttl_days,
            auto_save_interval=self.config.auto_save_interval_seconds
        )
        
        # 状态管理器
        self.state_manager = StateManager()
        self.state_manager.register_state_change_callback(self._on_state_changed)
    
    def _on_token_level_changed(self, event: TokenLevelChangedEvent) -> None:
        """Token档位变化回调"""
        logger.warning(f"Token level changed: {event.old_level.value} -> {event.new_level.value}")
        
        # L1档位暂停执行
        if event.new_level == TokenLevel.L1_HALT:
            logger.critical("Token level L1_HALT - Pausing execution")
            self.pause(reason="Token budget exhausted")
    
    def _on_state_changed(self, old_state: ExecutorState, new_state: ExecutorState, reason: str) -> None:
        """状态变化回调"""
        logger.info(f"Engine state: {old_state.value} -> {new_state.value}, reason={reason}")
    
    # ─────────────────────────────────────────────────────────────────
    # 核心执行接口
    # ─────────────────────────────────────────────────────────────────
    
    async def execute_task(self, task: Task, 
                          resume_state: Dict[str, Any] = None) -> TaskResult:
        """
        执行单个任务
        
        Args:
            task: 要执行的任务
            resume_state: 恢复状态（从Checkpoint）
            
        Returns:
            任务执行结果
        """
        # 1. Token检查
        decision = self.token_scheduler.schedule_task(task)
        if decision["action"] == "block":
            return TaskResult(
                task_id=task.task_id,
                status="skipped",
                output={"reason": decision.get("reason", "Token level blocked")},
                token_consumed=0,
                time_elapsed=0
            )
        
        if decision["action"] == "defer":
            return TaskResult(
                task_id=task.task_id,
                status="deferred",
                output={"reason": decision.get("reason", "Insufficient token budget")},
                token_consumed=0,
                time_elapsed=0
            )
        
        # 2. 获取处理器
        handler = self._get_handler(task.category)
        if not handler:
            return TaskResult(
                task_id=task.task_id,
                status="failed",
                output={},
                token_consumed=0,
                time_elapsed=0,
                error=f"No handler found for category: {task.category}"
            )
        
        # 3. 验证任务
        if not handler.validate(task):
            return TaskResult(
                task_id=task.task_id,
                status="failed",
                output={},
                token_consumed=0,
                time_elapsed=0,
                error="Task validation failed"
            )
        
        # 4. 执行任务
        start_time = time.time()
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now()
        
        try:
            # 如果有恢复状态，恢复处理器
            if resume_state:
                handler.restore_from_checkpoint(resume_state)
            
            # 执行
            result = handler.execute(task, checkpoint_state=resume_state)
            
            # 如果结果是迭代器，消费它
            if hasattr(result, '__iter__') and not isinstance(result, TaskResult):
                final_result = None
                for r in result:
                    if isinstance(r, TaskResult):
                        final_result = r
                        # 处理中间检查点
                        if r.status == "checkpoint":
                            await self._create_task_checkpoint(task, r.output.get("state"))
                result = final_result or TaskResult(
                    task_id=task.task_id,
                    status="completed",
                    output={},
                    token_consumed=0,
                    time_elapsed=time.time() - start_time
                )
            
            # 记录Token消耗
            elapsed = time.time() - start_time
            self.token_engine.consume(result.token_consumed, task.task_id)
            result.time_elapsed = elapsed
            
            # 更新任务状态
            if result.status == "completed":
                task.status = TaskStatus.COMPLETED
            elif result.status == "failed":
                task.status = TaskStatus.FAILED
            
            task.completed_at = datetime.now()
            task.token_consumed = result.token_consumed
            
            return result
            
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"Task execution error: {task.task_id}, error={e}")
            return TaskResult(
                task_id=task.task_id,
                status="failed",
                output={},
                token_consumed=0,
                time_elapsed=elapsed,
                error=str(e)
            )
    
    async def execute_batch(self, batch: TaskBatch, 
                           context: ExecutionContext = None) -> TaskResult:
        """
        执行批次任务
        
        Args:
            batch: 任务批次
            context: 执行上下文
            
        Returns:
            批次执行结果
        """
        context = context or ExecutionContext()
        
        # 设置批次
        self.state_manager.set_batch(batch)
        self.state_manager.set_state(ExecutorState.RUNNING, "Batch execution started")
        
        # 设置当前批次检查点
        checkpoint = None
        if self.config.checkpoint_enabled:
            checkpoint = await self.checkpoint_manager.create_batch_checkpoint(
                batch=batch,
                processed_ids=[],
                pending_ids=[t.task_id for t in batch.tasks],
                failed_ids=[]
            )
            context.checkpoint_id = checkpoint.checkpoint_id
        
        # 启动自动保存
        if self.config.checkpoint_enabled:
            self.checkpoint_manager.start_auto_save(
                lambda: self.state_manager.to_dict()
            )
        
        self._running = True
        processed_ids = []
        failed_ids = []
        
        try:
            while self._running and self.state_manager.has_pending_tasks():
                # 检查暂停
                if self.state_manager.is_paused():
                    await self._pause_event.wait()
                    self._pause_event.clear()
                
                # 检查停止
                if self._stop_event.is_set():
                    break
                
                # 获取下一个任务
                task = self.state_manager.get_next_task()
                if not task:
                    break
                
                # 执行
                result = await self.execute_task(task)
                
                # 更新状态
                if result.status == "completed":
                    self.state_manager.complete_task(task.task_id, result)
                    processed_ids.append(task.task_id)
                elif result.status == "failed":
                    self.state_manager.fail_task(task.task_id, result.error or "Unknown error")
                    failed_ids.append(task.task_id)
                elif result.status == "skipped":
                    self.state_manager.skip_task(task.task_id, result.output.get("reason", ""))
                
                # 更新批次进度
                self.state_manager.update_batch_progress()
                
                # 触发回调
                for callback in self._task_complete_callbacks:
                    callback(result)
                
                # 定期保存Checkpoint
                if self.config.checkpoint_enabled and checkpoint:
                    interval = self.registry.get_checkpoint_interval(task.category)
                    if len(processed_ids) % interval == 0:
                        await self.checkpoint_manager.update_checkpoint(
                            checkpoint.checkpoint_id,
                            progress=len(processed_ids) / len(batch.tasks),
                            processed_ids=processed_ids,
                            pending_ids=[t.task_id for t in batch.tasks if t.task_id not in processed_ids and t.task_id not in failed_ids],
                            failed_ids=failed_ids
                        )
            
            # 完成
            self.state_manager.set_state(ExecutorState.STOPPED, "Batch execution completed")
            
            if checkpoint:
                await self.checkpoint_manager.complete_checkpoint(checkpoint.checkpoint_id)
            
            # 生成报告
            report = self.state_manager.generate_report("batch")
            
            return TaskResult(
                task_id=batch.batch_id,
                status="completed",
                output={
                    "report": report.get_summary(),
                    "processed": len(processed_ids),
                    "failed": len(failed_ids),
                },
                token_consumed=self.token_engine.budget.consumed,
                time_elapsed=report.duration_seconds
            )
            
        except Exception as e:
            logger.error(f"Batch execution error: {e}")
            self.state_manager.set_state(ExecutorState.ERROR, str(e))
            
            if checkpoint:
                await self.checkpoint_manager.fail_checkpoint(checkpoint.checkpoint_id, str(e))
            
            return TaskResult(
                task_id=batch.batch_id,
                status="failed",
                output={},
                token_consumed=self.token_engine.budget.consumed,
                time_elapsed=0,
                error=str(e)
            )
        
        finally:
            self._running = False
            self.checkpoint_manager.stop_auto_save()
    
    async def execute(self, tasks: List[Task], 
                     context: ExecutionContext = None) -> TaskResult:
        """
        执行任务列表（统一入口）
        
        Args:
            tasks: 任务列表
            context: 执行上下文
            
        Returns:
            执行结果
        """
        if not tasks:
            return TaskResult(
                task_id="empty",
                status="completed",
                output={"message": "No tasks to execute"},
                token_consumed=0,
                time_elapsed=0
            )
        
        # 创建批次
        batch = TaskBatch(
            tasks=tasks,
            token_budget_total=self.config.token_default_budget
        )
        
        return await self.execute_batch(batch, context)
    
    # ─────────────────────────────────────────────────────────────────
    # 控制接口
    # ─────────────────────────────────────────────────────────────────
    
    def pause(self, reason: str = "") -> None:
        """暂停执行"""
        if self.state_manager.is_running():
            self.state_manager.set_state(ExecutorState.PAUSED, reason or "User requested")
            self._pause_event.clear()
            logger.info(f"Execution paused: {reason}")
    
    def resume(self) -> None:
        """恢复执行"""
        if self.state_manager.is_paused():
            self.state_manager.set_state(ExecutorState.RUNNING, "User resumed")
            self._pause_event.set()
            logger.info("Execution resumed")
    
    def stop(self) -> None:
        """停止执行"""
        self._running = False
        self._stop_event.set()
        self.state_manager.set_state(ExecutorState.STOPPING, "User requested stop")
        logger.info("Execution stopping...")
    
    async def resume_from_checkpoint(self, checkpoint_id: str) -> Optional[TaskResult]:
        """
        从Checkpoint恢复执行
        
        Args:
            checkpoint_id: 检查点ID
            
        Returns:
            执行结果
        """
        result = await self.checkpoint_manager.resume_from_checkpoint(checkpoint_id)
        
        if not result.success:
            logger.error(f"Failed to resume: {result.error}")
            return TaskResult(
                task_id=checkpoint_id,
                status="failed",
                output={},
                token_consumed=0,
                time_elapsed=0,
                error=result.error
            )
        
        # 恢复Token状态
        self.token_engine.budget.consumed = result.checkpoint.token_consumed
        
        # 恢复状态
        if result.checkpoint.execution_state:
            self.state_manager.from_dict(result.checkpoint.execution_state)
        
        # 恢复处理器状态
        if result.checkpoint.handler_state:
            # 恢复各个处理器的状态
            for category, state in result.checkpoint.handler_state.items():
                handler = self._get_handler(category)
                if handler:
                    handler.restore_from_checkpoint(state)
        
        # 重建批次
        if result.checkpoint.batch_id:
            batch = TaskBatch(
                batch_id=result.checkpoint.batch_id,
                task_ids=result.checkpoint.pending_task_ids + result.checkpoint.processed_task_ids
            )
            
            # 从状态管理器恢复任务
            for task_id in batch.task_ids:
                task = self.state_manager.get_task(task_id)
                if task:
                    batch.tasks.append(task)
            
            # 继续执行
            context = ExecutionContext(resume_from=checkpoint_id)
            return await self.execute_batch(batch, context)
        
        return TaskResult(
            task_id=checkpoint_id,
            status="completed",
            output={"message": "Checkpoint restored but no batch found"},
            token_consumed=0,
            time_elapsed=0
        )
    
    # ─────────────────────────────────────────────────────────────────
    # 处理器管理
    # ─────────────────────────────────────────────────────────────────
    
    def _get_handler(self, category: str) -> Optional[TaskHandler]:
        """获取处理器（带缓存）"""
        if category in self._handler_cache:
            return self._handler_cache[category]
        
        handler = self.registry.get_handler(category)
        if handler:
            self._handler_cache[category] = handler
        
        return handler
    
    def register_handler(self, handler_class: type) -> None:
        """注册处理器"""
        self.registry.register_handler(handler_class)
        # 清除缓存
        self._handler_cache.clear()
    
    def load_plugins(self) -> int:
        """加载所有插件"""
        count = self.registry.auto_discover_plugins()
        self._handler_cache.clear()
        return count
    
    # ─────────────────────────────────────────────────────────────────
    # Checkpoint管理
    # ─────────────────────────────────────────────────────────────────
    
    async def _create_task_checkpoint(self, task: Task, handler_state: Dict[str, Any]) -> None:
        """为任务创建检查点"""
        if not self.config.checkpoint_enabled:
            return
        
        checkpoint = await self.checkpoint_manager.create_task_checkpoint(
            task=task,
            handler_state=handler_state
        )
        
        for callback in self._checkpoint_callbacks:
            callback(checkpoint.checkpoint_id)
    
    async def list_checkpoints(self) -> List[Dict[str, Any]]:
        """列出所有检查点"""
        checkpoints = await self.checkpoint_manager.list_resumable()
        return [cp.to_dict() for cp in checkpoints]
    
    # ─────────────────────────────────────────────────────────────────
    # 统计和报告
    # ─────────────────────────────────────────────────────────────────
    
    def get_stats(self) -> Dict[str, Any]:
        """获取执行统计"""
        return {
            "state": self.state_manager.state.value,
            "token": self.token_engine.get_consumption_stats(),
            "queue": self.state_manager.get_queue_counts(),
            "metrics": {
                "tasks_submitted": self.state_manager.get_metrics().tasks_submitted,
                "tasks_completed": self.state_manager.get_metrics().tasks_completed,
                "tasks_failed": self.state_manager.get_metrics().tasks_failed,
                "success_rate": self.state_manager.get_metrics().get_success_rate(),
            }
        }
    
    def generate_report(self) -> Dict[str, Any]:
        """生成执行报告"""
        report = self.state_manager.generate_report()
        return report.to_dict()
    
    # ─────────────────────────────────────────────────────────────────
    # 回调注册
    # ─────────────────────────────────────────────────────────────────
    
    def on_task_complete(self, callback: Callable[[TaskResult], None]) -> None:
        """注册任务完成回调"""
        self._task_complete_callbacks.append(callback)
    
    def on_checkpoint(self, callback: Callable[[str], None]) -> None:
        """注册检查点回调"""
        self._checkpoint_callbacks.append(callback)
    
    # ─────────────────────────────────────────────────────────────────
    # 生命周期管理
    # ─────────────────────────────────────────────────────────────────
    
    async def startup(self) -> None:
        """启动引擎"""
        self.state_manager.set_state(ExecutorState.INITIALIZING, "Engine starting")
        
        # 加载插件
        self.load_plugins()
        
        # 恢复未完成的检查点
        if self.config.checkpoint_enabled:
            resumable = await self.checkpoint_manager.list_resumable()
            if resumable:
                logger.info(f"Found {len(resumable)} resumable checkpoints")
        
        self.state_manager.set_state(ExecutorState.IDLE, "Engine ready")
        logger.info("TaskEngine started")
    
    async def shutdown(self) -> None:
        """关闭引擎"""
        self.stop()
        self.checkpoint_manager.stop_auto_save()
        self.state_manager.set_state(ExecutorState.STOPPED, "Engine shutdown")
        logger.info("TaskEngine shutdown")
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.startup()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.shutdown()


# 便捷的创建函数
def create_engine(config_path: str = None, **kwargs) -> TaskEngine:
    """
    创建任务引擎
    
    Args:
        config_path: 配置文件路径
        **kwargs: 其他配置参数
        
    Returns:
        任务引擎实例
    """
    config = ExecutorConfig()
    
    if config_path and os.path.exists(config_path):
        # 从文件加载配置
        import yaml
        with open(config_path, 'r') as f:
            data = yaml.safe_load(f)
            if data and 'executor' in data:
                config_data = data['executor']
                for key, value in config_data.items():
                    if hasattr(config, key):
                        setattr(config, key, value)
    
    # 覆盖配置
    for key, value in kwargs.items():
        if hasattr(config, key):
            setattr(config, key, value)
    
    return TaskEngine(config)
