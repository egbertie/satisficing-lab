#!/usr/bin/env python3
"""
checkpoint-manager 单元测试
覆盖率目标: >80%
"""

import unittest
import tempfile
import shutil
import os
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys

# 添加被测模块路径
sys.path.insert(0, str(Path(__file__).parent))
from checkpoint_manager import CheckpointManager


class TestCheckpointManager(unittest.TestCase):
    """CheckpointManager单元测试"""
    
    def setUp(self):
        """每个测试前创建临时目录"""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = CheckpointManager(base_dir=self.temp_dir)
    
    def tearDown(self):
        """每个测试后清理临时目录"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_init_creates_directory(self):
        """测试初始化创建目录"""
        self.assertTrue(Path(self.temp_dir).exists())
    
    def test_generate_checkpoint_id_format(self):
        """测试检查点ID格式"""
        checkpoint_id = self.manager._generate_checkpoint_id()
        self.assertTrue(checkpoint_id.startswith("checkpoint-"))
        self.assertEqual(len(checkpoint_id), 33)  # checkpoint-YYYYMMDD-HHMMSS-microseconds
    
    def test_calculate_file_hash_existing_file(self):
        """测试文件哈希计算（文件存在）"""
        # 创建测试文件
        test_file = Path(self.temp_dir) / "test.txt"
        test_file.write_text("test content")
        
        hash1 = self.manager._calculate_file_hash(test_file)
        hash2 = self.manager._calculate_file_hash(test_file)
        
        self.assertEqual(len(hash1), 32)  # MD5哈希长度
        self.assertEqual(hash1, hash2)  # 相同内容哈希相同
    
    def test_calculate_file_hash_nonexistent_file(self):
        """测试文件哈希计算（文件不存在）"""
        nonexistent = Path(self.temp_dir) / "nonexistent.txt"
        hash_value = self.manager._calculate_file_hash(nonexistent)
        self.assertEqual(hash_value, "")
    
    def test_create_checkpoint_success(self):
        """测试成功创建检查点"""
        success, result = self.manager.create_checkpoint({"test": True})
        
        self.assertTrue(success)
        self.assertTrue(result.startswith("checkpoint-"))
        
        # 验证检查点目录存在
        checkpoint_dir = Path(self.temp_dir) / result
        self.assertTrue(checkpoint_dir.exists())
        
        # 验证元数据文件存在
        metadata_file = checkpoint_dir / "metadata.json"
        self.assertTrue(metadata_file.exists())
    
    def test_create_checkpoint_metadata_content(self):
        """测试检查点元数据内容"""
        context = {"task": "test", "token_consumed": 1000}
        success, checkpoint_id = self.manager.create_checkpoint(context)
        
        self.assertTrue(success)
        
        # 读取并验证元数据
        metadata_file = Path(self.temp_dir) / checkpoint_id / "metadata.json"
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        
        self.assertEqual(metadata["checkpoint_id"], checkpoint_id)
        self.assertIn("created_at", metadata)
        self.assertIn("files", metadata)
        self.assertEqual(metadata["context"], context)
        self.assertEqual(metadata["token_consumed"], 1000)
    
    def test_create_checkpoint_low_disk_space(self):
        """测试磁盘空间不足时的处理"""
        # Mock磁盘空间检查
        with patch('checkpoint_manager.shutil.disk_usage') as mock_disk:
            mock_disk.return_value = MagicMock(free=50*1024*1024)  # 50MB，低于100MB要求
            
            success, result = self.manager.create_checkpoint()
            
            self.assertFalse(success)
            self.assertIn("磁盘空间不足", result)
    
    def test_list_checkpoints_empty(self):
        """测试空检查点列表"""
        checkpoints = self.manager.list_checkpoints()
        self.assertEqual(len(checkpoints), 0)
    
    def test_list_checkpoints_multiple(self):
        """测试多个检查点列表"""
        import time
        import tempfile
        import shutil
        
        # 使用独立测试目录避免与其他测试冲突
        test_dir = tempfile.mkdtemp(prefix="checkpoint_test_")
        test_manager = CheckpointManager(base_dir=test_dir)
        test_manager.max_checkpoints = 100  # 设置较大的值以保留所有检查点
        
        try:
            # 创建3个检查点
            checkpoint_ids = []
            for i in range(3):
                success, cp_id = test_manager.create_checkpoint({"index": i})
                self.assertTrue(success)
                checkpoint_ids.append(cp_id)
                time.sleep(0.1)  # 小延迟确保时间戳不同
            
            checkpoints = test_manager.list_checkpoints()
            self.assertEqual(len(checkpoints), 3)
            
            # 验证按时间排序（最新的在前）
            for i in range(len(checkpoints) - 1):
                self.assertGreaterEqual(
                    checkpoints[i]["created_at"],
                    checkpoints[i+1]["created_at"]
                )
        finally:
            # 清理测试目录
            shutil.rmtree(test_dir, ignore_errors=True)
    
    def test_list_checkpoints_structure(self):
        """测试检查点列表结构"""
        self.manager.create_checkpoint({"test": True})
        checkpoints = self.manager.list_checkpoints()
        
        self.assertEqual(len(checkpoints), 1)
        cp = checkpoints[0]
        
        self.assertIn("id", cp)
        self.assertIn("created_at", cp)
        self.assertIn("file_count", cp)
        self.assertIn("context", cp)
    
    def test_verify_checkpoint_success(self):
        """测试验证成功的检查点"""
        success, checkpoint_id = self.manager.create_checkpoint()
        self.assertTrue(success)
        
        verify_success, result = self.manager.verify_checkpoint(checkpoint_id)
        self.assertTrue(verify_success)
        self.assertIn("验证通过", result)
    
    def test_verify_checkpoint_nonexistent(self):
        """测试验证不存在的检查点"""
        success, result = self.manager.verify_checkpoint("checkpoint-nonexistent")
        self.assertFalse(success)
        self.assertIn("检查点不存在", result)
    
    def test_verify_checkpoint_missing_metadata(self):
        """测试验证缺少元数据的检查点"""
        # 创建空检查点目录
        checkpoint_dir = Path(self.temp_dir) / "checkpoint-test"
        checkpoint_dir.mkdir()
        
        success, result = self.manager.verify_checkpoint("checkpoint-test")
        self.assertFalse(success)
        self.assertIn("元数据文件缺失", result)
    
    def test_cleanup_old_checkpoints(self):
        """测试清理旧检查点"""
        # 创建7个检查点
        checkpoint_ids = []
        for i in range(7):
            success, cp_id = self.manager.create_checkpoint({"index": i})
            self.assertTrue(success)
            checkpoint_ids.append(cp_id)
        
        # 触发清理（保留5个）
        self.manager._cleanup_old_checkpoints()
        
        # 验证只剩5个
        remaining = list(Path(self.temp_dir).glob("checkpoint-*"))
        self.assertLessEqual(len(remaining), 5)
    
    def test_calculate_file_hash_consistency(self):
        """测试哈希计算一致性"""
        test_file = Path(self.temp_dir) / "consistency_test.txt"
        content = "consistent content"
        test_file.write_text(content)
        
        # 多次计算应该相同
        hashes = [self.manager._calculate_file_hash(test_file) for _ in range(5)]
        self.assertEqual(len(set(hashes)), 1)  # 所有哈希相同
        
        # 修改内容后应该不同
        test_file.write_text(content + " modified")
        new_hash = self.manager._calculate_file_hash(test_file)
        self.assertNotEqual(hashes[0], new_hash)


class TestCheckpointManagerEdgeCases(unittest.TestCase):
    """边界情况和异常测试"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.manager = CheckpointManager(base_dir=self.temp_dir)
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_create_checkpoint_with_empty_context(self):
        """测试空上下文"""
        success, checkpoint_id = self.manager.create_checkpoint({})
        self.assertTrue(success)
        
        # 验证元数据
        metadata_file = Path(self.temp_dir) / checkpoint_id / "metadata.json"
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        
        self.assertEqual(metadata["context"], {})
        self.assertEqual(metadata["token_consumed"], 0)
    
    def test_create_checkpoint_with_none_context(self):
        """测试None上下文"""
        success, checkpoint_id = self.manager.create_checkpoint(None)
        self.assertTrue(success)
        
        metadata_file = Path(self.temp_dir) / checkpoint_id / "metadata.json"
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        
        self.assertEqual(metadata["context"], {})
    
    def test_special_characters_in_context(self):
        """测试特殊字符上下文"""
        context = {
            "text": "中文测试 🎉 \"quoted\" \n newline",
            "number": 123.456,
            "bool": True,
            "null": None
        }
        success, checkpoint_id = self.manager.create_checkpoint(context)
        self.assertTrue(success)
        
        metadata_file = Path(self.temp_dir) / checkpoint_id / "metadata.json"
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        self.assertEqual(metadata["context"]["text"], context["text"])


if __name__ == "__main__":
    # 运行测试并生成覆盖率报告
    unittest.main(verbosity=2)
