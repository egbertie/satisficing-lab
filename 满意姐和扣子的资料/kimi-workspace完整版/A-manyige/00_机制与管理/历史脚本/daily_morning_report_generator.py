#!/usr/bin/env python3
"""
每日晨报自动生成脚本 - Daily Morning Report Generator
版本: 1.0.0
作者: 满意解研究所
功能: 自动生成格式化的每日晨报，整合MEMORY.md、Skill状态、任务管理等信息
"""

import json
import re
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class Task:
    """任务数据类"""
    id: str
    title: str
    priority: str  # P0/P1/P2/P3
    status: str  # todo/doing/done/blocked
    due_date: Optional[str] = None
    category: str = "general"
    source: str = "memory"  # memory/skill/calendar


@dataclass
class SkillStatus:
    """Skill状态数据类"""
    name: str
    version: str
    priority: str
    status: str
    description: str


@dataclass
class MorningReport:
    """晨报数据类"""
    date: str
    weekday: str
    greeting: str
    focus_tasks: List[Task]  # 今日重点
    in_progress: List[Task]  # 进行中
    blocked_tasks: List[Task]  # 阻塞任务
    completed_count: int
    total_count: int
    completion_rate: float
    time_suggestions: List[Dict[str, str]]
    long_term_reminder: str
    stats: Dict[str, Any]


class Config:
    """配置管理器"""
    
    DEFAULT_CONFIG = {
        "workspace_path": "/root/.openclaw/workspace",
        "output_path": "/root/.openclaw/workspace/A满意哥专属文件夹/01_🔥今日重点",
        "long_term_goals": {
            "官宣日期": "2026-03-25",
            "里程碑提醒": "距3/25官宣还有{}天"
        },
        "time_allocation_rules": {
            "P0任务数>=3": {"深度工作": "4小时", "沟通协作": "1小时", "学习研究": "0.5小时"},
            "P0任务数=2": {"深度工作": "3小时", "沟通协作": "1小时", "学习研究": "1小时"},
            "P0任务数=1": {"深度工作": "2小时", "沟通协作": "1.5小时", "学习研究": "1.5小时"},
            "P0任务数=0": {"深度工作": "1小时", "沟通协作": "2小时", "学习研究": "2小时"}
        },
        "greetings": {
            "周一": "新的一周，元气满满！",
            "周二": "保持节奏，稳步推进。",
            "周三": "周中冲刺，再接再厉！",
            "周四": "胜利在望，坚持就是胜利。",
            "周五": "收官之日，完美结束本周。",
            "周六": "周末时光，充电蓄能。",
            "周日": "休整之余，规划下周。"
        },
        "weekday_names": {
            "Monday": "周一",
            "Tuesday": "周二", 
            "Wednesday": "周三",
            "Thursday": "周四",
            "Friday": "周五",
            "Saturday": "周六",
            "Sunday": "周日"
        },
        "priority_emojis": {
            "P0": "🔥",
            "P1": "⭐",
            "P2": "📌",
            "P3": "💭"
        },
        "status_emojis": {
            "todo": "⬜",
            "doing": "🔄",
            "done": "✅",
            "blocked": "🚫"
        },
        "task_patterns": {
            "todo": r"- \[ \] (.+)",
            "done": r"- \[x\] (.+)",
            "priority": r"(P\d).*:?\s*(.+)"
        }
    }
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or "/root/.openclaw/workspace/scripts/morning_report_config.json"
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """加载配置文件"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return {**self.DEFAULT_CONFIG, **json.load(f)}
            except Exception as e:
                print(f"[警告] 配置文件加载失败，使用默认配置: {e}")
        return self.DEFAULT_CONFIG
    
    def save_config(self):
        """保存配置到文件"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
    
    def get(self, key: str, default=None):
        """获取配置项"""
        return self.config.get(key, default)


