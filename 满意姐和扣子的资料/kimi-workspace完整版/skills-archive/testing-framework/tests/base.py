"""
测试基类和通用工具

参考对象: xUnit Test Patterns (Gerard Meszaros)
设计原则: Arrange-Act-Assert, Given-When-Then
"""

import json
import time
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable
from unittest.mock import MagicMock, patch, mock_open


class TestDataBuilder:
    """测试数据构建器模式"""
    
    def __init__(self):
        self.data = {}
    
    def with_field(self, key: str, value: Any) -> "TestDataBuilder":
        """添加字段"""
        self.data[key] = value
        return self
    
    def with_timestamp(self, timestamp: int = None) -> "TestDataBuilder":
        """添加时间戳"""
        self.data["timestamp"] = timestamp or int(time.time())
        return self
    
    def with_date(self, date_str: str = None) -> "TestDataBuilder":
        """添加日期"""
        self.data["date"] = date_str or datetime.now().strftime("%Y-%m-%d")
        return self
    
    def build(self) -> Dict[str, Any]:
        """构建数据"""
        return self.data.copy()


class HeartbeatStateBuilder(TestDataBuilder):
    """Heartbeat状态数据构建器"""
    
    def __init__(self):
        super().__init__()
        self.data = {
            "lastChecks": {
                "email": int(time.time()) - 3600,
                "calendar": int(time.time()) - 7200,
                "weather": int(time.time()) - 10800
            }
        }
    
    def with_user_activity(self, seconds_ago: int) -> "HeartbeatStateBuilder":
        """设置用户活动时间"""
        self.data["lastChecks"]["user_activity"] = int(time.time()) - seconds_ago
        return self
    
    def with_idle_time(self, idle_seconds: int) -> "HeartbeatStateBuilder":
        """设置空闲时间（负数表示过去）"""
        return self.with_user_activity(idle_seconds)


class TokenBudgetBuilder(TestDataBuilder):
    """Token预算数据构建器"""
    
    def __init__(self):
        super().__init__()
        current_time = int(time.time())
        self.data = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "daily_budget": 50000,
            "used_today": 0,
            "remaining_percentage": 100,
            "last_updated": current_time
        }
    
    def with_usage(self, used: int) -> "TokenBudgetBuilder":
        """设置已使用量"""
        self.data["used_today"] = used
        self.data["remaining_percentage"] = int(
            (self.data["daily_budget"] - used) / self.data["daily_budget"] * 100
        )
        return self
    
    def with_percentage(self, percentage: int) -> "TokenBudgetBuilder":
        """设置剩余百分比"""
        self.data["remaining_percentage"] = percentage
        self.data["used_today"] = int(
            self.data["daily_budget"] * (100 - percentage) / 100
        )
        return self
    
    def critical(self) -> "TokenBudgetBuilder":
        """设置为临界状态（<15%）"""
        return self.with_percentage(10)
    
    def low(self) -> "TokenBudgetBuilder":
        """设置为低状态（15-30%）"""
        return self.with_percentage(20)
    
    def normal(self) -> "TokenBudgetBuilder":
        """设置为正常状态（>30%）"""
        return self.with_percentage(70)


class ZeroIdleStateBuilder(TestDataBuilder):
    """Zero-Idle状态构建器"""
    
    def __init__(self):
        super().__init__()
        self.data = {
            "last_fill_time": int(time.time()) - 86400,  # 24小时前
            "fill_count_today": 0,
            "total_fills": 10
        }
    
    def with_last_fill(self, seconds_ago: int) -> "ZeroIdleStateBuilder":
        """设置上次补位时间"""
        self.data["last_fill_time"] = int(time.time()) - seconds_ago
        return self
    
    def recently_filled(self, minutes_ago: int = 30) -> "ZeroIdleStateBuilder":
        """设置为最近已补位"""
        return self.with_last_fill(minutes_ago * 60)
    
    def never_filled(self) -> "ZeroIdleStateBuilder":
        """设置为从未补位"""
        self.data["last_fill_time"] = 0
        return self


