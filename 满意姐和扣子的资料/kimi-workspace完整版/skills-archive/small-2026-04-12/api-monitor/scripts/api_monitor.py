#!/usr/bin/env python3
"""
API监控脚本 - 5标准实现
功能：监控API可用性、响应时间、错误率
"""

import json
import os
import sys
import time
import requests
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = Path("/root/.openclaw/workspace")
CONFIG_FILE = WORKSPACE / "skills" / "api-monitor" / "config" / "endpoints.json"
LOG_DIR = WORKSPACE / "skills" / "api-monitor" / "logs"
STATE_FILE = WORKSPACE / "memory" / "api-monitor-state.json"

def load_config():
    """加载配置"""
    if not CONFIG_FILE.exists():
        return {"endpoints": []}
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def check_endpoint(endpoint):
    """检查单个端点"""
    result = {
        "name": endpoint.get("name", "unknown"),
        "url": endpoint["url"],
        "timestamp": datetime.now().isoformat(),
        "status": "unknown",
        "response_time_ms": 0,
        "status_code": 0,
        "error": None
    }
    
    try:
        start = time.time()
        response = requests.request(
            method=endpoint.get("method", "GET"),
            url=endpoint["url"],
            headers=endpoint.get("headers", {}),
            timeout=endpoint.get("timeout", 10)
        )
        result["response_time_ms"] = int((time.time() - start) * 1000)
        result["status_code"] = response.status_code
        
        expected = endpoint.get("expected_status", 200)
        if response.status_code == expected:
            result["status"] = "up"
        else:
            result["status"] = "down"
            result["error"] = f"Unexpected status: {response.status_code}"
            
    except requests.exceptions.Timeout:
        result["status"] = "timeout"
        result["error"] = "Request timeout"
    except requests.exceptions.ConnectionError:
        result["status"] = "connection_error"
        result["error"] = "Connection failed"
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
    
    return result

def check_all():
    """检查所有端点"""
    config = load_config()
    results = []
    
    for endpoint in config.get("endpoints", []):
        # 重试3次
        for attempt in range(3):
            result = check_endpoint(endpoint)
            if result["status"] == "up":
                break
            if attempt < 2:
                time.sleep(1)
        results.append(result)
    
    return results

def save_results(results):
    """保存结果"""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d")
    log_file = LOG_DIR / f"checks-{date_str}.jsonl"
    
    with open(log_file, 'a') as f:
        for result in results:
            f.write(json.dumps(result) + '\n')

def generate_report(results):
    """生成报告"""
    total = len(results)
    up = sum(1 for r in results if r["status"] == "up")
    down = total - up
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total": total,
            "up": up,
            "down": down,
            "uptime_percentage": round(up / total * 100, 2) if total > 0 else 0
        },
        "details": results
    }
    
    return report

def main():
    if len(sys.argv) < 2:
        print("Usage: api_monitor.py [check|status|report]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "check":
        results = check_all()
        save_results(results)
        report = generate_report(results)
        print(json.dumps(report, indent=2))
        
        # 如果有down的，返回错误码
        if report["summary"]["down"] > 0:
            sys.exit(1)
            
    elif command == "status":
        config = load_config()
        print(f"监控端点数: {len(config.get('endpoints', []))}")
        print(f"日志目录: {LOG_DIR}")
        
    elif command == "report":
        # 生成日报
        results = check_all()
        report = generate_report(results)
        print(json.dumps(report, indent=2))
        
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
