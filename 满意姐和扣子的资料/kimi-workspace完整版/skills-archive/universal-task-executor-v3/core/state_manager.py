"""
Universal Task Executor V3.0 - 状态管理器
管理执行器状态、任务队列、执行统计
"""

import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from .structures import Task, TaskBatch, TaskStatus, TaskResult, ExecutionReport

logger = logging.getLogger(__name__)


class ExecutorState(Enum):
    """执行器状态"""
    IDLE = "idle"           # 空闲
    INITIALIZING = "initializing"  # 初始化中
    RUNNING = "running"     # 运行中
    PAUSED = "paused"       # 已暂停
    STOPPING = "stopping"   # 停止中
    STOPPED = "stopped"     # 已停止
    ERROR = "error"         # 错误状态


@dataclass
class TaskQueueState:
    """任务队列状态"""
    pending: List[str] = field(default_factory=list)
    running: List[str] = field(default_factory=list)
    completed: List[str] = field(default_factory=list)
    failed: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)
    deferred: List[str] = field(default_factory=list)
    
    def get_counts(self) -> Dict[str, int]:
        """获取各状态数量"""
        return {
            "pending": len(self.pending),
            "running": len(self.running),
            "completed": len(self.completed),
            "failed": len(self.failed),
            "skipped": len(self.skipped),
            "deferred": len(self.deferred),
        }
    
    def get_total(self) -> int:
        """获取总数"""
        return sum(self.get_counts().values())


@dataclass
class ExecutionMetrics:
    """执行指标"""
    tasks_submitted: int = 0
    tasks_started: int = 0
    tasks_completed: int = 0
    tasks_failed: int = 0
    tasks_skipped: int = 0
    tasks_deferred: int = 0
    
    total_token_consumed: int = 0
    total_time_elapsed: float = 0.0
    
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    last_checkpoint_time: Optional[datetime] = None
    
    errors: List[Dict[str, Any]] = field(default_factory=list)
    
    def record_error(self, error: str, context: str = ""):
        """记录错误"""
        self.errors.append({
            "error": error,
            "context": context,
            "timestamp": datetime.now().isoformat()
        })
    
    def get_success_rate(self) -> float:
        """获取成功率"""
        completed = self.tasks_completed
        failed = self.tasks_failed
        total = completed + failed
        return completed / total if total > 0 else 0.0


