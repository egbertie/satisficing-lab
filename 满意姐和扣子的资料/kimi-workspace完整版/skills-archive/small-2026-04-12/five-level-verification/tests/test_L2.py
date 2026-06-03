#!/usr/bin/env python3
"""
L2 Test Cases - 语法验证测试
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



class TestL2Syntax(unittest.TestCase):
    """L2: 语法验证测试"""
    
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
        os.makedirs(os.path.join(self.skill_path, "scripts"))
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_valid_python(self):
        """测试有效的Python代码"""
        with open(os.path.join(self.skill_path, "scripts", "main.py"), "w") as f:
            f.write("#!/usr/bin/env python3\n")
            f.write("def main():\n")
            f.write("    print('Hello')\n")
        
        verifier = FiveLevelVerifier(self.skill_name)
        verifier.skill_path = self.skill_path
        
        passed, result = verifier.verify_L2()
        self.assertTrue(passed)
        self.assertTrue(result["checks"]["python_syntax"])
    
    def test_invalid_python_syntax(self):
        """测试Python语法错误"""
        with open(os.path.join(self.skill_path, "scripts", "broken.py"), "w") as f:
            f.write("def broken(\n")  # 语法错误
        
        verifier = FiveLevelVerifier(self.skill_name)
        verifier.skill_path = self.skill_path
        
        passed, result = verifier.verify_L2()
        self.assertFalse(passed)
        self.assertFalse(result["checks"]["python_syntax"])
    
    def test_valid_json(self):
        """测试有效的JSON"""
        with open(os.path.join(self.skill_path, "data.json"), "w") as f:
            f.write('{"key": "value", "number": 123}')
        
        verifier = FiveLevelVerifier(self.skill_name)
        verifier.skill_path = self.skill_path
        
        passed, result = verifier.verify_L2()
        self.assertTrue(passed)
        self.assertTrue(result["checks"]["json_valid"])
    
    def test_invalid_json(self):
        """测试无效的JSON"""
        with open(os.path.join(self.skill_path, "data.json"), "w") as f:
            f.write('{"key": value}')  # 无效JSON
        
        verifier = FiveLevelVerifier(self.skill_name)
        verifier.skill_path = self.skill_path
        
        passed, result = verifier.verify_L2()
        self.assertFalse(passed)
        self.assertFalse(result["checks"]["json_valid"])
    
    def test_valid_yaml(self):
        """测试有效的YAML"""
        with open(os.path.join(self.skill_path, "extra.yaml"), "w") as f:
            f.write("key: value\n")
            f.write("list:\n")
            f.write("  - item1\n")
            f.write("  - item2\n")
        
        verifier = FiveLevelVerifier(self.skill_name)
        verifier.skill_path = self.skill_path
        
        passed, result = verifier.verify_L2()
        self.assertTrue(passed)
        self.assertTrue(result["checks"]["yaml_valid"])
    
    def test_invalid_yaml(self):
        """测试无效的YAML"""
        with open(os.path.join(self.skill_path, "broken.yaml"), "w") as f:
            f.write("key: value\n")
            f.write(" bad_indent: wrong")  # 缩进错误
        
        verifier = FiveLevelVerifier(self.skill_name)
        verifier.skill_path = self.skill_path
        
        passed, result = verifier.verify_L2()
        self.assertFalse(passed)
        self.assertFalse(result["checks"]["yaml_valid"])


if __name__ == "__main__":
    unittest.main()
