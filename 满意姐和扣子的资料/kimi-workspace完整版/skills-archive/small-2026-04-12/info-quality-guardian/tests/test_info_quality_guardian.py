#!/usr/bin/env python3
"""
info-quality-guardian 功能测试
测试真实实现
"""

import unittest
import tempfile
import json
from pathlib import Path
from datetime import datetime, timedelta
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from info_quality_guardian import InfoQualityGuardian, InfoItem, QualityReport, QualityIssue, InfoQualityLevel, CheckType


class TestInfoQualityGuardianReal(unittest.TestCase):
    """真实功能测试"""

    def setUp(self):
        """设置"""
        self.guardian = InfoQualityGuardian()

    def test_01_check_complete_info(self):
        """测试完整信息检查"""
        items = [
            InfoItem(
                content="这是一条完整的信息内容，长度足够",
                source="官方数据源",
                timestamp=datetime.now().isoformat(),
                category="新闻"
            )
        ]

        report = self.guardian.check(items)

        self.assertIsInstance(report, QualityReport)
        self.assertEqual(report.item_count, 1)

    def test_02_detect_incomplete_content(self):
        """测试检测不完整内容"""
        items = [
            InfoItem(
                content="短",  # 太短
                source="官方",
                timestamp=datetime.now().isoformat(),
                category="新闻"
            )
        ]

        report = self.guardian.check(items)

        incomplete_issues = [i for i in report.issues if i.check_type == CheckType.COMPLETENESS.value]
        self.assertGreater(len(incomplete_issues), 0)

    def test_03_detect_missing_source(self):
        """测试检测缺失来源"""
        items = [
            InfoItem(
                content="这是一条信息内容，长度足够长",
                source="",  # 缺失
                timestamp=datetime.now().isoformat(),
                category="新闻"
            )
        ]

        report = self.guardian.check(items)

        source_issues = [i for i in report.issues if i.field == "source"]
        self.assertGreater(len(source_issues), 0)

    def test_04_detect_outdated_info(self):
        """测试检测过期信息"""
        old_time = (datetime.now() - timedelta(hours=48)).isoformat()

        items = [
            InfoItem(
                content="这是一条信息内容，长度足够长",
                source="官方",
                timestamp=old_time,
                category="新闻"
            )
        ]

        report = self.guardian.check(items)

        time_issues = [i for i in report.issues if i.check_type == CheckType.TIMELINESS.value]
        self.assertGreater(len(time_issues), 0)

    def test_05_quality_level_calculation(self):
        """测试质量等级计算"""
        # 高质量信息
        good_items = [
            InfoItem(
                content="这是高质量的信息内容，来源可靠，时效性强",
                source="可信来源",
                timestamp=datetime.now().isoformat(),
                category="新闻"
            )
        ]

        good_report = self.guardian.check(good_items)
        self.assertIn(good_report.quality_level, [InfoQualityLevel.RELIABLE.value, InfoQualityLevel.USABLE.value])

        # 低质量信息 (多个问题)
        bad_items = [
            InfoItem(
                content="",
                source="",
                timestamp="",
                category=""
            ),
            InfoItem(
                content="",
                source="",
                timestamp="",
                category=""
            )
        ]

        bad_report = self.guardian.check(bad_items)
        # 多个严重问题应该导致低质量等级
        self.assertLess(bad_report.overall_score, 70)

    def test_06_generate_recommendations(self):
        """测试生成建议"""
        items = [
            InfoItem(
                content="短",  # 有问题
                source="",
                timestamp=(datetime.now() - timedelta(hours=48)).isoformat(),
                category="新闻"
            )
        ]

        report = self.guardian.check(items)

        self.assertGreater(len(report.recommendations), 0)

    def test_07_empty_data(self):
        """测试空数据处理"""
        report = self.guardian.check([])

        self.assertEqual(report.item_count, 0)
        self.assertEqual(report.quality_level, InfoQualityLevel.UNRELIABLE.value)

    def test_08_export_report_json(self):
        """测试JSON导出"""
        items = [
            InfoItem(
                content="测试信息",
                source="测试来源",
                timestamp=datetime.now().isoformat(),
                category="测试"
            )
        ]

        report = self.guardian.check(items)
        json_str = self.guardian.export_report(report, "json")
        data = json.loads(json_str)

        self.assertIn("overall_score", data)
        self.assertIn("quality_level", data)

    def test_09_export_report_markdown(self):
        """测试Markdown导出"""
        items = [
            InfoItem(
                content="测试信息",
                source="测试来源",
                timestamp=datetime.now().isoformat(),
                category="测试"
            )
        ]

        report = self.guardian.check(items)
        md = self.guardian.export_report(report, "markdown")

        self.assertIn("# 信息采集质量报告", md)
        self.assertIn("总体评分", md)

    def test_10_has_obvious_errors(self):
        """测试明显错误检测"""
        self.assertTrue(InfoQualityGuardian._has_obvious_errors("这是一个错误：数据"))
        self.assertTrue(InfoQualityGuardian._has_obvious_errors("这是错误的error信息"))
        self.assertFalse(InfoQualityGuardian._has_obvious_errors("这是正常信息"))


class TestInfoQualityGuardianIntegration(unittest.TestCase):
    """集成测试"""

    def test_cli_with_data(self):
        """测试CLI数据检查"""
        import subprocess

        # 创建测试数据
        test_data = [
            {
                "content": "这是一条测试信息内容",
                "source": "测试来源",
                "timestamp": datetime.now().isoformat(),
                "category": "测试"
            }
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

            self.assertEqual(result.returncode, 0)
            output = result.stdout
            self.assertIn("overall_score", output)
        finally:
            Path(data_path).unlink()


if __name__ == "__main__":
    unittest.main(verbosity=2)