class StateManager:
    """
    状态管理器 - 核心组件
    
    职责:
    1. 管理执行器状态机
    2. 管理任务队列
    3. 记录执行统计
    4. 生成执行报告
    5. 支持状态序列化/反序列化
    """
    
    def __init__(self):
        """初始化状态管理器"""
        self._state = ExecutorState.IDLE
        self._queue_state = TaskQueueState()
        self._metrics = ExecutionMetrics()
        
        # 任务存储
        self._tasks: Dict[str, Task] = {}
        self._batch: Optional[TaskBatch] = None
        
        # 当前执行上下文
        self._current_task_id: Optional[str] = None
        self._current_batch_id: Optional[str] = None
        
        # 状态变更回调
        self._state_change_callbacks: List[callable] = []
        
        logger.info("StateManager initialized")
    
    # ─────────────────────────────────────────────────────────────────
    # 状态管理
    # ─────────────────────────────────────────────────────────────────
    
    @property
    def state(self) -> ExecutorState:
        """获取当前状态"""
        return self._state
    
    def set_state(self, new_state: ExecutorState, reason: str = "") -> None:
        """
        设置新状态
        
        Args:
            new_state: 新状态
            reason: 状态变更原因
        """
        old_state = self._state
        if old_state == new_state:
            return
        
        self._state = new_state
        logger.info(f"State changed: {old_state.value} -> {new_state.value}, reason={reason}")
        
        # 触发回调
        for callback in self._state_change_callbacks:
            try:
                callback(old_state, new_state, reason)
            except Exception as e:
                logger.warning(f"State change callback failed: {e}")
        
        # 更新指标
        if new_state == ExecutorState.RUNNING and not self._metrics.start_time:
            self._metrics.start_time = datetime.now()
        elif new_state in [ExecutorState.STOPPED, ExecutorState.ERROR]:
            self._metrics.end_time = datetime.now()
    
    def register_state_change_callback(self, callback: callable) -> None:
        """注册状态变更回调"""
        self._state_change_callbacks.append(callback)
    
    def is_running(self) -> bool:
        """检查是否正在运行"""
        return self._state == ExecutorState.RUNNING
    
    def is_paused(self) -> bool:
        """检查是否已暂停"""
        return self._state == ExecutorState.PAUSED
    
    def can_execute(self) -> bool:
        """检查是否可以执行"""
        return self._state in [ExecutorState.IDLE, ExecutorState.RUNNING]
    
    # ─────────────────────────────────────────────────────────────────
    # 任务队列管理
    # ─────────────────────────────────────────────────────────────────
    
    def add_task(self, task: Task) -> None:
        """添加任务到队列"""
        self._tasks[task.task_id] = task
        if task.task_id not in self._queue_state.pending:
            self._queue_state.pending.append(task.task_id)
        self._metrics.tasks_submitted += 1
        logger.debug(f"Task added: {task.task_id}")
    
    def add_tasks(self, tasks: List[Task]) -> None:
        """批量添加任务"""
        for task in tasks:
            self.add_task(task)
        logger.info(f"Added {len(tasks)} tasks to queue")
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """获取任务"""
        return self._tasks.get(task_id)
    
    def get_next_task(self) -> Optional[Task]:
        """获取下一个待处理任务"""
        while self._queue_state.pending:
            task_id = self._queue_state.pending.pop(0)
            task = self._tasks.get(task_id)
            if task and task.status == TaskStatus.PENDING:
                self._queue_state.running.append(task_id)
                self._current_task_id = task_id
                return task
        return None
    
    def complete_task(self, task_id: str, result: TaskResult) -> None:
        """完成任务"""
        if task_id in self._queue_state.running:
            self._queue_state.running.remove(task_id)
        
        self._queue_state.completed.append(task_id)
        
        task = self._tasks.get(task_id)
        if task:
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            task.token_consumed = result.token_consumed
        
        self._metrics.tasks_completed += 1
        self._metrics.total_token_consumed += result.token_consumed
        self._metrics.total_time_elapsed += result.time_elapsed
        
        logger.debug(f"Task completed: {task_id}")
    
    def fail_task(self, task_id: str, error: str) -> None:
        """标记任务失败"""
        if task_id in self._queue_state.running:
            self._queue_state.running.remove(task_id)
        
        self._queue_state.failed.append(task_id)
        
        task = self._tasks.get(task_id)
        if task:
            task.status = TaskStatus.FAILED
            task.completed_at = datetime.now()
        
        self._metrics.tasks_failed += 1
        self._metrics.record_error(error, f"task={task_id}")
        
        logger.error(f"Task failed: {task_id}, error={error}")
    
    def skip_task(self, task_id: str, reason: str = "") -> None:
        """跳过任务"""
        if task_id in self._queue_state.pending:
            self._queue_state.pending.remove(task_id)
        if task_id in self._queue_state.running:
            self._queue_state.running.remove(task_id)
        
        self._queue_state.skipped.append(task_id)
        
        task = self._tasks.get(task_id)
        if task:
            task.status = TaskStatus.SKIPPED
        
        self._metrics.tasks_skipped += 1
        logger.info(f"Task skipped: {task_id}, reason={reason}")
    
    def defer_task(self, task_id: str, reason: str = "") -> None:
        """推迟任务"""
        if task_id in self._queue_state.running:
            self._queue_state.running.remove(task_id)
        
        if task_id not in self._queue_state.pending:
            self._queue_state.pending.append(task_id)
        
        self._metrics.tasks_deferred += 1
        logger.info(f"Task deferred: {task_id}, reason={reason}")
    
    def has_pending_tasks(self) -> bool:
        """检查是否有待处理任务"""
        return len(self._queue_state.pending) > 0
    
    def get_queue_counts(self) -> Dict[str, int]:
        """获取队列统计"""
        return self._queue_state.get_counts()
    
    # ─────────────────────────────────────────────────────────────────
    # 批次管理
    # ─────────────────────────────────────────────────────────────────
    
    def set_batch(self, batch: TaskBatch) -> None:
        """设置当前批次"""
        self._batch = batch
        self._current_batch_id = batch.batch_id
        
        # 将批次任务添加到队列
        for task in batch.tasks:
            self.add_task(task)
        
        logger.info(f"Batch set: {batch.batch_id}, tasks={len(batch.tasks)}")
    
    def get_batch(self) -> Optional[TaskBatch]:
        """获取当前批次"""
        return self._batch
    
    def update_batch_progress(self) -> None:
        """更新批次进度"""
        if not self._batch:
            return
        
        counts = self._queue_state.get_counts()
        self._batch.status_counts = counts
        self._batch.token_consumed_total = self._metrics.total_token_consumed
    
    # ─────────────────────────────────────────────────────────────────
    # 指标和报告
    # ─────────────────────────────────────────────────────────────────
    
    def get_metrics(self) -> ExecutionMetrics:
        """获取执行指标"""
        return self._metrics
    
    def record_checkpoint(self) -> None:
        """记录检查点时间"""
        self._metrics.last_checkpoint_time = datetime.now()
    
    def generate_report(self, report_type: str = "summary") -> ExecutionReport:
        """
        生成执行报告
        
        Args:
            report_type: 报告类型 (batch/task/summary)
            
        Returns:
            执行报告
        """
        counts = self._queue_state.get_counts()
        
        report = ExecutionReport(
            report_type=report_type,
            batch_id=self._current_batch_id,
            total_tasks=self._queue_state.get_total(),
            completed=self._metrics.tasks_completed,
            failed=self._metrics.tasks_failed,
            skipped=self._metrics.tasks_skipped,
            deferred=self._metrics.tasks_deferred,
            token_budget=self._batch.token_budget_total if self._batch else 0,
            token_consumed=self._metrics.total_token_consumed,
            started_at=self._metrics.start_time,
            completed_at=self._metrics.end_time,
            duration_seconds=self._calculate_duration(),
        )
        
        # 计算效率
        if report.token_consumed > 0:
            report.token_efficiency = report.completed / report.token_consumed
        
        # 添加建议
        if report.failed > 0:
            report.recommendations.append(f"有{report.failed}个任务失败，建议检查日志")
        
        if self._metrics.errors:
            report.recommendations.append(f"执行过程中发生{len(self._metrics.errors)}个错误")
        
        return report
    
    def _calculate_duration(self) -> float:
        """计算执行时长"""
        if not self._metrics.start_time:
            return 0.0
        
        end = self._metrics.end_time or datetime.now()
        return (end - self._metrics.start_time).total_seconds()
    
    # ─────────────────────────────────────────────────────────────────
    # 序列化/反序列化
    # ─────────────────────────────────────────────────────────────────
    
    def to_dict(self) -> Dict[str, Any]:
        """序列化状态"""
        return {
            "state": self._state.value,
            "queue_state": {
                "pending": self._queue_state.pending,
                "running": self._queue_state.running,
                "completed": self._queue_state.completed,
                "failed": self._queue_state.failed,
                "skipped": self._queue_state.skipped,
                "deferred": self._queue_state.deferred,
            },
            "metrics": {
                "tasks_submitted": self._metrics.tasks_submitted,
                "tasks_started": self._metrics.tasks_started,
                "tasks_completed": self._metrics.tasks_completed,
                "tasks_failed": self._metrics.tasks_failed,
                "tasks_skipped": self._metrics.tasks_skipped,
                "tasks_deferred": self._metrics.tasks_deferred,
                "total_token_consumed": self._metrics.total_token_consumed,
                "total_time_elapsed": self._metrics.total_time_elapsed,
                "start_time": self._metrics.start_time.isoformat() if self._metrics.start_time else None,
                "end_time": self._metrics.end_time.isoformat() if self._metrics.end_time else None,
                "last_checkpoint_time": self._metrics.last_checkpoint_time.isoformat() if self._metrics.last_checkpoint_time else None,
            },
            "tasks": {tid: task.to_dict() for tid, task in self._tasks.items()},
            "current_task_id": self._current_task_id,
            "current_batch_id": self._current_batch_id,
            "timestamp": datetime.now().isoformat(),
        }
    
    def from_dict(self, data: Dict[str, Any]) -> None:
        """从字典恢复状态"""
        # 恢复状态
        self._state = ExecutorState(data.get("state", "idle"))
        
        # 恢复队列状态
        qs = data.get("queue_state", {})
        self._queue_state = TaskQueueState(
            pending=qs.get("pending", []),
            running=qs.get("running", []),
            completed=qs.get("completed", []),
            failed=qs.get("failed", []),
            skipped=qs.get("skipped", []),
            deferred=qs.get("deferred", []),
        )
        
        # 恢复指标
        m = data.get("metrics", {})
        self._metrics = ExecutionMetrics(
            tasks_submitted=m.get("tasks_submitted", 0),
            tasks_started=m.get("tasks_started", 0),
            tasks_completed=m.get("tasks_completed", 0),
            tasks_failed=m.get("tasks_failed", 0),
            tasks_skipped=m.get("tasks_skipped", 0),
            tasks_deferred=m.get("tasks_deferred", 0),
            total_token_consumed=m.get("total_token_consumed", 0),
            total_time_elapsed=m.get("total_time_elapsed", 0.0),
        )
        
        if m.get("start_time"):
            self._metrics.start_time = datetime.fromisoformat(m["start_time"])
        if m.get("end_time"):
            self._metrics.end_time = datetime.fromisoformat(m["end_time"])
        if m.get("last_checkpoint_time"):
            self._metrics.last_checkpoint_time = datetime.fromisoformat(m["last_checkpoint_time"])
        
        # 恢复任务
        tasks_data = data.get("tasks", {})
        self._tasks = {}
        for tid, task_data in tasks_data.items():
            try:
                self._tasks[tid] = Task.from_dict(task_data)
            except Exception as e:
                logger.warning(f"Failed to restore task {tid}: {e}")
        
        # 恢复当前上下文
        self._current_task_id = data.get("current_task_id")
        self._current_batch_id = data.get("current_batch_id")
        
        logger.info(f"State restored: state={self._state.value}, "
                   f"tasks={len(self._tasks)}, pending={len(self._queue_state.pending)}")
    
    def to_json(self) -> str:
        """序列化为JSON"""
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)
    
    def from_json(self, json_str: str) -> None:
        """从JSON恢复"""
        data = json.loads(json_str)
        self.from_dict(data)
    
    # ─────────────────────────────────────────────────────────────────
    # 重置
    # ─────────────────────────────────────────────────────────────────
    
    def reset(self) -> None:
        """重置所有状态"""
        self._state = ExecutorState.IDLE
        self._queue_state = TaskQueueState()
        self._metrics = ExecutionMetrics()
        self._tasks = {}
        self._batch = None
        self._current_task_id = None
        self._current_batch_id = None
        logger.info("StateManager reset")
    
    def clear_completed(self) -> int:
        """清理已完成的任务"""
        count = 0
        for task_id in self._queue_state.completed[:]:
            if task_id in self._tasks:
                del self._tasks[task_id]
                count += 1
        logger.debug(f"Cleared {count} completed tasks")
        return count
