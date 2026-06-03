#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
满意解研究所 - 任务管理脚本
功能：任务创建、追踪、遗忘扫描、优先级管理
版本：1.0
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional


class TaskManager:
    """任务管理器核心类"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.base_path = Path("/root/.openclaw/workspace")
        self.config_path = Path(config_path or "/root/.openclaw/skills/task-manager/config/settings.json")
        self.config = self._load_config()
        self.tasks: List[Dict] = []
        
    def _load_config(self) -> Dict:
        """加载配置文件"""
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return self._default_config()
    
    def _default_config(self) -> Dict:
        """默认配置"""
        return {
            "scan_interval_hours": 24,
            "reminder_days": 3,
            "priority_weights": {
                "高": 3,
                "中": 2,
                "低": 1
            },
            "auto_archive_days": 30
        }
    
    def create_task(
        self,
        title: str,
        priority: str = "中",
        deadline: Optional[str] = None,
        assignee: str = "满意妞",
        description: str = "",
        tags: List[str] = None
    ) -> Dict:
        """创建新任务"""
        task = {
            "id": f"T{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "title": title,
            "priority": priority,
            "status": "待开始",
            "deadline": deadline,
            "assignee": assignee,
            "description": description,
            "tags": tags or [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "completed_at": None
        }
        self.tasks.append(task)
        return task
    
    def scan_forgotten_tasks(self) -> List[Dict]:
        """扫描被遗忘的任务"""
        forgotten = []
        scan_window = timedelta(days=7)
        
        for task in self.tasks:
            if task["status"] in ["待开始", "进行中"]:
                created = datetime.fromisoformat(task["created_at"])
                if datetime.now() - created > scan_window:
                    task["forgotten_days"] = (datetime.now() - created).days
                    forgotten.append(task)
        
        return sorted(forgotten, key=lambda x: x["forgotten_days"], reverse=True)
    
    def get_todos(self, priority: Optional[str] = None) -> List[Dict]:
        """获取待办清单"""
        todos = [t for t in self.tasks if t["status"] in ["待开始", "进行中"]]
        
        if priority:
            todos = [t for t in todos if t["priority"] == priority]
        
        # 按优先级和截止日期排序
        priority_order = {"高": 0, "中": 1, "低": 2}
        todos.sort(key=lambda x: (
            priority_order.get(x["priority"], 3),
            x.get("deadline") or "9999-12-31"
        ))
        
        return todos
    
    def get_urgent_tasks(self, days: int = 3) -> List[Dict]:
        """获取即将到期任务"""
        urgent = []
        deadline = datetime.now() + timedelta(days=days)
        
        for task in self.tasks:
            if task["deadline"] and task["status"] in ["待开始", "进行中"]:
                task_deadline = datetime.strptime(task["deadline"], "%Y-%m-%d")
                if task_deadline <= deadline:
                    urgent.append(task)
        
        return sorted(urgent, key=lambda x: x["deadline"])
    
    def update_task(self, task_id: str, **kwargs) -> Optional[Dict]:
        """更新任务"""
        for task in self.tasks:
            if task["id"] == task_id:
                task.update(kwargs)
                task["updated_at"] = datetime.now().isoformat()
                if kwargs.get("status") == "已完成":
                    task["completed_at"] = datetime.now().isoformat()
                return task
        return None
    
    def complete_task(self, task_id: str) -> Optional[Dict]:
        """完成任务"""
        return self.update_task(task_id, status="已完成")
    
    def generate_report(self) -> Dict:
        """生成任务统计报告"""
        total = len(self.tasks)
        completed = len([t for t in self.tasks if t["status"] == "已完成"])
        in_progress = len([t for t in self.tasks if t["status"] == "进行中"])
        pending = len([t for t in self.tasks if t["status"] == "待开始"])
        
        return {
            "total": total,
            "completed": completed,
            "in_progress": in_progress,
            "pending": pending,
            "completion_rate": round(completed / total * 100, 1) if total else 0,
            "forgotten_count": len(self.scan_forgotten_tasks()),
            "urgent_count": len(self.get_urgent_tasks())
        }


if __name__ == "__main__":
    # 测试运行
    tm = TaskManager()
    
    # 创建示例任务
    tm.create_task(
        title="测试任务",
        priority="高",
        deadline="2026-03-15",
        assignee="满意妞"
    )
    
    # 生成报告
    report = tm.generate_report()
    print(f"任务统计: {report}")
    
    # 获取待办
    todos = tm.get_todos()
    print(f"待办任务: {len(todos)} 个")
