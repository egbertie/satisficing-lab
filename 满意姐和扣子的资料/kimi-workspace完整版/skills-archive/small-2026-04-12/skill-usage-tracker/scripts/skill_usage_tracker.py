#!/usr/bin/env python3
"""
skill-usage-tracker - Skill使用追踪器
真正实现版本

功能:
- 追踪Skill使用频率
- 检测手工操作绕过
- 生成使用率报告
- 强制使用提醒
- 习惯培养

作者: 满意妞 (蓝军监督)
版本: 1.0.0-real
日期: 2026-04-03
"""

import json
import os
import re
import time
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
import subprocess
import hashlib


class ActionType(Enum):
    """操作类型"""
    SKILL_USED = "skill_used"           # 使用Skill
    MANUAL_WORKAROUND = "manual"        # 手工操作（疑似绕过）
    DIRECT_EDIT = "direct_edit"         # 直接编辑文件


@dataclass
class UsageEvent:
    """使用事件"""
    timestamp: float
    action_type: str
    skill_name: Optional[str]
    command: str
    target_file: Optional[str]
    context: str
    success: bool


@dataclass
class WeeklyReport:
    """周使用报告"""
    week_start: str
    week_end: str
    total_events: int
    skill_events: int
    manual_events: int
    skill_usage_rate: float
    top_skills: List[tuple]
    bypass_alerts: List[str]
    recommendations: List[str]


class SkillUsageTracker:
    """Skill使用追踪器"""
    
    # 定义所有已实现的Skill
    REGISTERED_SKILLS = [
        "ai-meeting-notes",
        "cost-redlines",
        "data-quality-auditor",
        "info-quality-guardian",
        "quality-assessment",
        "quality-assurance",
        "quality-closure",
        "quality-gate-system",
        "token-throttle-controller",
        "token-weekly-monitor",
        "zero-idle-enforcer"
    ]
    
    # 疑似绕过行为的模式
    BYPASS_PATTERNS = [
        (r"vim?\s+.+\.py", "直接使用vim编辑Python文件"),
        (r"nano\s+.+\.py", "直接使用nano编辑Python文件"),
        (r"cat\s+>.+\.py", "直接创建Python文件"),
        (r"echo\s+.+\s+>.+\.py", "使用echo创建Python文件"),
        (r"cp\s+.+\.py", "直接复制Python文件"),
        (r"touch\s+.+\.py", "直接创建空Python文件"),
    ]
    
    def __init__(self, data_dir: Optional[str] = None):
        """初始化"""
        self.data_dir = Path(data_dir) if data_dir else Path(__file__).parent.parent / "data"
        self.data_dir.mkdir(exist_ok=True)
        
        self.usage_file = self.data_dir / "skill_usage.json"
        self.config_file = self.data_dir / "tracker_config.json"
        
        self.config = self._load_config()
        self.events: List[UsageEvent] = self._load_events()
        
        # 目标使用率
        self.target_usage_rate = self.config.get('target_usage_rate', 0.8)
        self.alert_threshold = self.config.get('alert_threshold', 3)  # 连续3次手工操作预警
    
    def _load_config(self) -> Dict:
        """加载配置"""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            'target_usage_rate': 0.8,
            'alert_threshold': 3,
            'track_manual_edits': True,
            'auto_remind': True
        }
    
    def _save_config(self):
        """保存配置"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
    
    def _load_events(self) -> List[UsageEvent]:
        """加载事件历史"""
        if self.usage_file.exists():
            with open(self.usage_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [UsageEvent(**item) for item in data]
        return []
    
    def _save_events(self):
        """保存事件"""
        with open(self.usage_file, 'w', encoding='utf-8') as f:
            data = [self._event_to_dict(e) for e in self.events]
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _event_to_dict(self, event: UsageEvent) -> Dict:
        """转换事件为字典"""
        return {
            'timestamp': event.timestamp,
            'action_type': event.action_type,
            'skill_name': event.skill_name,
            'command': event.command,
            'target_file': event.target_file,
            'context': event.context,
            'success': event.success
        }
    
    def record_skill_usage(self, skill_name: str, command: str,
                          target_file: Optional[str] = None,
                          context: str = "", success: bool = True):
        """记录Skill使用"""
        event = UsageEvent(
            timestamp=time.time(),
            action_type=ActionType.SKILL_USED.value,
            skill_name=skill_name,
            command=command,
            target_file=target_file,
            context=context,
            success=success
        )
        self.events.append(event)
        self._save_events()
    
    def record_manual_action(self, command: str, target_file: Optional[str] = None,
                            context: str = ""):
        """记录手工操作"""
        # 检测是否是绕过行为
        bypass_detected = self._detect_bypass(command)
        
        event = UsageEvent(
            timestamp=time.time(),
            action_type=ActionType.MANUAL_WORKAROUND.value if bypass_detected else ActionType.DIRECT_EDIT.value,
            skill_name=None,
            command=command,
            target_file=target_file,
            context=context,
            success=True
        )
        self.events.append(event)
        self._save_events()
        
        # 如果检测到绕过，给出提醒
        if bypass_detected and self.config.get('auto_remind', True):
            return self._generate_bypass_reminder(command, bypass_detected)
        return None
    
    def _detect_bypass(self, command: str) -> Optional[str]:
        """检测是否是绕过行为"""
        for pattern, description in self.BYPASS_PATTERNS:
            if re.search(pattern, command):
                return description
        return None
    
    def _generate_bypass_reminder(self, command: str, bypass_type: str) -> str:
        """生成绕过提醒"""
        # 找到可能相关的Skill
        suggested_skills = self._suggest_skills_for_command(command)
        
        reminder = f"""
