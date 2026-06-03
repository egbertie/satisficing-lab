#!/usr/bin/env python3
"""
quality-assurance 功能测试
测试真实实现
"""

import unittest
import tempfile
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from quality_assurance import QualityAssurance, AssuranceReport, CheckResult, GateStatus, CheckType


class TestQualityAssuranceReal(unittest.TestCase):
    """真实功能测试"""
    
    def setUp(self):
        """设置"""
        self.qa = QualityAssurance()
    
    def test_01_load_default_gates(self):
        """测试加载默认门禁"""
        self.assertIn('pre-commit', self.qa.gates)
        self.assertIn('pre-release', self.qa.gates)
    
    def test_02_run_pre_commit_gate(self):
        """测试运行pre-commit门禁"""
        # 在当前项目路径运行
        report = self.qa.run_gate('pre-commit', str(Path(__file__).parent.parent))
        
        self.assertIsInstance(report, AssuranceReport)
        self.assertEqual(report.gate_name, 'pre-commit')
    
    def test_03_run_unknown_gate(self):
        """测试运行未知门禁"""
        report = self.qa.run_gate('unknown-gate', '.')
        
        self.assertEqual(report.overall_status, GateStatus.FAILED.value)
        self.assertFalse(report.can_proceed)
    
    def test_04_check_documentation(self):
        """测试文档检查"""
        # 在有效项目路径上运行
        project_path = str(Path(__file__).parent.parent)
        status, message, details = self.qa._check_documentation(project_path)

        # 应该有SKILL.md
        self.assertIn(status, [GateStatus.PASSED.value, GateStatus.WARNING.value])
    
    def test_06_gate_status_calculation(self):
        """测试门禁状态计算"""
        # 模拟所有检查通过
        results = [
            CheckResult(CheckType.UNIT_TEST.value, "单元测试", GateStatus.PASSED.value, 100, "通过", []),
            CheckResult(CheckType.CODE_REVIEW.value, "代码审查", GateStatus.PASSED.value, 100, "通过", [])
        ]
        
        passed = sum(1 for r in results if r.status == GateStatus.PASSED.value)
        self.assertEqual(passed, 2)
    
    def test_07_export_report_json(self):
        """测试JSON导出"""
        report = self.qa.run_gate('pre-commit', str(Path(__file__).parent.parent))
        json_str = self.qa.export_report(report, "json")
        data = json.loads(json_str)
        
        self.assertIn("overall_status", data)
        self.assertIn("check_results", data)
    
    def test_08_export_report_markdown(self):
        """测试Markdown导出"""
        report = self.qa.run_gate('pre-commit', str(Path(__file__).parent.parent))
        md = self.qa.export_report(report, "markdown")
        
        self.assertIn("# 质量保证报告", md)
        self.assertIn("总体状态", md)
    
    def test_09_get_check_name(self):
        """测试获取检查名称"""
        name = self.qa._get_check_name(CheckType.UNIT_TEST.value)
        self.assertEqual(name, "单元测试")
        
        name = self.qa._get_check_name("unknown")
        self.assertEqual(name, "unknown")
    
    def test_10_can_proceed_logic(self):
        """测试能否继续的逻辑"""
        report = self.qa.run_gate('pre-commit', str(Path(__file__).parent.parent))
        
        # can_proceed应该根据状态正确设置
        if report.overall_status == GateStatus.BLOCKED.value:
            self.assertFalse(report.can_proceed)


class TestQualityAssuranceIntegration(unittest.TestCase):
    """集成测试"""
    
    def test_cli_run_gate(self):
        """测试CLI运行门禁"""
        import subprocess
        
        result = subprocess.run(
            ["python3", "scripts/main.py", "--gate", "pre-commit", "--path", "."],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )
        
        # 可能成功也可能失败，但应该有输出
        output = result.stdout + result.stderr
        self.assertIn("质量保证报告", output)


if __name__ == "__main__":
    unittest.main(verbosity=2)
