#!/usr/bin/env python3
"""
6 Worker蜂群激活记录系统 - M006
记录每次任务前的Worker选择和激活状态

创建时间: 2026-03-31
状态: 整改完成
"""

import json
from datetime import datetime
from pathlib import Path
from enum import Enum

class WorkerType(Enum):
    META_STRATEGIST = "Meta-Strategist"
    SUPERVISOR_BIZ = "Supervisor-Biz"
    SUPERVISOR_TECH = "Supervisor-Tech"
    WORKER_ANALYSIS = "Worker-Analysis"
    WORKER_EXECUTION = "Worker-Execution"
    WORKER_CREATIVE = "Worker-Creative"

class WorkerSwarmTracker:
    """Worker蜂群跟踪器"""
    
    def __init__(self, workspace="/root/.openclaw/workspace"):
        self.workspace = Path(workspace)
        self.activation_dir = self.workspace / "diary" / "worker_activations"
        self.activation_dir.mkdir(parents=True, exist_ok=True)
        
        # 当前激活状态
        self.current_activation = {
            "task_id": None,
            "activated_workers": [],
            "start_time": None,
            "status": "idle"
        }
    
    def activate_workers(self, task_id, task_description, selected_workers):
        """
        激活Worker蜂群
        
        Args:
            task_id: 任务ID
            task_description: 任务描述
            selected_workers: 选择的Worker列表
        """
        activation_record = {
            "task_id": task_id,
            "task_description": task_description,
            "activated_workers": selected_workers,
            "start_time": datetime.now().isoformat(),
            "hierarchy": self._build_hierarchy(selected_workers),
            "status": "activated"
        }
        
        # 保存激活记录
        self._save_activation(activation_record)
        
        # 更新当前状态
        self.current_activation = activation_record
        
        print(f"[WORKER-SWARM] 任务 {task_id} 激活Worker蜂群")
        print(f"  选择的Worker: {', '.join(selected_workers)}")
        print(f"  层级结构: {activation_record['hierarchy']}")
        
        return activation_record
    
    def _build_hierarchy(self, workers):
        """构建Worker层级结构"""
        hierarchy = {
            "meta": [],
            "supervisors": [],
            "workers": []
        }
        
        for worker in workers:
            if "Strategist" in worker:
                hierarchy["meta"].append(worker)
            elif "Supervisor" in worker:
                hierarchy["supervisors"].append(worker)
            else:
                hierarchy["workers"].append(worker)
        
        return hierarchy
    
    def complete_task(self, task_id, result_summary):
        """完成任务，记录结果"""
        # 查找并更新记录
        activation_file = self.activation_dir / f"{task_id}.json"
        
        if activation_file.exists():
            with open(activation_file, 'r', encoding='utf-8') as f:
                record = json.load(f)
            
            record["end_time"] = datetime.now().isoformat()
            record["result_summary"] = result_summary
            record["status"] = "completed"
            
            with open(activation_file, 'w', encoding='utf-8') as f:
                json.dump(record, f, ensure_ascii=False, indent=2)
            
            print(f"[WORKER-SWARM] 任务 {task_id} 完成")
            print(f"  结果: {result_summary}")
        
        # 重置当前状态
        self.current_activation = {
            "task_id": None,
            "activated_workers": [],
            "start_time": None,
            "status": "idle"
        }
    
    def _save_activation(self, record):
        """保存激活记录"""
        task_id = record["task_id"]
        activation_file = self.activation_dir / f"{task_id}.json"
        
        with open(activation_file, 'w', encoding='utf-8') as f:
            json.dump(record, f, ensure_ascii=False, indent=2)
    
    def get_activation_stats(self):
        """获取Worker激活统计"""
        stats = {
            "total_activations": 0,
            "by_worker": {},
            "completed": 0,
            "in_progress": 0
        }
        
        for f in self.activation_dir.glob("*.json"):
            with open(f, 'r', encoding='utf-8') as file:
                record = json.load(file)
                stats["total_activations"] += 1
                
                for worker in record.get("activated_workers", []):
                    stats["by_worker"][worker] = stats["by_worker"].get(worker, 0) + 1
                
                if record.get("status") == "completed":
                    stats["completed"] += 1
                else:
                    stats["in_progress"] += 1
        
        return stats
    
    def print_current_status(self):
        """打印当前Worker激活状态"""
        print("=== 当前Worker蜂群状态 ===")
        
        if self.current_activation["status"] == "idle":
            print("状态: 空闲（无激活任务）")
        else:
            print(f"任务ID: {self.current_activation['task_id']}")
            print(f"激活Worker: {', '.join(self.current_activation['activated_workers'])}")
            print(f"开始时间: {self.current_activation['start_time']}")
            print(f"层级: {self.current_activation.get('hierarchy', {})}")

# Worker选择决策树
def select_workers_for_task(task_type, complexity):
    """
    根据任务类型和复杂度选择Worker
    
    决策树:
    - 复杂任务/需要全局编排 → Meta-Strategist
    - 业务相关 → Supervisor-Biz
    - 技术相关 → Supervisor-Tech
    - 需要数据分析 → Worker-Analysis
    - 需要执行操作 → Worker-Execution
    - 需要创意设计 → Worker-Creative
    """
    workers = []
    
    # 所有任务都需要Meta-Strategist全局编排
    workers.append("Meta-Strategist")
    
    # 根据复杂度添加Supervisor
    if complexity in ["high", "critical"]:
        workers.extend(["Supervisor-Biz", "Supervisor-Tech"])
    
    # 根据任务类型添加Worker
    if task_type == "analysis":
        workers.append("Worker-Analysis")
    elif task_type == "execution":
        workers.append("Worker-Execution")
    elif task_type == "creative":
        workers.append("Worker-Creative")
    
    return workers

# 使用示例
if __name__ == "__main__":
    tracker = WorkerSwarmTracker()
    
    # 示例：激活Worker处理复杂分析任务
    print("=== 6 Worker蜂群激活示例 ===")
    print()
    
    task_id = f"TASK-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    task_desc = "分析历史数据并生成报告"
    
    # 选择Worker
    selected = select_workers_for_task("analysis", "high")
    
    # 激活
    tracker.activate_workers(task_id, task_desc, selected)
    print()
    
    # 查看统计
    stats = tracker.get_activation_stats()
    print(f"总激活次数: {stats['total_activations']}")
    print(f"已完成: {stats['completed']}")
    print(f"进行中: {stats['in_progress']}")
