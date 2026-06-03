#!/usr/bin/env python3
"""
token-budget-enforcer 自动化测试
"""

import unittest
import sys
import os
from pathlib import Path

# 添加Skill目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

class TestTokenBudgetEnforcer(unittest.TestCase):
    """token-budget-enforcer 测试套件"""
    
    def test_01_skill_md_exists(self):
        """测试SKILL.md存在"""
        skill_md = Path(__file__).parent.parent / "SKILL.md"
        self.assertTrue(skill_md.exists(), "SKILL.md应存在")
    
    def test_02_scripts_exist(self):
        """测试核心脚本存在"""
        scripts_dir = Path(__file__).parent.parent / "scripts"
        self.assertTrue(scripts_dir.exists(), "scripts目录应存在")
        
        required_scripts = ["enforcer.py", "allocator.py", "estimator.py", "reporter.py"]
        for script in required_scripts:
            script_path = scripts_dir / script
            self.assertTrue(script_path.exists(), f"{script}应存在")
    
    def test_03_config_exists(self):
        """测试配置目录存在"""
        config_dir = Path(__file__).parent.parent / "config"
        self.assertTrue(config_dir.exists(), "config目录应存在")


if __name__ == "__main__":
    unittest.main(verbosity=2)
