#!/usr/bin/env python3
"""
zero-idle-enforcer - 零空置执行器
真正实现版本

功能:
- 任务空置检测
- 自动任务分配
- 时间利用率追踪
- 闲置预警
- 自动补救建议

作者: 满意妞 (重构)
版本: 2.0.1-real
日期: 2026-04-03
"""

import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable
from enum import Enum
import threading


class TaskStatus(Enum):
    """任务状态"""
    IDLE = "idle"           # 空闲
    ASSIGNED = "assigned"   # 已分配
    IN_PROGRESS = "in_progress"  # 进行中
    COMPLETED = "completed" # 已完成
    BLOCKED = "blocked"     # 阻塞


class IdleSeverity(Enum):
    """空置严重程度"""
    NONE = "none"
    LOW = "low"             # < 5分钟
    MEDIUM = "medium"       # 5-15分钟
    HIGH = "high"           # 15-30分钟
    CRITICAL = "critical"   # > 30分钟


@dataclass
class IdlePeriod:
    """空置时段"""
    start_time: float
    end_time: Optional[float]
    duration_seconds: int
    severity: str
    reason: str
    suggested_task: str


@dataclass
class Task:
    """任务"""
    task_id: str
    name: str
    priority: int  # 1-5, 1最高
    estimated_minutes: int
    status: str
    assigned_at: Optional[str]
    started_at: Optional[str]
    completed_at: Optional[str]
    source: str
    auto_assignable: bool
    created_at: str = ""


@dataclass
class UtilizationStats:
    """利用率统计"""
    date: str
    total_minutes: int
    active_minutes: int
    idle_minutes: int
    utilization_rate: float
    tasks_completed: int
    tasks_created: int
    idle_periods: List[IdlePeriod]


