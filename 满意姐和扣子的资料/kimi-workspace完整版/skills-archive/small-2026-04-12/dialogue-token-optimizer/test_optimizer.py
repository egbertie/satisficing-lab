#!/usr/bin/env python3
"""
dialogue-token-optimizer测试
"""

import unittest
from pathlib import Path


class TestDialogueTokenOptimizer(unittest.TestCase):
    """对话Token优化测试"""
    
    def test_structure(self):
        """测试结构"""
        skill_dir = Path(__file__).parent
        self.assertTrue(skill_dir.exists())


if __name__ == '__main__':
    unittest.main(verbosity=2)
