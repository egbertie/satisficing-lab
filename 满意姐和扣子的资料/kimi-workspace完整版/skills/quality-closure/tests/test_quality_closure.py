#!/usr/bin/env python3
"""
quality-closure 功能测试
测试真实实现
"""

import unittest
import tempfile
import json
from pathlib import Path
from datetime import datetime, timedelta
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from quality_closure import QualityClosure, QualityIssue, ClosureReport, IssueStatus, IssueSeverity, ClosureType


class TestQualityClosureReal(unittest.TestCase):
    """真实功能测试"""
    
    def setUp(self):
        """设置 - 使用临时目录"""
        self.temp_dir = tempfile.mkdtemp()
        self.qc = QualityClosure(self.temp_dir)
    
    def tearDown(self):
        """清理"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_01_create_issue(self):
        """测试创建问题"""
        issue = self.qc.create_issue(
            title="测试问题",
            description="这是一个测试问题",
            severity=IssueSeverity.HIGH.value
        )
        
        self.assertIsInstance(issue, QualityIssue)
        self.assertTrue(issue.id.startswith("QI-"))
        self.assertEqual(issue.title, "测试问题")
        self.assertEqual(issue.status, IssueStatus.OPEN.value)
    
    def test_02_get_issue(self):
        """测试获取问题"""
        created = self.qc.create_issue("测试", "描述", IssueSeverity.MEDIUM.value)
        
        found = self.qc.get_issue(created.id)
        self.assertIsNotNone(found)
        self.assertEqual(found.id, created.id)
        
        not_found = self.qc.get_issue("QI-9999")
        self.assertIsNone(not_found)
    
    def test_03_list_issues(self):
        """测试列出问题"""
        self.qc.create_issue("问题1", "描述1", IssueSeverity.HIGH.value)
        self.qc.create_issue("问题2", "描述2", IssueSeverity.MEDIUM.value)
        
        all_issues = self.qc.list_issues()
        self.assertEqual(len(all_issues), 2)
        
        high_issues = self.qc.list_issues(severity=IssueSeverity.HIGH.value)
        self.assertEqual(len(high_issues), 1)
    
    def test_04_resolve_issue(self):
        """测试解决问题"""
        issue = self.qc.create_issue("测试", "描述", IssueSeverity.HIGH.value)
        
        resolved = self.qc.resolve_issue(
            issue.id,
            solution="修复了代码",
            root_cause="逻辑错误",
            user="测试员"
        )
        
        self.assertIsNotNone(resolved)
        self.assertEqual(resolved.status, IssueStatus.RESOLVED.value)
        self.assertEqual(resolved.solution, "修复了代码")
        self.assertEqual(resolved.root_cause, "逻辑错误")
    
    def test_05_verify_issue(self):
        """测试验证问题"""
        issue = self.qc.create_issue("测试", "描述", IssueSeverity.HIGH.value)
        self.qc.resolve_issue(issue.id, "修复", "原因", "测试员")
        
        verified = self.qc.verify_issue(issue.id, True, "验证员", "测试通过")
        
        self.assertIsNotNone(verified)
        self.assertEqual(verified.status, IssueStatus.VERIFIED.value)
        self.assertEqual(verified.verified_by, "验证员")
    
    def test_06_close_issue(self):
        """测试关闭问题"""
        issue = self.qc.create_issue("测试", "描述", IssueSeverity.LOW.value)
        
        closed = self.qc.close_issue(
            issue.id,
            ClosureType.FIXED.value,
            "管理员",
            "问题已解决"
        )
        
        self.assertIsNotNone(closed)
        self.assertEqual(closed.status, IssueStatus.CLOSED.value)
        self.assertEqual(closed.closure_type, ClosureType.FIXED.value)
        self.assertIsNotNone(closed.closed_at)
    
    def test_07_reopen_issue(self):
        """测试重新打开问题"""
        issue = self.qc.create_issue("测试", "描述", IssueSeverity.HIGH.value)
        self.qc.close_issue(issue.id, ClosureType.FIXED.value, "用户", "关闭")
        
        reopened = self.qc.update_status(issue.id, IssueStatus.REOPENED.value, "问题复现", "用户")
        
        self.assertIsNotNone(reopened)
        self.assertEqual(reopened.status, IssueStatus.REOPENED.value)
        self.assertEqual(reopened.reopen_count, 1)
    
    def test_08_generate_report(self):
        """测试生成报告"""
        # 创建一些问题
        self.qc.create_issue("问题1", "描述", IssueSeverity.CRITICAL.value)
        self.qc.create_issue("问题2", "描述", IssueSeverity.HIGH.value)
        
        report = self.qc.generate_report("monthly")
        
        self.assertIsInstance(report, ClosureReport)
        self.assertEqual(report.total_issues, 2)
        self.assertEqual(report.open_issues, 2)
        self.assertIn(IssueSeverity.CRITICAL.value, report.by_severity)
    
    def test_09_closure_rate_calculation(self):
        """测试闭环率计算"""
        # 创建并关闭一个问题
        issue = self.qc.create_issue("测试", "描述", IssueSeverity.HIGH.value)
        self.qc.close_issue(issue.id, ClosureType.FIXED.value, "用户", "关闭")
        
        # 创建另一个未关闭的问题
        self.qc.create_issue("测试2", "描述", IssueSeverity.MEDIUM.value)
        
        report = self.qc.generate_report()
        
        self.assertEqual(report.total_issues, 2)
        self.assertEqual(report.closed_count, 1)
        self.assertAlmostEqual(report.closure_rate, 0.5)
    
    def test_10_export_report_json(self):
        """测试JSON导出"""
        self.qc.create_issue("测试", "描述", IssueSeverity.HIGH.value)
        report = self.qc.generate_report()
        
        json_str = self.qc.export_report(report, "json")
        data = json.loads(json_str)
        
        self.assertIn("total_issues", data)
        self.assertIn("closure_rate", data)
    
    def test_11_export_report_markdown(self):
        """测试Markdown导出"""
        self.qc.create_issue("测试", "描述", IssueSeverity.HIGH.value)
        report = self.qc.generate_report()
        
        md = self.qc.export_report(report, "markdown")
        
        self.assertIn("# 质量闭环报告", md)
        self.assertIn("总问题数", md)


class TestQualityClosureIntegration(unittest.TestCase):
    """集成测试"""

    def test_cli_create_and_list(self):
        """测试CLI创建和列出"""
        import subprocess
        import shutil

        temp_dir = tempfile.mkdtemp()
        try:
            # 创建问题
            result = subprocess.run(
                ["python3", "-c", f"""
import sys
sys.path.insert(0, 'scripts')
from quality_closure import QualityClosure, IssueSeverity
qc = QualityClosure('{temp_dir}')
issue = qc.create_issue('CLI测试', '测试描述', IssueSeverity.HIGH.value)
print(f'Created: {{issue.id}}')
"""],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent.parent
            )

            self.assertEqual(result.returncode, 0)
            self.assertIn("Created:", result.stdout)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
