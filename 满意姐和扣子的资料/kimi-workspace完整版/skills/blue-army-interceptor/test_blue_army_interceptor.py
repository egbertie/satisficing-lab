#!/usr/bin/env python3
"""
blue-army-interceptor测试文件
"""

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import importlib.util
spec = importlib.util.spec_from_file_location("blue_army_interceptor", 
    str(Path(__file__).parent / 'blue_army_interceptor.py'))
interceptor_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(interceptor_module)


class TestBlueArmyInterceptor(unittest.TestCase):
    """蓝军拦截器测试"""
    
    def test_module_import(self):
        """测试模块导入"""
        self.assertIsNotNone(interceptor_module)
    
    def test_token_optimizer_exists(self):
        """测试token优化器存在"""
        optimizer_file = Path(__file__).parent / 'token_optimizer.py'
        self.assertTrue(optimizer_file.exists())
    
    def test_5standard_report_exists(self):
        """测试5标准报告存在"""
        report_file = Path(__file__).parent / '5standard-completion-report.md'
        self.assertTrue(report_file.exists())


if __name__ == '__main__':
    unittest.main(verbosity=2)
