"""
Unit Tests for Gates Module
"""

import pytest
from qa_system.gates import (
    QualityGate, PrerequisitesCheck, ComplianceCheck, 
    ResultsCheck, DocumentationCheck, create_gate
)
from qa_system.core import GateStatus


@pytest.mark.unit
class TestPrerequisitesCheck:
    """测试前置条件检查"""
    
    def test_prerequisites_check_init(self):
        """测试初始化"""
        check = PrerequisitesCheck()
        
        assert check.name == "prerequisites"
        assert check.weight == 0.15
        assert check.blocking is True
    
    def test_prerequisites_evaluation(self):
        """测试前置条件评估"""
        check = PrerequisitesCheck()
        result = check.evaluate(None)
        
        assert isinstance(result.result, bool)
        assert 0 <= result.score <= 100
        assert "env_vars" in result.details
        assert "dependencies" in result.details


@pytest.mark.unit
class TestComplianceCheck:
    """测试合规检查"""
    
    def test_compliance_check_init(self):
        """测试初始化"""
        check = ComplianceCheck()
        
        assert check.name == "compliance"
        assert check.weight == 0.25
        assert check.blocking is True
    
    def test_compliance_evaluation(self):
        """测试合规评估"""
        check = ComplianceCheck()
        result = check.evaluate(None)
        
        assert isinstance(result.result, bool)
        assert 0 <= result.score <= 100
        assert "code_style" in result.details
        assert "security_scan" in result.details


@pytest.mark.unit
class TestResultsCheck:
    """测试结果检查"""
    
    def test_results_check_init(self):
        """测试初始化"""
        check = ResultsCheck()
        
        assert check.name == "results"
        assert check.weight == 0.40
        assert check.blocking is True
    
    def test_results_evaluation(self):
        """测试结果评估"""
        check = ResultsCheck()
        result = check.evaluate(None)
        
        assert isinstance(result.result, bool)
        assert 0 <= result.score <= 100
        assert "unit_tests" in result.details
        assert "coverage" in result.details


@pytest.mark.unit
class TestDocumentationCheck:
    """测试文档检查"""
    
    def test_documentation_check_init(self):
        """测试初始化"""
        check = DocumentationCheck()
        
        assert check.name == "documentation"
        assert check.weight == 0.20
        assert check.blocking is False
    
    def test_documentation_evaluation(self):
        """测试文档评估"""
        check = DocumentationCheck()
        result = check.evaluate(None)
        
        assert isinstance(result.result, bool)
        assert 0 <= result.score <= 100


@pytest.mark.unit
class TestQualityGate:
    """测试质量门禁"""
    
    def test_gate_creation(self):
        """测试门禁创建"""
        gate = QualityGate(name="test", min_score=75.0, block_on_fail=True)
        
        assert gate.name == "test"
        assert gate.min_score == 75.0
        assert gate.block_on_fail is True
    
    def test_add_check(self):
        """测试添加检查项"""
        gate = QualityGate(name="test")
        gate.add_check(PrerequisitesCheck())
        
        assert len(gate.checks) == 1
        assert isinstance(gate.checks[0], PrerequisitesCheck)
    
    def test_gate_execution(self, basic_gate):
        """测试门禁执行"""
        result = basic_gate.execute(None)
        
        assert result.gate_name == "test-gate"
        assert isinstance(result.status, GateStatus)
        assert 0 <= result.total_score <= 100
        assert len(result.checks) >= 1


@pytest.mark.unit
class TestCreateGate:
    """测试门禁工厂函数"""
    
    def test_create_basic_gate(self):
        """测试创建基础门禁"""
        gate = create_gate("basic")
        
        assert gate.name == "basic-gate"
        assert gate.min_score == 60
        assert gate.block_on_fail is False
    
    def test_create_standard_gate(self):
        """测试创建标准门禁"""
        gate = create_gate("standard")
        
        assert gate.name == "standard-gate"
        assert gate.min_score == 75
        assert gate.block_on_fail is True
        assert len(gate.checks) == 3
    
    def test_create_critical_gate(self):
        """测试创建关键门禁"""
        gate = create_gate("critical")
        
        assert gate.name == "critical-gate"
        assert gate.min_score == 90
        assert gate.block_on_fail is True
        assert len(gate.checks) == 4
    
    def test_create_unknown_gate_defaults_to_standard(self):
        """测试未知类型默认使用标准"""
        gate = create_gate("unknown")
        
        assert gate.min_score == 75  # 使用standard配置
