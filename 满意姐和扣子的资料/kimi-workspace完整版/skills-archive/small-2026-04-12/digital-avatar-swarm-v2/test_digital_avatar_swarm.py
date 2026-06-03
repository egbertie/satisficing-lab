#!/usr/bin/env python3
"""
digital-avatar-swarm-v2 单元测试
"""

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from digital_avatar_swarm import DigitalAvatarSwarm, AvatarRole


class TestDigitalAvatarSwarm(unittest.TestCase):
    """DigitalAvatarSwarm单元测试"""
    
    def setUp(self):
        self.swarm = DigitalAvatarSwarm()
    
    def test_init_avatars(self):
        """测试角色初始化"""
        self.assertGreater(len(self.swarm.avatars), 0)
    
    def test_activate_avatar(self):
        """测试角色激活"""
        success = self.swarm.activate_avatar(AvatarRole.BLUE_ARMY_AUDITOR)
        self.assertTrue(success)
        
        avatar = self.swarm.get_avatar_status(AvatarRole.BLUE_ARMY_AUDITOR)
        self.assertTrue(avatar.is_active)
        self.assertEqual(avatar.activation_count, 1)
    
    def test_get_active_avatars(self):
        """测试获取活跃角色"""
        # 激活一个角色
        self.swarm.activate_avatar(AvatarRole.SATISFY_NOW)
        
        active = self.swarm.get_active_avatars()
        self.assertEqual(len(active), 1)
    
    def test_token_optimizer(self):
        """测试Token优化器"""
        optimizer = self.swarm.avatars.get(AvatarRole.TOKEN_OPTIMIZER)
        self.assertIsNotNone(optimizer)
        
        result = optimizer.optimize("skill_building")
        self.assertIn("suggestion", result)


if __name__ == "__main__":
    unittest.main(verbosity=2)


def run_tests():
    """蓝军审计要求的测试入口"""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()
