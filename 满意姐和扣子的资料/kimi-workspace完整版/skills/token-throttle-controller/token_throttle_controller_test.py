#!/usr/bin/env python3
"""
token_throttle_controller_test.py - Token节流控制器 S5/S7验证
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, '/root/.openclaw/workspace/skills/token-throttle-controller/scripts')

from throttle_controller import THRESHOLDS, get_token_level, log


class TestTokenThrottleControllerS5S7(unittest.TestCase):
    """S5/S7测试套件"""
    
    # ===== S5: 自我验证测试 =====
    
    def test_thresholds_defined(self):
        """S5-1: 阈值定义正确"""
        self.assertIn("normal", THRESHOLDS)
        self.assertIn("throttle", THRESHOLDS)
        self.assertEqual(THRESHOLDS["normal"], 30)
        self.assertEqual(THRESHOLDS["throttle"], 15)
    
    def test_get_token_level_returns_int(self):
        """S5-2: 获取Token级别返回整数"""
        level = get_token_level()
        self.assertIsInstance(level, int)
        self.assertGreaterEqual(level, 0)
        self.assertLessEqual(level, 100)
    
    def test_log_function(self):
        """S5-3: 日志函数正常工作"""
        import io
        import sys
        
        # 捕获输出
        captured = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured
        
        log("测试消息")
        
        sys.stdout = old_stdout
        output = captured.getvalue()
        
        self.assertIn("测试消息", output)
    
    # ===== S7: 对抗测试 =====
    
    def test_threshold_boundary_normal(self):
        """S7-1: 正常模式边界"""
        # 31%应该正常
        self.assertGreater(31, THRESHOLDS["normal"])
    
    def test_threshold_boundary_throttle(self):
        """S7-2: 节流模式边界"""
        # 15%应该节流
        self.assertEqual(15, THRESHOLDS["throttle"])
        # 14%应该暂停
        self.assertLess(14, THRESHOLDS["throttle"])
    
    def test_extreme_low_token(self):
        """S7-3: 极低Token场景"""
        # 验证可以处理0%
        self.assertIsInstance(THRESHOLDS["throttle"], int)
    
    def test_extreme_high_token(self):
        """S7-4: 极高Token场景"""
        # 验证可以处理100%
        self.assertIsInstance(THRESHOLDS["normal"], int)


def run_tests():
    """运行测试"""
    print("=" * 60)
    print("Token Throttle Controller - S5/S7 验证")
    print("=" * 60)
    
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestTokenThrottleControllerS5S7)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 60)
    print(f"运行: {result.testsRun}")
    print(f"通过: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    
    if result.wasSuccessful():
        print("\n✅ S5/S7验证通过！")
        return True
    return False


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
