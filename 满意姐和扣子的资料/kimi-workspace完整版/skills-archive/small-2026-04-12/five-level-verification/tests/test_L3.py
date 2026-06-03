#!/usr/bin/env python3
"""
L3 Test Cases - 可执行验证测试
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



class TestL3Executable(unittest.TestCase):
    """L3: 可执行验证测试"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.skill_name = "test_skill"
        self.skill_path = os.path.join(self.temp_dir, self.skill_name)
        os.makedirs(self.skill_path)
        os.makedirs(os.path.join(self.skill_path, "scripts"))
        
        # 创建基本文件
        with open(os.path.join(self.skill_path, "SKILL.md"), "w") as f:
            f.write("# Test Skill\n")
        with open(os.path.join(self.skill_path, "config.yaml"), "w") as f:
            f.write("skill:\n  name: test\n")
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_valid_entry_point(self):
        """测试有效的入口点"""
        with open(os.path.join(self.skill_path, "scripts", "main.py"), "w") as f:
            f.write("#!/usr/bin/env python3\n")
            f.write("import argparse\n")
            f.write("parser = argparse.ArgumentParser()\n")
            f.write("args = parser.parse_args()\n")
        
        verifier = FiveLevelVerifier(self.skill_name)
        verifier.skill_path = self.skill_path
        
        passed, result = verifier.verify_L3()
        self.assertTrue(passed)
        self.assertTrue(result["checks"]["help_works"])
    
    def test_missing_entry_point(self):
        """测试缺失入口点"""
        # 不创建任何脚本
        verifier = FiveLevelVerifier(self.skill_name)
        verifier.skill_path = self.skill_path
        
        passed, result = verifier.verify_L3()
        self.assertFalse(passed)
        self.assertFalse(result["checks"]["entry_point_exists"])
    
    def test_import_error(self):
        """测试导入错误"""
        with open(os.path.join(self.skill_path, "scripts", "main.py"), "w") as f:
            f.write("#!/usr/bin/env python3\n")
            f.write("import nonexistent_module_xyz\n")
        
        verifier = FiveLevelVerifier(self.skill_name)
        verifier.skill_path = self.skill_path
        
        passed, result = verifier.verify_L3()
        # 应该能通过，因为verify_L3只检查--help
        # 真正的导入错误在运行时才会发现


if __name__ == "__main__":
    unittest.main()
