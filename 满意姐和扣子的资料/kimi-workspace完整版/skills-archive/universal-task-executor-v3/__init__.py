"""
Universal Task Executor V3.0

1-6类任务通用执行引擎，支持暂停/重启、Token优化、可插拔处理器

核心特性:
- 支持1-6类任务: 治理、Cron、系统建设、数据治理、杂项清理、全量审计
- Token优化: L1-L5五级档位自动切换
- Checkpoint: 每5分钟自动保存，支持任意时刻暂停/重启
- 插件化: 可插拔处理器架构，支持动态扩展
- 预留接口: 支持热升级和版本迁移

目录结构:
    core/           - 核心引擎模块
    plugins/        - 处理器插件目录
    config/         - 配置文件
    tests/          - 测试用例

快速开始:
    from core import TaskEngine, Task, TaskPriority
    
    engine = TaskEngine()
    task = Task(category="category_6", priority=TaskPriority.P0, title="示例任务")
    
    async with engine:
        result = await engine.execute([task])
"""

__version__ = "3.0.0"
__author__ = "Universal Task Executor Team"

# 导出核心类
from core.engine import TaskEngine, create_engine, ExecutionContext
from core.structures import (
    Task, TaskBatch, TaskResult, TaskStatus, TaskPriority,
    TokenLevel, Checkpoint, ExecutorConfig
)

__all__ = [
    "__version__",
    "TaskEngine",
    "create_engine",
    "ExecutionContext",
    "Task",
    "TaskBatch",
    "TaskResult",
    "TaskStatus",
    "TaskPriority",
    "TokenLevel",
    "Checkpoint",
    "ExecutorConfig",
]
