#!/usr/bin/env python3
"""
worker-orchestrator: 6 Worker分配引擎
实现DAG任务编排和Worker任务路由

作者: 满意妞
版本: 1.0.0
日期: 2026-03-28
"""

import json
import uuid
import threading
import time
from enum import Enum
from typing import Dict, List, Optional, Callable, Any, Set, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
import copy


class WorkerType(Enum):
    """6 Worker类型定义"""
    META_STRATEGIST = "meta_strategist"      # 全局编排
    SUPERVISOR_BIZ = "supervisor_biz"        # 业务域监督
    SUPERVISOR_TECH = "supervisor_tech"      # 技术域监督
    WORKER_ANALYSIS = "worker_analysis"      # 数据分析
    WORKER_EXECUTION = "worker_execution"    # 执行操作
    WORKER_CREATIVE = "worker_creative"      # 创意生成


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"          # 等待中
    RUNNING = "running"          # 执行中
    COMPLETED = "completed"      # 完成
    FAILED = "failed"            # 失败
    CANCELLED = "cancelled"      # 取消


@dataclass
class Task:
    """任务定义"""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    worker_type: WorkerType = WorkerType.WORKER_EXECUTION
    input_data: Dict = field(default_factory=dict)
    output_data: Dict = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)  # 依赖任务ID列表
    status: TaskStatus = TaskStatus.PENDING
    priority: int = 5  # 1-10, 数字越小优先级越高
    max_retries: int = 3
    retry_count: int = 0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error_message: str = ""
    
    def to_dict(self) -> Dict:
        """序列化"""
        data = asdict(self)
        data['worker_type'] = self.worker_type.value
        data['status'] = self.status.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> "Task":
        """反序列化"""
        data = copy.deepcopy(data)
        data['worker_type'] = WorkerType(data['worker_type'])
        data['status'] = TaskStatus(data['status'])
        return cls(**data)


@dataclass
class Worker:
    """Worker定义"""
    id: str
    worker_type: WorkerType
    name: str
    status: str = "idle"  # idle, busy, offline
    current_task: Optional[str] = None
    capabilities: List[str] = field(default_factory=list)
    total_tasks: int = 0
    success_tasks: int = 0
    
    def to_dict(self) -> Dict:
        data = asdict(self)
        data['worker_type'] = self.worker_type.value
        return data


