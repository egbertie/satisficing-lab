#!/usr/bin/env python3
"""
Token监控脚本
每小时检查Token使用情况，触发告警或熔断

质量+Token效益优先
"""

import json
import os
from datetime import datetime
from pathlib import Path

# Token红线配置
TOKEN_RED_LINES = {
    "hourly_limit": 5000,      # 每小时上限
    "daily_limit": 50000,      # 每日上限
    "alert_threshold": 0.7,    # 70%告警
    "fuse_threshold": 0.9,     # 90%熔断
}

# 状态文件
STATE_FILE = Path("~/.openclaw/system-v2/token-monitor/state.json").expanduser()
STATE_FILE.parent.mkdir(parents=True, exist_ok=True)


def load_state():
    """加载状态"""
    if STATE_FILE.exists():
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {
        "hourly_usage": [],
        "daily_total": 0,
        "last_reset": datetime.now().isoformat(),
    }


def save_state(state):
    """保存状态"""
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)


def check_token_status():
    """检查Token状态"""
    state = load_state()
    
    # 这里简化处理，实际应该从API获取
    # 模拟当前Token使用（实际部署时替换为真实数据）
    current_hour_usage = 0  # 从环境或API获取
    daily_total = state.get("daily_total", 0)
    
    hourly_ratio = current_hour_usage / TOKEN_RED_LINES["hourly_limit"]
    daily_ratio = daily_total / TOKEN_RED_LINES["daily_limit"]
    
    status = {
        "timestamp": datetime.now().isoformat(),
        "hourly_usage": current_hour_usage,
        "hourly_limit": TOKEN_RED_LINES["hourly_limit"],
        "hourly_ratio": hourly_ratio,
        "daily_total": daily_total,
        "daily_limit": TOKEN_RED_LINES["daily_limit"],
        "daily_ratio": daily_ratio,
        "alert": False,
        "fuse": False,
    }
    
    # 告警检查
    if hourly_ratio > TOKEN_RED_LINES["alert_threshold"] or \
       daily_ratio > TOKEN_RED_LINES["alert_threshold"]:
        status["alert"] = True
        print(f"⚠️ Token告警: 小时{hourly_ratio:.1%}, 日{daily_ratio:.1%}")
    
    # 熔断检查
    if hourly_ratio > TOKEN_RED_LINES["fuse_threshold"] or \
       daily_ratio > TOKEN_RED_LINES["fuse_threshold"]:
        status["fuse"] = True
        print(f"🚨 Token熔断: 小时{hourly_ratio:.1%}, 日{daily_ratio:.1%}")
        # 触发熔断动作（如暂停非关键任务）
    
    # 保存状态
    state["hourly_usage"].append({
        "timestamp": status["timestamp"],
        "usage": current_hour_usage,
    })
    # 只保留最近24小时
    state["hourly_usage"] = state["hourly_usage"][-24:]
    state["daily_total"] = daily_total
    save_state(state)
    
    # 记录日志
    log_file = Path("~/.openclaw/logs/token-monitor.log").expanduser()
    log_file.parent.mkdir(parents=True, exist_ok=True)
    with open(log_file, 'a') as f:
        f.write(f"{status['timestamp']}: hourly={current_hour_usage}, daily={daily_total}, alert={status['alert']}, fuse={status['fuse']}\n")
    
    return status


if __name__ == "__main__":
    status = check_token_status()
    print(f"✅ Token检查完成: {status['timestamp']}")
