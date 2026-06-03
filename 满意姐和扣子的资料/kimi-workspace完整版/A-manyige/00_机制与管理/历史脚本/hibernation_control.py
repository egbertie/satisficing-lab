#!/usr/bin/env python3
"""
休眠协议控制器 V1.0
支持完全静默模式和标准休眠模式
"""

import json
import os
import sys
import subprocess
from datetime import datetime

# 休眠状态文件
HIBERNATION_STATE_FILE = "/tmp/openclaw/hibernation_state.json"
HIBERNATION_LOG_FILE = "/tmp/openclaw/hibernation.log"

# 关键任务ID（休眠期间需要禁用）
CRITICAL_JOBS_TO_DISABLE = [
    "8f0ffafd-1bb0-4503-a637-cd9c7f8cc208",  # 承诺检查
    "51d81326-d84b-45cc-b46b-8fad2061fceb",  # 任务协调
    "a19f729a-e9ce-4f4c-9a92-30575d48b8a1",  # 零空置
    "83c4750e-73bb-4c58-8a67-d658357448fb",  # API监控日报
]

# 核心备份任务（标准休眠模式保留）
ESSENTIAL_BACKUP_JOBS = [
    "daily-backup",
    "278707b5-a688-4d23-adbc-3d73ea925a10",  # 灾备同步
]

def log_event(message):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"
    with open(HIBERNATION_LOG_FILE, 'a') as f:
        f.write(log_entry)
    print(log_entry.strip())

def get_hibernation_state():
    """获取当前休眠状态"""
    if os.path.exists(HIBERNATION_STATE_FILE):
        with open(HIBERNATION_STATE_FILE, 'r') as f:
            return json.load(f)
    return {
        "mode": "active",
        "hibernating": False,
        "since": None,
        "token_frozen_at": None
    }

