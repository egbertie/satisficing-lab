#!/usr/bin/env python3
"""
blackboard-manager 单元测试
"""

import unittest
import tempfile
import shutil
import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from blackboard_manager import BlackboardManager, StateEntry


class TestBlackboardManager(unittest.TestCase):
    """BlackboardManager单元测试"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.bb = BlackboardManager(storage_path=f"{self.temp_dir}/state.yaml")
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_write_and_read(self):
        """测试写入和读取"""
        success, version, msg = self.bb.write("test_key", "test_value", "test_worker")
        self.assertTrue(success)
        
        value, ver = self.bb.read("test_key")
        self.assertEqual(value, "test_value")
        self.assertEqual(ver, 1)
    
    def test_version_increment(self):
        """测试版本递增"""
        self.bb.write("key", "v1", "w1")
        self.bb.write("key", "v2", "w2")
        
        value, version = self.bb.read("key")
        self.assertEqual(value, "v2")
        self.assertEqual(version, 2)
    
    def test_optimistic_lock_success(self):
        """测试乐观锁成功"""
        self.bb.write("key", "v1", "w1")
        
        # 使用正确版本号更新
        success, version, msg = self.bb.write("key", "v2", "w2", expected_version=1)
        self.assertTrue(success)
        self.assertEqual(version, 2)
    
    def test_optimistic_lock_fail(self):
        """测试乐观锁失败"""
        self.bb.write("key", "v1", "w1")
        
        # 使用错误版本号更新
        success, version, msg = self.bb.write("key", "v2", "w2", expected_version=999)
        self.assertFalse(success)
        self.assertIn("版本冲突", msg)
    
    def test_delete(self):
        """测试删除"""
        self.bb.write("key", "value", "worker")
        
        success, msg = self.bb.delete("key")
        self.assertTrue(success)
        
        value, version = self.bb.read("key")
        self.assertIsNone(value)
    
    def test_get_all_keys(self):
        """测试获取所有键"""
        self.bb.write("key1", "v1", "w1")
        self.bb.write("key2", "v2", "w2")
        
        keys = self.bb.get_all_keys()
        self.assertEqual(len(keys), 2)
        self.assertIn("key1", keys)
        self.assertIn("key2", keys)
    
    def test_persistence(self):
        """测试持久化"""
        self.bb.write("key", "value", "worker")
        self.bb.force_save()
        
        # 创建新的实例，应该能读取之前的数据
        bb2 = BlackboardManager(storage_path=f"{self.temp_dir}/state.yaml")
        value, version = bb2.read("key")
        self.assertEqual(value, "value")


if __name__ == "__main__":
    unittest.main(verbosity=2)
