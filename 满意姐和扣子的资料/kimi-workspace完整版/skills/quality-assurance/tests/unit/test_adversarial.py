"""
Unit Tests for Adversarial Module
"""

import pytest
from qa_system.adversarial import (
    DefectInjector, AdversarialTestRunner, 
    MutationTesting, run_adversarial_tests
)


@pytest.mark.unit
class TestDefectInjector:
    """测试缺陷注入器"""
    
    def test_get_available_defects(self):
        """测试获取可用缺陷类型"""
        defects = DefectInjector.get_available_defects()
        
        assert len(defects) > 0
        assert "syntax_error" in defects
        assert "sql_injection" in defects
    
    def test_inject_syntax_error(self, sample_code):
        """测试注入语法错误"""
        mutated = DefectInjector.inject_defect(sample_code, "syntax_error")
        
        assert "df " in mutated
        assert "def " not in mutated or mutated.count("df ") > mutated.count("def ")
    
    def test_inject_sql_injection(self, sample_code):
        """测试注入SQL注入漏洞"""
        mutated = DefectInjector.inject_defect(sample_code, "sql_injection")
        
        assert 'f"SELECT' in mutated
        assert "user_id" in mutated


@pytest.mark.unit
class TestAdversarialTestRunner:
    """测试对抗测试运行器"""
    
    def test_runner_initialization(self):
        """测试运行器初始化"""
        runner = AdversarialTestRunner("qa_system")
        
        assert runner.target_path.name == "qa_system"
        assert runner.results == []
    
    def test_run_all_tests(self):
        """测试运行所有对抗测试"""
        runner = AdversarialTestRunner()
        report = runner.run_all_tests()
        
        assert len(report.results) > 0
        assert 0 <= report.detection_rate <= 100
        assert report.status in ["PASS", "FAIL"]
    
    def test_detection_rate_calculation(self):
        """测试检测率计算"""
        runner = AdversarialTestRunner()
        report = runner.run_all_tests()
        
        detected = sum(1 for r in report.results if r.detected)
        expected_rate = detected / len(report.results) * 100
        
        assert abs(report.detection_rate - expected_rate) < 0.01


@pytest.mark.unit
class TestMutationTesting:
    """测试变异测试"""
    
    def test_mutation_generation(self, sample_code):
        """测试变异生成"""
        mt = MutationTesting(sample_code)
        mutations = mt.generate_mutations()
        
        assert len(mutations) > 0
        assert all("operator" in m for m in mutations)
        assert all("mutated_code" in m for m in mutations)
    
    def test_mutation_operators(self, sample_code):
        """测试变异算子应用"""
        mt = MutationTesting(sample_code)
        mutations = mt.generate_mutations()
        
        # 检查算子是否正确应用
        for mutation in mutations:
            if mutation["operator"] == "+>-":
                assert "-" in mutation["mutated_code"]
            elif mutation["operator"] == "==>!=":
                assert "!=" in mutation["mutated_code"]


@pytest.mark.unit
class TestAdversarialReport:
    """测试对抗测试报告"""
    
    def test_report_to_dict(self):
        """测试报告转换为字典"""
        from qa_system.core import AdversarialReport, AdversarialResult
        from datetime import datetime
        
        results = [
            AdversarialResult(
                defect_type="test",
                description="Test defect",
                expected_detection="UNIT_TEST",
                detected=True,
                details="Detected"
            )
        ]
        
        report = AdversarialReport(
            results=results,
            detection_rate=100.0,
            status="PASS"
        )
        
        data = report.to_dict()
        
        assert data["total_injections"] == 1
        assert data["detected"] == 1
        assert data["detection_rate"] == 100.0
        assert data["status"] == "PASS"
