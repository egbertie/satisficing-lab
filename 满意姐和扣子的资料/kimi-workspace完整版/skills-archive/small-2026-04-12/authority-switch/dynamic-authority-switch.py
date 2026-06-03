#!/usr/bin/env python3
"""
动态权威切换脚本
功能: 根据Token/任务状态自动切换系统模式
触发: 每30分钟检查 + Token阈值触发
"""

import json
import os
import sys

AUTHORITY_LEVELS = {
    "NORMAL": {
        "level": 1,
        "token_threshold": (0, 70),
        "actions": ["全功能开放", "所有Skill可用", "Cron正常运行"],
        "trigger": "Token < 70%"
    },
    "CAUTION": {
        "level": 2,
        "token_threshold": (70, 80),
        "actions": ["精简响应", "延迟非紧急任务", "预警通知"],
        "trigger": "Token 70-80%"
    },
    "WARNING": {
        "level": 3,
        "token_threshold": (80, 90),
        "actions": ["ULTRA-LEAN模式", "仅P0/P1任务", "暂停非必要Cron"],
        "trigger": "Token 80-90%"
    },
    "CRITICAL": {
        "level": 4,
        "token_threshold": (90, 95),
        "actions": ["完全静默模式", "仅响应用户唤醒", "所有Cron暂停"],
        "trigger": "Token 90-95%"
    },
    "EMERGENCY": {
        "level": 5,
        "token_threshold": (95, 100),
        "actions": ["紧急熔断", "零Token保证", "仅核心备份"],
        "trigger": "Token > 95%"
    }
}

def get_current_token_usage():
    """获取当前Token使用率"""
    try:
        # 从文件读取或使用默认值
        token_file = "/root/.openclaw/workspace/memory/token-weekly-monitor.json"
        if os.path.exists(token_file):
            with open(token_file, "r") as f:
                data = json.load(f)
                return data.get("usage_percent", 87)
    except:
        pass
    return 87  # 默认值

def check_authority_level(token_percent):
    """根据Token使用率确定权威层级"""
    for level_name, config in AUTHORITY_LEVELS.items():
        min_val, max_val = config["token_threshold"]
        if min_val <= token_percent < max_val:
            return level_name, config
    return "EMERGENCY", AUTHORITY_LEVELS["EMERGENCY"]

def switch_authority_level():
    """执行权威切换"""
    
    token_percent = get_current_token_usage()
    level_name, config = check_authority_level(token_percent)
    
    # 记录切换日志
    switch_record = {
        "timestamp": __import__('datetime').datetime.now().isoformat(),
        "token_percent": token_percent,
        "authority_level": level_name,
        "level_number": config["level"],
        "actions": config["actions"],
        "trigger": config["trigger"]
    }
    
    # 保存记录
    log_file = "/root/.openclaw/workspace/memory/authority-switches.json"
    switches = []
    if os.path.exists(log_file):
        with open(log_file, "r") as f:
            switches = json.load(f)
    
    switches.append(switch_record)
    
    # 只保留最近100条
    switches = switches[-100:]
    
    with open(log_file, "w") as f:
        json.dump(switches, f, indent=2)
    
    # 输出切换信息
    print(f"[AUTHORITY-SWITCH] Level {config['level']}: {level_name}")
    print(f"Token: {token_percent}% | Trigger: {config['trigger']}")
    print(f"Actions: {', '.join(config['actions'])}")
    
    return switch_record

if __name__ == "__main__":
    switch_authority_level()