🟡 检测到疑似Skill绕过行为
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
操作: {bypass_type}
命令: {command}

💡 建议改用Skill：
"""
        for skill in suggested_skills:
            reminder += f"  • {skill}\n"
        
        reminder += """
💡 为什么要用Skill？
  • 确保输出符合质量标准
  • 自动记录和追踪
  • 可复用和沉淀知识
  • 减少重复劳动

使用 skill-usage-tracker --report 查看使用率
"""
        return reminder
    
    def _suggest_skills_for_command(self, command: str) -> List[str]:
        """根据命令建议Skill"""
        suggestions = []
        
        if '.py' in command:
            suggestions.extend([
                "quality-assessment (评估代码质量)",
                "quality-gate-system (质量门禁检查)",
                "data-quality-auditor (数据质量审计)"
            ])
        
        if 'test' in command.lower():
            suggestions.append("quality-assurance (质量保证)")
        
        if 'cost' in command.lower() or 'budget' in command.lower():
            suggestions.append("cost-redlines (成本红线)")
        
        if 'token' in command.lower():
            suggestions.extend([
                "token-throttle-controller (Token节流)",
                "token-weekly-monitor (Token周度监控)"
            ])
        
        if 'task' in command.lower() or 'todo' in command.lower():
            suggestions.append("zero-idle-enforcer (零空置执行)")
        
        return suggestions if suggestions else ["查看可用Skill: ls skills/"]
    
    def get_usage_stats(self, days: int = 7) -> Dict:
        """获取使用统计"""
        cutoff = time.time() - (days * 24 * 3600)
        recent_events = [e for e in self.events if e.timestamp > cutoff]
        
        skill_events = [e for e in recent_events if e.action_type == ActionType.SKILL_USED.value]
        manual_events = [e for e in recent_events if e.action_type in 
                        [ActionType.MANUAL_WORKAROUND.value, ActionType.DIRECT_EDIT.value]]
        
        total = len(skill_events) + len(manual_events)
        skill_rate = len(skill_events) / total if total > 0 else 0
        
        # 统计各Skill使用次数
        skill_counts = {}
        for e in skill_events:
            name = e.skill_name or "unknown"
            skill_counts[name] = skill_counts.get(name, 0) + 1
        
        top_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # 检测连续绕过
        bypass_alerts = self._detect_continuous_bypass(recent_events)
        
        return {
            'period_days': days,
            'total_events': total,
            'skill_events': len(skill_events),
            'manual_events': len(manual_events),
            'skill_usage_rate': skill_rate,
            'target_rate': self.target_usage_rate,
            'meets_target': skill_rate >= self.target_usage_rate,
            'top_skills': top_skills,
            'bypass_alerts': bypass_alerts,
            'unused_skills': list(set(self.REGISTERED_SKILLS) - set(skill_counts.keys()))
        }
    
    def _detect_continuous_bypass(self, events: List[UsageEvent]) -> List[str]:
        """检测连续绕过行为"""
        alerts = []
        consecutive_manual = 0
        
        for e in sorted(events, key=lambda x: x.timestamp):
            if e.action_type == ActionType.MANUAL_WORKAROUND.value:
                consecutive_manual += 1
                if consecutive_manual >= self.alert_threshold:
                    alerts.append(f"连续{consecutive_manual}次手工操作，建议检查Skill使用习惯")
            else:
                consecutive_manual = 0
        
        return alerts
    
    def generate_weekly_report(self) -> WeeklyReport:
        """生成周报告"""
        now = datetime.now()
        week_start = (now - timedelta(days=now.weekday())).strftime('%Y-%m-%d')
        week_end = now.strftime('%Y-%m-%d')
        
        stats = self.get_usage_stats(days=7)
        
        recommendations = []
        if not stats['meets_target']:
            recommendations.append(f"⚠️ Skill使用率{stats['skill_usage_rate']:.1%}，低于目标{stats['target_rate']:.1%}")
        
        if stats['unused_skills']:
            recommendations.append(f"💡 以下Skill从未使用: {', '.join(stats['unused_skills'][:3])}")
        
        if stats['bypass_alerts']:
            recommendations.append("🔴 检测到多次Skill绕过行为，请检查工作习惯")
        
        return WeeklyReport(
            week_start=week_start,
            week_end=week_end,
            total_events=stats['total_events'],
            skill_events=stats['skill_events'],
            manual_events=stats['manual_events'],
            skill_usage_rate=stats['skill_usage_rate'],
            top_skills=stats['top_skills'],
            bypass_alerts=stats['bypass_alerts'],
            recommendations=recommendations
        )
    
    def monitor_shell_command(self, command: str) -> Optional[str]:
        """监控shell命令，检测绕过"""
        # 检查是否是Skill使用
        for skill in self.REGISTERED_SKILLS:
            if skill in command:
                self.record_skill_usage(skill, command)
                return None
        
        # 检查是否是手工操作
        if self.config.get('track_manual_edits', True):
            return self.record_manual_action(command)
        
        return None
    
    def set_target_rate(self, rate: float):
        """设置目标使用率"""
        self.config['target_usage_rate'] = max(0, min(1, rate))
        self._save_config()
    
    def export_report(self, report: WeeklyReport, format: str = "markdown") -> str:
        """导出报告"""
        if format == "json":
            return json.dumps(report.__dict__, ensure_ascii=False, indent=2)
        elif format == "markdown":
            return self._format_markdown(report)
        return ""
    
    def _format_markdown(self, report: WeeklyReport) -> str:
        """格式化为Markdown"""
        rate_color = "🟢" if report.skill_usage_rate >= 0.8 else \
                    "🟡" if report.skill_usage_rate >= 0.6 else "🔴"
        
        lines = [
            f"# Skill使用周报",
            "",
            f"**统计周期**: {report.week_start} ~ {report.week_end}",
            f"**Skill使用率**: {rate_color} {report.skill_usage_rate:.1%}",
            "",
            "---",
            "",
            "## 📊 使用统计",
            "",
            f"- **总操作数**: {report.total_events}",
            f"- **Skill使用**: {report.skill_events}",
            f"- **手工操作**: {report.manual_events}",
            "",
            "## 🏆 常用Skill TOP5",
            ""
        ]
        
        for i, (skill, count) in enumerate(report.top_skills, 1):
            lines.append(f"{i}. **{skill}**: {count}次")
        
        if report.bypass_alerts:
            lines.extend([
                "",
                "## ⚠️ 绕过行为预警",
                ""
            ])
            for alert in report.bypass_alerts:
                lines.append(f"- {alert}")
        
        if report.recommendations:
            lines.extend([
                "",
                "## 💡 建议",
                ""
            ])
            for rec in report.recommendations:
                lines.append(f"- {rec}")
        
        return '\n'.join(lines)


def main():
    """主入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Skill Usage Tracker - Skill使用追踪器')
    parser.add_argument('--record-skill', nargs=2, metavar=('SKILL', 'COMMAND'),
                       help='记录Skill使用')
    parser.add_argument('--record-manual', metavar='COMMAND',
                       help='记录手工操作')
    parser.add_argument('--stats', action='store_true',
                       help='查看使用统计')
    parser.add_argument('--report', action='store_true',
                       help='生成周报')
    parser.add_argument('--days', type=int, default=7,
                       help='统计天数')
    parser.add_argument('--target', type=float,
                       help='设置目标使用率 (0-1)')
    parser.add_argument('--monitor', metavar='COMMAND',
                       help='监控命令')
    parser.add_argument('--format', choices=['json', 'markdown'], default='markdown',
                       help='报告格式')
    parser.add_argument('--data-dir', help='数据目录')
    
    args = parser.parse_args()
    
    try:
        tracker = SkillUsageTracker(args.data_dir)
        
        if args.record_skill:
            tracker.record_skill_usage(args.record_skill[0], args.record_skill[1])
            print(f"✅ 已记录Skill使用: {args.record_skill[0]}")
        
        elif args.record_manual:
            reminder = tracker.record_manual_action(args.record_manual)
            if reminder:
                print(reminder)
            else:
                print("✅ 已记录手工操作")
        
        elif args.target is not None:
            tracker.set_target_rate(args.target)
            print(f"✅ 目标使用率已设置为: {args.target:.0%}")
        
        elif args.monitor:
            reminder = tracker.monitor_shell_command(args.monitor)
            if reminder:
                print(reminder)
        
        elif args.stats:
            stats = tracker.get_usage_stats(args.days)
            print("=" * 50)
            print(f"Skill使用统计（近{args.days}天）")
            print("=" * 50)
            print(f"总操作: {stats['total_events']}")
            print(f"Skill使用: {stats['skill_events']} ({stats['skill_usage_rate']:.1%})")
            print(f"手工操作: {stats['manual_events']}")
            print(f"目标: {stats['target_rate']:.1%} {'✅' if stats['meets_target'] else '⚠️'}")
            print("=" * 50)
            
            if stats['top_skills']:
                print("\n常用Skill:")
                for skill, count in stats['top_skills']:
                    print(f"  • {skill}: {count}次")
            
            if stats['unused_skills']:
                print(f"\n未使用的Skill: {', '.join(stats['unused_skills'])}")
        
        elif args.report:
            report = tracker.generate_weekly_report()
            output = tracker.export_report(report, args.format)
            print(output)
        
        else:
            # 默认显示统计
            stats = tracker.get_usage_stats(7)
            print(f"Skill使用率: {stats['skill_usage_rate']:.1%} (目标: {stats['target_rate']:.1%})")
            if not stats['meets_target']:
                print(f"⚠️ 低于目标，建议增加Skill使用")
        
        return 0
        
    except Exception as e:
        print(f"❌ 错误: {e}", file=__import__('sys').stderr)
        return 1


if __name__ == '__main__':
    import sys
    sys.exit(main())
