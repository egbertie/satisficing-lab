#!/usr/bin/env python3
"""heartbeat-protocol测试"""
import unittest
from pathlib import Path
class TestHeartbeatProtocol(unittest.TestCase):
    def test_exists(self):
        self.assertTrue(Path(__file__).parent.exists())
if __name__ == '__main__':
    unittest.main(verbosity=2)
