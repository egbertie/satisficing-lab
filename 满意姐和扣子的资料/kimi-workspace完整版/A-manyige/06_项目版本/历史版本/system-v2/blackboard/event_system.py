"""
Blackboard - 事件系统模块
提供发布-订阅模式的事件机制
"""

import re
import threading
from typing import Any, Callable, Dict, List, Set


class EventSystem:
    """
    事件发布-订阅系统
    
    特性：
    - 支持模式匹配（通配符 *）
    - 线程安全
    - 同步/异步回调支持
    
    模式示例：
    - "data:user:123" - 精确匹配
    - "data:user:*"   - 匹配所有用户
    - "data:*"        - 匹配所有数据事件
    """
    
    def __init__(self):
        self._subscribers: Dict[str, Set[Callable]] = {}
        self._lock = threading.RLock()
        self._event_count = 0
    
    def subscribe(self, pattern: str, callback: Callable) -> None:
        """
        订阅事件模式
        
        Args:
            pattern: 事件模式，支持 * 通配符
            callback: 回调函数，接收 event_type 和 data 两个参数
        """
        with self._lock:
            if pattern not in self._subscribers:
                self._subscribers[pattern] = set()
            self._subscribers[pattern].add(callback)
    
    def unsubscribe(self, pattern: str, callback: Callable) -> None:
        """取消订阅"""
        with self._lock:
            if pattern in self._subscribers:
                self._subscribers[pattern].discard(callback)
                if not self._subscribers[pattern]:
                    del self._subscribers[pattern]
    
    def publish(self, event_type: str, data: Any) -> int:
        """
        发布事件
        
        Args:
            event_type: 事件类型
            data: 事件数据
        
        Returns:
            通知的订阅者数量
        """
        with self._lock:
            self._event_count += 1
            notified = 0
            
            for pattern, callbacks in self._subscribers.items():
                if self._match_pattern(event_type, pattern):
                    for callback in callbacks:
                        try:
                            callback(event_type, data)
                            notified += 1
                        except Exception as e:
                            # 捕获回调异常，防止影响其他订阅者
                            print(f"[EventSystem] Callback error: {e}")
            
            return notified
    
    def _match_pattern(self, event_type: str, pattern: str) -> bool:
        """
        匹配事件类型与模式
        
        支持两种模式：
        1. 精确匹配：pattern == event_type
        2. 通配符匹配：pattern 中的 * 匹配任意字符
        """
        if pattern == event_type:
            return True
        
        # 转换通配符模式为正则表达式
        if '*' in pattern:
            regex = pattern.replace('*', '.*')
            return bool(re.match(f"^{regex}$", event_type))
        
        return False
    
    def get_patterns(self) -> List[str]:
        """获取所有订阅模式"""
        with self._lock:
            return list(self._subscribers.keys())
    
    def get_subscribers(self, pattern: str) -> Set[Callable]:
        """获取指定模式的订阅者"""
        with self._lock:
            return set(self._subscribers.get(pattern, []))
    
    def clear(self) -> None:
        """清空所有订阅"""
        with self._lock:
            self._subscribers.clear()
            self._event_count = 0
    
    def stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        with self._lock:
            return {
                "patterns": len(self._subscribers),
                "total_subscribers": sum(len(s) for s in self._subscribers.values()),
                "events_processed": self._event_count
            }
