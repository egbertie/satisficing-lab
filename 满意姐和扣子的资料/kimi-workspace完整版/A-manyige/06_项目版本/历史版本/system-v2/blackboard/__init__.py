"""
Blackboard V2 - 共享黑板系统

提供：
- BlackboardManager: 核心管理器
- SharedMemory: 共享内存
- EventSystem: 事件系统
- AuditLogger: 审计日志

Usage:
    from system_v2.blackboard import BlackboardManager, get_blackboard
    
    # 方式1：直接使用管理器
    board = BlackboardManager("my_app")
    board.set("key", "value")
    
    # 方式2：上下文管理器
    with BlackboardManager("my_app") as board:
        board.set("key", "value")
        value = board.get("key")
    
    # 方式3：全局单例
    board = get_blackboard("default")
    board.set("key", "value")
"""

from .blackboard_manager import BlackboardManager, get_blackboard
from .shared_memory import SharedMemory
from .event_system import EventSystem
from .audit_logger import AuditLogger

__version__ = "2.0.0"
__all__ = [
    "BlackboardManager",
    "SharedMemory", 
    "EventSystem",
    "AuditLogger",
    "get_blackboard",
]
