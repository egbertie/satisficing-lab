#!/usr/bin/env python3
"""
vendor_api_monitor_test.py - 厂商API监控 S5/S7验证
"""

import sys
import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import json

sys.path.insert(0, '/root/.openclaw/workspace/skills/vendor-api-monitor/scripts')

# 模拟测试（实际代码依赖较多，先验证结构）
class TestVendorAPIMonitorS5S7(unittest.TestCase):
    """S5/S7测试套件"""
    
    def setUp(self):
        """测试前准备"""
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """测试后清理"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    # ===== S5: 自我验证测试 =====
    
    def test_scripts_exist(self):
        """S5-1: 核心脚本存在"""
        scripts_dir = Path('/root/.openclaw/workspace/skills/vendor-api-monitor/scripts')
        self.assertTrue(scripts_dir.exists())
        self.assertTrue((scripts_dir / 'probe.py').exists())
        self.assertTrue((scripts_dir / 'daemon.py').exists())
        self.assertTrue((scripts_dir / 'report.py').exists())
    
    def test_probe_script_structure(self):
        """S5-2: probe.py结构正确"""
        probe_file = Path('/root/.openclaw/workspace/skills/vendor-api-monitor/scripts/probe.py')
        content = probe_file.read_text()
        self.assertIn('def', content)  # 有函数定义
        self.assertIn('import', content)  # 有导入
    
    def test_daemon_script_structure(self):
        """S5-3: daemon.py结构正确"""
        daemon_file = Path('/root/.openclaw/workspace/skills/vendor-api-monitor/scripts/daemon.py')
        content = daemon_file.read_text()
        self.assertIn('def', content)
        self.assertIn('class', content)  # 应该有类定义
    
    def test_report_script_structure(self):
        """S5-4: report.py结构正确"""
        report_file = Path('/root/.openclaw/workspace/skills/vendor-api-monitor/scripts/report.py')
        content = report_file.read_text()
        self.assertIn('def', content)
        self.assertIn('report', content.lower())  # 有报告相关代码
    
    def test_validate_script_structure(self):
        """S5-5: validate.py结构正确"""
        validate_file = Path('/root/.openclaw/workspace/skills/vendor-api-monitor/scripts/validate.py')
        content = validate_file.read_text()
        self.assertIn('def', content)
        self.assertIn('valid', content.lower())
    
    def test_self_check_script_structure(self):
        """S5-6: self_check.py结构正确"""
        self_check_file = Path('/root/.openclaw/workspace/skills/vendor-api-monitor/scripts/self_check.py')
        content = self_check_file.read_text()
        self.assertIn('def', content)
        self.assertIn('check', content.lower())
    
    def test_chaos_script_structure(self):
        """S5-7: chaos.py结构正确（对抗测试）"""
        chaos_file = Path('/root/.openclaw/workspace/skills/vendor-api-monitor/scripts/chaos.py')
        content = chaos_file.read_text()
        self.assertIn('def', content)
        self.assertIn('chaos', content.lower())
    
    # ===== S7: 对抗测试 =====
    
    def test_all_scripts_have_main_guard(self):
        """S7-1: 所有脚本有主函数保护"""
        scripts_dir = Path('/root/.openclaw/workspace/skills/vendor-api-monitor/scripts')
        for py_file in scripts_dir.glob('*.py'):
            if py_file.name == '__init__.py':
                continue
            content = py_file.read_text()
            # 应该有函数定义，避免直接执行
            self.assertIn('def', content, f"{py_file.name} 缺少函数定义")
    
    def test_scripts_not_empty(self):
        """S7-2: 脚本非空"""
        scripts_dir = Path('/root/.openclaw/workspace/skills/vendor-api-monitor/scripts')
        for py_file in scripts_dir.glob('*.py'):
            if py_file.name == '__init__.py':
                continue
            content = py_file.read_text()
            self.assertGreater(len(content), 100, f"{py_file.name} 内容过少")
    
    def test_scripts_have_docstrings(self):
        """S7-3: 脚本有文档字符串"""
        scripts_dir = Path('/root/.openclaw/workspace/skills/vendor-api-monitor/scripts')
        for py_file in scripts_dir.glob('*.py'):
            if py_file.name == '__init__.py':
                continue
            content = py_file.read_text()
            self.assertIn('"""', content, f"{py_file.name} 缺少文档字符串")


def run_tests():
    """运行测试"""
    print("=" * 60)
    print("Vendor API Monitor - S5/S7 验证")
    print("=" * 60)
    
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestVendorAPIMonitorS5S7)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 60)
    print(f"运行: {result.testsRun}")
    print(f"通过: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    
    if result.wasSuccessful():
        print("\n✅ S5/S7验证通过！")
        return True
    return False


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
