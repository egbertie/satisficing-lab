#!/usr/bin/env python3
"""
cost-redlines 功能测试
测试真实实现
"""

import unittest
import tempfile
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from cost_redlines import CostMonitor, CostEntry, Alert, CostReport, AlertLevel


class TestCostMonitorReal(unittest.TestCase):
    """真实功能测试"""
    
    def setUp(self):
        """设置"""
        self.monitor = CostMonitor()
    
    def test_01_record_cost(self):
        """测试成本记录"""
        entry = self.monitor.record_cost(
            amount=100.0,
            category="人力",
            level="L1_BASE",
            description="测试成本"
        )
        self.assertIsInstance(entry, CostEntry)
        self.assertEqual(entry.amount, 100.0)
        self.assertEqual(entry.category, "人力")
    
    def test_02_get_total_cost(self):
        """测试总成本计算"""
        self.monitor.record_cost(100.0, "人力", "L1_BASE")
        self.monitor.record_cost(200.0, "设备", "L2_EXTENDED")
        
        total = self.monitor.get_total_cost()
        self.assertEqual(total, 300.0)
    
    def test_03_get_cost_by_category(self):
        """测试按类别统计"""
        self.monitor.record_cost(100.0, "人力", "L1_BASE")
        self.monitor.record_cost(200.0, "人力", "L1_BASE")
        self.monitor.record_cost(150.0, "设备", "L2_EXTENDED")
        
        by_category = self.monitor.get_cost_by_category()
        self.assertEqual(by_category["人力"], 300.0)
        self.assertEqual(by_category["设备"], 150.0)
    
    def test_04_get_cost_by_level(self):
        """测试按级别统计"""
        self.monitor.record_cost(100.0, "人力", "L1_BASE")
        self.monitor.record_cost(200.0, "设备", "L2_EXTENDED")
        
        by_level = self.monitor.get_cost_by_level()
        self.assertEqual(by_level["L1_BASE"], 100.0)
        self.assertEqual(by_level["L2_EXTENDED"], 200.0)
    
    def test_05_warning_alert(self):
        """测试警告预警 (80%)"""
        # 设置预算1000，使用850 (85%)
        self.monitor.config['budget_limit'] = 1000.0
        self.monitor.record_cost(850.0, "服务", "L3_VALUE_ADDED")
        
        alert_level = self.monitor.get_alert_level()
        self.assertEqual(alert_level, AlertLevel.WARNING)
    
    def test_06_critical_alert(self):
        """测试临界预警 (95%)"""
        self.monitor.config['budget_limit'] = 1000.0
        self.monitor.record_cost(960.0, "服务", "L3_VALUE_ADDED")
        
        alert_level = self.monitor.get_alert_level()
        self.assertEqual(alert_level, AlertLevel.CRITICAL)
    
    def test_07_exceeded_alert(self):
        """测试超支预警 (100%+)"""
        self.monitor.config['budget_limit'] = 1000.0
        self.monitor.record_cost(1100.0, "服务", "L4_RISK")
        
        alert_level = self.monitor.get_alert_level()
        self.assertEqual(alert_level, AlertLevel.EXCEEDED)
    
    def test_08_generate_report(self):
        """测试生成报告"""
        self.monitor.record_cost(500.0, "人力", "L1_BASE", "开发工作")
        self.monitor.record_cost(300.0, "设备", "L2_EXTENDED", "服务器")
        
        report = self.monitor.generate_report()
        
        self.assertIsInstance(report, CostReport)
        self.assertEqual(report.total_cost, 800.0)
        self.assertIn("人力", report.cost_by_category)
        self.assertIn("设备", report.cost_by_category)
    
    def test_09_check_budget_available(self):
        """测试预算可用性检查"""
        self.monitor.config['budget_limit'] = 1000.0
        self.monitor.record_cost(500.0, "人力", "L1_BASE")
        
        # 检查可用
        available, message = self.monitor.check_budget_available(200.0)
        self.assertTrue(available)
        
        # 检查不足
        available, message = self.monitor.check_budget_available(600.0)
        self.assertFalse(available)
    
    def test_10_generate_recommendations(self):
        """测试生成优化建议"""
        # 高使用率应生成建议
        recommendations = self.monitor._generate_recommendations(0.85)
        self.assertGreater(len(recommendations), 0)
        
        # 正常使用率不应生成警告建议
        recommendations = self.monitor._generate_recommendations(0.50)
        self.assertEqual(len(recommendations), 0)
    
    def test_11_export_report_json(self):
        """测试JSON格式导出"""
        self.monitor.record_cost(500.0, "人力", "L1_BASE")
        report = self.monitor.generate_report()
        
        json_str = self.monitor.export_report(report, "json")
        data = json.loads(json_str)
        
        self.assertIn("total_cost", data)
        self.assertIn("cost_by_category", data)
    
    def test_12_export_report_markdown(self):
        """测试Markdown格式导出"""
        self.monitor.record_cost(500.0, "人力", "L1_BASE")
        report = self.monitor.generate_report()
        
        md = self.monitor.export_report(report, "markdown")
        
        self.assertIn("# 成本监控报告", md)
        self.assertIn("500.0", md)


class TestCostMonitorIntegration(unittest.TestCase):
    """集成测试"""
    
    def test_cli_record_cost(self):
        """测试CLI记录成本"""
        import subprocess
        
        result = subprocess.run(
            ["python3", "scripts/main.py", "--record", "150.0", "人力", "L1_BASE", "测试支出"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )
        
        self.assertEqual(result.returncode, 0)
        self.assertIn("成本已记录", result.stdout)
    
    def test_cli_generate_report(self):
        """测试CLI生成报告"""
        import subprocess
        
        # 先记录一些成本
        subprocess.run(
            ["python3", "scripts/main.py", "--record", "100.0", "设备", "L2_EXTENDED", "服务器费用"],
            capture_output=True,
            cwd=Path(__file__).parent.parent
        )
        
        # 生成报告
        result = subprocess.run(
            ["python3", "scripts/main.py", "--report", "--format", "json"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )
        
        self.assertEqual(result.returncode, 0)
        output = result.stdout
        self.assertIn("total_cost", output)


if __name__ == "__main__":
    unittest.main(verbosity=2)
