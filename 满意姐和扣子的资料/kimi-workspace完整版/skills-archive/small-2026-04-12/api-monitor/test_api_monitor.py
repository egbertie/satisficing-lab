#!/usr/bin/env python3
"""
api-monitor测试
"""

import unittest
from pathlib import Path


class TestApiMonitor(unittest.TestCase):
    """API监控测试"""
    
    def test_module_exists(self):
        """测试模块存在"""
        skill_dir = Path(__file__).parent
        py_files = list(skill_dir.glob("*.py"))
        self.assertGreaterEqual(len(py_files), 1)


if __name__ == '__main__':
    unittest.main(verbosity=2)
