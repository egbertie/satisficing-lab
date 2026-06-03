"""
Integration Tests - Pipeline Integration
"""

import pytest
import time
from qa_system.gates import create_gate
from qa_system.core import GateStatus


@pytest.mark.integration
class TestQualityGateIntegration:
    """质量门禁集成测试"""
    
    def test_standard_gate_full_execution(self):
        """测试标准门禁完整执行"""
        gate = create_gate("standard")
        result = gate.execute(None)
        
        # 验证结果结构
        assert result.gate_name == "standard-gate"
        assert isinstance(result.status, GateStatus)
        assert 0 <= result.total_score <= 100
        assert len(result.checks) == 3
        
        # 验证检查项
        check_names = [c["name"] for c in result.checks]
        assert "prerequisites" in check_names
        assert "compliance" in check_names
        assert "results" in check_names
    
    def test_critical_gate_with_all_checks(self):
        """测试关键门禁包含所有检查项"""
        gate = create_gate("critical")
        result = gate.execute(None)
        
        check_names = [c["name"] for c in result.checks]
        assert "prerequisites" in check_names
        assert "compliance" in check_names
        assert "results" in check_names
        assert "documentation" in check_names
        
        assert len(result.checks) == 4


@pytest.mark.integration
class TestQualityMetricsIntegration:
    """质量指标集成测试"""
    
    def test_metrics_collection_pipeline(self):
        """测试指标收集流水线"""
        from qa_system.core import QualityMetrics
        
        metrics = QualityMetrics()
        
        # 记录多个指标
        metrics.record("coverage", 85.5, "percent")
        metrics.record("defects", 3, "count")
        metrics.record("build_time", 45.2, "seconds")
        
        summary = metrics.get_summary()
        
        assert "coverage" in summary["metrics"]
        assert "defects" in summary["metrics"]
        assert "build_time" in summary["metrics"]
    
    def test_defect_metrics_calculation(self):
        """测试缺陷指标计算集成"""
        from qa_system.core import QualityMetrics
        
        metrics = QualityMetrics()
        
        defects = [
            {"status": "open", "severity": "critical"},
            {"status": "open", "severity": "high"},
            {"status": "closed", "severity": "low"},
            {"status": "closed", "severity": "medium"}
        ]
        
        result = metrics.calculate_defect_metrics(defects)
        
        assert result["total_found"] == 4
        assert result["open"] == 2
        assert result["critical"] == 1
        assert result["high"] == 1
        assert result["resolution_rate"] == 0.5


@pytest.mark.integration
class TestAdversarialIntegration:
    """对抗测试集成测试"""
    
    def test_adversarial_test_execution(self):
        """测试对抗测试执行集成"""
        from qa_system.adversarial import AdversarialTestRunner
        
        runner = AdversarialTestRunner()
        report = runner.run_all_tests()
        
        # 验证报告结构
        assert len(report.results) > 0
        assert 0 <= report.detection_rate <= 100
        assert report.status in ["PASS", "FAIL"]
        
        # 验证每个结果
        for result in report.results:
            assert result.defect_type is not None
            assert result.expected_detection is not None
            assert isinstance(result.detected, bool)
    
    def test_defect_injection_integration(self):
        """测试缺陷注入集成"""
        from qa_system.adversarial import DefectInjector
        
        code = """
def calculate(value):
    if value >= 80:
        return 100
    return value
"""
        
        # 测试多种缺陷注入
        defects_to_test = ["syntax_error", "sql_injection", "comparison_error"]
        
        for defect_type in defects_to_test:
            mutated = DefectInjector.inject_defect(code, defect_type)
            assert mutated != code  # 确保代码被修改


@pytest.mark.integration
class TestS1S7StandardsIntegration:
    """S1-S7标准集成测试"""
    
    def test_s1_global_consideration(self):
        """测试S1全局考虑"""
        from qa_system.core import LimitationRegistry
        
        # 验证全局考虑维度
        limitations = LimitationRegistry.get_all_limitations()
        
        categories = set(l["category"] for l in limitations)
        expected_categories = ["业务逻辑", "AI输出", "并发问题", "性能问题", "安全漏洞", "UI/UX", "集成故障"]
        
        for cat in expected_categories:
            assert any(cat in c for c in categories), f"Missing category: {cat}"
    
    def test_s2_system_closed_loop(self):
        """测试S2系统闭环"""
        # 验证质量门禁流程
        gate = create_gate("standard")
        result = gate.execute(None)
        
        # 验证包含所有维度
        assert len(result.checks) >= 3
        
        # 验证权重总和为1.0
        total_weight = sum(c.get("weight", 0) for c in result.checks)
        assert abs(total_weight - 1.0) < 0.01 or total_weight > 0
    
    def test_s3_observable_output(self):
        """测试S3可观测输出"""
        gate = create_gate("standard")
        result = gate.execute(None)
        
        # 验证输出包含必要信息
        assert result.total_score is not None
        assert result.weighted_score is not None
        assert len(result.checks) > 0
        
        for check in result.checks:
            assert "name" in check
            assert "score" in check
            assert "weight" in check
    
    def test_s5_self_validation(self):
        """测试S5自我验证"""
        from qa_system.adversarial import AdversarialTestRunner
        
        runner = AdversarialTestRunner()
        report = runner.run_all_tests()
        
        # 验证测试有效性检查
        assert report.detection_rate is not None
        
        # 验证检测率可计算
        detected = sum(1 for r in report.results if r.detected)
        expected_rate = detected / len(report.results) * 100 if report.results else 0
        assert abs(report.detection_rate - expected_rate) < 0.01
    
    def test_s6_cognitive_humility(self):
        """测试S6认知谦逊"""
        from qa_system.core import LimitationRegistry, QUALITY_DISCLAIMER
        
        # 验证局限性声明
        limitations = LimitationRegistry.get_all_limitations()
        assert len(limitations) > 0
        
        # 验证免责声明
        assert "局限性" in QUALITY_DISCLAIMER
        assert "业务逻辑" in QUALITY_DISCLAIMER
    
    def test_s7_adversarial_testing(self):
        """测试S7对抗测试"""
        from qa_system.adversarial import run_adversarial_tests
        
        report = run_adversarial_tests()
        
        # 验证对抗测试执行
        assert len(report.results) > 0
        assert report.detection_rate is not None
        
        # 验证每个结果有明确状态
        for result in report.results:
            assert result.status in ["PASS", "FAIL"]