class WorkerOrchestrator:
    """
    Worker编排器 - 6 Worker分配引擎
    
    功能:
    - 6 Worker类型识别与分配
    - DAG（有向无环图）任务编排
    - 任务优先级管理
    - 任务失败重试
    """
    
    def __init__(self, storage_path: str = "~/.openclaw/system-v2/orchestrator"):
        """初始化编排器"""
        self.storage_path = Path(storage_path).expanduser()
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self._tasks: Dict[str, Task] = {}
        self._workers: Dict[str, Worker] = {}
        self._task_handlers: Dict[WorkerType, Callable] = {}
        self._lock = threading.RLock()
        
        # 初始化6个Worker
        self._init_workers()
        
        # 加载已有任务
        self._load_tasks()
    
    def _init_workers(self):
        """初始化6 Worker"""
        workers_config = [
            (WorkerType.META_STRATEGIST, "meta-1", "Meta-Strategist", ["决策", "规划"]),
            (WorkerType.SUPERVISOR_BIZ, "super-biz-1", "Supervisor-Biz", ["业务分析", "需求理解"]),
            (WorkerType.SUPERVISOR_TECH, "super-tech-1", "Supervisor-Tech", ["技术分析", "架构设计"]),
            (WorkerType.WORKER_ANALYSIS, "worker-ana-1", "Worker-Analysis", ["数据分析", "报告生成"]),
            (WorkerType.WORKER_EXECUTION, "worker-exec-1", "Worker-Execution", ["代码执行", "文件操作"]),
            (WorkerType.WORKER_CREATIVE, "worker-cre-1", "Worker-Creative", ["创意生成", "内容创作"]),
        ]
        
        for worker_type, worker_id, name, capabilities in workers_config:
            self._workers[worker_id] = Worker(
                id=worker_id,
                worker_type=worker_type,
                name=name,
                capabilities=capabilities,
            )
    
    def _load_tasks(self):
        """从存储加载任务"""
        tasks_file = self.storage_path / "tasks.json"
        if tasks_file.exists():
            try:
                with open(tasks_file, 'r', encoding='utf-8') as f:
                    tasks_data = json.load(f)
                
                for task_id, task_data in tasks_data.items():
                    self._tasks[task_id] = Task.from_dict(task_data)
            except Exception as e:
                print(f"[Orchestrator] 加载任务失败: {e}")
    
    def _save_tasks(self):
        """保存任务到存储"""
        try:
            tasks_data = {task_id: task.to_dict() for task_id, task in self._tasks.items()}
            
            # 原子写入
            temp_file = self.storage_path / "tasks.json.tmp"
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(tasks_data, f, ensure_ascii=False, indent=2)
            
            temp_file.replace(self.storage_path / "tasks.json")
        except Exception as e:
            print(f"[Orchestrator] 保存任务失败: {e}")
    
    def register_task_handler(self, worker_type: WorkerType, handler: Callable[[Task], Tuple[bool, Dict]]):
        """
        注册任务处理器
        
        Args:
            worker_type: Worker类型
            handler: 处理函数，接收Task，返回(成功标志, 输出数据)
        """
        self._task_handlers[worker_type] = handler
    
    def submit_task(
        self,
        name: str,
        worker_type: WorkerType,
        input_data: Dict,
        dependencies: List[str] = None,
        priority: int = 5,
    ) -> str:
        """
        提交任务
        
        Args:
            name: 任务名称
            worker_type: Worker类型
            input_data: 输入数据
            dependencies: 依赖任务ID列表
            priority: 优先级（1-10，数字越小越高）
            
        Returns:
            任务ID
        """
        with self._lock:
            task = Task(
                name=name,
                worker_type=worker_type,
                input_data=input_data,
                dependencies=dependencies or [],
                priority=priority,
            )
            
            self._tasks[task.id] = task
            self._save_tasks()
            
            return task.id
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """获取任务"""
        with self._lock:
            return copy.deepcopy(self._tasks.get(task_id))
    
    def get_task_status(self, task_id: str) -> Optional[str]:
        """获取任务状态"""
        task = self.get_task(task_id)
        return task.status.value if task else None
    
    def _get_ready_tasks(self) -> List[Task]:
        """获取准备就绪的任务（依赖已完成）"""
        ready_tasks = []
        
        for task in self._tasks.values():
            if task.status != TaskStatus.PENDING:
                continue
            
            # 检查依赖是否都已完成
            deps_completed = all(
                self._tasks.get(dep_id) and 
                self._tasks[dep_id].status == TaskStatus.COMPLETED
                for dep_id in task.dependencies
            )
            
            if deps_completed:
                ready_tasks.append(task)
        
        # 按优先级排序
        ready_tasks.sort(key=lambda t: t.priority)
        return ready_tasks
    
    def _assign_worker(self, task: Task) -> Optional[str]:
        """为任务分配Worker"""
        # 找到空闲且类型匹配的Worker
        for worker_id, worker in self._workers.items():
            if worker.status == "idle" and worker.worker_type == task.worker_type:
                return worker_id
        return None
    
    def execute_task(self, task_id: str) -> Tuple[bool, str]:
        """
        执行任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            (成功标志, 消息)
        """
        with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                return False, f"任务不存在: {task_id}"
            
            if task.status != TaskStatus.PENDING:
                return False, f"任务状态错误: {task.status.value}"
            
            # 分配Worker
            worker_id = self._assign_worker(task)
            if not worker_id:
                return False, "无可用Worker"
            
            # 更新状态
            worker = self._workers[worker_id]
            worker.status = "busy"
            worker.current_task = task_id
            
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.now().isoformat()
            self._save_tasks()
        
        # 执行任务（在锁外执行，避免阻塞）
        try:
            handler = self._task_handlers.get(task.worker_type)
            if not handler:
                raise Exception(f"未找到Worker类型 {task.worker_type.value} 的处理器")
            
            success, output_data = handler(task)
            
            # 更新任务结果
            with self._lock:
                task.output_data = output_data
                task.completed_at = datetime.now().isoformat()
                
                if success:
                    task.status = TaskStatus.COMPLETED
                else:
                    task.retry_count += 1
                    if task.retry_count >= task.max_retries:
                        task.status = TaskStatus.FAILED
                        task.error_message = "达到最大重试次数"
                    else:
                        task.status = TaskStatus.PENDING  # 重新排队
                
                # 更新Worker状态
                worker.status = "idle"
                worker.current_task = None
                worker.total_tasks += 1
                if success:
                    worker.success_tasks += 1
                
                self._save_tasks()
            
            return success, "执行完成" if success else task.error_message
            
        except Exception as e:
            # 执行异常
            with self._lock:
                task.status = TaskStatus.FAILED
                task.error_message = str(e)
                task.completed_at = datetime.now().isoformat()
                
                worker.status = "idle"
                worker.current_task = None
                
                self._save_tasks()
            
            return False, str(e)
    
    def get_all_tasks(self) -> List[Dict]:
        """获取所有任务列表"""
        with self._lock:
            return [task.to_dict() for task in self._tasks.values()]
    
    def get_workers_status(self) -> List[Dict]:
        """获取所有Worker状态"""
        with self._lock:
            return [worker.to_dict() for worker in self._workers.values()]
    
    def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        with self._lock:
            task = self._tasks.get(task_id)
            if task and task.status == TaskStatus.PENDING:
                task.status = TaskStatus.CANCELLED
                self._save_tasks()
                return True
            return False
    
    def get_dag_status(self) -> Dict[str, int]:
        """获取DAG整体状态统计"""
        with self._lock:
            status_count = {status.value: 0 for status in TaskStatus}
            for task in self._tasks.values():
                status_count[task.status.value] += 1
            return status_count


