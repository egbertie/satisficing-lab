#!/usr/bin/env python3
"""
Token消耗监控与熔断系统 V2.0
基于周预算进度比例的分级熔断机制
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = Path("/root/.openclaw/workspace")
TOKEN_STATE_FILE = WORKSPACE / "memory" / "token-weekly-monitor.json"
FUSE_STATE_FILE = WORKSPACE / "memory" / "token-fuse-state.json"

# 熔断阈值配置 - 基于周预算进度比例
# 假设每周预算100%，按7天平均分配，每天约14.3%
# 超额10%触发预警（即当天消耗超过24.3%）
FUSE_THRESHOLDS = {
    "yellow": 110,   # 黄色预警：超出预算10%，暂停P3+P4任务
    "orange": 120,  # 橙色预警：超出预算20%，仅保留P0+P1
    "red": 130,     # 红色熔断：超出预算30%，仅保留P0
    "emergency": 150 # 紧急状态：超出预算50%，完全静默
}

# 预期进度（每天结束时）
DAILY_EXPECTED_PROGRESS = {
    0: 0,      # 周一开始
    1: 14.3,   # 周一结束
    2: 28.6,   # 周二结束
    3: 42.9,   # 周三结束
    4: 57.2,   # 周四结束
    5: 71.5,   # 周五结束
    6: 85.8,   # 周六结束
    7: 100     # 周日结束
}


def get_week_progress_percentage():
    """
    计算当前周预算消耗进度百分比
    返回: (实际消耗%, 预期进度%, 超额比例%)
    """
    now = datetime.now()
    weekday = now.weekday()  # 0=周一, 6=周日

    # 读取Token监控数据（2026-04-12 修正：统一读取 token-zero-tracker.json）
    ZERO_TRACKER = WORKSPACE / "memory" / "token-zero-tracker.json"
    if ZERO_TRACKER.exists():
        with open(ZERO_TRACKER, 'r', encoding='utf-8') as f:
            zero_data = json.load(f)
            display = zero_data.get("display", {})
            weekly_used = display.get("display_percentage", 0)
    elif TOKEN_STATE_FILE.exists():
        with open(TOKEN_STATE_FILE, 'r') as f:
            data = json.load(f)
            weekly_used = data.get("currentStatus", {}).get("percentage", 0)
    else:
        weekly_used = 0

    # 计算预期进度（基于当前是周几）
    expected = DAILY_EXPECTED_PROGRESS.get(weekday, 100)

    # 计算超额比例
    if expected > 0:
        excess_ratio = (weekly_used / expected) * 100
    else:
        excess_ratio = 100 if weekly_used > 0 else 0

    return weekly_used, expected, excess_ratio


def determine_fuse_level(excess_ratio):
    """根据超额比例确定熔断等级"""
    if excess_ratio >= FUSE_THRESHOLDS["emergency"]:
        return "emergency"
    elif excess_ratio >= FUSE_THRESHOLDS["red"]:
        return "red"
    elif excess_ratio >= FUSE_THRESHOLDS["orange"]:
        return "orange"
    elif excess_ratio >= FUSE_THRESHOLDS["yellow"]:
        return "yellow"
    return "normal"


def get_task_tiers():
    """任务分级 - 已合并重复任务"""
    return {
        "P0_CRITICAL": [  # 即使熔断也必须保留
            "backup-daily-001",           # 每日备份
            "278707b5-a688-4d23-adbc-3d73ea925a10",  # 灾备复刻每日同步（合并后）
        ],
        "P1_ESSENTIAL": [  # 橙色预警时保留
            "milestone-daily-check",      # 里程碑检查
            "bc640356-84e1-4e07-a2d5-cb93dab7e9ef",  # 每日安全检查
            "3d7db435-1497-4b00-9e63-2cd9c34cdf8f",  # 每日进度报告
        ],
        "P2_IMPORTANT": [  # 黄色预警时保留
            "f2ddbbb7-2374-4745-b73b-631a53e4f38a",  # 每日站会
            "8f0ffafd-1bb0-4503-a637-cd9c7f8cc208",  # 承诺保障检查
            "8dbc8186-b268-4895-8053-04305c9b28a1",  # 安全检查
            "2bcfc0c8-24bd-4768-b382-0ed99f767850",  # 每日知识萃取
        ],
        "P3_ROUTINE": [  # 正常状态运行，预警时暂停
            "0c1c5e75-562b-4edc-8419-f20b06a1bcf5",  # 文件治理
            "ad1fb129-d204-4a66-9b41-490e883d855e",  # 自主执行摘要
            "83c4750e-73bb-4c58-8a67-d658357448fb",  # API能力监控
            "0991f0cf-1c59-4dff-abd6-93b617636077",  # 每周六复盘
            "249ef31e-3fc7-4d45-9a68-681d5deb0b25",  # 引用一致性检查（已合并）
        ],
        "P4_LOW_FREQ": [  # 低频任务，可灵活调整
            "a4e7fe12-b645-4a84-b495-5697df8a3903",  # 每周组织罗盘
            "30014b47-8363-4555-b24f-04574dc356a7",  # API双周审查
            "backup-weekly-001",          # 每周全量备份
            "backup-cleanup-001",         # 备份清理
            "cb5e062f-8a69-4afc-a4e6-5c4eb4bc0d6e",  # 密钥轮换提醒
        ]
    }


def trigger_fuse(fuse_level, weekly_used, expected, excess_ratio):
    """触发熔断机制"""
    print(f"\n🔴 TOKEN熔断触发: {fuse_level.upper()}")
    print(f"周预算消耗: {weekly_used:.1f}%")
    print(f"预期进度: {expected:.1f}%")
    print(f"超额比例: {excess_ratio:.1f}%")
    print("=" * 50)
    
    task_tiers = get_task_tiers()
    
    # 根据熔断等级确定保留任务
    if fuse_level == "emergency":
        keep = set(task_tiers["P0_CRITICAL"])
    elif fuse_level == "red":
        keep = set(task_tiers["P0_CRITICAL"] + task_tiers["P1_ESSENTIAL"])
    elif fuse_level == "orange":
        keep = set(task_tiers["P0_CRITICAL"] + task_tiers["P1_ESSENTIAL"] + 
                   task_tiers["P2_IMPORTANT"])
    elif fuse_level == "yellow":
        keep = set(task_tiers["P0_CRITICAL"] + task_tiers["P1_ESSENTIAL"] + 
                   task_tiers["P2_IMPORTANT"] + task_tiers["P3_ROUTINE"])
    else:
        keep = set()
    
    # 记录熔断状态
    fuse_state = {
        "level": fuse_level,
        "weekly_used_percentage": weekly_used,
        "expected_percentage": expected,
        "excess_ratio": excess_ratio,
        "triggered_at": datetime.now().isoformat(),
        "kept_jobs": list(keep)
    }
    
    with open(FUSE_STATE_FILE, 'w') as f:
        json.dump(fuse_state, f, indent=2)
    
    print(f"保留任务: {len(keep)}个")
    return fuse_state


def monitor_loop():
    """监控循环 - 由Cron每2小时调用"""
    weekly_used, expected, excess_ratio = get_week_progress_percentage()
    fuse_level = determine_fuse_level(excess_ratio)
    
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] "
          f"周消耗: {weekly_used:.1f}%, 预期: {expected:.1f}%, 超额: {excess_ratio:.1f}%")
    
    if fuse_level != "normal":
        # 检查是否已经处于熔断状态
        if FUSE_STATE_FILE.exists():
            with open(FUSE_STATE_FILE, 'r') as f:
                current_fuse = json.load(f)
            if current_fuse.get("level") == fuse_level:
                print(f"  当前已处于{fuse_level}熔断状态")
                return
        
        trigger_fuse(fuse_level, weekly_used, expected, excess_ratio)
    else:
        # 检查是否需要解除熔断
        if FUSE_STATE_FILE.exists():
            with open(FUSE_STATE_FILE, 'r') as f:
                current_fuse = json.load(f)
            if current_fuse.get("level") != "normal":
                print("  解除熔断，恢复正常运行")
                # 记录解除
                with open(FUSE_STATE_FILE, 'w') as f:
                    json.dump({"level": "normal", "released_at": datetime.now().isoformat()}, f)


def status():
    """显示当前熔断状态"""
    weekly_used, expected, excess_ratio = get_week_progress_percentage()
    fuse_level = determine_fuse_level(excess_ratio)
    
    print("\n📊 Token熔断系统状态 V2.0")
    print("=" * 50)
    print(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"周预算消耗: {weekly_used:.1f}%")
    print(f"预期进度: {expected:.1f}%")
    print(f"超额比例: {excess_ratio:.1f}%")
    print(f"熔断等级: {fuse_level}")
    print("-" * 50)
    print("熔断阈值（超额比例）:")
    for level, threshold in FUSE_THRESHOLDS.items():
        status_icon = "🔴" if excess_ratio >= threshold else "🟢"
        print(f"  {status_icon} {level}: {threshold}%")
    print("=" * 50)


def main():
    if len(sys.argv) < 2:
        print("Usage: token-fuse-system.py [monitor|status]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "monitor":
        monitor_loop()
    elif command == "status":
        status()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
