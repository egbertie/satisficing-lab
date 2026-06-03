#!/usr/bin/env python3
"""
interrupt_recovery_integration.py
中断恢复机制集成 - 不新增监控，只整合到现有流程
"""

import sys
import os
sys.path.insert(0, '/root/.openclaw/workspace/skills/interrupt-recovery')

from interrupt_tracker import InterruptTracker
from retry_scheduler import RetryScheduler, format_retry_schedule
from recovery_checker import RecoveryChecker
from rate_limiter import check_rate, record

class InterruptRecoveryIntegration:
    """
    中断恢复集成器
    
    设计原则：
    - 不新增独立监控进程（避免Token消耗）
    - 只在实际任务中使用
    - 失败时自动重试，不重试时立即报告
    """
    
    def __init__(self):
        self.tracker = InterruptTracker()
        self.scheduler = RetryScheduler(tracker=self.tracker, verbose=False)
        self.checker = RecoveryChecker()
    
    def execute_with_recovery(self, task_id: str, task_type: str, 
                             steps: int, 
                             execute_func, 
                             *args, **kwargs):
        """
        执行任务，支持中断恢复
        
        使用方式：
            recovery = InterruptRecoveryIntegration()
            result = recovery.execute_with_recovery(
                "skill-build-001",
                "skill_creation", 
                5,
                build_skill_function,
                param1, param2
            )
        """
        # 检查频限
        if not check_rate():
            print("⚠️  接近频限，暂停执行")
            return None
        
        record()  # 记录这次调用
        
        # 检查是否有未恢复的中断任务
        interrupted = self.tracker.get_last_interrupted()
        if interrupted:
            info = self.tracker.get_recovery_info()
            print(f"🔄 发现中断任务: {info['task_id']} @ {info['checkpoint']}")
            
            if self.tracker.should_retry():
                print(f"🔄 尝试恢复（第{info['attempts']+1}次）")
            else:
                print("⚠️  已达到最大重试次数，需要人工介入")
                return None
        
        # 开始新任务或恢复旧任务
        if not interrupted:
            self.tracker.start_task(task_id, task_type, steps)
        else:
            self.tracker.mark_recovering()
        
        try:
            # 执行实际任务
            result = execute_func(*args, **kwargs)
            
            # 标记完成
            self.tracker.mark_completed({"result": str(result)})
            return result
            
        except Exception as e:
            # 标记中断
            error_msg = str(e)
            self.tracker.mark_interrupted("execution_failed", error_msg)
            
            # 如果是API rate limit，特殊处理
            if "rate limit" in error_msg.lower():
                print(f"⚠️  触发频限，任务中断: {task_id}")
                print(f"⏱️  请等待3-5小时后重试")
                
                # 不自动重试rate limit，等待人工决策
                return None
            
            # 其他错误，尝试恢复
            if self.tracker.should_retry():
                print(f"🔄 执行失败，准备重试...")
                # 这里可以递归调用，但避免无限递归
                return None
            else:
                print(f"❌ 任务失败且无法恢复: {task_id}")
                return None
    
    def quick_execute(self, task_func, *args, **kwargs):
        """
        快速执行，只记录不恢复
        适用于简单任务
        """
        if not check_rate():
            print("⚠️  接近频限，暂停")
            return None
        
        record()
        
        try:
            return task_func(*args, **kwargs)
        except Exception as e:
            if "rate limit" in str(e).lower():
                print("⚠️  频限触发，暂停工作")
            raise


# 全局实例
_recovery = None

def get_recovery():
    """获取全局恢复实例"""
    global _recovery
    if _recovery is None:
        _recovery = InterruptRecoveryIntegration()
    return _recovery


def with_recovery(task_id: str, task_type: str, steps: int = 1):
    """装饰器：为函数添加中断恢复能力"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            recovery = get_recovery()
            return recovery.execute_with_recovery(
                task_id, task_type, steps,
                func, *args, **kwargs
            )
        return wrapper
    return decorator
