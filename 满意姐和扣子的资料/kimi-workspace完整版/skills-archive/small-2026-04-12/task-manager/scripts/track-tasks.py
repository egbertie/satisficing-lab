#!/usr/bin/env python3
"""
任务跟踪脚本 - Task Tracker
版本: V1.0
创建时间: 2026-03-10

功能:
1. 任务CRUD操作（创建、读取、更新、删除）
2. 任务状态跟踪
3. 遗忘任务扫描
4. 报告生成
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
import argparse

# 配置路径
WORKSPACE_DIR = Path("/root/.openclaw/workspace")
TASK_MASTER_PATH = WORKSPACE_DIR / "docs" / "TASK_MASTER.md"
MEMORY_DIR = WORKSPACE_DIR / "memory"
CONFIG_PATH = Path(__file__).parent.parent / "config" / "reminder-rules.json"

class TaskManager:
    """任务管理器"""
    
    def __init__(self):
        self.tasks = []
        self.load_tasks()
    
    def load_tasks(self):
        """从TASK_MASTER.md加载任务列表"""
        # 简化版：解析Markdown文件提取任务
        # 实际实现需要更复杂的Markdown解析
        pass
    
    def add_task(self, name: str, deadline: str, priority: str = "P2", 
                 assignee: str = "满意妞", description: str = "") -> Dict:
        """添加新任务"""
        task_id = f"TASK-{datetime.now().strftime('%Y%m%d')}-{len(self.tasks)+1:03d}"
        task = {
            "id": task_id,
            "name": name,
            "deadline": deadline,
            "priority": priority,
            "assignee": assignee,
            "description": description,
            "status": "待启动",
            "progress": 0,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "completed_at": None
        }
        self.tasks.append(task)
        self.save_task(task)
        print(f"✅ 任务已创建: {task_id} - {name}")
        print(f"   截止日期: {deadline} | 优先级: {priority}")
        return task
    
    def update_status(self, task_id: str, status: str, progress: Optional[int] = None):
        """更新任务状态"""
        for task in self.tasks:
            if task["id"] == task_id:
                task["status"] = status
                task["updated_at"] = datetime.now().isoformat()
                if progress is not None:
                    task["progress"] = progress
                if status == "已完成":
                    task["completed_at"] = datetime.now().isoformat()
                    task["progress"] = 100
                self.save_task(task)
                print(f"✅ 任务 {task_id} 状态更新为: {status}")
                return task
        print(f"❌ 任务 {task_id} 未找到")
        return None
    
    def get_overdue_tasks(self) -> List[Dict]:
        """获取逾期任务"""
        today = datetime.now().date()
        overdue = []
        for task in self.tasks:
            if task["status"] not in ["已完成", "已取消"]:
                deadline = datetime.strptime(task["deadline"], "%Y-%m-%d").date()
                if deadline < today:
                    overdue.append(task)
        return overdue
    
    def get_upcoming_tasks(self, days: int = 3) -> List[Dict]:
        """获取即将到期的任务"""
        today = datetime.now().date()
        upcoming = []
        for task in self.tasks:
            if task["status"] not in ["已完成", "已取消"]:
                deadline = datetime.strptime(task["deadline"], "%Y-%m-%d").date()
                delta = (deadline - today).days
                if 0 <= delta <= days:
                    upcoming.append({**task, "days_left": delta})
        return sorted(upcoming, key=lambda x: x["days_left"])
    
    def scan_forgotten_tasks(self) -> List[Dict]:
        """扫描被遗忘的任务"""
        # 从memory文件中查找提到但未完成的任务
        forgotten = []
        memory_files = sorted(MEMORY_DIR.glob("2026-*.md"))
        
        # 读取TASK_MASTER中的被遗忘任务列表
        if TASK_MASTER_PATH.exists():
            content = TASK_MASTER_PATH.read_text(encoding='utf-8')
            # 查找被遗忘任务表格
            if "被遗忘任务" in content:
                # 简化提取逻辑
                pass
        
        return forgotten
    
    def generate_morning_report(self) -> str:
        """生成晨报"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        # 读取模板
        template_path = Path(__file__).parent.parent / "templates" / "daily-report.md"
        if template_path.exists():
            template = template_path.read_text(encoding='utf-8')
        else:
            template = self._default_morning_template()
        
        # 填充数据
        report = template.replace("{{DATE}}", today)
        
        # 获取今日任务
        today_tasks = [t for t in self.tasks if t["deadline"] == today]
        
        # 获取进行中任务
        wip_tasks = [t for t in self.tasks if t["status"] == "进行中"]
        
        # 获取即将到期
        upcoming = self.get_upcoming_tasks(3)
        
        # 获取逾期
        overdue = self.get_overdue_tasks()
        
        # 构建报告内容
        sections = []
        
        # 今日重点
        sections.append("### 今日重点\n")
        if today_tasks:
            for i, task in enumerate(today_tasks[:3], 1):
                sections.append(f"{i}. **{task['name']}** - {task['priority']} - {task['progress']}%\n")
        else:
            sections.append("1. 无今日截止任务\n")
        
        # 进行中
        sections.append("\n### 进行中\n")
        for task in wip_tasks[:5]:
            sections.append(f"- 🔄 {task['name']} - {task['progress']}%\n")
        
        # 即将到期提醒
        if upcoming:
            sections.append("\n### ⏰ 即将到期提醒\n")
            for task in upcoming:
                sections.append(f"- {task['name']} - 还有{task['days_left']}天\n")
        
        # 逾期警告
        if overdue:
            sections.append("\n### ⚠️ 逾期任务\n")
            for task in overdue:
                sections.append(f"- 🔴 {task['name']} - 已逾期\n")
        
        report = report.replace("{{CONTENT}}", "".join(sections))
        
        return report
    
    def _default_morning_template(self) -> str:
        """默认晨报模板"""
        return """## 晨报 - {{DATE}}

{{CONTENT}}

---
*自动生成于 {{DATE}} 09:00*
"""
    
    def save_task(self, task: Dict):
        """保存任务到TASK_MASTER.md"""
        # 实际实现：更新Markdown文件
        # 这里仅作示例
        pass
    
    def print_summary(self):
        """打印任务摘要"""
        total = len(self.tasks)
        completed = len([t for t in self.tasks if t["status"] == "已完成"])
        wip = len([t for t in self.tasks if t["status"] == "进行中"])
        overdue = len(self.get_overdue_tasks())
        
        print(f"\n📊 任务统计")
        print(f"   总计: {total}")
        print(f"   ✅ 已完成: {completed}")
        print(f"   🔄 进行中: {wip}")
        print(f"   ⚠️ 逾期: {overdue}")


