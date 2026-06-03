#!/usr/bin/env python3
"""
rate_limiter.py - 极简速率限制器
只在内存中记录，不写文件，零Token开销
"""

import time
from collections import deque
from typing import Optional, Callable
import functools

class SimpleRateLimiter:
    """简单速率限制器 - 无持久化，零监控开销"""
    
    def __init__(self, max_calls: int = 10, window_seconds: int = 60):
        self.max_calls = max_calls
        self.window = window_seconds
        self.calls = deque()  # 只保留内存中，不写入文件
    
    def can_call(self) -> bool:
        """检查是否允许调用"""
        now = time.time()
        # 清理过期记录
        while self.calls and self.calls[0] < now - self.window:
            self.calls.popleft()
        return len(self.calls) < self.max_calls
    
    def record_call(self):
        """记录一次调用"""
        self.calls.append(time.time())
    
    def wait_if_needed(self, callback: Optional[Callable] = None):
        """如果需要，等待直到可以调用"""
        while not self.can_call():
            if callback:
                callback()
            time.sleep(1)
        self.record_call()

# 全局限制器实例 - 5小时频限周期内控制
# 每5小时周期：最多100次调用，避免触发频限
_global_limiter = SimpleRateLimiter(max_calls=100, window_seconds=18000)

def limited_call(func: Callable) -> Callable:
    """装饰器：限制函数调用频率"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        _global_limiter.wait_if_needed()
        return func(*args, **kwargs)
    return wrapper

# 快捷函数
def check_rate() -> bool:
    """检查是否可以调用"""
    return _global_limiter.can_call()

def record():
    """记录一次调用"""
    _global_limiter.record_call()
