#!/usr/bin/env python3
"""
防中断自检脚本 — 检查当前任务是否执行了防中断保护
运行方式: python3 anti_interrupt_self_check.py
"""

import os
import subprocess
from datetime import datetime

def check_progress_file():
    """检查是否有进度追踪文件"""
    print("[检查1] 进度追踪文件")
    print("  · 当前目录是否有 *进度追踪*.md 文件？")
    # 实际应由调用者检查
    print("  → [请确认] 是/否")
    return None

def check_unit_breakdown():
    """检查是否拆分为单元"""
    print("\n[检查2] 单元化拆分")
    print("  · 当前任务是否拆分为U1/U2/U3...？")
    print("  · 每个单元预计时间 ≤ 30分钟？")
    print("  → [请确认] 是/否")
    return None

def check_serial_execution():
    """检查是否串行执行"""
    print("\n[检查3] 串行执行")
    print("  · 当前是否只推进一个单元？")
    print("  · 上一个单元是否已标记✅？")
    print("  → [请确认] 是/否")
    return None

def check_git_status():
    """检查Git状态"""
    print("\n[检查4] Git存档")
    try:
        result = subprocess.run(['git', 'status', '--short'], 
                              capture_output=True, text=True, timeout=5)
        if result.stdout.strip():
            print(f"  ⚠️  有未提交的变更:")
            print(f"  {result.stdout[:200]}")
            print("  → 建议立即执行: git add . && git commit -m '防中断存档'")
        else:
            print("  ✅ 工作区干净，已存档")
    except Exception as e:
        print(f"  ? 无法检查Git状态: {e}")
    return None

def run_self_check():
    """执行完整自检"""
    print("=" * 60)
    print("防中断自检 — 快速检查")
    print("=" * 60)
    print(f"检查时间: {datetime.now().isoformat()}")
    print()
    
    check_progress_file()
    check_unit_breakdown()
    check_serial_execution()
    check_git_status()
    
    print("\n" + "=" * 60)
    print("如果以上有任何一项为'否'，立即执行3层存档:")
    print("  1. 更新进度追踪文件")
    print("  2. git add + commit")
    print("  3. 更新memory文件")
    print("=" * 60)

if __name__ == "__main__":
    run_self_check()
