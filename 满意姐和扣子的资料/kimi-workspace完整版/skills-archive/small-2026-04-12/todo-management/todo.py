#!/usr/bin/env python3
"""
TODO管理模块
5标准化实现
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional

class TodoManager:
    """任务管理器"""
    
    def __init__(self, workspace="/root/.openclaw/workspace"):
        self.workspace = Path(workspace)
        self.todo_dir = self.workspace / "memory" / "todos"
        self.todo_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = self.todo_dir / "index.json"
        
        # 初始化索引
        if not self.index_file.exists():
            self._save_index({"counter": 0, "todos": []})
    
    def _load_index(self) -> Dict:
        """加载索引"""
        with open(self.index_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _save_index(self, index: Dict):
        """保存索引"""
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(index, f, ensure_ascii=False, indent=2)
    
    def create(self, title: str, description: str = "", 
               priority: str = "P2", due_date: str = "") -> str:
        """创建任务"""
        # S7: 空标题检测
        if not title.strip():
            return "❌ 任务标题不能为空"
        
        # S7: 无效优先级检测
        if priority not in ["P0", "P1", "P2", "P3"]:
            return "❌ 优先级必须是 P0/P1/P2/P3"
        
        index = self._load_index()
        index["counter"] += 1
        todo_id = f"T{index['counter']:03d}"
        
        todo = {
            "id": todo_id,
            "title": title,
            "description": description,
            "priority": priority,
            "due_date": due_date,
            "status": "todo",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # 保存任务文件
        todo_file = self.todo_dir / f"{todo_id}.json"
        with open(todo_file, 'w', encoding='utf-8') as f:
            json.dump(todo, f, ensure_ascii=False, indent=2)
        
        # 更新索引
        index["todos"].append(todo_id)
        self._save_index(index)
        
        return f"✅ 任务创建成功: {todo_id} - {title}"
    
    def update(self, todo_id: str, **kwargs) -> str:
        """更新任务"""
        todo_file = self.todo_dir / f"{todo_id}.json"
        
        # S7: 不存在检测
        if not todo_file.exists():
            return f"❌ 任务不存在: {todo_id}"
        
        with open(todo_file, 'r', encoding='utf-8') as f:
            todo = json.load(f)
        
        # 更新字段
        allowed_fields = ["title", "description", "priority", "due_date", "status"]
        for key, value in kwargs.items():
            if key in allowed_fields:
                todo[key] = value
        
        todo["updated_at"] = datetime.now().isoformat()
        
        with open(todo_file, 'w', encoding='utf-8') as f:
            json.dump(todo, f, ensure_ascii=False, indent=2)
        
        return f"✅ 任务更新成功: {todo_id}"
    
    def list(self, status: str = "", priority: str = "") -> str:
        """列出任务 - S3输出规范"""
        index = self._load_index()
        
        if not index["todos"]:
            return "## 📋 任务列表\n\n暂无任务"
        
        # 加载所有任务
        todos = []
        for todo_id in index["todos"]:
            todo_file = self.todo_dir / f"{todo_id}.json"
            if todo_file.exists():
                with open(todo_file, 'r', encoding='utf-8') as f:
                    todo = json.load(f)
                    # 筛选
                    if status and todo.get("status") != status:
                        continue
                    if priority and todo.get("priority") != priority:
                        continue
                    todos.append(todo)
        
        # 按优先级排序
        priority_order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
        todos.sort(key=lambda x: priority_order.get(x.get("priority", "P3"), 3))
        
        # S3: 格式化输出
        output = "## 📋 任务列表\n\n"
        
        # 分组
        status_groups = {"todo": "⏸️ 待启动", "doing": "🔄 进行中", 
                        "done": "✅ 已完成", "blocked": "🔴 阻塞"}
        
        for status_key, status_label in status_groups.items():
            group_todos = [t for t in todos if t.get("status") == status_key]
            if group_todos:
                output += f"### {status_label} ({len(group_todos)})\n\n"
                output += "| ID | 任务 | 优先级 | 截止 |\n"
                output += "|----|------|--------|------|\n"
                for todo in group_todos:
                    tid = todo.get("id", "")
                    title = todo.get("title", "")[:20]
                    pri = todo.get("priority", "")
                    due = todo.get("due_date", "-")
                    output += f"| {tid} | {title} | {pri} | {due} |\n"
                output += "\n"
        
        return output
    
    def check_overdue(self) -> List[Dict]:
        """检查逾期任务"""
        index = self._load_index()
        overdue = []
        today = datetime.now().date()
        
        for todo_id in index["todos"]:
            todo_file = self.todo_dir / f"{todo_id}.json"
            if todo_file.exists():
                with open(todo_file, 'r', encoding='utf-8') as f:
                    todo = json.load(f)
                
                due_date = todo.get("due_date", "")
                status = todo.get("status", "")
                
                if due_date and status not in ["done"]:
                    try:
                        due = datetime.strptime(due_date, "%Y-%m-%d").date()
                        if due < today:
                            overdue.append(todo)
                    except:
                        pass
        
        return overdue

def main():
    """测试"""
    print("🧪 测试TODO管理...")
    
    manager = TodoManager()
    
    # 测试创建
    print(manager.create("测试任务1", "描述", "P1", "2026-03-30"))
    print(manager.create("测试任务2", "描述", "P2", "2026-04-01"))
    
    # 测试列表
    print("\n" + manager.list())
    
    # 测试逾期检查
    overdue = manager.check_overdue()
    print(f"\n逾期任务: {len(overdue)}")

if __name__ == "__main__":
    main()
