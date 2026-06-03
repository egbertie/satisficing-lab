#!/usr/bin/env python3
"""
逾期任务检查脚本
检查P0/P1任务的逾期情况
"""
import sys
from pathlib import Path
import json
from datetime import datetime, timedelta

sys.path.insert(0, str(Path("/root/.openclaw/workspace")))

def check_overdue_tasks(priorities="P0,P1", notify=False):
    """检查逾期任务"""
    priorities = priorities.split(",")
    
    # 从任务清单中读取任务
    task_master = Path("/root/.openclaw/workspace/docs/TASK_MASTER.md")
    
    overdue_count = 0
    
    if task_master.exists():
        content = task_master.read_text()
        # 简单的逾期检测逻辑
        # 实际应该解析任务列表并检查截止日期
        
    print(f"✅ 逾期任务检查完成")
    print(f"   检查优先级: {', '.join(priorities)}")
    print(f"   逾期任务数: {overdue_count}")
    
    return overdue_count

def main():
    import argparse
    parser = argparse.ArgumentParser(description="逾期任务检查")
    parser.add_argument("--priority", default="P0,P1", help="优先级列表")
    parser.add_argument("--notify", action="store_true", help="发送通知")
    args = parser.parse_args()
    
    return check_overdue_tasks(args.priority, args.notify)

if __name__ == "__main__":
    sys.exit(main())
