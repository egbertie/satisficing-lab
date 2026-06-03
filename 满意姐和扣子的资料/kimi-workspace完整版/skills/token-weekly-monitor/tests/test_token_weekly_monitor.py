#!/usr/bin/env python3
"""
token-weekly-monitor 功能测试
测试真实实现
"""

import unittest
import tempfile
import json
from pathlib import Path
from datetime import datetime, timedelta
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from token_weekly_monitor import (
    TokenWeeklyMonitor, WeeklyReport, DailyUsage,
    AlertLevel
)


class TestTokenWeeklyMonitorReal(unittest.TestCase):
    """真实功能测试"""

    def setUp(self):
        """设置"""
        self.temp_dir = tempfile.mkdtemp()
        self.monitor = TokenWeeklyMonitor(self.temp_dir)

    def tearDown(self):
        """清理"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_01_record_daily_usage(self):
        """测试记录每日使用"""
        usage = self.monitor.record_daily_usage("2026-04-01", 5000, 100)

        self.assertIsInstance(usage, DailyUsage)
        self.assertEqual(usage.date, "2026-04-01")
        self.assertEqual(usage.tokens_used, 5000)
        self.assertEqual(usage.operations, 100)

    def test_02_load_and_save_usage(self):
        """测试加载和保存使用记录"""
        # 记录一些数据
        self.monitor.record_daily_usage("2026-04-01", 5000, 100)
        self.monitor.record_daily_usage("2026-04-02", 6000, 120)

        # 重新加载
        monitor2 = TokenWeeklyMonitor(self.temp_dir)

        self.assertEqual(len(monitor2.usage_history), 2)

    def test_03_generate_weekly_report(self):
        """测试生成周报"""
        # 记录一周的数据
        for i in range(7):
            date = (datetime(2026, 4, 1) + timedelta(days=i)).strftime('%Y-%m-%d')
            self.monitor.record_daily_usage(date, 5000 + i * 1000, 100 + i * 10)

        report = self.monitor.generate_weekly_report("2026-04-01")

        self.assertIsInstance(report, WeeklyReport)
        self.assertEqual(report.week_start, "2026-04-01")
        self.assertEqual(len(report.daily_breakdown), 7)

    def test_04_analyze_trend_up(self):
        """测试上升趋势分析"""
        daily_data = [
            DailyUsage("2026-04-01", 1000, 10000, 10, 12, 100),
            DailyUsage("2026-04-02", 2000, 10000, 10, 12, 200),
            DailyUsage("2026-04-03", 3000, 10000, 10, 12, 300),
            DailyUsage("2026-04-04", 4000, 10000, 10, 12, 400),
        ]

        trend = self.monitor._analyze_trend(daily_data)
        self.assertEqual(trend, "up")

    def test_05_detect_anomalies(self):
        """测试异常检测"""
        daily_data = [
            DailyUsage("2026-04-01", 1000, 10000, 10, 12, 100),
            DailyUsage("2026-04-02", 1100, 10000, 10, 12, 110),
            DailyUsage("2026-04-03", 1050, 10000, 10, 12, 105),
            DailyUsage("2026-04-04", 1000, 10000, 10, 12, 100),
            DailyUsage("2026-04-05", 50000, 10000, 10, 12, 5000),  # 明显的异常
        ]

        anomalies = self.monitor._detect_anomalies(daily_data)
        self.assertGreater(len(anomalies), 0)

    def test_06_alert_level_calculation(self):
        """测试预警级别计算"""
        self.assertEqual(
            self.monitor._determine_alert_level(0.5, []),
            AlertLevel.NORMAL.value
        )
        self.assertEqual(
            self.monitor._determine_alert_level(0.8, []),
            AlertLevel.CAUTION.value
        )
        self.assertEqual(
            self.monitor._determine_alert_level(0.95, []),
            AlertLevel.WARNING.value
        )
        self.assertEqual(
            self.monitor._determine_alert_level(1.1, []),
            AlertLevel.CRITICAL.value
        )

    def test_07_get_current_week_status(self):
        """测试获取本周状态"""
        # 记录今天
        today = datetime.now().strftime('%Y-%m-%d')
        self.monitor.record_daily_usage(today, 5000, 100)

        status = self.monitor.get_current_week_status()

        self.assertIn('week_start', status)
        self.assertIn('used', status)
        self.assertIn('budget', status)
        self.assertIn('usage_percentage', status)

    def test_08_export_report_json(self):
        """测试JSON导出"""
        for i in range(3):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            self.monitor.record_daily_usage(date, 5000, 100)

        report = self.monitor.generate_weekly_report()
        json_str = self.monitor.export_report(report, "json")
        data = json.loads(json_str)

        self.assertIn('total_tokens', data)
        self.assertIn('usage_percentage', data)

    def test_09_export_report_markdown(self):
        """测试Markdown导出"""
        for i in range(3):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            self.monitor.record_daily_usage(date, 5000, 100)

        report = self.monitor.generate_weekly_report()
        md = self.monitor.export_report(report, "markdown")

        self.assertIn("# Token周度监控报告", md)
        self.assertIn("使用概览", md)

    def test_10_update_existing_record(self):
        """测试更新已有记录"""
        self.monitor.record_daily_usage("2026-04-01", 5000, 100)
        self.monitor.record_daily_usage("2026-04-01", 6000, 150)  # 更新

        record = next((u for u in self.monitor.usage_history if u.date == "2026-04-01"), None)
        self.assertIsNotNone(record)
        self.assertEqual(record.tokens_used, 6000)


class TestTokenWeeklyMonitorIntegration(unittest.TestCase):
    """集成测试"""

    def test_cli_record_and_report(self):
        """测试CLI记录和报告"""
        import subprocess
        import shutil

        temp_dir = tempfile.mkdtemp()
        try:
            # 记录数据
            result = subprocess.run(
                ["python3", "scripts/main.py", "--record", "2026-04-01", "5000", "100", "--data-dir", temp_dir],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent.parent
            )

            self.assertEqual(result.returncode, 0)
            self.assertIn("已记录", result.stdout)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
