#!/usr/bin/env python3
"""category6_full_task_processor_test.py - S5/S7验证"""
import unittest
from pathlib import Path

class TestCategory6ProcessorS5S7(unittest.TestCase):
    def test_scripts_directory_exists(self):
        """S5-1: 脚本目录存在"""
        scripts_dir = Path('/root/.openclaw/workspace/skills/category6-full-task-processor/scripts')
        self.assertTrue(scripts_dir.exists())
    
    def test_run_script_exists(self):
        """S5-2: 主脚本存在"""
        run_script = Path('/root/.openclaw/workspace/skills/category6-full-task-processor/scripts/run.py')
        self.assertTrue(run_script.exists())
    
    def test_skill_md_exists(self):
        """S5-3: SKILL.md存在"""
        skill_md = Path('/root/.openclaw/workspace/skills/category6-full-task-processor/SKILL.md')
        self.assertTrue(skill_md.exists())
    
    def test_run_script_not_empty(self):
        """S7-1: 脚本非空"""
        run_script = Path('/root/.openclaw/workspace/skills/category6-full-task-processor/scripts/run.py')
        content = run_script.read_text()
        self.assertGreater(len(content), 50)

if __name__ == '__main__':
    unittest.main(verbosity=2)
