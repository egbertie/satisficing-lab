"""
OpenClaw Skills Testing Framework - Shared Fixtures and Utilities

参考对象: pytest官方最佳实践 + Clean Architecture测试模式
"""

import os
import sys
import json
import tempfile
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Generator
from unittest.mock import MagicMock, patch

import pytest

# 添加项目路径
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "skills"))

# Skill路径
ZERO_IDLE_PATH = PROJECT_ROOT / "skills" / "zero-idle-enforcer"
TOKEN_BUDGET_PATH = PROJECT_ROOT / "skills" / "token-budget-enforcer"
BLUE_SENTINEL_PATH = PROJECT_ROOT / "skills" / "blue-sentinel"

# ============================================================================
# S1: 被测Skill注册表
# ============================================================================

REGISTERED_SKILLS = {
    "zero-idle-enforcer": {
        "path": "skills/zero-idle-enforcer",
        "risk_level": "P0",
        "test_markers": ["zero_idle", "critical"],
        "coverage_target": 90,
        "test_levels": ["unit", "integration", "e2e"]
    },
    "token-budget-enforcer": {
        "path": "skills/token-budget-enforcer",
        "risk_level": "P0",
        "test_markers": ["token_budget", "critical"],
        "coverage_target": 90,
        "test_levels": ["unit", "integration", "e2e"]
    },
    "blue-sentinel": {
        "path": "skills/blue-sentinel",
        "risk_level": "P1",
        "test_markers": ["blue_sentinel"],
        "coverage_target": 80,
        "test_levels": ["unit", "integration", "e2e"]
    }
}


# ============================================================================
# 基础Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def project_root() -> Path:
    """项目根目录"""
    return PROJECT_ROOT


@pytest.fixture(scope="session")
def workspace_dir() -> Path:
    """工作空间目录"""
    return PROJECT_ROOT


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """临时目录，每个测试后自动清理"""
    tmp = tempfile.mkdtemp(prefix="openclaw_test_")
    yield Path(tmp)
    shutil.rmtree(tmp, ignore_errors=True)


@pytest.fixture
def mock_time() -> MagicMock:
    """模拟时间"""
    with patch("time.time") as mock:
        mock.return_value = 1704067200  # 2024-01-01 00:00:00 UTC
        yield mock


@pytest.fixture
def mock_datetime_now() -> Generator[datetime, None, None]:
    """模拟datetime.now()"""
    fixed_now = datetime(2024, 1, 1, 12, 0, 0)
    with patch("datetime.datetime") as mock_dt:
        mock_dt.now.return_value = fixed_now
        mock_dt.utcnow.return_value = fixed_now
        yield fixed_now


# ============================================================================
# Memory Fixtures
# ============================================================================

@pytest.fixture
def memory_dir(temp_dir: Path) -> Path:
    """模拟memory目录"""
    mem_dir = temp_dir / "memory"
    mem_dir.mkdir(exist_ok=True)
    return mem_dir


@pytest.fixture
def logs_dir(temp_dir: Path) -> Path:
    """模拟logs目录"""
    log_dir = temp_dir / "logs"
    log_dir.mkdir(exist_ok=True)
    return log_dir


@pytest.fixture
def mock_heartbeat_state(memory_dir: Path) -> Path:
    """创建模拟的heartbeat-state.json"""
    state_file = memory_dir / "heartbeat-state.json"
    state = {
        "lastChecks": {
            "email": 1704063600,
            "calendar": 1704060000,
            "weather": 1704056400,
            "user_activity": 1704063600  # 1小时前
        }
    }
    state_file.write_text(json.dumps(state, indent=2))
    return state_file


@pytest.fixture
def mock_token_weekly_monitor(memory_dir: Path) -> Path:
    """创建模拟的token-weekly-monitor.json"""
    monitor_file = memory_dir / "token-weekly-monitor.json"
    monitor = {
        "date": "2024-01-01",
        "daily_budget": 50000,
        "used_today": 15000,
        "remaining_percentage": 70,
        "weekly_total": 350000,
        "weekly_used": 105000
    }
    monitor_file.write_text(json.dumps(monitor, indent=2))
    return monitor_file


# ============================================================================
# Zero-Idle-Enforcer Fixtures
# ============================================================================

@pytest.fixture
def zero_idle_enforcer_path() -> Path:
    """zero-idle-enforcer路径"""
    return ZERO_IDLE_PATH


@pytest.fixture
def zero_idle_state(memory_dir: Path) -> Path:
    """创建zero-idle状态文件"""
    state_file = memory_dir / "zero-idle-state.json"
    state = {
        "last_fill_time": 1703977200  # 24小时前
    }
    state_file.write_text(json.dumps(state, indent=2))
    return state_file


