#!/usr/bin/env python3
"""
L1 Test Cases - 存在验证测试
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



class TestL1Existence(unittest.TestCase):
    """L1: 存在验证测试"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.skill_name = "test_skill"
        self.skill_path = os.path.join(self.temp_dir, self.skill_name)
        os.makedirs(self.skill_path)
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_all_files_present(self):
        """测试所有必需文件存在"""
        # 创建必需文件
        with open(os.path.join(self.skill_path, "SKILL.md"), "w") as f:
            f.write("# Test Skill\n")
        with open(os.path.join(self.skill_path, "config.yaml"), "w") as f:
            f.write("skill:\n  name: test\n")
        os.makedirs(os.path.join(self.skill_path, "scripts"))
        
        verifier = FiveLevelVerifier(self.skill_name)
        verifier.skill_path = self.skill_path
        
        passed, result = verifier.verify_L1()
        self.assertTrue(passed)
        self.assertEqual(result["score"], 100)
    
    def test_missing_skill_md(self):
        """测试缺失SKILL.md"""
        with open(os.path.join(self.skill_path, "config.yaml"), "w") as f:
            f.write("skill:\n  name: test\n")
        os.makedirs(os.path.join(self.skill_path, "scripts"))
        
        verifier = FiveLevelVerifier(self.skill_name)
        verifier.skill_path = self.skill_path
        
        passed, result = verifier.verify_L1()
        self.assertFalse(passed)
        self.assertIn("SKILL.md", str(result["checks"]))
    
    def test_empty_skill_md(self):
        """测试空的SKILL.md"""
        with open(os.path.join(self.skill_path, "SKILL.md"), "w") as f:
            f.write("")  # 空文件
        with open(os.path.join(self.skill_path, "config.yaml"), "w") as f:
            f.write("skill:\n  name: test\n")
        os.makedirs(os.path.join(self.skill_path, "scripts"))
        
        verifier = FiveLevelVerifier(self.skill_name)
        verifier.skill_path = self.skill_path
        
        passed, result = verifier.verify_L1()
        self.assertFalse(passed)
    
    def test_missing_config(self):
        """测试缺失config.yaml"""
        with open(os.path.join(self.skill_path, "SKILL.md"), "w") as f:
            f.write("# Test Skill\n")
        os.makedirs(os.path.join(self.skill_path, "scripts"))
        
        verifier = FiveLevelVerifier(self.skill_name)
        verifier.skill_path = self.skill_path
        
        passed, result = verifier.verify_L1()
        self.assertFalse(passed)


if __name__ == "__main__":
    unittest.main()