class BaseTestCase(ABC):
    """测试基类"""
    
    @abstractmethod
    def setup_method(self):
        """每个测试方法前的设置"""
        pass
    
    @abstractmethod
    def teardown_method(self):
        """每个测试方法后的清理"""
        pass


class SkillTestCase(BaseTestCase):
    """Skill测试基类"""
    
    SKILL_NAME: str = ""
    SKILL_PATH: Optional[Path] = None
    
    def setup_method(self):
        """设置测试环境"""
        self.mock_files: List[Path] = []
        self.patches: List[Any] = []
    
    def teardown_method(self):
        """清理测试环境"""
        # 停止所有patch
        for p in self.patches:
            p.stop()
    
    def patch(self, target: str, **kwargs) -> MagicMock:
        """创建并跟踪patch，返回mock对象"""
        p = patch(target, **kwargs)
        mock = p.start()
        self.patches.append(p)
        return mock
    
    def create_temp_file(self, temp_dir: Path, name: str, content: str) -> Path:
        """创建临时文件"""
        file_path = temp_dir / name
        file_path.write_text(content, encoding="utf-8")
        self.mock_files.append(file_path)
        return file_path
    
    def create_temp_json(self, temp_dir: Path, name: str, data: Dict) -> Path:
        """创建临时JSON文件"""
        return self.create_temp_file(temp_dir, name, json.dumps(data, indent=2))


# ============================================================================
# 断言辅助函数
# ============================================================================

class AssertHelpers:
    """断言辅助类"""
    
    @staticmethod
    def assert_within_range(value: float, expected: float, tolerance: float, msg: str = None):
        """断言值在范围内"""
        diff = abs(value - expected)
        assert diff <= tolerance, msg or f"值 {value} 与预期 {expected} 的差 {diff} 超出容差 {tolerance}"
    
    @staticmethod
    def assert_is_valid_timestamp(timestamp: int, max_age_seconds: int = 60):
        """断言是有效时间戳"""
        now = int(time.time())
        assert isinstance(timestamp, int), f"时间戳必须是整数，得到 {type(timestamp)}"
        assert timestamp > 0, f"时间戳必须为正，得到 {timestamp}"
        assert timestamp <= now, f"时间戳不能是未来，得到 {timestamp} > {now}"
        assert now - timestamp <= max_age_seconds, f"时间戳太旧，{now - timestamp} 秒前"
    
    @staticmethod
    def assert_json_structure(data: Dict, required_keys: List[str]):
        """断言JSON结构"""
        for key in required_keys:
            assert key in data, f"缺少必需的键: {key}"
    
    @staticmethod
    def assert_file_contains(file_path: Path, substring: str):
        """断言文件包含子串"""
        assert file_path.exists(), f"文件不存在: {file_path}"
        content = file_path.read_text(encoding="utf-8")
        assert substring in content, f"文件内容不包含 '{substring}'"
    
    @staticmethod
    def assert_valid_log_entry(log_line: str, expected_level: str = None):
        """断言有效的日志条目"""
        # 格式: [2024-01-01 12:00:00] [LEVEL] message
        assert log_line.startswith("["), f"日志条目应以[开头: {log_line}"
        parts = log_line.split("] [", 1)
        assert len(parts) == 2, f"日志格式错误: {log_line}"
        
        if expected_level:
            level_part = parts[1].split("]", 1)[0]
            assert level_part == expected_level, f"日志级别应为 {expected_level}，得到 {level_part}"


# ============================================================================
# 测试装饰器
# ============================================================================

def retry_on_failure(max_retries: int = 3, delay: float = 0.1):
    """失败重试装饰器（用于不稳定测试）"""
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        time.sleep(delay)
            raise last_exception
        return wrapper
    return decorator


def timeout(seconds: float):
    """超时装饰器"""
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            import signal
            
            def handler(signum, frame):
                raise TimeoutError(f"测试超时（{seconds}秒）")
            
            old_handler = signal.signal(signal.SIGALRM, handler)
            signal.alarm(int(seconds))
            try:
                return func(*args, **kwargs)
            finally:
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)
        return wrapper
    return decorator
