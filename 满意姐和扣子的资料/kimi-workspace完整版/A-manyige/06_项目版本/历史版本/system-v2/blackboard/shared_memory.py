"""
Blackboard - 共享内存模块
提供线程安全的内存存储
"""

import threading
from typing import Any, Dict, List, Optional


class SharedMemory:
    """
    共享内存实现
    
    特性：
    - 线程安全（RLock）
    - 命名空间隔离
    - 支持任意Python对象
    """
    
    # 类级存储：namespace -> {key: value}
    _storage: Dict[str, Dict[str, Any]] = {}
    _lock = threading.RLock()
    
    def __init__(self, namespace: str = "default"):
        self.namespace = namespace
        with self._lock:
            if namespace not in self._storage:
                self._storage[namespace] = {}
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取值"""
        with self._lock:
            return self._storage[self.namespace].get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """设置值"""
        with self._lock:
            self._storage[self.namespace][key] = value
    
    def delete(self, key: str) -> bool:
        """删除键，返回是否成功"""
        with self._lock:
            if key in self._storage[self.namespace]:
                del self._storage[self.namespace][key]
                return True
            return False
    
    def keys(self) -> List[str]:
        """获取所有键"""
        with self._lock:
            return list(self._storage[self.namespace].keys())
    
    def exists(self, key: str) -> bool:
        """检查键是否存在"""
        with self._lock:
            return key in self._storage[self.namespace]
    
    def clear(self) -> None:
        """清空当前命名空间"""
        with self._lock:
            self._storage[self.namespace].clear()
    
    def dump(self) -> Dict[str, Any]:
        """导出当前命名空间数据"""
        with self._lock:
            return dict(self._storage[self.namespace])
    
    def load(self, data: Dict[str, Any]) -> None:
        """加载数据到当前命名空间"""
        with self._lock:
            self._storage[self.namespace] = dict(data)
    
    @classmethod
    def get_namespaces(cls) -> List[str]:
        """获取所有命名空间"""
        with cls._lock:
            return list(cls._storage.keys())
    
    @classmethod
    def clear_namespace(cls, namespace: str) -> bool:
        """清空指定命名空间"""
        with cls._lock:
            if namespace in cls._storage:
                cls._storage[namespace].clear()
                return True
            return False
    
    @classmethod
    def reset_all(cls) -> None:
        """重置所有存储（危险操作，仅测试使用）"""
        with cls._lock:
            cls._storage.clear()