def main():
    parser = argparse.ArgumentParser(description="任务跟踪工具")
    parser.add_argument("command", choices=[
        "add", "update", "today", "forgotten", 
        "morning-report", "daily-report", "summary"
    ])
    parser.add_argument("--name", help="任务名称")
    parser.add_argument("--deadline", help="截止日期 (YYYY-MM-DD)")
    parser.add_argument("--priority", default="P2", help="优先级 (P0/P1/P2/P3)")
    parser.add_argument("--assignee", default="满意妞", help="负责人")
    parser.add_argument("--status", help="任务状态")
    parser.add_argument("--progress", type=int, help="进度百分比")
    parser.add_argument("--task-id", help="任务ID")
    
    args = parser.parse_args()
    
    tm = TaskManager()
    
    if args.command == "add":
        if not args.name or not args.deadline:
            print("❌ 需要提供 --name 和 --deadline")
            sys.exit(1)
        tm.add_task(args.name, args.deadline, args.priority, args.assignee)
    
    elif args.command == "update":
        if not args.task_id:
            print("❌ 需要提供 --task-id")
            sys.exit(1)
        tm.update_status(args.task_id, args.status, args.progress)
    
    elif args.command == "today":
        today = datetime.now().strftime("%Y-%m-%d")
        tasks = [t for t in tm.tasks if t["deadline"] == today]
        print(f"\n📅 今日任务 ({today}):")
        for task in tasks:
            print(f"   {task['id']}: {task['name']} - {task['status']}")
    
    elif args.command == "forgotten":
        forgotten = tm.scan_forgotten_tasks()
        if forgotten:
            print("\n⚠️ 发现被遗忘的任务:")
            for task in forgotten:
                print(f"   - {task['name']}")
        else:
            print("\n✅ 未发现被遗忘的任务")
    
    elif args.command == "morning-report":
        report = tm.generate_morning_report()
        print(report)
        # 保存到文件
        today = datetime.now().strftime("%Y-%m-%d")
        report_path = MEMORY_DIR / f"晨报_{today}.md"
        report_path.write_text(report, encoding='utf-8')
        print(f"\n✅ 晨报已保存到: {report_path}")
    
    elif args.command == "summary":
        tm.print_summary()


if __name__ == "__main__":
    main()
