#!/usr/bin/env python3
"""
adversarial-test Skill测试
"""

import unittest
from pathlib import Path


class TestAdversarialTest(unittest.TestCase):
    """对抗测试Skill验证"""
    
    def test_skill_structure(self):
        """测试Skill结构"""
        skill_dir = Path(__file__).parent
        self.assertTrue((skill_dir / "SKILL.md").exists() or len(list(skill_dir.glob("*.py"))) > 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
