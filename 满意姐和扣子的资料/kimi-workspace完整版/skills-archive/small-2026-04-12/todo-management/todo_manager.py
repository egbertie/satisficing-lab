#!/usr/bin/env python3
"""
五路图腾 · TODO管理系统
WLU-TODO-v1.0-FIN-260328
"""

import json
import os
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# 配置路径
TODO_DIR = Path("/root/.openclaw/workspace/data/todo")
ACTIVE_DIR = TODO_DIR / "active"
COMPLETED_DIR = TODO_DIR / "completed"
ARCHIVED_DIR = TODO_DIR / "archived"
MASTER_FILE = TODO_DIR / "todo-master.json"

# 有效值定义
VALID_STATUSES = ['pending', 'in_progress', 'completed', 'cancelled', 'archived']
VALID_PRIORITIES = ['P0', 'P1', 'P2', 'P3']
VALID_CATEGORIES = ['工作', '学习', '生活', '健康', '其他']
VALID_TOTEMS = ['LIU', 'SIMON', 'GUANYIN', 'CONFUCIUS', 'HUINENG']

class TodoManager:
    """TODO管理核心类"""
    
    def __init__(self):
        self._ensure_directories()
        self.master = self._load_master()
    
    def _ensure_directories(self):
        """确保目录结构存在"""
        ACTIVE_DIR.mkdir(parents=True, exist_ok=True)
        COMPLETED_DIR.mkdir(parents=True, exist_ok=True)
        ARCHIVED_DIR.mkdir(parents=True, exist_ok=True)
    
    def _load_master(self) -> Dict:
        """加载主索引文件"""
        if MASTER_FILE.exists():
            with open(MASTER_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "version": "1.0",
            "last_updated": datetime.now().isoformat(),
            "stats": {
                "total_active": 0,
                "total_completed_today": 0,
                "by_priority": {"P0": 0, "P1": 0, "P2": 0, "P3": 0},
                "by_totem": {"LIU": 0, "SIMON": 0, "GUANYIN": 0, "CONFUCIUS": 0, "HUINENG": 0}
            },
            "active_tasks": [],
            "overdue_tasks": [],
            "today_due": []
        }
    
    def _save_master(self):
        """保存主索引文件"""
        self.master["last_updated"] = datetime.now().isoformat()
        with open(MASTER_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.master, f, ensure_ascii=False, indent=2)
    
    def _generate_id(self) -> str:
        """生成TODO ID"""
        today = datetime.now().strftime("%Y%m%d")
        # 查找今天的最大序号
        max_seq = 0
        for task_file in ACTIVE_DIR.glob(f"TODO-{today}-*.json"):
            match = re.search(rf'TODO-{today}-(\d+)', task_file.name)
            if match:
                max_seq = max(max_seq, int(match.group(1)))
        return f"TODO-{today}-{max_seq + 1:03d}"
    
    def _detect_totem(self, title: str, description: str = "") -> str:
        """
        智能检测五路图腾对齐
        基于关键词匹配
        """
        text = (title + " " + description).lower()
        
        # LIU - 关系、合作、信任
        liu_keywords = ['合作', '关系', '信任', '团队', '沟通', '会议', '客户', '伙伴', '邀请', '联系']
        # SIMON - 决策、分析、规划
        simon_keywords = ['决策', '分析', '规划', '评估', '方案', '报告', '审计', '检查', '优化', '设计']
        # GUANYIN - 应变、调整、洞察
        guanyin_keywords = ['调整', '应变', '监控', '预警', '风险', '变化', '适应', '灵活', '感知', '观察']
        # CONFUCIUS - 伦理、原则、底线
        confucius_keywords = ['伦理', '原则', '底线', '道德', '规范', '合规', '诚信', '责任', '安全', '保密']
        # HUINENG - 突破、创新、顿悟
        huineng_keywords = ['创新', '突破', '灵感', '顿悟', '尝试', '实验', '探索', '新', '突破', '变革']
        
        scores = {
            'LIU': sum(1 for k in liu_keywords if k in text),
            'SIMON': sum(1 for k in simon_keywords if k in text),
            'GUANYIN': sum(1 for k in guanyin_keywords if k in text),
            'CONFUCIUS': sum(1 for k in confucius_keywords if k in text),
            'HUINENG': sum(1 for k in huineng_keywords if k in text)
        }
        
        # 返回得分最高的图腾
        return max(scores, key=scores.get) if max(scores.values()) > 0 else 'SIMON'
    
    def _parse_priority(self, text: str) -> str:
        """从文本中提取优先级"""
        if 'P0' in text or '紧急' in text or '立即' in text:
            return 'P0'
        elif 'P1' in text or '重要' in text:
            return 'P1'
        elif 'P2' in text or '一般' in text:
            return 'P2'
        elif 'P3' in text or '低' in text:
            return 'P3'
        return 'P2'  # 默认
    
    def _parse_due_date(self, text: str) -> Optional[str]:
        """从文本中提取截止时间"""
        now = datetime.now()
        
        # 匹配"今天"
        if '今天' in text:
            return (now.replace(hour=23, minute=59, second=59)).isoformat()
        
        # 匹配"明天"
        if '明天' in text:
            tomorrow = now + timedelta(days=1)
            return tomorrow.replace(hour=23, minute=59, second=59).isoformat()
        
        # 匹配"后天"
        if '后天' in text:
            day_after = now + timedelta(days=2)
            return day_after.replace(hour=23, minute=59, second=59).isoformat()
        
        # 匹配"X天后"
        match = re.search(r'(\d+)天后', text)
        if match:
            days = int(match.group(1))
            future = now + timedelta(days=days)
            return future.replace(hour=23, minute=59, second=59).isoformat()
        
        # 匹配"本周X"
        weekday_map = {'一': 0, '二': 1, '三': 2, '四': 3, '五': 4, '六': 5, '日': 6, '天': 6}
        match = re.search(r'本周([一二三四五六日天])', text)
        if match:
            target_weekday = weekday_map[match.group(1)]
            current_weekday = now.weekday()
            days_diff = target_weekday - current_weekday
            if days_diff <= 0:
                days_diff += 7
            target_date = now + timedelta(days=days_diff)
            return target_date.replace(hour=23, minute=59, second=59).isoformat()
        
        # 匹配"下周X"
        match = re.search(r'下周([一二三四五六日天])', text)
        if match:
            target_weekday = weekday_map[match.group(1)]
            days_until_next_monday = 7 - now.weekday()
            target_date = now + timedelta(days=days_until_next_monday + target_weekday)
            return target_date.replace(hour=23, minute=59, second=59).isoformat()
        
        return None
    
    def validate(self, todo: Dict) -> Tuple[bool, List[str]]:
        """验证TODO数据完整性"""
        errors = []
        
        # 必填字段检查
        required = ['id', 'title', 'status', 'priority', 'created_at']
        for field in required:
            if field not in todo:
                errors.append(f"缺少必填字段: {field}")
        
        # 状态有效性
        if todo.get('status') not in VALID_STATUSES:
            errors.append(f"无效状态: {todo.get('status')}")
        
        # 优先级有效性
        if todo.get('priority') not in VALID_PRIORITIES:
            errors.append(f"无效优先级: {todo.get('priority')}")
        
        # 图腾有效性
        if todo.get('totem_alignment') not in VALID_TOTEMS:
            errors.append(f"无效图腾: {todo.get('totem_alignment')}")
        
        # 时间逻辑检查
        if todo.get('completed_at') and todo.get('created_at'):
            try:
                completed = datetime.fromisoformat(todo['completed_at'])
                created = datetime.fromisoformat(todo['created_at'])
                if completed < created:
                    errors.append("完成时间不能早于创建时间")
            except:
                errors.append("时间格式错误")
        
        return len(errors) == 0, errors
    
    def create(self, title: str, description: str = "", priority: str = None, 
               due_at: str = None, category: str = "工作", tags: List[str] = None) -> Dict:
        """
        创建新TODO
        
        Args:
            title: 任务标题
            description: 详细描述
            priority: 优先级 (P0/P1/P2/P3)，None则自动检测
            due_at: 截止时间 (ISO格式)，None则自动检测
            category: 分类
            tags: 标签列表
        
        Returns:
            创建的TODO对象
        """
        # 自动解析优先级
        combined_text = f"{title} {description}"
        if priority is None:
            priority = self._parse_priority(combined_text)
        
        # 自动解析截止时间
        if due_at is None:
            due_at = self._parse_due_date(combined_text)
        
        # 生成TODO对象
        todo = {
            "id": self._generate_id(),
            "title": title,
            "description": description,
            "status": "pending",
            "priority": priority,
            "category": category,
            "created_at": datetime.now().isoformat(),
            "due_at": due_at,
            "completed_at": None,
            "reminders": [
                {"type": "24h_before", "sent": False},
                {"type": "2h_before", "sent": False},
                {"type": "overdue", "sent": False}
            ] if due_at else [],
            "tags": tags or [],
            "source": "user_created",
            "totem_alignment": self._detect_totem(title, description)
        }
        
        # 验证
        is_valid, errors = self.validate(todo)
        if not is_valid:
            raise ValueError(f"TODO验证失败: {', '.join(errors)}")
        
        # 保存
        todo_file = ACTIVE_DIR / f"{todo['id']}.json"
        with open(todo_file, 'w', encoding='utf-8') as f:
            json.dump(todo, f, ensure_ascii=False, indent=2)
        
        # 更新主索引
        self.master["active_tasks"].append(todo['id'])
        self.master["stats"]["total_active"] += 1
        self.master["stats"]["by_priority"][priority] += 1
        self.master["stats"]["by_totem"][todo['totem_alignment']] += 1
        self._save_master()
        
        return todo
    
    def get(self, todo_id: str) -> Optional[Dict]:
        """获取单个TODO"""
        # 先在活跃目录查找
        todo_file = ACTIVE_DIR / f"{todo_id}.json"
        if todo_file.exists():
            with open(todo_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # 在已完成目录查找
        todo_file = COMPLETED_DIR / f"{todo_id}.json"
        if todo_file.exists():
            with open(todo_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return None
    
    def update(self, todo_id: str, **kwargs) -> Optional[Dict]:
        """更新TODO"""
        todo = self.get(todo_id)
        if not todo:
            return None
        
        # 可更新字段
        allowed_fields = ['title', 'description', 'priority', 'category', 'due_at', 'tags', 'status']
        
        old_priority = todo.get('priority')
        old_totem = todo.get('totem_alignment')
        
        for key, value in kwargs.items():
            if key in allowed_fields:
                todo[key] = value
        
        # 如果状态变为completed，设置完成时间
        if kwargs.get('status') == 'completed' and todo.get('status') == 'completed':
            if not todo.get('completed_at'):
                todo['completed_at'] = datetime.now().isoformat()
        
        # 重新检测图腾（如果标题或描述变更）
        if 'title' in kwargs or 'description' in kwargs:
            todo['totem_alignment'] = self._detect_totem(
                todo.get('title', ''), 
                todo.get('description', '')
            )
        
        # 验证
        is_valid, errors = self.validate(todo)
        if not is_valid:
            raise ValueError(f"TODO验证失败: {', '.join(errors)}")
        
        # 保存
        if todo['status'] in ['completed', 'cancelled']:
            # 移动到已完成目录
            old_file = ACTIVE_DIR / f"{todo_id}.json"
            new_file = COMPLETED_DIR / f"{todo_id}.json"
            if old_file.exists():
                old_file.unlink()
        else:
            todo_file = ACTIVE_DIR / f"{todo_id}.json"
            new_file = todo_file
        
        with open(new_file, 'w', encoding='utf-8') as f:
            json.dump(todo, f, ensure_ascii=False, indent=2)
        
        # 更新主索引统计
        if old_priority != todo.get('priority'):
            self.master["stats"]["by_priority"][old_priority] -= 1
            self.master["stats"]["by_priority"][todo['priority']] += 1
        
        if old_totem != todo.get('totem_alignment'):
            self.master["stats"]["by_totem"][old_totem] -= 1
            self.master["stats"]["by_totem"][todo['totem_alignment']] += 1
        
        self._save_master()
        
        return todo
    
    def list(self, status: str = None, priority: str = None, 
             totem: str = None, category: str = None) -> List[Dict]:
        """列出TODO，支持筛选"""
        todos = []
        
        # 从活跃目录加载
        for todo_file in ACTIVE_DIR.glob("TODO-*.json"):
            with open(todo_file, 'r', encoding='utf-8') as f:
                todo = json.load(f)
                
                # 应用筛选
                if status and todo.get('status') != status:
                    continue
                if priority and todo.get('priority') != priority:
                    continue
                if totem and todo.get('totem_alignment') != totem:
                    continue
                if category and todo.get('category') != category:
                    continue
                
                todos.append(todo)
        
        # 按优先级和创建时间排序
        priority_order = {'P0': 0, 'P1': 1, 'P2': 2, 'P3': 3}
        todos.sort(key=lambda x: (
            priority_order.get(x.get('priority', 'P3'), 3),
            x.get('created_at', '')
        ))
        
        return todos
    
    def delete(self, todo_id: str) -> bool:
        """删除TODO"""
        todo = self.get(todo_id)
        if not todo:
            return False
        
        # 删除文件
        for dir_path in [ACTIVE_DIR, COMPLETED_DIR]:
            todo_file = dir_path / f"{todo_id}.json"
            if todo_file.exists():
                todo_file.unlink()
        
        # 更新主索引
        if todo_id in self.master["active_tasks"]:
            self.master["active_tasks"].remove(todo_id)
        self.master["stats"]["total_active"] = max(0, self.master["stats"]["total_active"] - 1)
        self.master["stats"]["by_priority"][todo['priority']] = max(0, self.master["stats"]["by_priority"][todo['priority']] - 1)
        self.master["stats"]["by_totem"][todo['totem_alignment']] = max(0, self.master["stats"]["by_totem"][todo['totem_alignment']] - 1)
        self._save_master()
        
        return True
    
    def get_overdue(self) -> List[Dict]:
        """获取已逾期任务"""
        now = datetime.now()
        overdue = []
        
        for todo in self.list():
            due_at = todo.get('due_at')
            if due_at and todo.get('status') not in ['completed', 'cancelled', 'archived']:
                try:
                    due_time = datetime.fromisoformat(due_at)
                    if due_time < now:
                        overdue.append(todo)
                except:
                    pass
        
        return overdue
    
    def get_today_due(self) -> List[Dict]:
        """获取今日到期任务"""
        now = datetime.now()
        today_start = now.replace(hour=0, minute=0, second=0)
        today_end = now.replace(hour=23, minute=59, second=59)
        today_due = []
        
        for todo in self.list():
            due_at = todo.get('due_at')
            if due_at and todo.get('status') not in ['completed', 'cancelled', 'archived']:
                try:
                    due_time = datetime.fromisoformat(due_at)
                    if today_start <= due_time <= today_end:
                        today_due.append(todo)
                except:
                    pass
        
        return today_due
    
    def generate_daily_report(self) -> str:
        """生成每日报告"""
        now = datetime.now()
        todos = self.list()
        
        # 统计
        by_priority = {'P0': 0, 'P1': 0, 'P2': 0, 'P3': 0}
        by_totem = {'LIU': 0, 'SIMON': 0, 'GUANYIN': 0, 'CONFUCIUS': 0, 'HUINENG': 0}
        overdue_count = 0
        today_completed = 0
        
        today_start = now.replace(hour=0, minute=0, second=0)
        
        for todo in todos:
            priority = todo.get('priority', 'P3')
            totem = todo.get('totem_alignment', 'SIMON')
            by_priority[priority] = by_priority.get(priority, 0) + 1
            by_totem[totem] = by_totem.get(totem, 0) + 1
            
            # 检查逾期
            due_at = todo.get('due_at')
            if due_at and todo.get('status') not in ['completed', 'cancelled']:
                try:
                    if datetime.fromisoformat(due_at) < now:
                        overdue_count += 1
                except:
                    pass
            
            # 检查今日完成
            completed_at = todo.get('completed_at')
            if completed_at:
                try:
                    if datetime.fromisoformat(completed_at) >= today_start:
                        today_completed += 1
                except:
                    pass
        
        # 构建报告
        report = f"""📋 每日TODO报告 ({now.strftime('%Y-%m-%d')})
━━━━━━━━━━━━━━━━━━━━
🔥 P0: {by_priority['P0']}个
⚡ P1: {by_priority['P1']}个  
📌 P2: {by_priority['P2']}个
💡 P3: {by_priority['P3']}个

今日完成: {today_completed}个
⚠️ 逾期任务: {overdue_count}个
━━━━━━━━━━━━━━━━━━━━
五路图腾分布:
🦉 LIU: {by_totem['LIU']}  |  ⚒️ SIMON: {by_totem['SIMON']}
🛡️ GUANYIN: {by_totem['GUANYIN']}  |  📜 CONFUCIUS: {by_totem['CONFUCIUS']}
🔥 HUINENG: {by_totem['HUINENG']}
"""
        
        return report


# 全局实例
todo_manager = TodoManager()


if __name__ == "__main__":
    # 测试代码
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python todo_manager.py <command> [args]")
        print("Commands: create, list, get, update, delete, report")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "create":
        if len(sys.argv) < 3:
            print("Usage: python todo_manager.py create '<title>' [description]")
            sys.exit(1)
        todo = todo_manager.create(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "")
        print(f"✅ 已创建 {todo['id']}")
        print(f"   标题: {todo['title']}")
        print(f"   优先级: {todo['priority']}")
        print(f"   图腾对齐: {todo['totem_alignment']}")
    
    elif cmd == "list":
        todos = todo_manager.list()
        if not todos:
            print("暂无TODO任务")
        else:
            for todo in todos[:10]:  # 最多显示10个
                status_icon = "⏳" if todo['status'] == 'pending' else "🔄" if todo['status'] == 'in_progress' else "✅"
                print(f"{status_icon} [{todo['priority']}] {todo['title']} ({todo['id']})")
    
    elif cmd == "report":
        print(todo_manager.generate_daily_report())
    
    else:
        print(f"Unknown command: {cmd}")
