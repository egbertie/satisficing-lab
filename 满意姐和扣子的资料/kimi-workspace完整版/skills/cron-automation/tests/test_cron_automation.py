#!/usr/bin/env python3
"""
cron-automation 自动化测试
"""

import unittest
import sys
import os
from pathlib import Path

# 添加Skill目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

class TestCronAutomation(unittest.TestCase):
    """cron-automation 测试套件"""
    
    def test_01_skill_md_exists(self):
        """测试SKILL.md存在"""
        skill_md = Path(__file__).parent.parent / "SKILL.md"
        self.assertTrue(skill_md.exists(), "SKILL.md应存在")
    
    def test_02_scripts_exist(self):
        """测试核心脚本存在"""
        scripts_dir = Path(__file__).parent.parent / "scripts"
        self.assertTrue(scripts_dir.exists(), "scripts目录应存在")
        
        # 检查至少有一些Python脚本
        py_files = list(scripts_dir.glob("*.py"))
        self.assertTrue(len(py_files) > 0, "应存在Python脚本")
    
    def test_03_cron_config_exists(self):
        """测试cron配置存在"""
        config_dir = Path(__file__).parent.parent / "config"
        self.assertTrue(config_dir.exists(), "config目录应存在")


if __name__ == "__main__":
    unittest.main(verbosity=2)
