"""
Test Configuration and Fixtures
"""

import pytest
from pathlib import Path
import sys

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from qa_system.core import QualityResult, ConfidenceLevel, QualityMetrics
from qa_system.gates import QualityGate, PrerequisitesCheck, ComplianceCheck


@pytest.fixture
def sample_quality_result():
    """示例质量结果"""
    return QualityResult(
        result=True,
        confidence=ConfidenceLevel.HIGH,
        score=95.0,
        notes="Test passed"
    )


@pytest.fixture
def quality_metrics():
    """质量指标收集器"""
    return QualityMetrics()


@pytest.fixture
def basic_gate():
    """基础门禁"""
    gate = QualityGate(name="test-gate", min_score=60, block_on_fail=False)
    gate.add_check(PrerequisitesCheck())
    return gate


@pytest.fixture
def sample_code():
    """示例代码"""
    return """
def calculate_score(value: int) -> int:
    if value >= 80:
        return 100
    return value * 1.25
"""


# Test markers
def pytest_configure(config):
    """配置pytest"""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "e2e: End-to-end tests")
    config.addinivalue_line("markers", "critical: Critical path")
    config.addinivalue_line("markers", "slow: Slow tests")
    config.addinivalue_line("markers", "adversarial: Adversarial tests")
