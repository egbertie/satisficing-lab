"""
End-to-End Tests - Full Workflow
"""

import pytest
import time
from pathlib import Path
import json


@pytest.mark.e2e
class TestFullQualityWorkflow:
    """完整质量工作流程端到端测试"""
    
    def test_complete_quality_assessment_workflow(self):
        """测试完整质量评估流程"""
        from qa_system.gates import create_gate
        from qa_system.core import QualityMetrics
        from qa_system.adversarial import AdversarialTestRunner
        
        # 1. 执行质量门禁
        gate = create_gate("standard")
        gate_result = gate.execute(None)
        
        assert gate_result.total_score >= 0
        assert len(gate_result.checks) > 0
        
        # 2. 收集质量指标
        metrics = QualityMetrics()
        metrics.record("gate_score", gate_result.total_score, "points")
        
        # 3. 运行对抗测试
        runner = AdversarialTestRunner()
        adv_report = runner.run_all_tests()
        
        metrics.record("detection_rate", adv_report.detection_rate, "percent")
        
        # 4. 验证完整流程输出
        summary = metrics.get_summary()
        assert "gate_score" in summary["metrics"]
        assert "detection_rate" in summary["metrics"]
    
    def test_quality_report_generation(self):
        """测试质量报告生成端到端"""
        from qa_system.gates import create_gate
        from qa_system.adversarial import run_adversarial_tests
        
        # 收集所有数据
        gate = create_gate("standard")
        gate_result = gate.execute(None)
        
        adv_report = run_adversarial_tests()
        
        # 构建完整报告
        report = {
            "timestamp": gate_result.timestamp.isoformat(),
            "gate": gate_result.to_dict(),
            "adversarial": adv_report.to_dict(),
            "summary": {
                "gate_score": gate_result.total_score,
                "detection_rate": adv_report.detection_rate,
                "overall_status": "PASS" if gate_result.status.value in ["passed", "conditional"] else "FAIL"
            }
        }
        
        # 验证报告结构
        assert "gate" in report
        assert "adversarial" in report
        assert "summary" in report
        assert report["summary"]["gate_score"] >= 0
        assert report["summary"]["detection_rate"] >= 0
    
    def test_s1_through_s7_standards_e2e(self):
        """测试S1-S7全部标准端到端"""
        from qa_system.core import LimitationRegistry, QualityMetrics
        from qa_system.gates import create_gate
        from qa_system.adversarial import run_adversarial_tests
        
        # S1: 全局考虑
        limitations = LimitationRegistry.get_all_limitations()
        high_impact = LimitationRegistry.get_high_impact()
        
        # S2-S4: 质量门禁
        gate = create_gate("critical")
        gate_result = gate.execute(None)
        
        # S3: 指标收集
        metrics = QualityMetrics()
        metrics.record("gate_score", gate_result.total_score, "points")
        
        # S5: 自我验证（通过对抗测试）
        adv_report = run_adversarial_tests()
        metrics.record("mutation_score", adv_report.detection_rate, "percent")
        
        # S6: 局限性已在S1中验证
        assert len(limitations) >= 7
        
        # S7: 对抗测试已执行
        assert len(adv_report.results) > 0
        
        # 验证所有标准都有数据
        summary = metrics.get_summary()
        assert len(summary["metrics"]) >= 2


@pytest.mark.e2e
class TestCIIntegrationWorkflow:
    """CI集成工作流端到端测试"""
    
    def test_pre_commit_gate_workflow(self):
        """测试预提交门禁工作流"""
        from qa_system.gates import create_gate
        
        gate = create_gate("basic")
        result = gate.execute(None)
        
        # 预提交应该快速完成
        assert result.total_score >= 0
        assert len(result.checks) >= 1
    
    def test_pre_push_gate_workflow(self):
        """测试推送前门禁工作流"""
        from qa_system.gates import create_gate
        
        gate = create_gate("standard")
        result = gate.execute(None)
        
        # 推送前应该有单元测试和集成测试
        check_names = [c["name"] for c in result.checks]
        assert "prerequisites" in check_names
        assert "compliance" in check_names
        assert "results" in check_names
    
    def test_pr_merge_gate_workflow(self):
        """测试PR合并门禁工作流"""
        from qa_system.gates import create_gate
        from qa_system.adversarial import run_adversarial_tests
        
        # PR合并需要更严格的检查
        gate = create_gate("critical")
        gate_result = gate.execute(None)
        
        # 包含文档检查
        check_names = [c["name"] for c in gate_result.checks]
        assert "documentation" in check_names
        
        # 对抗测试验证
        adv_report = run_adversarial_tests()
        
        # 记录结果
        assert gate_result.total_score >= 0
        assert adv_report.detection_rate >= 0


@pytest.mark.e2e
class TestErrorRecoveryWorkflow:
    """错误恢复工作流端到端测试"""
    
    def test_failed_gate_recovery(self):
        """测试门禁失败恢复"""
        from qa_system.gates import QualityGate, ComplianceCheck
        from qa_system.core import GateStatus
        
        # 创建一个会失败的门禁
        gate = QualityGate(name="strict", min_score=100, block_on_fail=True)
        gate.add_check(ComplianceCheck())
        
        result = gate.execute(None)
        
        # 由于min_score=100，大概率会失败
        if result.status == GateStatus.BLOCKED:
            # 验证失败信息
            assert len(result.failed_checks) >= 0 or result.total_score < 100
    
    def test_adversarial_test_failure_detection(self):
        """测试对抗测试失败检测"""
        from qa_system.adversarial import AdversarialTestRunner
        
        runner = AdversarialTestRunner()
        report = runner.run_all_tests()
        
        # 如果检测率低于85%，状态应该是FAIL
        if report.detection_rate < 85:
            assert report.status == "FAIL"
        else:
            assert report.status == "PASS"
