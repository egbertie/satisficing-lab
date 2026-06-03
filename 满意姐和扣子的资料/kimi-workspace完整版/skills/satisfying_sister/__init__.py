"""
满意姐 (Satisfying Sister) - 核心AI角色定义系统
基于《新AI角色定义初稿.md》的代码级实现
"""

from .role_engine import RoleEngine, RoleMode
from .command_parser import CommandParser
from .intent_contract import IntentContract
from .memory_citation import MemoryCitation
from .totem_os import TotemOS
from .blue_army_trigger import BlueArmyTrigger
from .language_guard import LanguageGuard
from .health_fuse import HealthFuse

__all__ = [
    "RoleEngine", "RoleMode",
    "CommandParser",
    "IntentContract",
    "MemoryCitation",
    "TotemOS",
    "BlueArmyTrigger",
    "LanguageGuard",
    "HealthFuse",
]
