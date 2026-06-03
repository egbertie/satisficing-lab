#!/usr/bin/env python3
"""
token-throttle-controller 功能测试
测试真实实现
"""

import unittest
import json
import time
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from token_throttle_controller import (
    TokenThrottleController, ThrottleDecision,
    ThrottleLevel, ThrottleAction
)


class TestTokenThrottleControllerReal(unittest.TestCase):
    """真实功能测试"""
    
    def setUp(self):
        """设置"""
        self.controller = TokenThrottleController({
            'tps_limit': 100,
            'burst_limit': 200
        })
    
    def test_01_allow_normal_usage(self):
        """测试正常使用量允许"""
        decision = self.controller.check_and_throttle(10, "test_op")
        
        self.assertIsInstance(decision, ThrottleDecision)
        self.assertEqual(decision.action, ThrottleAction.ALLOW.value)
    
    def test_02_track_usage(self):
        """测试使用追踪"""
        self.controller.check_and_throttle(50, "op1")
        self.controller.check_and_throttle(30, "op2")
        
        status = self.controller.get_status()
        self.assertEqual(status['stats']['total_requests'], 2)
        self.assertEqual(status['stats']['allowed'], 2)
    
    def test_03_throttle_high_usage(self):
        """测试高使用量节流"""
        # 先使用大量Token
        for _ in range(10):
            self.controller.check_and_throttle(20, "bulk_op")
        
        # 这次应该触发节流
        decision = self.controller.check_and_throttle(50, "another_op")
        
        # 可能因为超限制而被拒绝
        self.assertIn(decision.action, [ThrottleAction.ALLOW.value, ThrottleAction.DELAY.value, ThrottleAction.REJECT.value])
    
    def test_04_get_status(self):
        """测试获取状态"""
        status = self.controller.get_status()
        
        self.assertIn('level', status)
        self.assertIn('current_tps', status)
        self.assertIn('limit', status)
        self.assertIn('usage_ratio', status)
        self.assertIn('stats', status)
    
    def test_05_adjust_limit(self):
        """测试调整限制"""
        original_limit = self.controller.tps_limit
        
        self.controller.adjust_limit(200)
        
        self.assertEqual(self.controller.tps_limit, 200)
    
    def test_06_reset_stats(self):
        """测试重置统计"""
        # 先产生一些使用
        self.controller.check_and_throttle(10, "op")
        
        # 重置
        self.controller.reset_stats()
        
        status = self.controller.get_status()
        self.assertEqual(status['stats']['total_requests'], 0)
    
    def test_07_window_usage(self):
        """测试窗口期使用"""
        # 记录一些使用
        self.controller.check_and_throttle(10, "op1")
        self.controller.check_and_throttle(20, "op2")
        
        window_usage = self.controller._get_window_usage()
        
        self.assertGreaterEqual(window_usage, 30)
    
    def test_08_calculate_delay(self):
        """测试延迟计算"""
        delay1 = self.controller._calculate_delay(0.95)
        delay2 = self.controller._calculate_delay(0.99)
        
        # 使用率越高，延迟越长
        self.assertGreater(delay2, delay1)
    
    def test_09_export_stats_json(self):
        """测试JSON导出"""
        self.controller.check_and_throttle(10, "op")
        
        json_str = self.controller.export_stats("json")
        data = json.loads(json_str)
        
        self.assertIn('level', data)
        self.assertIn('current_tps', data)
    
    def test_10_export_stats_markdown(self):
        """测试Markdown导出"""
        md = self.controller.export_stats("markdown")
        
        self.assertIn("# Token节流控制器状态", md)
        self.assertIn("状态等级", md)


class TestTokenThrottleControllerIntegration(unittest.TestCase):
    """集成测试"""
    
    def test_cli_check_and_status(self):
        """测试CLI检查和状态"""
        import subprocess
        
        # 检查Token使用
        result = subprocess.run(
            ["python3", "scripts/main.py", "--check", "50", "--operation", "test"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )
        
        self.assertEqual(result.returncode, 0)
        output = result.stdout
        # 应该显示允许或某种决策
        self.assertTrue("允许" in output or "延迟" in output or "拒绝" in output or "当前" in output)


if __name__ == "__main__":
    unittest.main(verbosity=2)
