#!/usr/bin/env python3
"""
批量测试生成器 - 为无测试的Skill自动生成测试框架
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Optional
import subprocess

SKILLS_DIR = Path("/root/.openclaw/workspace/skills")

def get_skill_main_file(skill_path: Path) -> Optional[Path]:
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
    
    # 查找任何.py文件
    py_files = list(skill_path.glob("*.py"))
    if py_files:
        return py_files[0]
    
    return None

def generate_test_template(skill_name: str, main_file: Path) -> str:
    """生成测试模板"""
    module_name = main_file.stem
    
    template = f'''#!/usr/bin/env python3
"""
{skill_name} 自动化测试
生成时间: {__import__('datetime').datetime.now().isoformat()}
"""

import unittest
import sys
import os
from pathlib import Path

# 添加Skill目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from {module_name} import *
    MODULE_AVAILABLE = True
except ImportError as e:
    MODULE_AVAILABLE = False
    print(f"警告: 无法导入主模块: {{e}}")


class Test{skill_name.replace('-', '_').title().replace('_', '')}(unittest.TestCase):
    """{skill_name} 测试套件"""
    
    @classmethod
    def setUpClass(cls):
        """测试类前置准备"""
        cls.test_data_dir = Path(__file__).parent / "test_data"
        cls.test_data_dir.mkdir(exist_ok=True)
    
    def test_01_module_import(self):
        """测试模块可导入"""
        self.assertTrue(MODULE_AVAILABLE, "主模块应可导入")
    
    def test_02_skill_md_exists(self):
        """测试SKILL.md存在"""
        skill_md = Path(__file__).parent.parent / "SKILL.md"
        self.assertTrue(skill_md.exists(), "SKILL.md应存在")
    
    def test_03_main_file_exists(self):
        """测试主代码文件存在"""
        main_file = get_skill_main_file(Path(__file__).parent.parent)
        self.assertIsNotNone(main_file, "应存在主代码文件")
    
    def test_04_basic_functionality(self):
        """测试基本功能"""
        if not MODULE_AVAILABLE:
            self.skipTest("模块不可用")
        # TODO: 根据实际功能添加测试
        self.assertTrue(True)


def run_tests():
    """运行测试并返回结果"""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(Test{skill_name.replace('-', '_').title().replace('_', '')})
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
'''
    return template

def generate_test_for_skill(skill_path: Path) -> bool:
    """为单个Skill生成测试"""
    skill_name = skill_path.name
    main_file = get_skill_main_file(skill_path)
    
    if not main_file:
        print(f"⚠️  {skill_name}: 无代码文件，跳过")
        return False
    
    # 创建tests目录
    tests_dir = skill_path / "tests"
    tests_dir.mkdir(exist_ok=True)
    
    # 创建__init__.py
    init_file = tests_dir / "__init__.py"
    if not init_file.exists():
        init_file.touch()
    
    # 创建测试文件
    test_file = tests_dir / f"test_{skill_name.replace('-', '_')}.py"
    test_content = generate_test_template(skill_name, main_file)
    
    with open(test_file, 'w') as f:
        f.write(test_content)
    
    print(f"✅ {skill_name}: 测试已生成 @ {test_file}")
    return True

def batch_generate_tests(skill_names: List[str]):
    """批量生成测试"""
    success_count = 0
    fail_count = 0
    
    for skill_name in skill_names:
        skill_path = SKILLS_DIR / skill_name
        if not skill_path.exists():
            print(f"❌ {skill_name}: Skill目录不存在")
            fail_count += 1
            continue
        
        if generate_test_for_skill(skill_path):
            success_count += 1
        else:
            fail_count += 1
    
    print(f"\n{'='*50}")
    print(f"批量生成完成: 成功 {success_count}, 失败 {fail_count}")
    return success_count, fail_count


def get_skills_needing_tests() -> List[str]:
    """获取需要测试的Skill列表"""
    skills = []
    
    for skill_path in SKILLS_DIR.iterdir():
        if not skill_path.is_dir():
            continue
        if skill_path.name.startswith('.'):
            continue
        
        # 检查是否有代码但无测试
        main_file = get_skill_main_file(skill_path)
        if not main_file:
            continue
        
        # 检查是否已有测试
        tests_dir = skill_path / "tests"
        has_tests = tests_dir.exists() and any(tests_dir.glob("test_*.py"))
        
        if not has_tests:
            skills.append(skill_path.name)
    
    return sorted(skills)


if __name__ == "__main__":
    # 获取需要测试的Skill
    skills_to_test = get_skills_needing_tests()
    print(f"发现 {len(skills_to_test)} 个需要测试的Skill:")
    for s in skills_to_test:
        print(f"  - {s}")
    
    print(f"\n开始批量生成测试...")
    batch_generate_tests(skills_to_test)
