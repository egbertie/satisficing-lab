#!/usr/bin/env python3
"""
主动升级机制 - 任务卡住时自动升级
用途: 监控任务状态，超时限自动升级
规则: 等待1h→提醒→4h→提案→不反对视为确认
"""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path

class TaskEscalationManager:
    """任务升级管理器"""
    
    def __init__(self):
        self.log_file = Path("/root/.openclaw/workspace/memory/task_escalation_log.json")
        self.escalation_rules = {
            "remind": timedelta(hours=1),      # 1小时提醒
            "propose": timedelta(hours=4),     # 4小时提案
            "execute": timedelta(hours=24)     # 24小时执行
        }
    
    def check_stuck_tasks(self):
        """检查卡住的任务"""
        # 从任务主清单读取
        task_master = Path("/root/.openclaw/workspace/docs/TASK_MASTER.md")
        if not task_master.exists():
            return []
        
        stuck_tasks = []
        # 解析任务清单，找出标记为"卡住"的任务
        # 实际实现需要解析md文件
        
        return stuck_tasks
    
    def escalate(self, task_id, current_status):
        """升级任务"""
        
        escalation_actions = {
            "waiting_1h": {
                "action": "remind",
                "message": "任务 '{}' 已等待1小时，请确认是否可以继续？"
            },
            "waiting_4h": {
                "action": "propose", 
                "message": "任务 '{}' 已等待4小时，这是我的提议方案，请纠正："
            },
            "waiting_24h": {
                "action": "execute",
                "message": "任务 '{}' 已等待24小时，按默认方案执行"
            }
        }
        
        # 记录升级日志
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "task_id": task_id,
            "from_status": current_status,
            "action": escalation_actions.get(current_status, {}).get("action"),
            "message": escalation_actions.get(current_status, {}).get("message", "").format(task_id)
        }
        
        self._log_escalation(log_entry)
        return log_entry
    
    def _log_escalation(self, entry):
        """记录升级日志"""
        logs = []
        if self.log_file.exists():
            with open(self.log_file, 'r') as f:
                try:
                    logs = json.load(f)
                except:
                    logs = []
        
        logs.append(entry)
        
        with open(self.log_file, 'w') as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    manager = TaskEscalationManager()
    print("=== 主动升级机制已初始化 ===")
    print(f"升级规则: 1h提醒 → 4h提案 → 24h执行")
    print(f"日志文件: {manager.log_file}")
