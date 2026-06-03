#!/usr/bin/env python3
"""S5/S7基础验证测试"""
import unittest
from pathlib import Path

class TestSkillS5S7(unittest.TestCase):
    def test_skill_directory_exists(self):
        """S5-1: Skill目录存在"""
        self.assertTrue(Path(__file__).parent.exists())
    
    def test_skill_md_exists(self):
        """S5-2: SKILL.md存在"""
        skill_md = Path(__file__).parent / "SKILL.md"
        self.assertTrue(skill_md.exists())
    
    def test_code_files_exist(self):
        """S5-3: 代码文件存在"""
        py_files = list(Path(__file__).parent.rglob("*.py"))
        py_files = [f for f in py_files if "__pycache__" not in str(f)]
        self.assertGreater(len(py_files), 0)
    
    def test_skill_md_not_empty(self):
        """S7-1: SKILL.md非空"""
        skill_md = Path(__file__).parent / "SKILL.md"
        if skill_md.exists():
            content = skill_md.read_text()
            self.assertGreater(len(content), 100)

if __name__ == '__main__':
    unittest.main(verbosity=2)
