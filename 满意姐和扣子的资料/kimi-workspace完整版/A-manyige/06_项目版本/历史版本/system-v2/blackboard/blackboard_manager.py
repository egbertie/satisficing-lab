"""
Blackboard - 共享黑板系统 V2
核心管理器 - 协调所有黑板组件
"""

import json
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set

try:
    from .shared_memory import SharedMemory
    from .event_system import EventSystem
    from .audit_logger import AuditLogger
except ImportError:
    # 直接运行时
    from shared_memory import SharedMemory
    from event_system import EventSystem
    from audit_logger import AuditLogger


class BlackboardManager:
    """
    黑板系统核心管理器
    
    职责：
    - 协调共享内存、事件系统、审计日志
    - 提供统一的数据读写接口
    - 管理组件生命周期
    """
    
    def __init__(self, namespace: str = "default", persist_dir: Optional[str] = None):
        self.namespace = namespace
        self.persist_dir = Path(persist_dir) if persist_dir else Path("/tmp/blackboard")
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        
        # 核心组件
        self._memory = SharedMemory(namespace)
        self._events = EventSystem()
        self._audit = AuditLogger(self.persist_dir / "audit.log")
        
        # 状态
        self._running = False
        self._lock = threading.RLock()
        self._subscriptions: Dict[str, Set[Callable]] = {}
        
        # 统计
        self._stats = {
            "created_at": datetime.now().isoformat(),
            "reads": 0,
            "writes": 0,
            "events": 0
        }
        
        self._audit.log("INIT", f"BlackboardManager initialized: {namespace}")
    
    # ========== 核心操作 ==========
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取数据"""
        with self._lock:
            self._stats["reads"] += 1
            value = self._memory.get(key, default)
            self._audit.log("GET", f"key={key}")
            return value
    
    def set(self, key: str, value: Any, notify: bool = True) -> None:
        """设置数据"""
        with self._lock:
            old_value = self._memory.get(key)
            self._memory.set(key, value)
            self._stats["writes"] += 1
            self._audit.log("SET", f"key={key}")
            
            if notify:
                self._events.publish(f"data:{key}", {
                    "key": key,
                    "old": old_value,
                    "new": value,
                    "timestamp": datetime.now().isoformat()
                })
    
    def delete(self, key: str) -> bool:
        """删除数据"""
        with self._lock:
            result = self._memory.delete(key)
            self._audit.log("DELETE", f"key={key}, result={result}")
            return result
    
    def keys(self) -> List[str]:
        """获取所有键"""
        return self._memory.keys()
    
    def exists(self, key: str) -> bool:
        """检查键是否存在"""
        return self._memory.exists(key)
    
    # ========== 事件系统 ==========
    
    def subscribe(self, pattern: str, callback: Callable) -> None:
        """订阅事件模式"""
        if pattern not in self._subscriptions:
            self._subscriptions[pattern] = set()
        self._subscriptions[pattern].add(callback)
        self._events.subscribe(pattern, callback)
        self._audit.log("SUBSCRIBE", f"pattern={pattern}")
    
    def unsubscribe(self, pattern: str, callback: Callable) -> None:
        """取消订阅"""
        if pattern in self._subscriptions:
            self._subscriptions[pattern].discard(callback)
        self._events.unsubscribe(pattern, callback)
    
    def publish(self, event_type: str, data: Any) -> None:
        """发布事件"""
        with self._lock:
            self._stats["events"] += 1
            self._events.publish(event_type, data)
            self._audit.log("PUBLISH", f"type={event_type}")
    
    # ========== 生命周期 ==========
    
    def start(self) -> None:
        """启动黑板系统"""
        with self._lock:
            self._running = True
            self._audit.log("START", "BlackboardManager started")
    
    def stop(self) -> None:
        """停止黑板系统"""
        with self._lock:
            self._running = False
            self._audit.log("STOP", "BlackboardManager stopped")
    
    def is_running(self) -> bool:
        """检查运行状态"""
        return self._running
    
    # ========== 持久化 ==========
    
    def save(self, filename: Optional[str] = None) -> str:
        """保存状态到文件"""
        filename = filename or f"{self.namespace}_{int(time.time())}.json"
        filepath = self.persist_dir / filename
        
        data = {
            "namespace": self.namespace,
            "stats": self._stats,
            "memory": self._memory.dump(),
            "saved_at": datetime.now().isoformat()
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        self._audit.log("SAVE", f"filepath={filepath}")
        return str(filepath)
    
    def load(self, filepath: str) -> bool:
        """从文件加载状态"""
        path = Path(filepath)
        if not path.exists():
            return False
        
        with open(path, 'r') as f:
            data = json.load(f)
        
        self._memory.load(data.get("memory", {}))
        self._audit.log("LOAD", f"filepath={filepath}")
        return True
    
    # ========== 统计信息 ==========
    
    def stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            **self._stats,
            "memory_keys": len(self._memory.keys()),
            "subscriptions": sum(len(s) for s in self._subscriptions.values()),
            "is_running": self._running
        }
    
    def get_audit_log(self, limit: int = 100) -> List[str]:
        """获取审计日志"""
        return self._audit.get_recent(limit)
    
    # ========== 上下文管理器 ==========
    
    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
        self.save()


# 全局黑板实例
_global_blackboard: Optional[BlackboardManager] = None


def get_blackboard(namespace: str = "default") -> BlackboardManager:
    """获取全局黑板实例（单例模式）"""
    global _global_blackboard
    if _global_blackboard is None or _global_blackboard.namespace != namespace:
        _global_blackboard = BlackboardManager(namespace)
    return _global_blackboard
