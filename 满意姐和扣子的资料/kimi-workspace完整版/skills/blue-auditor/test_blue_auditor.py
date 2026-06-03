#!/usr/bin/env python3
"""
blue-auditor测试文件
"""

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import importlib.util
spec = importlib.util.spec_from_file_location("blue_auditor", 
    str(Path(__file__).parent / 'blue_auditor.py'))
blue_auditor_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(blue_auditor_module)


class TestBlueAuditor(unittest.TestCase):
    """蓝军审计测试"""
    
    def test_module_import(self):
        """测试模块导入"""
        self.assertIsNotNone(blue_auditor_module)
    
    def test_sop_structure(self):
        """测试SOP结构"""
        sop_file = Path(__file__).parent / 'blue_army_sop.py'
        self.assertTrue(sop_file.exists())
    
    def test_runtime_verifier_exists(self):
        """测试运行时验证器存在"""
        verifier_file = Path(__file__).parent / 'runtime_verifier.py'
        self.assertTrue(verifier_file.exists())


if __name__ == '__main__':
    unittest.main(verbosity=2)
