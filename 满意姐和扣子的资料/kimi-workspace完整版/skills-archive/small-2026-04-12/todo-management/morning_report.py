#!/usr/bin/env python3
"""
每日晨报生成器
生成包含日程、TODO、提醒的晨报
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

# 添加TODO管理器路径
sys.path.insert(0, '/root/.openclaw/workspace/skills/todo-management')
from todo_manager import todo_manager


def get_calendar_events():
    """获取今日日程（预留接口）"""
    # TODO: 集成飞书日历API
    return []


def generate_morning_report():
    """生成晨报"""
    now = datetime.now()
    today_str = now.strftime('%Y年%m月%d日')
    weekday = ['一', '二', '三', '四', '五', '六', '日'][now.weekday()]
    
    # 获取TODO信息
    todos = todo_manager.list()
    today_due = todo_manager.get_today_due()
    overdue = todo_manager.get_overdue()
    
    # 统计
    p0_count = sum(1 for t in todos if t.get('priority') == 'P0' and t.get('status') not in ['completed', 'cancelled'])
    p1_count = sum(1 for t in todos if t.get('priority') == 'P1' and t.get('status') not in ['completed', 'cancelled'])
    
    # 构建晨报
    report = f"""🌅 早安，Egbertie

📅 {today_str} 星期{weekday}
━━━━━━━━━━━━━━━━━━━━

🔥 今日重点
"""
    
    # 今日到期任务
    if today_due:
        report += "\n⏰ 今日到期:\n"
        for todo in sorted(today_due, key=lambda x: x.get('priority', 'P3')):
            report += f"   [{todo['priority']}] {todo['title']}\n"
    else:
        report += "\n✨ 今日暂无到期任务\n"
    
    # 逾期任务提醒
    if overdue:
        report += f"\n⚠️ 逾期任务 ({len(overdue)}个):\n"
        for todo in overdue[:3]:  # 最多显示3个
            report += f"   [{todo['priority']}] {todo['title']}\n"
        if len(overdue) > 3:
            report += f"   ... 还有 {len(overdue) - 3} 个\n"
    
    # 优先级汇总
    report += f"""
📊 任务概览
   P0: {p0_count}个 | P1: {p1_count}个 | 总计: {len(todos)}个活跃

━━━━━━━━━━━━━━━━━━━━
🦉 LIU  ⚒️ SIMON  🛡️ GUANYIN  📜 CONFUCIUS  🔥 HUINENG
━━━━━━━━━━━━━━━━━━━━
"""
    
    return report


def save_and_output_report():
    """生成并输出晨报"""
    report = generate_morning_report()
    
    # 保存到文件
    report_dir = Path("/root/.openclaw/workspace/data/daily-reports")
    report_dir.mkdir(parents=True, exist_ok=True)
    
    today = datetime.now().strftime('%Y%m%d')
    report_file = report_dir / f"morning-report-{today}.txt"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    # 同时输出到控制台
    print(report)
    
    return report


if __name__ == "__main__":
    save_and_output_report()
