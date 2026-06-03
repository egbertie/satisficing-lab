#!/usr/bin/env python3
"""
进度追踪助手 - 自动创建和更新进度追踪文件
用法: python3 progress-tracker.py [任务名称]
"""

import sys
import datetime

task_name = sys.argv[1] if len(sys.argv) > 1 else "未命名任务"
date_str = datetime.datetime.now().strftime("%Y-%m-%d")
time_str = datetime.datetime.now().strftime("%H:%M")

filename = f"progress-{date_str}.md"

content = f"""# 进度追踪 · {date_str}

## 任务信息
- **名称**: {task_name}
- **启动时间**: {date_str} {time_str}
- **运行模式**: L0正常

## 进度列表

| 序号 | 模块 | 状态 | Git提交 | 备注 |
|:-----|:-----|:----:|:-------|:-----|
| 1 | [模块名称] | ⬜ | | |
| 2 | [模块名称] | ⬜ | | |
| 3 | [模块名称] | ⬜ | | |

## 状态图例
- ⬜ 未开始
- 🔄 进行中
- ✅ 已完成
- ⏸️ 暂停

## 风险与阻塞
- **风险1**: [描述] → [应对措施]
- **阻塞1**: [描述] → [解决计划]

## 下步计划
1. [下一步行动]
2. [下一步行动]

---
*进度追踪文件 · 满意解研究所*
"""

with open(filename, "w") as f:
    f.write(content)

print(f"进度追踪文件已创建: {filename}")
