#!/usr/bin/env python3
"""
Token档位判断与检查项生成器
根据当前Token余量动态生成检查清单
"""

import json
import sys
from datetime import datetime
from pathlib import Path

def get_token_level(percentage):
    """根据Token百分比判断档位 (percentage是已消耗百分比)"""
    remaining = 100 - percentage
    if remaining > 70:
        return "L1", "正常频率(30分钟)"
    elif remaining > 50:
        return "L2", "降频33%(45分钟)"
    elif remaining > 30:
        return "L3", "降频50%(60分钟)"
    else:
        return "L4", "降频75%(120分钟，仅P0)"

def get_checklist(level, hour):
    """根据档位和时段生成检查清单"""
    checks = {
        "P0": ["token_monitor"],  # 始终必检
        "P1": [],
        "P2": [],
        "P3": []
    }
    
    # 深夜模式 (00:00-08:00)
    is_night = 0 <= hour < 8
    
    # L1档位：全部检查
    if level == "L1" and not is_night:
        checks["P1"] = ["calendar", "forgotten_tasks"]
        checks["P2"] = ["mentions"]
        
    # L2档位：P1全检，P2降频
    elif level == "L2" and not is_night:
        checks["P1"] = ["calendar", "forgotten_tasks"]
        if hour % 4 == 0:  # P2每4小时
            checks["P2"] = ["mentions"]
            
    # L3档位：P1降频，P2暂停
    elif level == "L3":
        if not is_night and hour % 2 == 0:  # P1每2小时
            checks["P1"] = ["calendar", "forgotten_tasks"]
            
    # L4档位：仅P0
    # 不添加任何其他检查项
    
    return checks

def main():
    # 读取当前Token状态（2026-04-12 修正：统一读取 token-zero-tracker.json）
    token_file = Path("/root/.openclaw/workspace/memory/token-zero-tracker.json")
    if token_file.exists():
        with open(token_file) as f:
            data = json.load(f)
            percentage = data.get("display", {}).get("display_percentage", 50)
    else:
        percentage = 50  # 默认值
    
    # 判断档位
    level, description = get_token_level(percentage)
    
    # 当前时间
    now = datetime.now()
    hour = now.hour
    
    # 生成检查清单
    checks = get_checklist(level, hour)
    
    # 输出结果
    result = {
        "timestamp": now.isoformat(),
        "token_percentage": percentage,
        "level": level,
        "description": description,
        "hour": hour,
        "is_night": 0 <= hour < 8,
        "checks": checks,
        "paused": ["email", "weather"],
        "response_format": f"HEARTBEAT_OK [{level}]"
    }
    
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # 更新状态文件
    state_file = Path("/root/.openclaw/workspace/memory/heartbeat-state.json")
    if state_file.exists():
        with open(state_file) as f:
            state = json.load(f)
        state["currentTokenLevel"] = level
        state["activeChecks"] = checks
        with open(state_file, "w") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
