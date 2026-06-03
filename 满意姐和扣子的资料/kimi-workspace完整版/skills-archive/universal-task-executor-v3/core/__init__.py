"""
Universal Task Executor V3.0 - Core Engine

核心引擎模块，提供1-6类任务的统一执行接口

主要组件:
- engine.py: 任务调度引擎（主入口）
- registry.py: 任务注册表（6类任务配置）
- state_manager.py: 状态管理器
- checkpoint.py: Checkpoint管理器（支持暂停/重启）
- token_engine.py: Token优化引擎（L1-L5档位）
- structures.py: 共享数据结构

使用示例:
    from core import TaskEngine, create_engine
    
    # 创建引擎
    engine = create_engine()
    
    # 创建任务
    task = Task(category="category_6", priority=TaskPriority.P0, title="审计任务")
    
    # 执行
    async with engine:
        result = await engine.execute([task])
"""

from .structures import (
    Task,
    TaskBatch,
    TaskResult,
    TaskStatus,
    TaskPriority,
    TokenLevel,
    TokenBudget,
    Checkpoint,
    AuditRecord,
    ExecutionReport,
    HandlerInfo,
    ExecutorConfig,
)

from .token_engine import (
    TokenEngine,
    TokenAwareScheduler,
    TokenLevelChangedEvent,
)

from .registry import (
    TaskRegistry,
    TaskHandler,
    TaskTypeConfig,
    get_registry,
)

from .checkpoint import (
    CheckpointManager,
    FileCheckpointStorage,
    ResumeResult,
    RecoveryResult,
)

from .state_manager import (
    StateManager,
    ExecutorState,
    ExecutionMetrics,
)

from .engine import (
    TaskEngine,
    ExecutionContext,
    create_engine,
)

__version__ = "3.0.0"
__all__ = [
    # 数据结构
    "Task",
    "TaskBatch",
    "TaskResult",
    "TaskStatus",
    "TaskPriority",
    "TokenLevel",
    "TokenBudget",
    "Checkpoint",
    "AuditRecord",
    "ExecutionReport",
    "HandlerInfo",
    "ExecutorConfig",
    
    # Token引擎
    "TokenEngine",
    "TokenAwareScheduler",
    "TokenLevelChangedEvent",
    
    # 注册表
    "TaskRegistry",
    "TaskHandler",
    "TaskTypeConfig",
    "get_registry",
    
    # Checkpoint
    "CheckpointManager",
    "FileCheckpointStorage",
    "ResumeResult",
    "RecoveryResult",
    
    # 状态管理
    "StateManager",
    "ExecutorState",
    "ExecutionMetrics",
    
    # 主引擎
    "TaskEngine",
    "ExecutionContext",
    "create_engine",
]
