#!/usr/bin/env python3
"""
data-quality-auditor 功能测试
测试真实实现
"""

import unittest
import tempfile
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from data_quality_auditor import DataQualityAuditor, DataIssue, QualityReport, QualityLevel, IssueType


class TestDataQualityAuditorReal(unittest.TestCase):
    """真实功能测试"""

    def setUp(self):
        """设置"""
        self.auditor = DataQualityAuditor()

    def test_01_audit_complete_data(self):
        """测试完整数据审计"""
        data = [
            {"name": "张三", "age": 25, "email": "zhangsan@example.com"},
            {"name": "李四", "age": 30, "email": "lisi@example.com"}
        ]

        report = self.auditor.audit(data)

        self.assertIsInstance(report, QualityReport)
        self.assertEqual(report.total_records, 2)
        self.assertEqual(report.total_fields, 3)

    def test_02_detect_missing_values(self):
        """测试检测缺失值"""
        data = [
            {"name": "张三", "age": None, "email": ""},
            {"name": "", "age": 30, "email": "lisi@example.com"}
        ]

        report = self.auditor.audit(data)

        missing_issues = [i for i in report.issues if i.issue_type == IssueType.MISSING.value]
        self.assertGreater(len(missing_issues), 0)

    def test_03_detect_invalid_types(self):
        """测试检测无效类型"""
        data = [
            {"name": "张三", "age": "not_a_number", "email": "invalid"}
        ]

        rules = {
            'field_types': {
                'age': 'integer',
                'email': 'email'
            }
        }

        report = self.auditor.audit(data, rules)

        invalid_issues = [i for i in report.issues if i.issue_type in [IssueType.INVALID.value, IssueType.FORMAT_ERROR.value]]
        self.assertGreater(len(invalid_issues), 0)

    def test_04_detect_duplicates(self):
        """测试检测重复数据"""
        data = [
            {"name": "张三", "age": 25},
            {"name": "张三", "age": 25}  # 重复
        ]

        report = self.auditor.audit(data)

        duplicate_issues = [i for i in report.issues if i.issue_type == IssueType.DUPLICATE.value]
        self.assertGreater(len(duplicate_issues), 0)

    def test_05_calculate_completeness(self):
        """测试完整度计算"""
        data = [
            {"name": "张三", "age": 25},
            {"name": "李四", "age": None}  # 缺失
        ]

        report = self.auditor.audit(data)

        age_stat = next((s for s in report.field_stats if s.field_name == "age"), None)
        self.assertIsNotNone(age_stat)
        self.assertEqual(age_stat.completeness, 0.5)  # 1/2

    def test_06_quality_level_calculation(self):
        """测试质量等级计算"""
        # 高质量数据
        good_data = [{"a": 1, "b": 2} for _ in range(10)]
        good_report = self.auditor.audit(good_data)
        self.assertIn(good_report.quality_level, [QualityLevel.EXCELLENT.value, QualityLevel.GOOD.value])

        # 低质量数据
        bad_data = [{"a": None, "b": ""} for _ in range(10)]
        bad_report = self.auditor.audit(bad_data)
        self.assertIn(bad_report.quality_level, [QualityLevel.POOR.value, QualityLevel.CRITICAL.value])

    def test_07_field_stats(self):
        """测试字段统计"""
        data = [
            {"name": "张三", "age": 25},
            {"name": "李四", "age": 30},
            {"name": "王五", "age": 25}  # age重复
        ]

        report = self.auditor.audit(data)

        name_stat = next((s for s in report.field_stats if s.field_name == "name"), None)
        self.assertIsNotNone(name_stat)
        self.assertEqual(name_stat.unique_count, 3)

        age_stat = next((s for s in report.field_stats if s.field_name == "age"), None)
        self.assertEqual(age_stat.unique_count, 2)

    def test_08_empty_data(self):
        """测试空数据处理"""
        report = self.auditor.audit([])

        self.assertEqual(report.total_records, 0)
        self.assertEqual(report.quality_level, QualityLevel.CRITICAL.value)

    def test_09_export_report_json(self):
        """测试JSON导出"""
        data = [{"name": "张三", "age": 25}]
        report = self.auditor.audit(data)

        json_str = self.auditor.export_report(report, "json")
        data_back = json.loads(json_str)

        self.assertIn("overall_score", data_back)
        self.assertIn("quality_level", data_back)

    def test_10_export_report_markdown(self):
        """测试Markdown导出"""
        data = [{"name": "张三", "age": 25}]
        report = self.auditor.audit(data)

        md = self.auditor.export_report(report, "markdown")

        self.assertIn("# 数据质量审计报告", md)
        self.assertIn("EXCELLENT", md)
        self.assertIn("总体评分", md)

    def test_11_email_validation(self):
        """测试邮箱验证"""
        self.assertTrue(DataQualityAuditor._is_email("test@example.com"))
        self.assertFalse(DataQualityAuditor._is_email("invalid"))

    def test_12_date_validation(self):
        """测试日期验证"""
        self.assertTrue(DataQualityAuditor._is_date("2026-04-03"))
        self.assertTrue(DataQualityAuditor._is_date("2026/04/03"))
        self.assertFalse(DataQualityAuditor._is_date("invalid"))


class TestDataQualityAuditorIntegration(unittest.TestCase):
    """集成测试"""

    def test_cli_with_data(self):
        """测试CLI数据审计"""
        import subprocess

        # 创建测试数据文件
        test_data = [
            {"name": "张三", "age": 25, "email": "zhangsan@example.com"},
            {"name": "李四", "age": None, "email": "invalid"}  # 有问题的数据
        ]

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(test_data, f)
            data_path = f.name

        try:
            result = subprocess.run(
                ["python3", "scripts/main.py", "--data", data_path, "--format", "json"],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent.parent
            )

            self.assertEqual(result.returncode, 0)  # 或1，取决于质量等级
            output = result.stdout
            self.assertIn("overall_score", output)
        finally:
            Path(data_path).unlink()


if __name__ == "__main__":
    unittest.main(verbosity=2)
