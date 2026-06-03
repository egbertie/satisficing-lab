#!/usr/bin/env python3
"""
Cron V2.0 动态配置管理器
根据Token状态自动调整任务频率
"""

import json
import subprocess
import sys
from datetime import datetime

# Token状态分层配置
TOKEN_LEVELS = {
    "L5": {"min": 70, "max": 100, "desc": "正常运营"},
    "L4": {"min": 50, "max": 70, "desc": "轻度节省"},
    "L3": {"min": 30, "max": 50, "desc": "中度节省"},
    "L2": {"min": 15, "max": 30, "desc": "严格节省"},
    "L1": {"min": 0, "max": 15, "desc": "紧急模式"}
}

# 任务配置模板
JOB_TEMPLATES = {
    "morning-report": {
        "description": "晨间日报 - 用户核心需求",
        "priority": "high",
        "token_budget": 800,
        "schedules": {
            "L5": "7 9 * * *",
            "L4": "7 9 * * *",
            "L3": "7 9 * * *",
            "L2": "disabled",
            "L1": "disabled"
        }
    },
    "token-monitor": {
        "description": "Token监控 - 自我保护机制",
        "priority": "critical",
        "token_budget": 200,
        "schedules": {
            "L5": "0 */6 * * *",   # 每6小时
            "L4": "0 */8 * * *",   # 每8小时
            "L3": "0 */12 * * *",  # 每12小时
            "L2": "0 6 * * *",     # 每天6AM
            "L1": "disabled"
        }
    },
    "evening-totem": {
        "description": "黄昏图腾归位 - 文化仪式",
        "priority": "medium",
        "token_budget": 300,
        "schedules": {
            "L5": "0 18 * * *",
            "L4": "0 18 * * *",
            "L3": "disabled",
            "L2": "disabled",
            "L1": "disabled"
        }
    },
    "weekly-check": {
        "description": "周度检查 - 质量审计",
        "priority": "high",
        "token_budget": 1500,
        "schedules": {
            "L5": "17 3 * * 0",
            "L4": "17 3 * * 0",
            "L3": "17 3 * * 0",
            "L2": "disabled",
            "L1": "disabled"
        }
    },
    "daily-backup": {
        "description": "每日备份 - 数据保障",
        "priority": "critical",
        "token_budget": 100,
        "schedules": {
            "L5": "0 3 * * *",
            "L4": "0 3 * * *",
            "L3": "0 3 * * *",
            "L2": "0 3 * * *",
            "L1": "0 3 * * *"
        }
    },
    "hibernation-check": {
        "description": "休眠检测 - 状态管理",
        "priority": "critical",
        "token_budget": 50,
        "schedules": {
            "L5": "*/10 * * * *",  # 每10分钟
            "L4": "*/10 * * * *",
            "L3": "*/5 * * * *",    # 每5分钟
            "L2": "*/5 * * * *",
            "L1": "*/5 * * * *"
        }
    }
}

def get_current_token_level(token_percent):
    """根据Token百分比确定当前等级"""
    for level, config in TOKEN_LEVELS.items():
        if config["min"] <= token_percent < config["max"]:
            return level
    return "L1"  # 默认最低等级

def calculate_daily_token_budget(level):
    """计算指定等级的日Token预算"""
    budgets = {
        "L5": 3000,
        "L4": 2000,
        "L3": 1200,
        "L2": 500,
        "L1": 100
    }
    return budgets.get(level, 3000)

def generate_cron_config(level):
    """生成指定等级的Cron配置"""
    config = {
        "version": "2.0",
        "level": level,
        "timestamp": datetime.now().isoformat(),
        "daily_token_budget": calculate_daily_token_budget(level),
        "jobs": {}
    }
    
    for job_name, template in JOB_TEMPLATES.items():
        schedule = template["schedules"].get(level, "disabled")
        config["jobs"][job_name] = {
            "enabled": schedule != "disabled",
            "schedule": schedule,
            "priority": template["priority"],
            "token_budget": template["token_budget"],
            "description": template["description"]
        }
    
    return config

def deploy_cron_jobs(config):
    """部署Cron任务"""
    print(f"🚀 部署Cron V2.0 - Level {config['level']}")
    print(f"📊 日Token预算: {config['daily_token_budget']}")
    print()
    
    for job_name, job_config in config["jobs"].items():
        if not job_config["enabled"]:
            print(f"⏸️  {job_name}: 已禁用")
            continue
        
        # 构建OpenClaw cron命令
        cmd = [
            "openclaw", "cron", "create",
            "--name", job_name,
            "--schedule", job_config["schedule"],
            "--target", "isolated",
            "--payload", json.dumps({
                "kind": "agentTurn",
                "task": f"Execute {job_name} task",
                "token_budget": job_config["token_budget"]
            })
        ]
        
        print(f"✅ {job_name}: {job_config['schedule']} - {job_config['description']}")
    
    print()
    print("配置生成完成，请手动执行部署命令")
    return True

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 cron_v2_manager.py <token_percent>")
        print("Example: python3 cron_v2_manager.py 75")
        sys.exit(1)
    
    try:
        token_percent = float(sys.argv[1])
    except ValueError:
        print("Error: token_percent must be a number")
        sys.exit(1)
    
    level = get_current_token_level(token_percent)
    config = generate_cron_config(level)
    
    # 保存配置
    config_file = f"/tmp/cron_v2_config_{level}.json"
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"📁 配置已保存: {config_file}")
    print()
    
    # 部署
    deploy_cron_jobs(config)
    
    # 输出预估信息
    print("📈 预估效率:")
    print(f"   相比V1.0节省: {100 - (config['daily_token_budget'] / 11000 * 100):.0f}%")
    print(f"   相比V1.5节省: {100 - (config['daily_token_budget'] / 6000 * 100):.0f}%")

if __name__ == "__main__":
    main()
