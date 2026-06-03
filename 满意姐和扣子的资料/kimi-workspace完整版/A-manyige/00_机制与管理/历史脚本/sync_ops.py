#!/usr/bin/env python3
"""
运营文档同步脚本
从core/运营体系.yaml生成Working层运营文档
"""

import yaml
import os
from datetime import datetime

def sync_ops():
    # 读取Core定义
    with open('core/运营体系.yaml', 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    metadata = data.get('metadata', {})
    operations = data.get('operations', {})
    
    # 确保输出目录存在
    os.makedirs('working/operations', exist_ok=True)
    
    # 生成30天提升计划文档
    team_enhancement = operations.get('team_enhancement_30d', {})
    
    content = f"""# {team_enhancement.get('name', '')}

> 状态: {team_enhancement.get('status', '')} | 周期: {team_enhancement.get('start_date', '')} ~ {team_enhancement.get('end_date', '')}
> 预算: {team_enhancement.get('budget', '')} | 总投入: {team_enhancement.get('total_investment', '')}
> > 本文件由core/运营体系.yaml自动生成，请勿手动修改

---

## 团队结构

| 层级 | 人数 | 目标 | 日均投入 | 总人时 |
|------|------|------|----------|--------|
| 核心层 | {team_enhancement.get('structure', {}).get('core_layer', {}).get('count', 0)} | {team_enhancement.get('structure', {}).get('core_layer', {}).get('target', '')} | {team_enhancement.get('structure', {}).get('core_layer', {}).get('daily_hours', 0)}h | {team_enhancement.get('structure', {}).get('core_layer', {}).get('total_hours', 0)} |
| 执行层 | {team_enhancement.get('structure', {}).get('execution_layer', {}).get('count', 0)} | {team_enhancement.get('structure', {}).get('execution_layer', {}).get('target', '')} | {team_enhancement.get('structure', {}).get('execution_layer', {}).get('daily_hours', 0)}h | {team_enhancement.get('structure', {}).get('execution_layer', {}).get('total_hours', 0)} |
| 储备层 | {team_enhancement.get('structure', {}).get('reserve_layer', {}).get('count', 0)} | {team_enhancement.get('structure', {}).get('reserve_layer', {}).get('target', '')} | {team_enhancement.get('structure', {}).get('reserve_layer', {}).get('daily_hours', 0)}h | {team_enhancement.get('structure', {}).get('reserve_layer', {}).get('total_hours', 0)} |

---

## 30天安排

"""
    
    schedule = team_enhancement.get('schedule', {})
    
    for week_key, week in schedule.items():
        content += f"### {week.get('name', '')} ({week.get('days', '')})\n\n"
        for activity in week.get('activities', []):
            content += f"- {activity}\n"
        content += "\n"
    
    # KPI
    content += "---\n\n## 关键指标\n\n"
    kpi = operations.get('kpi', {})
    content += "| 指标 | 当前 | 30天目标 | 提升 |\n"
    content += "|------|------|----------|------|\n"
    for metric_key, metric in kpi.items():
        content += f"| {metric_key} | {metric.get('current', '')} | {metric.get('target_30d', '')} | {metric.get('improvement', '')} |\n"
    
    content += "\n---\n\n*本文件由sync_ops.py自动生成*\n"
    
    # 写入文档
    with open('working/operations/team_enhancement_30d.md', 'w', encoding='utf-8') as f:
        f.write(content)
    
    # 生成里程碑文档
    milestones = operations.get('milestones', [])
    milestone_content = "# 满意解关键里程碑\n\n"
    for milestone in milestones:
        milestone_content += f"## {milestone.get('name', '')}\n"
        milestone_content += f"- **日期**: {milestone.get('date', '')}\n"
        milestone_content += f"- **状态**: {milestone.get('status', '')}\n"
        if milestone.get('days_remaining'):
            milestone_content += f"- **剩余天数**: {milestone['days_remaining']}\n"
        if milestone.get('current_count'):
            milestone_content += f"- **进度**: {milestone.get('current_count', 0)}/{milestone.get('target_count', 0)} ({milestone.get('completion_rate', '')})\n"
        milestone_content += "\n"
    
    with open('working/operations/milestones.md', 'w', encoding='utf-8') as f:
        f.write(milestone_content)
    
    print(f"✅ 运营文档同步完成")
    print(f"   - 提升计划: working/operations/team_enhancement_30d.md")
    print(f"   - 里程碑: working/operations/milestones.md")

if __name__ == '__main__':
    sync_ops()
