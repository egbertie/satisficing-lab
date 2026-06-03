#!/usr/bin/env python3
"""
task-manager 自动化测试
"""

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

class TestTaskManager(unittest.TestCase):
    """task-manager 测试套件"""
    
    def test_01_skill_md_exists(self):
        """测试SKILL.md存在"""
        skill_md = Path(__file__).parent.parent / "SKILL.md"
        self.assertTrue(skill_md.exists(), "SKILL.md应存在")
    
    def test_02_scripts_exist(self):
        """测试核心脚本存在"""
        scripts_dir = Path(__file__).parent.parent / "scripts"
        self.assertTrue(scripts_dir.exists(), "scripts目录应存在")
        
        required = ["task_manager.py", "track-tasks.py"]
        for script in required:
            self.assertTrue((scripts_dir / script).exists(), f"{script}应存在")


if __name__ == "__main__":
    unittest.main(verbosity=2)
