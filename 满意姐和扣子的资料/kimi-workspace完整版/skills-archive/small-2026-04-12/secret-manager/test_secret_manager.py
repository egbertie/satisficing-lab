#!/usr/bin/env python3
"""
secret-manager 单元测试
"""

import unittest
import tempfile
import shutil
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from secret_manager import SecretManager


class TestSecretManager(unittest.TestCase):
    """SecretManager单元测试"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        # 使用固定主密钥测试
        self.manager = SecretManager(
            storage_path=f"{self.temp_dir}/secrets",
            master_key="test-master-key-for-testing-only-12345"
        )
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_store_and_retrieve(self):
        """测试存储和检索"""
        # 存储
        success, msg = self.manager.store("test_key", "test_value")
        self.assertTrue(success)
        
        # 检索
        success, value = self.manager.retrieve("test_key")
        self.assertTrue(success)
        self.assertEqual(value, "test_value")
    
    def test_retrieve_nonexistent(self):
        """测试检索不存在的密钥"""
        success, msg = self.manager.retrieve("nonexistent")
        self.assertFalse(success)
        self.assertIn("不存在", msg)
    
    def test_delete(self):
        """测试删除"""
        # 存储
        self.manager.store("delete_key", "delete_value")
        
        # 删除
        success, msg = self.manager.delete("delete_key")
        self.assertTrue(success)
        
        # 确认删除
        success, _ = self.manager.retrieve("delete_key")
        self.assertFalse(success)
    
    def test_list_keys(self):
        """测试列出密钥"""
        self.manager.store("key1", "value1")
        self.manager.store("key2", "value2")
        
        keys = self.manager.list_keys()
        self.assertEqual(len(keys), 2)
        self.assertIn("key1", keys)
        self.assertIn("key2", keys)
    
    def test_audit_log(self):
        """测试审计日志"""
        self.manager.store("audit_key", "audit_value")
        self.manager.retrieve("audit_key")
        
        logs = self.manager.get_audit_log()
        self.assertGreaterEqual(len(logs), 2)  # 至少存储和检索两条日志


if __name__ == "__main__":
    unittest.main(verbosity=2)
