#!/usr/bin/env python3
"""
zero-idle-enforcer 功能测试
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

from zero_idle_enforcer import (
    ZeroIdleEnforcer, Task, IdlePeriod,
    TaskStatus, IdleSeverity
)


class TestZeroIdleEnforcerReal(unittest.TestCase):
    """真实功能测试"""

    def setUp(self):
        """设置"""
        self.temp_dir = tempfile.mkdtemp()
        self.enforcer = ZeroIdleEnforcer(self.temp_dir)

    def tearDown(self):
        """清理"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_01_create_task(self):
        """测试创建任务"""
        task = self.enforcer.create_task("测试任务", priority=2, estimated_minutes=60)

        self.assertIsInstance(task, Task)
        self.assertEqual(task.name, "测试任务")
        self.assertEqual(task.priority, 2)
        self.assertEqual(task.estimated_minutes, 60)
        self.assertEqual(task.status, TaskStatus.IDLE.value)

    def test_02_assign_task(self):
        """测试分配任务"""
        task = self.enforcer.create_task("测试任务")
        assigned = self.enforcer.assign_task(task.task_id)

        self.assertIsNotNone(assigned)
        self.assertEqual(assigned.status, TaskStatus.ASSIGNED.value)
        self.assertIsNotNone(assigned.assigned_at)

    def test_03_start_task(self):
        """测试开始任务"""
        task = self.enforcer.create_task("测试任务")
        self.enforcer.assign_task(task.task_id)
        started = self.enforcer.start_task(task.task_id)

        self.assertIsNotNone(started)
        self.assertEqual(started.status, TaskStatus.IN_PROGRESS.value)
        self.assertIsNotNone(started.started_at)

    def test_04_complete_task(self):
        """测试完成任务"""
        task = self.enforcer.create_task("测试任务")
        self.enforcer.start_task(task.task_id)
        completed = self.enforcer.complete_task(task.task_id)

        self.assertIsNotNone(completed)
        self.assertEqual(completed.status, TaskStatus.COMPLETED.value)
        self.assertIsNotNone(completed.completed_at)

    def test_05_suggest_task(self):
        """测试建议任务"""
        # 创建不同优先级的任务
        task1 = self.enforcer.create_task("高优先级", priority=1)
        task2 = self.enforcer.create_task("低优先级", priority=5)

        suggested = self.enforcer._suggest_task()

        # 应该建议高优先级任务
        self.assertIsNotNone(suggested)
        self.assertEqual(suggested.task_id, task1.task_id)

    def test_06_check_idle(self):
        """测试检查空置"""
        self.enforcer.mark_idle()
        time.sleep(0.5)  # 等待0.5秒

        idle_period = self.enforcer.check_idle()

        self.assertIsNotNone(idle_period)
        self.assertIsInstance(idle_period, IdlePeriod)
        self.assertGreaterEqual(idle_period.duration_seconds, 0)

    def test_07_idle_severity(self):
        """测试空置严重程度"""
        self.enforcer.mark_idle()

        # 短时间空置
        time.sleep(0.1)
        idle = self.enforcer.check_idle()
        self.assertEqual(idle.severity, IdleSeverity.LOW.value)

    def test_08_get_tasks_by_status(self):
        """测试按状态获取任务"""
        task1 = self.enforcer.create_task("任务1")
        task2 = self.enforcer.create_task("任务2")
        self.enforcer.start_task(task1.task_id)

        idle_tasks = self.enforcer.get_tasks_by_status(TaskStatus.IDLE.value)
        in_progress_tasks = self.enforcer.get_tasks_by_status(TaskStatus.IN_PROGRESS.value)

        self.assertEqual(len(idle_tasks), 1)
        self.assertEqual(len(in_progress_tasks), 1)

    def test_09_calculate_utilization(self):
        """测试计算利用率"""
        today = datetime.now().strftime('%Y-%m-%d')

        # 创建、分配、开始并完成任务
        task = self.enforcer.create_task("测试", estimated_minutes=60)
        self.enforcer.assign_task(task.task_id)  # 分配任务以设置 assigned_at
        self.enforcer.start_task(task.task_id)
        self.enforcer.complete_task(task.task_id)

        stats = self.enforcer.calculate_utilization(today)

        self.assertEqual(stats.date, today)
        self.assertEqual(stats.tasks_completed, 1)
        self.assertGreater(stats.active_minutes, 0)
        self.assertGreaterEqual(stats.utilization_rate, 0)

    def test_10_export_report_json(self):
        """测试JSON导出"""
        stats = self.enforcer.calculate_utilization()
        json_str = self.enforcer.export_report(stats, "json")
        data = json.loads(json_str)

        self.assertIn('date', data)
        self.assertIn('utilization_rate', data)
        self.assertIn('tasks_completed', data)

    def test_11_export_report_markdown(self):
        """测试Markdown导出"""
        stats = self.enforcer.calculate_utilization()
        md = self.enforcer.export_report(stats, "markdown")

        self.assertIn("# 零空置执行报告", md)
        self.assertIn("时间利用率", md)

    def test_12_load_and_save_tasks(self):
        """测试任务加载和保存"""
        # 创建任务
        task = self.enforcer.create_task("持久化测试")
        task_id = task.task_id

        # 重新加载
        enforcer2 = ZeroIdleEnforcer(self.temp_dir)
        loaded_task = next((t for t in enforcer2.tasks if t.task_id == task_id), None)

        self.assertIsNotNone(loaded_task)
        self.assertEqual(loaded_task.name, "持久化测试")


class TestZeroIdleEnforcerIntegration(unittest.TestCase):
    """集成测试"""

    def test_cli_create_and_list(self):
        """测试CLI创建和列出"""
        import subprocess
        import shutil

        temp_dir = tempfile.mkdtemp()
        try:
            # 创建任务
            result = subprocess.run(
                ["python3", "scripts/main.py", "--create", "CLI测试任务", "--data-dir", temp_dir],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent.parent
            )

            self.assertEqual(result.returncode, 0)
            self.assertIn("任务已创建", result.stdout)

            # 列出任务
            result2 = subprocess.run(
                ["python3", "scripts/main.py", "--list", "--data-dir", temp_dir],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent.parent
            )

            self.assertEqual(result2.returncode, 0)
            self.assertIn("CLI测试任务", result2.stdout)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
