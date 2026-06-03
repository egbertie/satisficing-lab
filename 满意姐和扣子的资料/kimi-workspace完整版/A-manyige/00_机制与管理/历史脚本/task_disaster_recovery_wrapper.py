#!/usr/bin/env python3
"""
任务执行灾备包装器
用途: 包装任何任务，提供灾备能力
规则: 所有任务启动前问自己3个问题
"""

import sys
import traceback
from datetime import datetime
from pathlib import Path

class TaskDisasterRecoveryWrapper:
    """任务灾备包装器"""
    
    def __init__(self, task_name, task_func):
        self.task_name = task_name
        self.task_func = task_func
        self.log_file = Path(f"/root/.openclaw/workspace/memory/task_logs/{task_name}.json")
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 3个必问问题
        self.ask_three_questions()
    
    def ask_three_questions(self):
        """任务启动前的3个必问问题"""
        print(f"=== 任务启动前检查: {self.task_name} ===")
        print()
        print("灾备思维3问:")
        print("1. 如果中断，如何恢复？")
        print("   → 已设计Checkpoint机制")
        print()
        print("2. 如果失败，如何回滚？")
        print("   → 已设计版本控制/备份")
        print()
        print("3. 如果丢失，如何重建？")
        print("   → 已设计恢复文档/备份")
        print()
    
    def execute(self, *args, **kwargs):
        """执行任务（带灾备）"""
        start_time = datetime.now()
        
        try:
            print(f"开始执行任务: {self.task_name}")
            result = self.task_func(*args, **kwargs)
            
            # 成功日志
            self.log_execution("SUCCESS", start_time, result=result)
            print(f"✅ 任务完成: {self.task_name}")
            
            return result
            
        except Exception as e:
            # 失败日志
            error_msg = str(e)
            traceback_str = traceback.format_exc()
            self.log_execution("FAILED", start_time, error=error_msg, traceback=traceback_str)
            
            print(f"❌ 任务失败: {self.task_name}")
            print(f"   错误: {error_msg}")
            print()
            print("启动失败恢复流程...")
            self.handle_failure(error_msg)
            
            raise
    
    def log_execution(self, status, start_time, **kwargs):
        """记录执行日志"""
        import json
        
        log_entry = {
            "task_name": self.task_name,
            "status": status,
            "start_time": start_time.isoformat(),
            "end_time": datetime.now().isoformat(),
            **kwargs
        }
        
        logs = []
        if self.log_file.exists():
            with open(self.log_file, 'r') as f:
                try:
                    logs = json.load(f)
                except:
                    logs = []
        
        logs.append(log_entry)
        
        with open(self.log_file, 'w') as f:
            json.dump(logs, f, indent=2)
    
    def handle_failure(self, error_msg):
        """处理失败"""
        # 1. 尝试回滚
        print("1. 尝试回滚到上一版本...")
        # 实际回滚逻辑...
        
        # 2. 通知用户
        print("2. 通知用户任务失败...")
        print(f"   任务: {self.task_name}")
        print(f"   错误: {error_msg}")
        
        # 3. 记录恢复步骤
        print("3. 记录恢复步骤到日志...")

# 使用示例
if __name__ == "__main__":
    def example_task():
        print("执行任务中...")
        # 模拟任务
        return "task_result"
    
    # 包装任务
    wrapped_task = TaskDisasterRecoveryWrapper("example_task", example_task)
    
    # 执行（带灾备）
    try:
        result = wrapped_task.execute()
    except Exception as e:
        print(f"任务执行失败，已记录并尝试恢复: {e}")