class DataCollector:
    """数据收集器 - 从各数据源收集信息"""
    
    def __init__(self, config: Config):
        self.config = config
        self.workspace = Path(config.get("workspace_path"))
        self.memory_file = self.workspace / "MEMORY.md"
        self.skills_dir = self.workspace / "skills"
        self.memory_dir = self.workspace / "memory"
    
    def collect_tasks_from_memory(self) -> List[Task]:
        """从MEMORY.md收集待办事项"""
        tasks = []
        
        if not self.memory_file.exists():
            return tasks
        
        try:
            with open(self.memory_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 解析待办事项部分
            # 匹配 - [ ] 任务内容 或 - [x] 已完成任务
            todo_pattern = self.config.get("task_patterns")["todo"]
            done_pattern = self.config.get("task_patterns")["done"]
            priority_pattern = self.config.get("task_patterns")["priority"]
            
            # 收集待办任务
            for match in re.finditer(todo_pattern, content, re.MULTILINE):
                task_text = match.group(1).strip()
                priority = self._extract_priority(task_text)
                
                task = Task(
                    id=f"MEM-{len(tasks)+1:03d}",
                    title=self._clean_task_title(task_text),
                    priority=priority,
                    status="todo",
                    due_date=self._extract_due_date(task_text),
                    source="memory"
                )
                tasks.append(task)
            
            # 收集已完成任务（用于计算完成率）
            for match in re.finditer(done_pattern, content, re.MULTILINE):
                task_text = match.group(1).strip()
                priority = self._extract_priority(task_text)
                
                task = Task(
                    id=f"MEM-DONE-{len(tasks)+1:03d}",
                    title=self._clean_task_title(task_text),
                    priority=priority,
                    status="done",
                    source="memory"
                )
                tasks.append(task)
                
        except Exception as e:
            print(f"[警告] 读取MEMORY.md失败: {e}")
        
        return tasks
    
    def collect_tasks_from_daily_log(self, date: str) -> List[Task]:
        """从每日日志收集任务"""
        tasks = []
        log_file = self.memory_dir / f"{date}.md"
        
        if not log_file.exists():
            return tasks
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 解析当日任务
            todo_pattern = self.config.get("task_patterns")["todo"]
            done_pattern = self.config.get("task_patterns")["done"]
            
            for match in re.finditer(todo_pattern, content, re.MULTILINE):
                task_text = match.group(1).strip()
                priority = self._extract_priority(task_text)
                
                task = Task(
                    id=f"LOG-{len(tasks)+1:03d}",
                    title=self._clean_task_title(task_text),
                    priority=priority,
                    status="todo",
                    source="daily_log"
                )
                tasks.append(task)
            
            for match in re.finditer(done_pattern, content, re.MULTILINE):
                task_text = match.group(1).strip()
                priority = self._extract_priority(task_text)
                
                task = Task(
                    id=f"LOG-DONE-{len(tasks)+1:03d}",
                    title=self._clean_task_title(task_text),
                    priority=priority,
                    status="done",
                    source="daily_log"
                )
                tasks.append(task)
                
        except Exception as e:
            print(f"[警告] 读取日志文件失败: {e}")
        
        return tasks
    
    def collect_skill_status(self) -> List[SkillStatus]:
        """从skill.json收集Skill状态"""
        skills = []
        skill_json = self.workspace / "skill.json"
        
        if not skill_json.exists():
            return skills
        
        try:
            with open(skill_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            skill_data = data.get("skills", {})
            for name, info in skill_data.items():
                skill = SkillStatus(
                    name=name,
                    version=info.get("version", "unknown"),
                    priority=info.get("priority", "P2"),
                    status=info.get("status", "unknown"),
                    description=info.get("description", "")
                )
                skills.append(skill)
                
        except Exception as e:
            print(f"[警告] 读取skill.json失败: {e}")
        
        return skills
    
    def _extract_priority(self, text: str) -> str:
        """提取优先级"""
        priority_pattern = self.config.get("task_patterns")["priority"]
        match = re.search(priority_pattern, text)
        if match:
            return match.group(1)
        return "P2"  # 默认优先级
    
    def _clean_task_title(self, text: str) -> str:
        """清理任务标题"""
        # 移除优先级标记
        text = re.sub(r'^P\d\s*[:\-]?\s*', '', text)
        # 移除日期标记
        text = re.sub(r'\(\d{4}-\d{2}-\d{2}\)', '', text)
        return text.strip()
    
    def _extract_due_date(self, text: str) -> Optional[str]:
        """提取截止日期"""
        # 匹配 (2026-03-25) 格式
        match = re.search(r'\((\d{4}-\d{2}-\d{2})\)', text)
        if match:
            return match.group(1)
        # 匹配 今天/明天/本周 等
        if "今天" in text:
            return datetime.now().strftime("%Y-%m-%d")
        if "明天" in text:
            return (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        return None


class ReportGenerator:
    """报告生成器"""
    
    def __init__(self, config: Config):
        self.config = config
        self.collector = DataCollector(config)
    
    def generate_report(self, target_date: str = None) -> MorningReport:
        """生成晨报"""
        if target_date is None:
            target_date = datetime.now().strftime("%Y-%m-%d")
        
        # 收集数据
        memory_tasks = self.collector.collect_tasks_from_memory()
        daily_tasks = self.collector.collect_tasks_from_daily_log(target_date)
        skills = self.collector.collect_skill_status()
        
        # 合并并去重任务
        all_tasks = self._merge_tasks(memory_tasks + daily_tasks)
        
        # 计算统计
        stats = self._calculate_stats(all_tasks, skills)
        
        # 生成今日重点（P0/P1优先级，未完成的任务）
        focus_tasks = self._get_focus_tasks(all_tasks)
        
        # 进行中任务
        in_progress = [t for t in all_tasks if t.status == "doing"]
        
        # 阻塞任务
        blocked_tasks = [t for t in all_tasks if t.status == "blocked"]
        
        # 时间分配建议
        time_suggestions = self._generate_time_suggestions(focus_tasks)
        
        # 长期目标提醒
        long_term_reminder = self._generate_long_term_reminder()
        
        # 获取问候语
        weekday = self._get_weekday(target_date)
        greeting = self.config.get("greetings", {}).get(weekday, "新的一天，加油！")
        
        return MorningReport(
            date=target_date,
            weekday=weekday,
            greeting=greeting,
            focus_tasks=focus_tasks[:5],  # 最多5个
            in_progress=in_progress,
            blocked_tasks=blocked_tasks,
            completed_count=stats["completed_count"],
            total_count=stats["total_count"],
            completion_rate=stats["completion_rate"],
            time_suggestions=time_suggestions,
            long_term_reminder=long_term_reminder,
            stats=stats
        )
    
    def _merge_tasks(self, tasks: List[Task]) -> List[Task]:
        """合并并去重任务"""
        # 使用任务标题作为去重键
        seen = {}
        unique_tasks = []
        
        for task in tasks:
            key = task.title.lower()
            if key not in seen:
                seen[key] = task
                unique_tasks.append(task)
        
        return unique_tasks
    
    def _calculate_stats(self, tasks: List[Task], skills: List[SkillStatus]) -> Dict:
        """计算统计数据"""
        total = len([t for t in tasks if t.status != "done"]) + len([t for t in tasks if t.status == "done"])
        completed = len([t for t in tasks if t.status == "done"])
        
        # 本周完成率计算（基于最近7天）
        completion_rate = (completed / total * 100) if total > 0 else 0
        
        return {
            "total_count": total,
            "completed_count": completed,
            "completion_rate": round(completion_rate, 0),
            "p0_count": len([t for t in tasks if t.priority == "P0"]),
            "p1_count": len([t for t in tasks if t.priority == "P1"]),
            "blocked_count": len([t for t in tasks if t.status == "blocked"]),
            "active_skills": len([s for s in skills if s.status == "active"]),
            "total_skills": len(skills)
        }
    
    def _get_focus_tasks(self, tasks: List[Task]) -> List[Task]:
        """获取今日重点任务"""
        # 优先级：P0 > P1 > 其他
        # 状态：未完成的优先
        unfinished = [t for t in tasks if t.status != "done"]
        
        # 按优先级排序
        priority_order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
        sorted_tasks = sorted(unfinished, key=lambda t: priority_order.get(t.priority, 4))
        
        return sorted_tasks
    
    def _generate_time_suggestions(self, focus_tasks: List[Task]) -> List[Dict[str, str]]:
        """生成时间分配建议"""
        p0_count = len([t for t in focus_tasks if t.priority == "P0"])
        
        rules = self.config.get("time_allocation_rules", {})
        
        if p0_count >= 3:
            allocation = rules.get("P0任务数>=3", {})
        elif p0_count == 2:
            allocation = rules.get("P0任务数=2", {})
        elif p0_count == 1:
            allocation = rules.get("P0任务数=1", {})
        else:
            allocation = rules.get("P0任务数=0", {})
        
        suggestions = []
        for activity, duration in allocation.items():
            # 根据任务内容生成关联建议
            related_task = ""
            if "深度工作" in activity and focus_tasks:
                p0_tasks = [t for t in focus_tasks if t.priority == "P0"]
                if p0_tasks:
                    related_task = f"（{p0_tasks[0].title[:15]}...）"
            
            suggestions.append({
                "activity": activity,
                "duration": duration,
                "related": related_task
            })
        
        return suggestions
    
    def _generate_long_term_reminder(self) -> str:
        """生成长期目标提醒"""
        target_date_str = self.config.get("long_term_goals", {}).get("官宣日期", "2026-03-25")
        template = self.config.get("long_term_goals", {}).get("里程碑提醒", "距3/25官宣还有{}天")
        
        try:
            target_date = datetime.strptime(target_date_str, "%Y-%m-%d")
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            target_date = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
            days_remaining = (target_date - today).days
            
            if days_remaining > 0:
                return template.format(days_remaining)
            elif days_remaining == 0:
                return "🎉 今天是官宣日，一切准备就绪！"
            else:
                return f"官宣已完成{-days_remaining}天，继续向前！"
        except Exception as e:
            print(f"[调试] 长期提醒计算失败: {e}")
            return "保持长期主义，稳扎稳打。"
    
    def _get_weekday(self, date_str: str) -> str:
        """获取星期几"""
        date = datetime.strptime(date_str, "%Y-%m-%d")
        weekday_en = date.strftime("%A")
        return self.config.get("weekday_names", {}).get(weekday_en, weekday_en)
    
    def format_markdown(self, report: MorningReport) -> str:
        """格式化为Markdown"""
        lines = []
        
        # 标题
        lines.append(f"🌅 满意解晨报 · {report.date} {report.weekday}")
        lines.append("")
        
        # 问候语
        lines.append(f"*{report.greeting}*")
        lines.append("")
        
        # 今日重点
        lines.append("【今日重点】")
        if report.focus_tasks:
            for task in report.focus_tasks[:5]:  # 最多5个
                emoji = self.config.get("priority_emojis", {}).get(task.priority, "📌")
                lines.append(f"{emoji} {task.priority}: {task.title}")
        else:
            lines.append("🎯 暂无高优先级任务，适合处理积累事项或学习充电")
        lines.append("")
        
        # 进行中
        if report.in_progress:
            lines.append(f"【进行中】{len(report.in_progress)}项正常推进")
        else:
            lines.append("【进行中】0项")
        
        # 阻塞
        if report.blocked_tasks:
            lines.append(f"【阻塞】⚠️ {len(report.blocked_tasks)}项需要关注")
            for task in report.blocked_tasks:
                lines.append(f"  - {task.title}")
        else:
            lines.append("【阻塞】0项")
        
        # 完成率
        lines.append(f"【完成率】本周{int(report.completion_rate)}%")
        lines.append("")
        
        # Skill状态摘要
        if report.stats.get("total_skills", 0) > 0:
            lines.append(f"【系统状态】{report.stats['active_skills']}/{report.stats['total_skills']}个Skill活跃运行")
            lines.append("")
        
        # 时间建议
        lines.append("【时间建议】")
        for suggestion in report.time_suggestions:
            related = suggestion.get("related", "")
            lines.append(f"- {suggestion['activity']}：{suggestion['duration']}{related}")
        lines.append("")
        
        # 长期提醒
        lines.append(f"💡 长期提醒：{report.long_term_reminder}")
        
        # 页脚
        lines.append("")
        lines.append("---")
        lines.append(f"*满意解研究所 · 晨报生成时间：{datetime.now().strftime('%H:%M')}*")
        
        return "\n".join(lines)
    
    def save_report(self, report: MorningReport, output_path: str = None):
        """保存报告到文件"""
        if output_path is None:
            output_dir = Path(self.config.get("output_path"))
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / f"晨报_{report.date}.md"
        
        content = self.format_markdown(report)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return output_path


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="每日晨报生成器")
    parser.add_argument("--date", help="指定日期 (YYYY-MM-DD)", default=None)
    parser.add_argument("--output", "-o", help="输出文件路径", default=None)
    parser.add_argument("--config", "-c", help="配置文件路径", default=None)
    parser.add_argument("--save-config", action="store_true", help="保存默认配置")
    parser.add_argument("--print", "-p", action="store_true", help="打印到控制台")
    
    args = parser.parse_args()
    
    # 初始化配置
    config = Config(args.config)
    
    if args.save_config:
        config.save_config()
        print(f"[信息] 默认配置已保存到: {config.config_path}")
        return
    
    # 生成报告
    generator = ReportGenerator(config)
    report = generator.generate_report(args.date)
    
    # 格式化输出
    markdown_content = generator.format_markdown(report)
    
    # 保存到文件
    output_path = generator.save_report(report, args.output)
    print(f"[信息] 晨报已保存到: {output_path}")
    
    # 打印到控制台
    if args.print:
        print("\n" + "="*60)
        print(markdown_content)
        print("="*60)
    
    return report


if __name__ == "__main__":
    main()
