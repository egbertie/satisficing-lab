"""
OpenClaw Skills Testing Framework

一个全面的单元测试框架，用于验证关键Skill的可靠性。

使用方法:
    pytest tests/                    # 运行所有测试
    pytest tests/unit/               # 仅运行单元测试
    pytest -m critical               # 运行关键测试
    pytest -m "zero_idle"            # 运行特定Skill测试
    pytest --cov=skills              # 生成覆盖率报告
    pytest -x                        # 失败即停止

参考对象:
    - pytest官方最佳实践
    - Google Testing Blog
    - Martin Fowler - Unit Testing
"""

__version__ = "1.0.0"
__author__ = "Satisficing Institute"

# 导出主要组件
from tests.base import (
    TestDataBuilder,
    HeartbeatStateBuilder,
    TokenBudgetBuilder,
    ZeroIdleStateBuilder,
    SkillTestCase,
    AssertHelpers,
)

__all__ = [
    "TestDataBuilder",
    "HeartbeatStateBuilder",
    "TokenBudgetBuilder",
    "ZeroIdleStateBuilder",
    "SkillTestCase",
    "AssertHelpers",
]