class ZeroIdleEnforcer:
    """零空置执行器"""
    
    def __init__(self, data_dir: Optional[str] = None):
        """初始化"""
        self.data_dir = Path(data_dir) if data_dir else Path(__file__).parent / "data"
        self.data_dir.mkdir(exist_ok=True)
        
        self.tasks_file = self.data_dir / "tasks.json"
        self.stats_file = self.data_dir / "utilization_stats.json"
        self.config_file = self.data_dir / "config.json"
        
        self.config = self._load_config()
        self.tasks: List[Task] = self._load_tasks()
        self.current_task: Optional[Task] = None
        self.idle_start: Optional[float] = None
        
        # 监控状态
        self.is_monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.idle_threshold_seconds = self.config.get('idle_threshold_seconds', 300)  # 5分钟
        
        # 回调
        self.on_idle_detected: Optional[Callable] = None
        self.on_task_assigned: Optional[Callable] = None
    
    def _load_config(self) -> Dict:
        """加载配置"""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return {
            'idle_threshold_seconds': 300,  # 5分钟
            'auto_assign': True,
            'suggest_tasks': True,
            'track_utilization': True
        }
    
    def _load_tasks(self) -> List[Task]:
        """加载任务列表"""
        if self.tasks_file.exists():
            with open(self.tasks_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [Task(**item) for item in data]
        return []
    
    def _save_tasks(self):
        """保存任务列表"""
        with open(self.tasks_file, 'w', encoding='utf-8') as f:
            data = [self._task_to_dict(t) for t in self.tasks]
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _task_to_dict(self, task: Task) -> Dict:
        """转换任务为字典"""
        return {
            'task_id': task.task_id,
            'name': task.name,
            'priority': task.priority,
            'estimated_minutes': task.estimated_minutes,
            'status': task.status,
            'assigned_at': task.assigned_at,
            'started_at': task.started_at,
            'completed_at': task.completed_at,
            'source': task.source,
            'auto_assignable': task.auto_assignable,
            'created_at': task.created_at
        }
    
    def create_task(self, name: str, priority: int = 3,
                   estimated_minutes: int = 30,
                   source: str = "manual",
                   auto_assignable: bool = True) -> Task:
        """创建任务"""
        task_id = f"TASK-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        now = datetime.now().isoformat()
        
        task = Task(
            task_id=task_id,
            name=name,
            priority=priority,
            estimated_minutes=estimated_minutes,
            status=TaskStatus.IDLE.value,
            assigned_at=None,
            started_at=None,
            completed_at=None,
            source=source,
            auto_assignable=auto_assignable,
            created_at=now
        )
        
        self.tasks.append(task)
        self._save_tasks()
        
        return task
    
    def assign_task(self, task_id: str) -> Optional[Task]:
        """分配任务"""
        task = next((t for t in self.tasks if t.task_id == task_id), None)
        if not task:
            return None
        
        # 更新当前任务
        if self.current_task:
            self.current_task.status = TaskStatus.IDLE.value
        
        task.status = TaskStatus.ASSIGNED.value
        task.assigned_at = datetime.now().isoformat()
        self.current_task = task
        
        self._save_tasks()
        
        # 重置空置计时
        self.idle_start = None
        
        if self.on_task_assigned:
            self.on_task_assigned(task)
        
        return task
    
    def start_task(self, task_id: str) -> Optional[Task]:
        """开始任务"""
        task = next((t for t in self.tasks if t.task_id == task_id), None)
        if not task:
            return None
        
        task.status = TaskStatus.IN_PROGRESS.value
        task.started_at = datetime.now().isoformat()
        self.current_task = task
        
        self._save_tasks()
        
        # 重置空置计时
        self.idle_start = None
        
        return task
    
    def complete_task(self, task_id: str) -> Optional[Task]:
        """完成任务"""
        task = next((t for t in self.tasks if t.task_id == task_id), None)
        if not task:
            return None
        
        task.status = TaskStatus.COMPLETED.value
        task.completed_at = datetime.now().isoformat()
        
        if self.current_task and self.current_task.task_id == task_id:
            self.current_task = None
            self.idle_start = time.time()
        
        self._save_tasks()
        
        return task
    
    def mark_idle(self, reason: str = "任务完成"):
        """标记空闲"""
        self.idle_start = time.time()
    
    def check_idle(self) -> Optional[IdlePeriod]:
        """检查空置状态"""
        if not self.idle_start:
            return None
        
        idle_duration = int(time.time() - self.idle_start)
        
        # 确定严重程度
        if idle_duration < 300:
            severity = IdleSeverity.LOW.value
        elif idle_duration < 900:
            severity = IdleSeverity.MEDIUM.value
        elif idle_duration < 1800:
            severity = IdleSeverity.HIGH.value
        else:
            severity = IdleSeverity.CRITICAL.value
        
        # 获取建议任务
        suggested = self._suggest_task()
        suggested_name = suggested.name if suggested else "暂无建议"
        
        return IdlePeriod(
            start_time=self.idle_start,
            end_time=None,
            duration_seconds=idle_duration,
            severity=severity,
            reason="当前无活动任务",
            suggested_task=suggested_name
        )
    
    def _suggest_task(self) -> Optional[Task]:
        """建议任务"""
        # 优先选择已分配但未开始的任务
        assigned = [t for t in self.tasks if t.status == TaskStatus.ASSIGNED.value]
        if assigned:
            return min(assigned, key=lambda t: t.priority)
        
        # 选择空闲的可自动分配任务
        idle_tasks = [t for t in self.tasks
                     if t.status == TaskStatus.IDLE.value and t.auto_assignable]
        if idle_tasks:
            return min(idle_tasks, key=lambda t: t.priority)
        
        return None
    
    def auto_assign_next(self) -> Optional[Task]:
        """自动分配下一个任务"""
        if not self.config.get('auto_assign', True):
            return None
        
        suggested = self._suggest_task()
        if suggested:
            return self.assign_task(suggested.task_id)
        
        return None
    
    def start_monitoring(self):
        """开始监控"""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        
        def monitor_loop():
            while self.is_monitoring:
                time.sleep(10)  # 每10秒检查一次
                
                if self.idle_start:
                    idle_period = self.check_idle()
                    if idle_period:
                        duration = idle_period.duration_seconds
                        
                        # 触发空置回调
                        if self.on_idle_detected:
                            self.on_idle_detected(idle_period)
                        
                        # 自动分配
                        if duration >= self.idle_threshold_seconds:
                            if self.config.get('auto_assign', True):
                                self.auto_assign_next()
        
        self.monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """停止监控"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)
    
    def get_tasks_by_status(self, status: str) -> List[Task]:
        """按状态获取任务"""
        return [t for t in self.tasks if t.status == status]
    
    def get_today_stats(self) -> Dict:
        """获取今日统计"""
        today = datetime.now().strftime('%Y-%m-%d')

        today_tasks = [
            t for t in self.tasks
            if (t.created_at and t.created_at.startswith(today)) or
               (t.assigned_at and t.assigned_at.startswith(today))
        ]

        completed = [t for t in today_tasks if t.status == TaskStatus.COMPLETED.value]
        in_progress = [t for t in today_tasks if t.status == TaskStatus.IN_PROGRESS.value]

        return {
            'date': today,
            'total_tasks': len(today_tasks),
            'completed': len(completed),
            'in_progress': len(in_progress),
            'idle': len(today_tasks) - len(completed) - len(in_progress),
            'current_task': self.current_task.name if self.current_task else None
        }
    
    def calculate_utilization(self, date: Optional[str] = None) -> UtilizationStats:
        """计算利用率"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        # 简化计算：基于任务完成情况
        day_tasks = [
            t for t in self.tasks
            if (t.assigned_at and t.assigned_at.startswith(date)) or
               (t.created_at and t.created_at.startswith(date))
        ]
        
        # 计算工作时间 (假设8小时)
        total_minutes = 8 * 60
        
        # 估算活跃时间
        active_minutes = sum(
            t.estimated_minutes for t in day_tasks
            if t.status == TaskStatus.COMPLETED.value
        )
        active_minutes += sum(
            t.estimated_minutes // 2 for t in day_tasks
            if t.status == TaskStatus.IN_PROGRESS.value
        )
        
        # 限制在总时间内
        active_minutes = min(active_minutes, total_minutes)
        idle_minutes = total_minutes - active_minutes
        utilization_rate = active_minutes / total_minutes if total_minutes > 0 else 0
        
        completed = [t for t in day_tasks if t.status == TaskStatus.COMPLETED.value]
        
        return UtilizationStats(
            date=date,
            total_minutes=total_minutes,
            active_minutes=active_minutes,
            idle_minutes=idle_minutes,
            utilization_rate=utilization_rate,
            tasks_completed=len(completed),
            tasks_created=len(day_tasks),
            idle_periods=[]
        )
    
    def export_report(self, stats: UtilizationStats, format: str = "json") -> str:
        """导出报告"""
        if format == "json":
            return json.dumps(stats.__dict__, ensure_ascii=False, indent=2, default=str)
        elif format == "markdown":
            return self._format_markdown(stats)
        return ""
    
    def _format_markdown(self, stats: UtilizationStats) -> str:
        """格式化为Markdown"""
        utilization_color = "🟢" if stats.utilization_rate >= 0.8 else \
                          "🟡" if stats.utilization_rate >= 0.6 else \
                          "🟠" if stats.utilization_rate >= 0.4 else "🔴"
        
        lines = [
            f"# 零空置执行报告",
            "",
            f"**日期**: {stats.date}",
            f"**时间利用率**: {utilization_color} {stats.utilization_rate:.1%}",
            "",
            "---",
            "",
            "## ⏱️ 时间统计",
            "",
            f"- **总时间**: {stats.total_minutes} 分钟",
            f"- **活跃时间**: {stats.active_minutes} 分钟",
            f"- **空置时间**: {stats.idle_minutes} 分钟",
            "",
            "## 📋 任务统计",
            "",
            f"- **创建任务**: {stats.tasks_created}",
            f"- **完成任务**: {stats.tasks_completed}",
            ""
        ]
        
        if stats.idle_periods:
            lines.extend([
                "",
                "## ⚠️ 空置时段",
                ""
            ])
            for period in stats.idle_periods:
                duration_mins = period.duration_seconds // 60
                lines.append(f"- **{duration_mins}分钟** - {period.reason}")
                lines.append(f"  建议: {period.suggested_task}")
        
        return '\n'.join(lines)


def main():
    """主入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Zero Idle Enforcer - 零空置执行器')
    parser.add_argument('--create', nargs='+', metavar='NAME',
                       help='创建任务')
    parser.add_argument('--priority', type=int, default=3,
                       help='任务优先级 (1-5)')
    parser.add_argument('--estimate', type=int, default=30,
                       help='预计耗时(分钟)')
    parser.add_argument('--assign', metavar='TASK_ID',
                       help='分配任务')
    parser.add_argument('--start', metavar='TASK_ID',
                       help='开始任务')
    parser.add_argument('--complete', metavar='TASK_ID',
                       help='完成任务')
    parser.add_argument('--list', action='store_true',
                       help='列出任务')
    parser.add_argument('--status', action='store_true',
                       help='查看状态')
    parser.add_argument('--report', action='store_true',
                       help='生成报告')
    parser.add_argument('--monitor', action='store_true',
                       help='启动监控')
    parser.add_argument('--data-dir', help='数据目录')
    
    args = parser.parse_args()
    
    try:
        enforcer = ZeroIdleEnforcer(args.data_dir)
        
        if args.create:
            name = ' '.join(args.create)
            task = enforcer.create_task(name, args.priority, args.estimate)
            print(f"✅ 任务已创建: {task.task_id}")
            print(f"   名称: {task.name}")
            print(f"   优先级: {task.priority}")
            print(f"   预计: {task.estimated_minutes}分钟")
        
        elif args.assign:
            task = enforcer.assign_task(args.assign)
            if task:
                print(f"✅ 已分配任务: {task.name}")
            else:
                print(f"❌ 未找到任务: {args.assign}")
        
        elif args.start:
            task = enforcer.start_task(args.start)
            if task:
                print(f"✅ 已开始任务: {task.name}")
            else:
                print(f"❌ 未找到任务: {args.start}")
        
        elif args.complete:
            task = enforcer.complete_task(args.complete)
            if task:
                print(f"✅ 已完成任务: {task.name}")
            else:
                print(f"❌ 未找到任务: {args.complete}")
        
        elif args.list:
            tasks = enforcer.tasks
            if not tasks:
                print("暂无任务")
            else:
                print(f"共 {len(tasks)} 个任务:")
                print("-" * 60)
                for t in tasks[:20]:  # 只显示前20个
                    status_icon = {
                        TaskStatus.IDLE.value: "⏸️",
                        TaskStatus.ASSIGNED.value: "📋",
                        TaskStatus.IN_PROGRESS.value: "▶️",
                        TaskStatus.COMPLETED.value: "✅"
                    }.get(t.status, "⚪")
                    print(f"{status_icon} [{t.task_id}] {t.name} ({t.status})")
        
        elif args.status:
            stats = enforcer.get_today_stats()
            print("=" * 50)
            print("零空置执行器 - 今日状态")
            print("=" * 50)
            print(f"日期: {stats['date']}")
            print(f"总任务: {stats['total_tasks']}")
            print(f"已完成: {stats['completed']}")
            print(f"进行中: {stats['in_progress']}")
            if stats['current_task']:
                print(f"当前任务: {stats['current_task']}")
            print("=" * 50)
        
        elif args.report:
            stats = enforcer.calculate_utilization()
            output = enforcer.export_report(stats, "markdown")
            print(output)
        
        elif args.monitor:
            print("🚀 启动零空置监控...")
            print("按 Ctrl+C 停止")
            
            def on_idle(period):
                mins = period.duration_seconds // 60
                print(f"\n⚠️ 检测到空置: {mins}分钟 - {period.suggested_task}")
            
            def on_assign(task):
                print(f"\n📋 自动分配任务: {task.name}")
            
            enforcer.on_idle_detected = on_idle
            enforcer.on_task_assigned = on_assign
            enforcer.start_monitoring()
            
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n\n🛑 停止监控")
                enforcer.stop_monitoring()
        
        else:
            # 默认显示状态
            stats = enforcer.get_today_stats()
            print(f"今日任务: {stats['completed']}/{stats['total_tasks']} 完成")
            if stats['current_task']:
                print(f"当前: {stats['current_task']}")
        
        return 0
        
    except Exception as e:
        print(f"❌ 错误: {e}", file=__import__('sys').stderr)
        return 1


if __name__ == '__main__':
    import sys
    sys.exit(main())
