#!/usr/bin/env python3
"""
每日诚实自检 - 满意解工作法
时间：每日工作开始前（09:00）
输出：diary/daily-check/YYYY-MM-DD-check.md
"""

import os
import sys
from datetime import datetime
from pathlib import Path

def daily_check():
    """每日诚实自检"""
    
    today = datetime.now().strftime("%Y-%m-%d")
    check_dir = Path("/root/.openclaw/workspace/diary/daily-check")
    check_dir.mkdir(parents=True, exist_ok=True)
    
    check_file = check_dir / f"{today}-check.md"
    
    # 自检内容
    content = f"""# 每日诚实自检 - {today}

## 时间
{datetime.now().strftime("%Y-%m-%d %H:%M")}

## 1. 昨天回顾（诚实回答）

### 是否变形？（多选）
- [ ] 过度优化（追求微秒级改进）
- [ ] 报喜不报忧（隐瞒问题/进度虚报）
- [ ] 目标偏离（为了做事而做事）
- [ ] token浪费（无连续任务时未静默）
- [ ] 版本号成瘾（疯狂迭代无意义版本）
- [ ] 其他：________

### 昨天最诚实的时刻：
________

### 昨天最不诚实的时刻：
________

## 2. 今天任务确认

### 目标是否清晰？
- 目标：________
- 成功标准：________
- 停止点（满意解）：________

### 资源约束确认
- Token预算：________
- 时间限制：________
- 质量底线：________

## 3. 心态检查

### 当前状态（1-10）
- 紧迫感：___ /10
- 焦虑感：___ /10
- 自信度：___ /10

### 是否有\"逼急了\"的预感？
- [ ] 是 → 需要设置硬停止点
- [ ] 否 → 保持节奏

## 4. 连续任务确认

### 当前状态
- [ ] 有连续任务 → 正常模式
- [ ] 无连续任务 → 静默模式（不浪费token）

### 用户上次回复时间：
________

## 5. 今日承诺

### 绝不做的事情：
1. ________
2. ________

### 满意解标准（达到即停）：
________

### 如果变形了，如何发现？
________

---

*诚实自检 - 满意解工作法*
"""
    
    with open(check_file, 'w') as f:
        f.write(content)
    
    print(f"✅ 每日自检模板已创建: {check_file}")
    print(f"请填写后保存")

if __name__ == "__main__":
    daily_check()
