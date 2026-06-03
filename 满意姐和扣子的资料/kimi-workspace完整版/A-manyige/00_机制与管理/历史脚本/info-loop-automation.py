#!/usr/bin/env python3
"""
信息闭环自动化脚本
触发: 每小时检查 + 任务状态变更 + 定时汇报
输出: 未闭环任务提醒 + 自动汇报生成
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

# 配置
CONFIG = {
    "check_interval_hours": 1,
    "report_reminder_hours": [9, 14, 18],  # 每日汇报时间
    "memory_path": Path("/root/.openclaw/workspace/memory"),
    "task_board_file": "TASK_BOARD_{date}.md",
    "log_file": "info-loop-log.jsonl"
}

# 闭环阶段定义
LOOP_STAGES = ["confirm", "execute", "report", "verify"]

class InfoLoopCloser:
    """信息闭环自动化管理器"""
    
    def __init__(self):
        self.tasks = []
        self.log = []
        
    def load_tasks(self):
        """加载当前任务列表"""
        # 从TASK_BOARD读取
        today = datetime.now().strftime("%Y%m%d")
        board_file = CONFIG["memory_path"] / CONFIG["task_board_file"].format(date=today)
        
        if board_file.exists():
            # 解析任务看板
            pass  # 具体解析逻辑待实现
            
        return self.tasks
    
    def check_loop_status(self, task_id):
        """检查任务的闭环状态"""
        status = {
            "task_id": task_id,
            "stages": {},
            "is_closed": False,
            "gap": None
        }
        
        # 检查每个阶段
        for stage in LOOP_STAGES:
            stage_info = self._get_stage_info(task_id, stage)
            status["stages"][stage] = stage_info
            
            if not stage_info["done"] and not status["gap"]:
                status["gap"] = stage
        
        status["is_closed"] = all(s["done"] for s in status["stages"].values())
        return status
    
    def _get_stage_info(self, task_id, stage):
        """获取阶段信息（从memory中检索）"""
        # TODO: 实现从memory搜索逻辑
        return {"done": False, "time": None, "content": None}
    
    def generate_reminder(self, task_id):
        """生成闭环提醒"""
        status = self.check_loop_status(task_id)
        
        if status["is_closed"]:
            return None
            
        gap = status["gap"]
        templates = {
            "confirm": f"【任务 {task_id}】需要确认启动 - 请确认目标和验收标准",
            "execute": f"【任务 {task_id}】需要进度汇报 - 当前执行状态如何？",
            "report": f"【任务 {task_id}】需要完成汇报 - 请提交交付物和验证方式",
            "verify": f"【任务 {task_id}】等待验收 - 请用户确认验收结果"
        }
        
        return templates.get(gap, f"【任务 {task_id}】信息闭环缺失")
    
    def generate_report(self, task_id, report_type):
        """生成标准汇报"""
        templates = {
            "start": """
【任务启动】{task_id}
【目标】{goal}
【标准】{criteria}
【时间】{deadline}
【节点】{checkpoints}
等待你的确认...
""",
            "progress": """
【进度更新】{task_id}
【已完成】{completed}
【进行中】{in_progress}
【阻塞】{blockers}
【变更】{changes}
""",
            "complete": """
【任务完成】{task_id}
【交付物】{deliverables}
【验证】{verification}
【质量】{quality}
请你验收...
"""
        }
        return templates.get(report_type, "未知汇报类型")
    
    def global_scan(self):
        """全局扫描所有任务"""
        self.load_tasks()
        unclosed = []
        
        for task in self.tasks:
            status = self.check_loop_status(task["id"])
            if not status["is_closed"]:
                unclosed.append({
                    "task_id": task["id"],
                    "gap": status["gap"],
                    "reminder": self.generate_reminder(task["id"])
                })
        
        return unclosed
    
    def run_hourly_check(self):
        """每小时检查"""
        unclosed = self.global_scan()
        
        if unclosed:
            report = "【信息闭环检查】发现 {} 个未闭环任务\n\n".format(len(unclosed))
            for item in unclosed:
                report += f"- {item['task_id']}: {item['reminder']}\n"
            return report
        
        return "【信息闭环检查】所有任务已闭环 ✅"
    
    def log_event(self, event_type, task_id, details):
        """记录事件"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "task_id": task_id,
            "details": details
        }
        self.log.append(entry)
        
        # 写入日志文件
        log_file = CONFIG["memory_path"] / CONFIG["log_file"]
        with open(log_file, "a") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def main():
    """主函数"""
    closer = InfoLoopCloser()
    
    # 解析命令行参数
    import sys
    if len(sys.argv) < 2:
        print("Usage: info-loop-automation.py [check|scan|report]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "check":
        task_id = sys.argv[2] if len(sys.argv) > 2 else None
        if task_id:
            status = closer.check_loop_status(task_id)
            print(json.dumps(status, indent=2, ensure_ascii=False))
        else:
            print("Please specify task_id")
            
    elif command == "scan":
        unclosed = closer.global_scan()
        print(json.dumps(unclosed, indent=2, ensure_ascii=False))
        
    elif command == "hourly":
        result = closer.run_hourly_check()
        print(result)
        
    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()