def main():
    """CLI入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Worker Orchestrator - 6 Worker分配引擎")
    parser.add_argument("--submit", type=str, help="提交任务（JSON格式）")
    parser.add_argument("--status", type=str, help="查询任务状态")
    parser.add_argument("--list", action="store_true", help="列出所有任务")
    parser.add_argument("--workers", action="store_true", help="显示Worker状态")
    parser.add_argument("--dag", action="store_true", help="显示DAG状态")
    parser.add_argument("--test", action="store_true", help="运行测试")
    
    args = parser.parse_args()
    
    orchestrator = WorkerOrchestrator()
    
    if args.submit:
        try:
            task_data = json.loads(args.submit)
            task_id = orchestrator.submit_task(
                name=task_data.get("name", "unnamed"),
                worker_type=WorkerType(task_data.get("worker_type", "worker_execution")),
                input_data=task_data.get("input", {}),
                dependencies=task_data.get("dependencies", []),
                priority=task_data.get("priority", 5),
            )
            print(f"✅ 任务提交成功: {task_id}")
        except Exception as e:
            print(f"❌ 提交失败: {e}")
            exit(1)
    
    elif args.status:
        status = orchestrator.get_task_status(args.status)
        if status:
            print(f"📋 任务 {args.status} 状态: {status}")
        else:
            print(f"❌ 任务不存在: {args.status}")
            exit(1)
    
    elif args.list:
        tasks = orchestrator.get_all_tasks()
        if tasks:
            print("📋 所有任务:")
            for task in tasks:
                print(f"  • {task['id']}: {task['name']} ({task['status']})")
        else:
            print("📭 无任务")
    
    elif args.workers:
        workers = orchestrator.get_workers_status()
        print("👷 Worker状态:")
        for worker in workers:
            print(f"  • {worker['name']}: {worker['status']} (任务: {worker['total_tasks']})")
    
    elif args.dag:
        status = orchestrator.get_dag_status()
        print("📊 DAG状态:")
        for state, count in status.items():
            print(f"  • {state}: {count}")
    
    elif args.test:
        print("🧪 请运行: python3 -m pytest test_worker_orchestrator.py")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
