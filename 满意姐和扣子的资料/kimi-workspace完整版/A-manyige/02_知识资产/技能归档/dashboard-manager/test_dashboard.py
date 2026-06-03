#!/usr/bin/env python3
"""
dashboard-manager测试
"""

import unittest
from pathlib import Path


class TestDashboardManager(unittest.TestCase):
    """仪表盘管理测试"""
    
    def test_structure(self):
        """测试结构"""
        skill_dir = Path(__file__).parent
        self.assertTrue(skill_dir.exists())


if __name__ == '__main__':
    unittest.main(verbosity=2)
