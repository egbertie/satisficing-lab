#!/usr/bin/env python3
"""
baseline-checker测试文件
验证基线检查器核心功能
"""

import unittest
import json
import sys
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

# 添加脚本路径
sys.path.insert(0, str(Path(__file__).parent))

# 导入baseline-checker-runner (处理连字符文件名)
import importlib.util
spec = importlib.util.spec_from_file_location("baseline_checker_runner", 
    str(Path(__file__).parent / 'baseline-checker-runner.py'))
baseline_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(baseline_module)
BaselineChecker = baseline_module.BaselineChecker


class TestBaselineChecker(unittest.TestCase):
    """基线检查器测试"""
    
    def setUp(self):
        """测试前置"""
        self.checker = BaselineChecker()
    
    def test_init(self):
        """测试初始化"""
        self.assertIsNotNone(self.checker.baselines)
        self.assertIsNotNone(self.checker.check_time)
    
    def test_load_baselines(self):
        """测试加载基线配置"""
        baselines = self.checker.baselines
        self.assertIn('categories', baselines)
        self.assertIn('version', baselines)
    
    @patch('psutil.cpu_percent')
    def test_collect_performance_data(self, mock_cpu):
        """测试性能数据收集"""
        mock_cpu.return_value = 50.0
        data = self.checker._collect_performance_data()
        self.assertIn('cpu_usage_percent', data)
        self.assertIsInstance(data['cpu_usage_percent'], (int, float))
    
    def test_check_indicator_pass(self):
        """测试指标检查 - 通过情况"""
        indicator = {
            'description': '测试指标',
            'max': 100,
            'min': 0,
            'unit': '%'
        }
        result = self.checker._check_indicator('test_metric', indicator, 50)
        self.assertEqual(result['status'], 'PASS')
    
    def test_check_indicator_violation(self):
        """测试指标检查 - 违规情况"""
        indicator = {
            'description': '测试指标',
            'max': 100,
            'min': 0,
            'unit': '%'
        }
        result = self.checker._check_indicator('test_metric', indicator, 150)
        self.assertEqual(result['status'], 'VIOLATION')
        self.assertIsNotNone(result['recommendation'])
    
    def test_check_indicator_warning(self):
        """测试指标检查 - 警告情况"""
        indicator = {
            'description': '测试指标',
            'max': 100,
            'target': 80
        }
        result = self.checker._check_indicator('test_metric', indicator, 90)
        # 90 > target 80 but < max 100, should be PASS or WARNING
        self.assertIn(result['status'], ['PASS', 'WARNING'])
    
    def test_calculate_total_summary(self):
        """测试总体摘要计算"""
        results = {
            'category1': {
                'summary': {'total': 5, 'pass': 3, 'warning': 1, 'violation': 1}
            },
            'category2': {
                'summary': {'total': 5, 'pass': 4, 'warning': 1, 'violation': 0}
            }
        }
        summary = self.checker._calculate_total_summary(results)
        self.assertEqual(summary['total'], 10)
        self.assertEqual(summary['pass'], 7)
        self.assertEqual(summary['pass_rate'], 70.0)
    
    def test_validate_baselines(self):
        """测试基线验证"""
        validation = self.checker.validate_baselines()
        self.assertIn('validations', validation)
        self.assertIn('total', validation)
    
    def test_run_adversarial_tests(self):
        """测试对抗测试"""
        result = self.checker.run_adversarial_tests()
        self.assertIn('tests_run', result)
        self.assertIn('sensitivity_score', result)
        self.assertIsInstance(result['sensitivity_score'], (int, float))


class TestBaselineCheckerIntegration(unittest.TestCase):
    """集成测试"""
    
    def test_full_check_flow(self):
        """测试完整检查流程"""
        checker = BaselineChecker()
        results = checker.check_all(['performance'])
        
        self.assertIn('check_time', results)
        self.assertIn('categories', results)
        self.assertIn('summary', results)
        self.assertIn('performance', results['categories'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
