"""
Unit Tests for Core Module
"""

import pytest
from qa_system.core import (
    QualityResult, ConfidenceLevel, GateStatus, 
    QualityMetrics, LimitationRegistry, QUALITY_DISCLAIMER
)


@pytest.mark.unit
class TestQualityResult:
    """测试质量结果类"""
    
    def test_quality_result_creation(self):
        """测试质量结果创建"""
        result = QualityResult(
            result=True,
            confidence=ConfidenceLevel.HIGH,
            score=85.5,
            notes="Test notes"
        )
        
        assert result.result is True
        assert result.confidence == ConfidenceLevel.HIGH
        assert result.score == 85.5
        assert result.notes == "Test notes"
    
    def test_quality_result_str(self):
        """测试字符串表示"""
        result = QualityResult(result=True, confidence=ConfidenceLevel.MEDIUM, score=75.0)
        str_repr = str(result)
        
        assert "True" in str_repr
        assert "medium" in str_repr
        assert "75.0" in str_repr


@pytest.mark.unit
class TestConfidenceLevel:
    """测试置信度等级"""
    
    def test_confidence_levels(self):
        """测试所有置信度等级"""
        assert ConfidenceLevel.HIGH.value == "high"
        assert ConfidenceLevel.MEDIUM.value == "medium"
        assert ConfidenceLevel.LOW.value == "low"
        assert ConfidenceLevel.UNKNOWN.value == "unknown"


@pytest.mark.unit
class TestQualityMetrics:
    """测试质量指标"""
    
    def test_metrics_recording(self, quality_metrics):
        """测试指标记录"""
        quality_metrics.record("test_metric", 100, "count")
        
        assert "test_metric" in quality_metrics.metrics
        assert quality_metrics.metrics["test_metric"]["value"] == 100
        assert quality_metrics.metrics["test_metric"]["unit"] == "count"
    
    def test_coverage_metrics_calculation(self, quality_metrics):
        """测试覆盖率指标计算"""
        coverage_data = {
            "line_coverage": 85.0,
            "branch_coverage": 78.0,
            "function_coverage": 92.0,
            "path_coverage": 75.0
        }
        
        metrics = quality_metrics.calculate_coverage_metrics(coverage_data)
        
        assert metrics["line_coverage"] == 85.0
        assert metrics["branch_coverage"] == 78.0
        assert metrics["function_coverage"] == 92.0
        assert metrics["path_coverage"] == 75.0
    
    def test_defect_metrics_calculation(self, quality_metrics):
        """测试缺陷指标计算"""
        defects = [
            {"status": "open", "severity": "critical"},
            {"status": "closed", "severity": "high"},
            {"status": "open", "severity": "low"}
        ]
        
        metrics = quality_metrics.calculate_defect_metrics(defects)
        
        assert metrics["total_found"] == 3
        assert metrics["open"] == 2
        assert metrics["critical"] == 1
        assert metrics["high"] == 1


@pytest.mark.unit
class TestLimitationRegistry:
    """测试局限性注册表"""
    
    def test_get_all_limitations(self):
        """测试获取所有局限性"""
        limitations = LimitationRegistry.get_all_limitations()
        
        assert len(limitations) > 0
        assert all("id" in l for l in limitations)
        assert all("category" in l for l in limitations)
        assert all("description" in l for l in limitations)
    
    def test_get_by_category(self):
        """测试按类别获取"""
        limitations = LimitationRegistry.get_by_category("业务逻辑")
        
        assert len(limitations) >= 1
        assert all(l["category"] == "业务逻辑" for l in limitations)
    
    def test_get_high_impact(self):
        """测试获取高影响局限"""
        limitations = LimitationRegistry.get_high_impact()
        
        assert len(limitations) >= 1
        assert all(l["impact"] == "高" for l in limitations)


@pytest.mark.unit
class TestQualityDisclaimer:
    """测试免责声明"""
    
    def test_disclaimer_exists(self):
        """测试免责声明存在"""
        assert QUALITY_DISCLAIMER is not None
        assert len(QUALITY_DISCLAIMER) > 0
    
    def test_disclaimer_content(self):
        """测试免责声明内容"""
        assert "局限性" in QUALITY_DISCLAIMER
        assert "业务逻辑" in QUALITY_DISCLAIMER
        assert "安全" in QUALITY_DISCLAIMER
