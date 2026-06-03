#!/usr/bin/env python3
"""
系统重启恢复脚本
用途: 系统重启后自动运行，恢复上次状态
触发: 系统启动时自动运行
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

def recover_from_restart():
    """系统重启后恢复"""
    
    print("=" * 60)
    print("SYSTEM RESTART RECOVERY")
    print(f"Time: {datetime.now().isoformat()}")
    print("=" * 60)
    print()
    
    # 1. 读取Checkpoint
    checkpoint_file = Path("/root/.openclaw/workspace/memory/system_state_checkpoint.json")
    if not checkpoint_file.exists():
        print("❌ CRITICAL: No checkpoint found!")
        print("   Creating fresh checkpoint...")
        checkpoint = create_fresh_checkpoint()
    else:
        with open(checkpoint_file, 'r') as f:
            checkpoint = json.load(f)
        print(f"✅ Checkpoint loaded: {checkpoint['timestamp']}")
    
    print()
    
    # 2. 验证关键文件存在
    print("STEP 1: Verifying critical files...")
    missing_files = []
    for name, path in checkpoint.get("critical_files", {}).items():
        if Path(path).exists():
            print(f"   ✅ {name}")
        else:
            print(f"   ❌ {name} - MISSING!")
            missing_files.append(name)
    
    if missing_files:
        print(f"\n⚠️  WARNING: {len(missing_files)} critical files missing!")
    else:
        print("\n✅ All critical files verified")
    
    print()
    
    # 3. 恢复活跃任务
    print("STEP 2: Restoring active tasks...")
    active_tasks = checkpoint.get("system_state", {}).get("active_tasks", [])
    if active_tasks:
        for task in active_tasks:
            print(f"   🔄 {task}")
    else:
        print("   ℹ️  No active tasks to restore")
    
    print()
    
    # 4. 输出恢复报告
    print("STEP 3: Recovery report...")
    recovery_report = {
        "timestamp": datetime.now().isoformat(),
        "checkpoint_age": checkpoint.get("timestamp", "unknown"),
        "files_verified": len(checkpoint.get("critical_files", {})),
        "files_missing": len(missing_files),
        "active_tasks_restored": len(active_tasks),
        "status": "RECOVERED" if not missing_files else "PARTIAL"
    }
    
    # 保存恢复报告
    report_file = Path("/root/.openclaw/workspace/memory/restart_recovery_report.json")
    with open(report_file, 'w') as f:
        json.dump(recovery_report, f, ensure_ascii=False, indent=2)
    
    print(f"   Status: {recovery_report['status']}")
    print(f"   Report saved: {report_file}")
    
    print()
    print("=" * 60)
    print("RECOVERY COMPLETE")
    print("=" * 60)
    print()
    print("⚠️  ACTION REQUIRED:")
    print("   1. Run checklists/STARTUP_SELF_CHECK.md")
    print("   2. Report recovery status to user")
    print("   3. Resume interrupted tasks if any")
    
    return recovery_report

def create_fresh_checkpoint():
    """创建新的Checkpoint（当没有历史时）"""
    return {
        "timestamp": datetime.now().isoformat(),
        "version": "1.0",
        "system_state": {"active_tasks": []},
        "critical_files": {},
        "note": "Fresh checkpoint - no history"
    }

if __name__ == "__main__":
    report = recover_from_restart()
    sys.exit(0 if report['status'] == 'RECOVERED' else 1)
