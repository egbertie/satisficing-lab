#!/usr/bin/env python3
"""
Token监控与休眠控制集成模块 V2.1
- 监控Token消耗
- 自动调整频率
- 休眠状态检测
"""

import json
import os
import subprocess
from datetime import datetime

STATE_FILE = "/tmp/openclaw/token_monitor_state.json"
LOG_FILE = "/tmp/openclaw/token_monitor.log"

# Token分层阈值
TOKEN_LEVELS = {
    "L5": {"min": 70, "max": 100, "color": "🟢"},
    "L4": {"min": 50, "max": 70, "color": "🟡"},
    "L3": {"min": 30, "max": 50, "color": "🟠"},
    "L2": {"min": 15, "max": 30, "color": "🔴"},
    "L1": {"min": 0, "max": 15, "color": "⚫"}
}

# 频率配置
FREQUENCY_CONFIG = {
    "L5": {"token_monitor": "0 */6 * * *", "stagger": "5m"},  # 每6小时
    "L4": {"token_monitor": "0 */8 * * *", "stagger": "5m"},  # 每8小时
    "L3": {"token_monitor": "0 */12 * * *", "stagger": "5m"}, # 每12小时
    "L2": {"token_monitor": "0 6 * * *", "stagger": "0"},     # 每天6AM
    "L1": {"token_monitor": "disabled", "stagger": "0"}       # 暂停
}

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}")

def get_current_level(token_pct):
    for level, cfg in TOKEN_LEVELS.items():
        if cfg["min"] <= token_pct < cfg["max"]:
            return level
    return "L1"

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"last_level": None, "adjustments": []}

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def adjust_cron_frequency(current_level):
    """根据Token等级调整Cron频率"""
    config = FREQUENCY_CONFIG.get(current_level)
    if not config:
        return False
    
    if config["token_monitor"] == "disabled":
        log(f"⚫ {current_level}: Token极低，建议进入休眠模式")
        return "hibernate"
    
    log(f"{TOKEN_LEVELS[current_level]['color']} {current_level}: Token监控频率调整为 {config['token_monitor']}")
    return True

def main():
    # 这里会从环境或参数获取当前Token百分比
    # 实际运行时由调用方传入
    token_pct = 75  # 示例值
    
    current_level = get_current_level(token_pct)
    state = load_state()
    
    log(f"Token监控启动 - 当前: {token_pct}% ({current_level})")
    
    # 检查是否需要调整
    if state.get("last_level") != current_level:
        log(f"等级变化: {state.get('last_level')} → {current_level}")
        result = adjust_cron_frequency(current_level)
        
        state["last_level"] = current_level
        state["adjustments"].append({
            "time": datetime.now().isoformat(),
            "from": state.get("last_level"),
            "to": current_level,
            "token_pct": token_pct
        })
        save_state(state)
        
        if result == "hibernate":
            log("🌙 触发休眠建议 - 等待用户确认")
    else:
        log(f"等级未变化 ({current_level})，维持当前配置")
    
    # 生成报告
    report = f"""
📊 Token监控报告
━━━━━━━━━━━━━━━━━━━━
当前Token: {token_pct}%
当前等级: {current_level} {TOKEN_LEVELS[current_level]['color']}
建议频率: {FREQUENCY_CONFIG[current_level]['token_monitor']}
━━━━━━━━━━━━━━━━━━━━
"""
    print(report)

if __name__ == "__main__":
    main()
