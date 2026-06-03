#!/usr/bin/env python3
"""
系统状态Checkpoint - 定期保存机制
用途: 每30分钟保存一次系统状态，防止极端事件丢失
保存: 当前任务、进度、验证状态、执行日志位置
"""

import json
import os
from datetime import datetime
from pathlib import Path

def save_checkpoint():
    """保存系统状态Checkpoint"""
    
    checkpoint = {
        "timestamp": datetime.now().isoformat(),
        "version": "1.0",
        "system_state": {
            "active_tasks": [],
            "running_validators": [],
            "last_execution_logs": [],
            "pending_escalations": []
        },
        "critical_files": {
            "soul_md": "/root/.openclaw/workspace/SOUL.md",
            "memory_today": "/root/.openclaw/workspace/memory/2026-03-30.md",
            "ten_methodology_checklist": "/root/.openclaw/workspace/checklists/TEN_METHODOLOGY_CHECKLIST.md",
            "deep_insight_validator": "/root/.openclaw/workspace/scripts/deep_insight_validator.py",
            "task_escalation_manager": "/root/.openclaw/workspace/scripts/task_escalation_manager.py",
            "methodology_index": "/root/.openclaw/workspace/docs/METHODOLOGY_INDEX.json",
            "task_master": "/root/.openclaw/workspace/docs/TASK_MASTER.md",
            "user_teaching_index": "/root/.openclaw/workspace/docs/USER_TEACHING_INDEX.md"
        },
        "recovery_instructions": {
            "step1": "Read SOUL.md for identity",
            "step2": "Read memory/2026-03-30.md for recent context",
            "step3": "Verify all critical files exist",
            "step4": "Run checklists/STARTUP_SELF_CHECK.md",
            "step5": "Report recovery status to user"
        }
    }
    
    # 检测当前运行的任务（从各种日志中）
    checkpoint["system_state"]["active_tasks"] = detect_active_tasks()
    
    # 保存Checkpoint
    checkpoint_file = Path("/root/.openclaw/workspace/memory/system_state_checkpoint.json")
    with open(checkpoint_file, 'w', encoding='utf-8') as f:
        json.dump(checkpoint, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Checkpoint saved: {checkpoint_file}")
    print(f"   Timestamp: {checkpoint['timestamp']}")
    print(f"   Active tasks: {len(checkpoint['system_state']['active_tasks'])}")
    
    return checkpoint

def detect_active_tasks():
    """检测当前活跃任务"""
    active_tasks = []
    
    # 从TASK_MASTER读取
    task_master = Path("/root/.openclaw/workspace/docs/TASK_MASTER.md")
    if task_master.exists():
        active_tasks.append("Task tracking from TASK_MASTER")
    
    # 从执行日志读取
    exec_log = Path("/root/.openclaw/workspace/memory/deep_insight_execution_log.json")
    if exec_log.exists():
        active_tasks.append("Deep insight execution tracking")
    
    # 从升级日志读取
    escalation_log = Path("/root/.openclaw/workspace/memory/task_escalation_log.json")
    if escalation_log.exists():
        active_tasks.append("Task escalation tracking")
    
    return active_tasks

if __name__ == "__main__":
    checkpoint = save_checkpoint()
    print("\n⚠️  Critical: Run this every 30 minutes via cron")
    print("   crontab: */30 * * * * python3 /root/.openclaw/workspace/scripts/state_checkpoint.py")
