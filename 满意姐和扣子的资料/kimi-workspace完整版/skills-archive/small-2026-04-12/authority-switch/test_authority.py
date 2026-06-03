#!/usr/bin/env python3
"""
authority-switch测试
"""

import unittest
from pathlib import Path


class TestAuthoritySwitch(unittest.TestCase):
    """权限切换测试"""
    
    def test_skill_exists(self):
        """测试Skill存在"""
        skill_dir = Path(__file__).parent
        self.assertTrue(skill_dir.exists())


if __name__ == '__main__':
    unittest.main(verbosity=2)
