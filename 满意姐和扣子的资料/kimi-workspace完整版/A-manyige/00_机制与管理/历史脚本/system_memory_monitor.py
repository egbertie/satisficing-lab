#!/usr/bin/env python3
"""
系统内存监控 - 修复版
监控实际系统内存，不是Python进程内存
"""

import psutil
import sys
from pathlib import Path

def check_system_memory():
    """检查系统内存（实际可用内存）"""
    mem = psutil.virtual_memory()
    
    # 实际指标
    total_mb = mem.total / (1024 * 1024)
    available_mb = mem.available / (1024 * 1024)
    used_mb = mem.used / (1024 * 1024)
    percent = mem.percent
    
    # 基线限制
    BASELINE_MAX = 1024  # MB
    
    status = {
        "total_mb": round(total_mb, 2),
        "available_mb": round(available_mb, 2),
        "used_mb": round(used_mb, 2),
        "percent": percent,
        "baseline_max": BASELINE_MAX,
        "exceeded": used_mb > BASELINE_MAX,
        "action": None
    }
    
    # 判断级别
    if used_mb > BASELINE_MAX * 2:  # > 2048MB
        status["level"] = "CRITICAL"
        status["action"] = "立即清理内存，停止非关键任务"
    elif used_mb > BASELINE_MAX:  # > 1024MB
        status["level"] = "WARNING"
        status["action"] = "内存超标，建议优化"
    else:
        status["level"] = "SAFE"
        status["action"] = "内存正常"
    
    return status

def log_status(status):
    """记录状态"""
    log_file = Path("/root/.openclaw/workspace/logs/system-memory-monitor.log")
    log_file.parent.mkdir(exist_ok=True)
    
    from datetime import datetime
    timestamp = datetime.now().isoformat()
    
    line = f"[{timestamp}] 使用:{status['used_mb']}MB 可用:{status['available_mb']}MB 级别:{status['level']}\n"
    
    with open(log_file, "a") as f:
        f.write(line)

def main():
    status = check_system_memory()
    log_status(status)
    
    print(f"系统内存: {status['used_mb']}MB / 基线: {status['baseline_max']}MB")
    print(f"级别: {status['level']}")
    print(f"建议: {status['action']}")
    
    if status["exceeded"]:
        print("⚠️ 内存超标，需要优化")
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
