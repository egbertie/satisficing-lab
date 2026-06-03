#!/usr/bin/env python3
"""
每日任务看板生成脚本 V2.0
准确识别所有任务状态
"""

import re
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/root/.openclaw/workspace")

def parse_task_master():
    """解析TASK_MASTER.md提取所有任务"""
    task_file = WORKSPACE / "TASK_MASTER.md"
    if not task_file.exists():
        return []
    
    content = task_file.read_text()
    tasks = []
    
    # 按###分割任务块
    sections = content.split('###')
    
    for section in sections[1:]:  # 跳过第一个空部分
        lines = section.strip().split('\n')
        if not lines:
            continue
        
        # 第一行是任务标题（含状态emoji）
        title_line = lines[0].strip()
        
        # 查找任务ID
        task_id = None
        status = '未知'
        
        for line in lines[:20]:  # 在前20行查找
            if '**任务ID**' in line and '|' in line:
                # 下一行应该是ID
                idx = lines.index(line)
                if idx + 1 < len(lines):
                    id_line = lines[idx + 1]
                    match = re.search(r'\|\s*([^|]+)\|', id_line)
                    if match:
                        task_id = match.group(1).strip()
            
            if '**状态**' in line:
                if '已完成' in line or '完成' in line:
                    status = '已完成'
                elif '进行中' in line:
                    status = '进行中'
                elif '阻塞' in line:
                    status = '阻塞'
                elif '逾期' in line:
                    status = '逾期'
        
        # 从标题推断状态（如果表格没找到）
        if status == '未知':
            if '✅' in title_line:
                status = '已完成'
            elif '🔄' in title_line:
                status = '进行中'
            elif '⏸️' in title_line:
                status = '阻塞'
            elif '⚠️' in title_line:
                status = '逾期'
        
        if task_id:
            tasks.append({
                'id': task_id,
                'status': status,
                'title': title_line
            })
    
    return tasks

def generate_board():
    """生成看板"""
    tasks = parse_task_master()
    now = datetime.now()
    
    # 分类
    in_progress = [t for t in tasks if t['status'] == '进行中']
    completed = [t for t in tasks if t['status'] == '已完成']
    blocked = [t for t in tasks if t['status'] == '阻塞']
    overdue = [t for t in tasks if t['status'] == '逾期']
    
    lines = []
    lines.append(f"# 每日任务看板 | {now.strftime('%Y-%m-%d %a')}")
    lines.append(f"**生成时间**: {now.strftime('%H:%M')}")
    lines.append("")
    
    # 进行中
    lines.append(f"## 🔄 进行中 ({len(in_progress)}项)")
    for t in in_progress[:10]:
        lines.append(f"- {t['id']}")
    if len(in_progress) > 10:
        lines.append(f"- ... 等共{len(in_progress)}项")
    if not in_progress:
        lines.append("- 无")
    lines.append("")
    
    # 阻塞
    lines.append(f"## ⏸️ 阻塞/需用户 ({len(blocked)}项)")
    for t in blocked:
        lines.append(f"- {t['id']}")
    if not blocked:
        lines.append("- 无")
    lines.append("")
    
    # 逾期
    lines.append(f"## ⚠️ 逾期 ({len(overdue)}项)")
    for t in overdue:
        lines.append(f"- {t['id']}")
    if not overdue:
        lines.append("- 无")
    lines.append("")
    
    # 已完成
    lines.append(f"## ✅ 已完成 ({len(completed)}项)")
    lines.append(f"- 共{len(completed)}项任务已完成")
    lines.append("")
    
    # 统计
    lines.append("## 📊 统计")
    lines.append(f"| 状态 | 数量 |")
    lines.append(f"|------|------|")
    lines.append(f"| 进行中 | {len(in_progress)} |")
    lines.append(f"| 阻塞 | {len(blocked)} |")
    lines.append(f"| 逾期 | {len(overdue)} |")
    lines.append(f"| 已完成 | {len(completed)} |")
    lines.append(f"| **总计** | **{len(tasks)}** |")
    
    return "\n".join(lines)

if __name__ == "__main__":
    board = generate_board()
    print(board)
    
    # 保存
    output_file = WORKSPACE / "memory" / f"TASK_BOARD_{datetime.now().strftime('%Y%m%d')}.md"
    output_file.write_text(board)
    print(f"\n看板已保存: {output_file}")