@pytest.fixture
def zero_idle_config() -> Dict[str, Any]:
    """zero-idle-enforcer配置"""
    return {
        "idle_threshold_seconds": 7200,  # 2小时
        "fill_interval_seconds": 7200,   # 2小时
        "max_inactive_days": 30,
        "token_critical_threshold": 15,
        "token_low_threshold": 30,
        "line1_tasks": [
            ("专家论文深度研读", "学习笔记"),
            ("AI模型/技术研究", "技术报告"),
            ("行业趋势分析", "洞察报告"),
            ("案例库扩展研究", "案例分析")
        ],
        "line2_tasks": [
            "当日工作复盘",
            "系统配置轻维护",
            "知识图谱更新",
            "Skill质量自检"
        ]
    }


# ============================================================================
# Token-Budget-Enforcer Fixtures
# ============================================================================

@pytest.fixture
def token_budget_enforcer_path() -> Path:
    """token-budget-enforcer路径"""
    return TOKEN_BUDGET_PATH


@pytest.fixture
def token_budget_config() -> Dict[str, Any]:
    """token-budget-enforcer配置"""
    return {
        "daily_budget": 50000,
        "strategic_reserve_percentage": 30,
        "operational_budget_percentage": 50,
        "innovation_fund_percentage": 20,
        "alert_thresholds": {
            "warning": 70,
            "critical": 90,
            "exhausted": 100
        },
        "circuit_breaker": {
            "single_task_overrun_multiplier": 2.0,
            "similarity_threshold": 0.8
        }
    }


@pytest.fixture
def token_budget_pools() -> Dict[str, Dict[str, int]]:
    """Token预算池状态"""
    return {
        "strategic_reserve": {
            "total": 15000,
            "used": 0,
            "available": 15000
        },
        "operational_budget": {
            "total": 25000,
            "used": 10000,
            "available": 15000
        },
        "innovation_fund": {
            "total": 10000,
            "used": 5000,
            "available": 5000
        }
    }


# ============================================================================
# Blue-Sentinel Fixtures
# ============================================================================

@pytest.fixture
def blue_sentinel_path() -> Path:
    """blue-sentinel路径"""
    return BLUE_SENTINEL_PATH


@pytest.fixture
def blue_sentinel_skills() -> list:
    """Blue Sentinel管理的5个Skill列表"""
    return [
        "adversarial_generator",
        "meta_auditor",
        "post_hoc_autopsy",
        "pre_mortem_auditor",
        "real_time_sentinel"
    ]


@pytest.fixture
def blue_sentinel_checklist() -> Dict[str, Any]:
    """认知审计检查清单模板"""
    return {
        "audit_id": "AUD-2024-001",
        "timestamp": "2024-01-01T12:00:00Z",
        "auditor": "blue-sentinel",
        "items": [
            {"id": "CK-001", "category": "确认偏误", "checked": False, "severity": "high"},
            {"id": "CK-002", "category": "锚定效应", "checked": False, "severity": "medium"},
            {"id": "CK-003", "category": "幸存者偏差", "checked": False, "severity": "medium"},
            {"id": "CK-004", "category": "叙事谬误", "checked": False, "severity": "high"},
            {"id": "CK-005", "category": "认知失调", "checked": False, "severity": "low"}
        ],
        "findings": [],
        "recommendations": []
    }


# ============================================================================
# 辅助函数
# ============================================================================

def create_mock_file(path: Path, content: str, mtime: float = None) -> Path:
    """创建模拟文件，可选设置修改时间"""
    path.write_text(content, encoding="utf-8")
    if mtime is not None:
        os.utime(path, (mtime, mtime))
    return path


def create_mock_json(path: Path, data: Dict[str, Any], mtime: float = None) -> Path:
    """创建模拟JSON文件"""
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    if mtime is not None:
        os.utime(path, (mtime, mtime))
    return path


def assert_json_file_contains(path: Path, key: str, expected_value: Any) -> None:
    """断言JSON文件包含特定键值"""
    assert path.exists(), f"文件不存在: {path}"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert key in data, f"键 '{key}' 不存在于文件中"
    assert data[key] == expected_value, f"键 '{key}' 的值 {data[key]} 不等于预期 {expected_value}"


def assert_log_contains(log_path: Path, substring: str, level: str = None) -> bool:
    """断言日志文件包含特定子串"""
    if not log_path.exists():
        return False
    content = log_path.read_text(encoding="utf-8")
    if level:
        substring = f"[{level}] {substring}"
    return substring in content


# ============================================================================
# 自定义Markers
# ============================================================================

def pytest_configure(config):
    """配置自定义markers"""
    config.addinivalue_line("markers", "zero_idle: zero-idle-enforcer tests")
    config.addinivalue_line("markers", "token_budget: token-budget-enforcer tests")
    config.addinivalue_line("markers", "blue_sentinel: blue-sentinel tests")
    config.addinivalue_line("markers", "critical: critical path tests (always run)")
    config.addinivalue_line("markers", "unit: Unit tests (fast, isolated)")
    config.addinivalue_line("markers", "integration: Integration tests (component interaction)")
    config.addinivalue_line("markers", "e2e: End-to-end tests (full workflow)")
