#!/usr/bin/env python3
"""
worker-orchestrator 单元测试
"""

import unittest
import tempfile
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from worker_orchestrator import WorkerOrchestrator, WorkerType, TaskStatus


class TestWorkerOrchestrator(unittest.TestCase):
    """WorkerOrchestrator单元测试"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.orch = WorkerOrchestrator(storage_path=f"{self.temp_dir}/orchestrator")
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_submit_task(self):
        """测试提交任务"""
        task_id = self.orch.submit_task(
            name="test_task",
            worker_type=WorkerType.WORKER_EXECUTION,
            input_data={"key": "value"},
        )
        
        self.assertIsNotNone(task_id)
        self.assertEqual(len(task_id), 8)  # UUID前8位
        
        task = self.orch.get_task(task_id)
        self.assertEqual(task.name, "test_task")
        self.assertEqual(task.status, TaskStatus.PENDING)
    
    def test_get_workers_status(self):
        """测试获取Worker状态"""
        workers = self.orch.get_workers_status()
        
        self.assertEqual(len(workers), 6)  # 6个Worker
        
        worker_types = [w["worker_type"] for w in workers]
        self.assertIn("meta_strategist", worker_types)
        self.assertIn("worker_execution", worker_types)
    
    def test_task_with_dependencies(self):
        """测试带依赖的任务"""
        task1_id = self.orch.submit_task(
            name="task1",
            worker_type=WorkerType.WORKER_EXECUTION,
            input_data={},
        )
        
        task2_id = self.orch.submit_task(
            name="task2",
            worker_type=WorkerType.WORKER_EXECUTION,
            input_data={},
            dependencies=[task1_id],
        )
        
        task2 = self.orch.get_task(task2_id)
        self.assertEqual(task2.dependencies, [task1_id])


if __name__ == "__main__":
    unittest.main(verbosity=2)
