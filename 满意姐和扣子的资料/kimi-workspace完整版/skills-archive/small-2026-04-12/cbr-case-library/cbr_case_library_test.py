#!/usr/bin/env python3
"""cbr_case_library_test.py - S5/S7验证"""
import unittest
from pathlib import Path

class TestCBRCaseLibraryS5S7(unittest.TestCase):
    def test_code_files_exist(self):
        """S5-1: 代码文件存在"""
        self.assertTrue(Path('/root/.openclaw/workspace/skills/cbr-case-library/dashboard_collector.py').exists())
        self.assertTrue(Path('/root/.openclaw/workspace/skills/cbr-case-library/arxiv_scraper.py').exists())
    
    def test_skill_md_exists(self):
        """S5-2: SKILL.md存在"""
        self.assertTrue(Path('/root/.openclaw/workspace/skills/cbr-case-library/SKILL.md').exists())
    
    def test_code_not_empty(self):
        """S5-3: 代码非空"""
        content = Path('/root/.openclaw/workspace/skills/cbr-case-library/arxiv_scraper.py').read_text()
        self.assertGreater(len(content), 100)
    
    def test_has_functions(self):
        """S7-1: 有函数定义"""
        content = Path('/root/.openclaw/workspace/skills/cbr-case-library/arxiv_scraper.py').read_text()
        self.assertIn('def', content)

if __name__ == '__main__':
    unittest.main(verbosity=2)