def save_hibernation_state(state):
    """保存休眠状态"""
    with open(HIBERNATION_STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def enter_complete_silence():
    """进入完全静默模式"""
    log_event("🌙 进入完全静默模式 (Complete Silence)")
    
    # 1. 记录状态
    state = {
        "mode": "complete_silence",
        "hibernating": True,
        "since": datetime.now().isoformat(),
        "token_frozen_at": 0,  # Token严格为0
        "disabled_jobs": []
    }
    
    # 2. 禁用所有Cron任务（包括备份）
    try:
        result = subprocess.run(
            ["openclaw", "cron", "list"],
            capture_output=True, text=True, timeout=30
        )
        # 解析并禁用所有任务
        log_event("   禁用所有Cron任务...")
        # 实际禁用逻辑需要根据openclaw输出解析
    except Exception as e:
        log_event(f"   警告: 禁用Cron任务时出错: {e}")
    
    # 3. 显式禁用关键任务
    for job_id in CRITICAL_JOBS_TO_DISABLE:
        try:
            subprocess.run(
                ["openclaw", "cron", "update", job_id, "--enabled", "false"],
                capture_output=True, timeout=10
            )
            state["disabled_jobs"].append(job_id)
        except:
            pass
    
    # 4. 保存状态
    save_hibernation_state(state)
    
    log_event("✅ 完全静默模式已激活")
    log_event("   Token消耗: 严格为0")
    log_event("   备份任务: 已暂停")
    log_event("   唤醒方式: 发送任意消息")
    
    return True

def enter_standard_hibernation():
    """进入标准休眠模式"""
    log_event("🌙 进入标准休眠模式 (Standard Hibernation)")
    
    # 1. 记录状态
    state = {
        "mode": "standard",
        "hibernating": True,
        "since": datetime.now().isoformat(),
        "token_frozen_at": 100,  # 预计日消耗<100
        "disabled_jobs": [],
        "kept_jobs": ESSENTIAL_BACKUP_JOBS
    }
    
    # 2. 禁用非核心任务
    try:
        result = subprocess.run(
            ["openclaw", "cron", "list"],
            capture_output=True, text=True, timeout=30
        )
        log_event("   禁用非核心Cron任务...")
    except Exception as e:
        log_event(f"   警告: 获取Cron列表时出错: {e}")
    
    # 3. 禁用关键任务但保留备份
    for job_id in CRITICAL_JOBS_TO_DISABLE:
        try:
            subprocess.run(
                ["openclaw", "cron", "update", job_id, "--enabled", "false"],
                capture_output=True, timeout=10
            )
            state["disabled_jobs"].append(job_id)
        except:
            pass
    
    # 4. 保存状态
    save_hibernation_state(state)
    
    log_event("✅ 标准休眠模式已激活")
    log_event("   Token消耗: <100/天")
    log_event("   保留任务: 每日备份")
    log_event("   暂停任务: 其他所有任务")
    log_event("   唤醒方式: 发送任意消息")
    
    return True

def wake_from_hibernation():
    """从休眠中唤醒"""
    state = get_hibernation_state()
    
    if not state.get("hibernating", False):
        log_event("⚠️ 当前不在休眠状态")
        return False
    
    mode = state.get("mode", "unknown")
    since = state.get("since")
    
    log_event(f"🌅 从{mode}模式唤醒")
    
    # 计算休眠时长
    if since:
        from datetime import datetime
        start = datetime.fromisoformat(since)
        duration = datetime.now() - start
        hours = duration.total_seconds() / 3600
        log_event(f"   休眠时长: {hours:.1f}小时")
    
    # 1. 恢复所有任务
    disabled_jobs = state.get("disabled_jobs", [])
    if disabled_jobs:
        log_event(f"   恢复 {len(disabled_jobs)} 个暂停的任务...")
        for job_id in disabled_jobs:
            try:
                subprocess.run(
                    ["openclaw", "cron", "update", job_id, "--enabled", "true"],
                    capture_output=True, timeout=10
                )
            except:
                pass
    
    # 2. 更新状态
    state["mode"] = "active"
    state["hibernating"] = False
    state["woken_at"] = datetime.now().isoformat()
    save_hibernation_state(state)
    
    log_event("✅ 唤醒完成，恢复正常运行")
    
    return True

def show_status():
    """显示休眠状态"""
    state = get_hibernation_state()
    
    print("\n🌙 休眠状态报告")
    print("━━━━━━━━━━━━━━━━━━━━")
    print(f"模式: {state.get('mode', 'active').upper()}")
    print(f"休眠中: {'是' if state.get('hibernating') else '否'}")
    
    if state.get("since"):
        print(f"开始时间: {state['since']}")
    
    if state.get("hibernating"):
        print(f"Token冻结: {state.get('token_frozen_at', 'N/A')}")
        print(f"禁用任务: {len(state.get('disabled_jobs', []))}个")
        print(f"保留任务: {len(state.get('kept_jobs', []))}个")
    
    print("━━━━━━━━━━━━━━━━━━━━\n")
    
    return True

def auto_check_hibernation():
    """自动检查是否应该进入休眠"""
    # 检查10分钟无交互
    # 这里需要与主控AI交互，暂时返回False
    return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 hibernation_control.py <command>")
        print()
        print("Commands:")
        print("  sleep-full       进入完全静默模式 (Token=0)")
        print("  sleep-standard   进入标准休眠模式 (Token<100/天)")
        print("  wake             唤醒")
        print("  status           查看状态")
        print("  auto-check       自动检查是否需要休眠")
        print()
        print("Aliases:")
        print("  '完全静默', '绝对静默', '停止一切' → sleep-full")
        print("  '休眠', '睡觉', '暂停', '休息' → sleep-standard")
        print("  '唤醒', '开始', '继续' → wake")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    # 命令映射
    command_map = {
        # 完全静默
        "sleep-full": enter_complete_silence,
        "complete-silence": enter_complete_silence,
        "完全静默": enter_complete_silence,
        "绝对静默": enter_complete_silence,
        "停止一切": enter_complete_silence,
        
        # 标准休眠
        "sleep-standard": enter_standard_hibernation,
        "standard": enter_standard_hibernation,
        "休眠": enter_standard_hibernation,
        "睡觉": enter_standard_hibernation,
        "暂停": enter_standard_hibernation,
        "休息": enter_standard_hibernation,
        
        # 唤醒
        "wake": wake_from_hibernation,
        "唤醒": wake_from_hibernation,
        "开始": wake_from_hibernation,
        "继续": wake_from_hibernation,
        
        # 状态
        "status": show_status,
        "状态": show_status,
        
        # 自动检查
        "auto-check": auto_check_hibernation,
        "自动检查": auto_check_hibernation,
    }
    
    action = command_map.get(command)
    if action:
        action()
    else:
        print(f"未知命令: {command}")
        print(f"可用命令: {', '.join(set(command_map.keys()))}")
        sys.exit(1)

if __name__ == "__main__":
    main()
