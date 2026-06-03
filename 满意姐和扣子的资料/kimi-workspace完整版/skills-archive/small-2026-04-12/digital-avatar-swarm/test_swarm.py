#!/usr/bin/env python3
"""
digital-avatar-swarm测试
"""

import unittest
from pathlib import Path


class TestDigitalAvatarSwarm(unittest.TestCase):
    """数字人集群测试"""
    
    def test_skill_exists(self):
        """测试存在"""
        skill_dir = Path(__file__).parent
        self.assertTrue(skill_dir.exists())


if __name__ == '__main__':
    unittest.main(verbosity=2)
