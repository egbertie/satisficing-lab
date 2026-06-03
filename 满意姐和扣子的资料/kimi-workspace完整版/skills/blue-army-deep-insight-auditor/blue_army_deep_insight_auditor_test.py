#!/usr/bin/env python3
"""blue_army_deep_insight_auditor_test.py - S5/S7验证"""
import unittest
import sys
from pathlib import Path

sys.path.insert(0, '/root/.openclaw/workspace/skills/blue-army-deep-insight-auditor')

class TestDeepInsightAuditorS5S7(unittest.TestCase):
    def test_code_file_exists(self):
        """S5-1: 代码文件存在"""
        code_file = Path('/root/.openclaw/workspace/skills/blue-army-deep-insight-auditor/deep_insight_auditor.py')
        self.assertTrue(code_file.exists())
    
    def test_skill_md_exists(self):
        """S5-2: SKILL.md存在"""
        skill_md = Path('/root/.openclaw/workspace/skills/blue-army-deep-insight-auditor/SKILL.md')
        self.assertTrue(skill_md.exists())
    
    def test_code_not_empty(self):
        """S5-3: 代码非空"""
        code_file = Path('/root/.openclaw/workspace/skills/blue-army-deep-insight-auditor/deep_insight_auditor.py')
        content = code_file.read_text()
        self.assertGreater(len(content), 100)
    
    def test_has_class_or_function(self):
        """S7-1: 有类或函数定义"""
        code_file = Path('/root/.openclaw/workspace/skills/blue-army-deep-insight-auditor/deep_insight_auditor.py')
        content = code_file.read_text()
        self.assertTrue('class' in content or 'def' in content)

if __name__ == '__main__':
    unittest.main(verbosity=2)
