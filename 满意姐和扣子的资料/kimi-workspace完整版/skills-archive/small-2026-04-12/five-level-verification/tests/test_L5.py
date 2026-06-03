#!/usr/bin/env python3
"""
L5 Test Cases - 端到端验证测试
"""

import os
import sys
import tempfile
import shutil
import unittest
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from verify import FiveLevelVerifier


def get_skill_main_file(skill_path: Path):
    """获取Skill的主代码文件"""
    skill_name = skill_path.name.replace('-', '_')
    candidates = [
        skill_path / f"{skill_name}.py",
        skill_path / "__init__.py",
        skill_path / "main.py",
        skill_path / "runner.py",
        skill_path / "skill.py",
    ]
    for c in candidates:
        if c.exists():
            return c
    py_files = list(skill_path.glob("*.py"))
    if py_files:
        return py_files[0]
    return None



class TestL5EndToEnd(unittest.TestCase):
    """L5: 端到端验证测试"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.skill_name = "test_skill"
        self.skill_path = os.path.join(self.temp_dir, self.skill_name)
        os.makedirs(self.skill_path)
        
        # 创建基本文件
        with open(os.path.join(self.skill_path, "SKILL.md"), "w") as f:
            f.write("# Test Skill\n")
        with open(os.path.join(self.skill_path, "config.yaml"), "w") as f:
            f.write("skill:\n  name: test\n")
        with open(os.path.join(self.skill_path, "README.md"), "w") as f:
            f.write("# README\n")
        os.makedirs(os.path.join(self.skill_path, "scripts"))
        os.makedirs(os.path.join(self.skill_path, ".github", "workflows"))
        with open(os.path.join(self.skill_path, ".github", "workflows", "ci.yml"), "w") as f:
            f.write("name: CI\n")
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_l5_requires_manual(self):
        """测试L5需要人工验证"""
        verifier = FiveLevelVerifier(self.skill_name)
        verifier.skill_path = self.skill_path
        
        passed, result = verifier.verify_L5()
        
        # L5 应该返回False（需要人工验证）
        self.assertFalse(passed)
        self.assertTrue(result.get("requires_manual"))
        self.assertIn("warnings", result)


if __name__ == "__main__":
    unittest.main()
