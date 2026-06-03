#!/usr/bin/env python3
"""
skill-usage-tracker 功能测试
测试真实实现
"""

import unittest
import tempfile
import time
import json
from pathlib import Path
from datetime import datetime
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from skill_usage_tracker import (
    SkillUsageTracker, UsageEvent, WeeklyReport,
    ActionType
)


class TestSkillUsageTrackerReal(unittest.TestCase):
    """真实功能测试"""
    
    def setUp(self):
        """设置"""
        self.temp_dir = tempfile.mkdtemp()
        self.tracker = SkillUsageTracker(self.temp_dir)
    
    def tearDown(self):
        """清理"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_01_record_skill_usage(self):
        """测试记录Skill使用"""
        self.tracker.record_skill_usage(
            "ai-meeting-notes",
            "python3 scripts/main.py input.md",
            target_file="meeting.md",
            success=True
        )
        
        self.assertEqual(len(self.tracker.events), 1)
        event = self.tracker.events[0]
        self.assertEqual(event.skill_name, "ai-meeting-notes")
        self.assertEqual(event.action_type, ActionType.SKILL_USED.value)
    
    def test_02_record_manual_action(self):
        """测试记录手工操作"""
        reminder = self.tracker.record_manual_action("vim test.py")
        
        self.assertEqual(len(self.tracker.events), 1)
        event = self.tracker.events[0]
        self.assertEqual(event.action_type, ActionType.MANUAL_WORKAROUND.value)
        # 应该返回绕过提醒
        self.assertIsNotNone(reminder)
    
    def test_03_detect_bypass(self):
        """测试绕过检测"""
        # 应该检测为绕过
        self.assertIsNotNone(self.tracker._detect_bypass("vim test.py"))
        self.assertIsNotNone(self.tracker._detect_bypass("nano main.py"))
        self.assertIsNotNone(self.tracker._detect_bypass("echo 'hello' > file.py"))
        
        # 不应该检测为绕过
        self.assertIsNone(self.tracker._detect_bypass("ls -la"))
        self.assertIsNone(self.tracker._detect_bypass("cd /tmp"))
    
    def test_04_get_usage_stats(self):
        """测试获取使用统计"""
        # 记录一些事件
        self.tracker.record_skill_usage("skill1", "cmd1")
        self.tracker.record_skill_usage("skill2", "cmd2")
        self.tracker.record_manual_action("vim test.py")
        
        stats = self.tracker.get_usage_stats(days=1)
        
        self.assertEqual(stats['total_events'], 3)
        self.assertEqual(stats['skill_events'], 2)
        self.assertEqual(stats['manual_events'], 1)
        self.assertAlmostEqual(stats['skill_usage_rate'], 2/3, places=2)
    
    def test_05_top_skills(self):
        """测试常用Skill统计"""
        self.tracker.record_skill_usage("skill1", "cmd1")
        self.tracker.record_skill_usage("skill1", "cmd2")
        self.tracker.record_skill_usage("skill2", "cmd3")
        
        stats = self.tracker.get_usage_stats()
        top_skills = stats['top_skills']
        
        self.assertEqual(len(top_skills), 2)
        self.assertEqual(top_skills[0][0], "skill1")  # 使用次数最多
        self.assertEqual(top_skills[0][1], 2)
    
    def test_06_detect_continuous_bypass(self):
        """测试连续绕过检测"""
        # 模拟连续手工操作
        self.tracker.record_manual_action("vim a.py")
        self.tracker.record_manual_action("vim b.py")
        self.tracker.record_manual_action("vim c.py")
        
        stats = self.tracker.get_usage_stats()
        
        self.assertGreater(len(stats['bypass_alerts']), 0)
    
    def test_07_set_target_rate(self):
        """测试设置目标使用率"""
        self.tracker.set_target_rate(0.9)
        
        self.assertEqual(self.tracker.config['target_usage_rate'], 0.9)
    
    def test_08_generate_weekly_report(self):
        """测试生成周报"""
        # 记录一些数据
        self.tracker.record_skill_usage("skill1", "cmd")
        self.tracker.record_manual_action("vim test.py")
        
        report = self.tracker.generate_weekly_report()
        
        self.assertIsInstance(report, WeeklyReport)
        self.assertEqual(report.total_events, 2)
        self.assertEqual(report.skill_events, 1)
    
    def test_09_export_report_markdown(self):
        """测试Markdown导出"""
        self.tracker.record_skill_usage("skill1", "cmd")
        
        report = self.tracker.generate_weekly_report()
        md = self.tracker.export_report(report, "markdown")
        
        self.assertIn("# Skill使用周报", md)
        self.assertIn("使用统计", md)
    
    def test_10_export_report_json(self):
        """测试JSON导出"""
        self.tracker.record_skill_usage("skill1", "cmd")
        
        report = self.tracker.generate_weekly_report()
        json_str = self.tracker.export_report(report, "json")
        data = json.loads(json_str)
        
        self.assertIn('week_start', data)
        self.assertIn('skill_usage_rate', data)
    
    def test_11_persistence(self):
        """测试数据持久化"""
        # 记录数据
        self.tracker.record_skill_usage("skill1", "cmd")
        
        # 重新加载
        tracker2 = SkillUsageTracker(self.temp_dir)
        
        self.assertEqual(len(tracker2.events), 1)
        self.assertEqual(tracker2.events[0].skill_name, "skill1")
    
    def test_12_suggest_skills(self):
        """测试Skill建议"""
        suggestions = self.tracker._suggest_skills_for_command("vim test.py")
        
        self.assertGreater(len(suggestions), 0)
        # 应该包含代码质量相关Skill
        self.assertTrue(any("quality" in s for s in suggestions))


class TestSkillUsageTrackerIntegration(unittest.TestCase):
    """集成测试"""
    
    def test_cli_record_and_report(self):
        """测试CLI记录和报告"""
        import subprocess
        import shutil
        
        temp_dir = tempfile.mkdtemp()
        try:
            # 记录Skill使用
            result = subprocess.run(
                ["python3", "scripts/main.py", "--record-skill", "test-skill", "test-cmd", "--data-dir", temp_dir],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent.parent
            )
            
            self.assertEqual(result.returncode, 0)
            self.assertIn("已记录", result.stdout)
            
            # 生成报告
            result2 = subprocess.run(
                ["python3", "scripts/main.py", "--report", "--format", "json", "--data-dir", temp_dir],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent.parent
            )
            
            self.assertEqual(result2.returncode, 0)
            data = json.loads(result2.stdout)
            self.assertIn('skill_usage_rate', data)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
