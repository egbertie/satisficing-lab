#!/usr/bin/env python3
"""
retry_scheduler.py
重试调度器 - 实现指数退避重试策略
"""

import time
import random
from datetime import datetime, timedelta
from typing import Callable, Optional, Dict, Any
from enum import Enum

class RetryStatus(Enum):
    """重试状态"""
    PENDING = "pending"
    WAITING = "waiting"
    CHECKING = "checking"
    RECOVERING = "recovering"
    SUCCESS = "success"
    FAILED = "failed"
    MAX_RETRIES_EXCEEDED = "max_retries_exceeded"

# 重试间隔（秒）：30s, 2min, 5min, 15min
RETRY_INTERVALS = [30, 120, 300, 900]
MAX_RETRIES = len(RETRY_INTERVALS)

# 添加随机抖动，避免多个任务同时重试
JITTER_RANGE = (0.8, 1.2)

class RetryScheduler:
    """
    重试调度器
    
    实现指数退避策略，支持：
    - 固定间隔重试
    - 条件检查
    - 随机抖动
    - 最大重试限制
    """
    
    def __init__(self, tracker=None, verbose: bool = True):
        self.tracker = tracker
        self.verbose = verbose
        self.status = RetryStatus.PENDING
        self.last_error = None
    
    def _log(self, message: str):
        """输出日志"""
        if self.verbose:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] {message}")
    
    def calculate_wait_time(self, attempt_count: int) -> int:
        """
        计算等待时间（带抖动）
        
        Args:
            attempt_count: 已尝试次数（从0开始）
        
        Returns:
            等待秒数
        """
        if attempt_count >= MAX_RETRIES:
            return -1
        
        base_delay = RETRY_INTERVALS[attempt_count]
        jitter = random.uniform(*JITTER_RANGE)
        return int(base_delay * jitter)
    
    def calculate_next_retry_time(self, attempt_count: int) -> Optional[datetime]:
        """计算下次重试时间"""
        wait_seconds = self.calculate_wait_time(attempt_count)
        if wait_seconds < 0:
            return None
        return datetime.now() + timedelta(seconds=wait_seconds)
    
    def wait(self, seconds: int, check_interval: int = 5,
             cancel_check: Optional[Callable] = None) -> bool:
        """
        等待指定时间，支持取消检查
        
        Args:
            seconds: 等待秒数
            check_interval: 检查间隔（秒）
            cancel_check: 取消检查函数，返回True则取消等待
        
        Returns:
            是否完成等待（False表示被取消）
        """
        self.status = RetryStatus.WAITING
        waited = 0
        
        while waited < seconds:
            if cancel_check and cancel_check():
                self._log("⛔ 等待被取消")
                return False
            
            sleep_time = min(check_interval, seconds - waited)
            time.sleep(sleep_time)
            waited += sleep_time
            
            # 每30秒输出一次进度
            if waited % 30 == 0 or waited == sleep_time:
                remaining = seconds - waited
                self._log(f"⏱️  等待中... 已等待{waited}s，还剩{remaining}s")
        
        return True
    
    def attempt_recovery(self, 
                        recovery_func: Callable[[], Any],
                        check_func: Callable[[], bool],
                        tracker=None,
                        on_success: Optional[Callable] = None,
                        on_failure: Optional[Callable] = None) -> RetryStatus:
        """
        尝试恢复
        
        Args:
            recovery_func: 恢复执行函数
            check_func: 恢复条件检查函数
            tracker: 中断追踪器（可选）
            on_success: 成功回调
            on_failure: 失败回调
        
        Returns:
            RetryStatus
        """
        # 获取当前尝试次数
        attempt_count = 0
        if tracker:
            info = tracker.get_recovery_info()
            if info:
                attempt_count = info.get("attempts", 0)
        
        # 检查是否超过最大重试次数
        if attempt_count >= MAX_RETRIES:
            self.status = RetryStatus.MAX_RETRIES_EXCEEDED
            self._log(f"⚠️ 已达到最大自动重试次数({MAX_RETRIES})，需要人工介入")
            if on_failure:
                on_failure("max_retries_exceeded")
            return self.status
        
        # 计算等待时间
        wait_seconds = self.calculate_wait_time(attempt_count)
        next_retry = datetime.now() + timedelta(seconds=wait_seconds)
        
        self._log(f"🔄 第{attempt_count + 1}次重试")
        self._log(f"⏱️  将在{wait_seconds}秒后尝试（约{next_retry.strftime('%H:%M:%S')}）")
        
        # 等待
        completed = self.wait(wait_seconds)
        if not completed:
            self.status = RetryStatus.PENDING
            return self.status
        
        # 检查恢复条件
        self.status = RetryStatus.CHECKING
        self._log("🔍 检查恢复条件...")
        
        if not check_func():
            self._log("❌ 恢复条件不满足，将等待下次重试")
            self.status = RetryStatus.FAILED
            if tracker:
                tracker.mark_interrupted("recovery_conditions_not_met")
            return self.status
        
        # 执行恢复
        self.status = RetryStatus.RECOVERING
        self._log("✅ 恢复条件满足，开始恢复执行")
        
        if tracker:
            tracker.mark_recovering()
        
        try:
            result = recovery_func()
            self.status = RetryStatus.SUCCESS
            self._log("✅ 恢复执行成功")
            
            if tracker:
                tracker.mark_completed({"recovery_result": result})
            
            if on_success:
                on_success(result)
            
            return self.status
            
        except Exception as e:
            self.status = RetryStatus.FAILED
            self.last_error = str(e)
            self._log(f"❌ 恢复执行失败: {e}")
            
            if tracker:
                tracker.mark_interrupted("recovery_execution_failed", str(e))
            
            if on_failure:
                on_failure(str(e))
            
            return self.status
    
    def run_recovery_loop(self,
                         recovery_func: Callable[[], Any],
                         check_func: Callable[[], bool],
                         tracker=None,
                         max_total_attempts: int = 4,
                         on_success: Optional[Callable] = None,
                         on_max_retries: Optional[Callable] = None) -> RetryStatus:
        """
        运行恢复循环，直到成功或达到最大重试次数
        
        Args:
            recovery_func: 恢复执行函数
            check_func: 恢复条件检查函数
            tracker: 中断追踪器
            max_total_attempts: 最大总尝试次数
            on_success: 成功回调
            on_max_retries: 达到最大重试次数回调
        
        Returns:
            RetryStatus
        """
        for attempt in range(max_total_attempts):
            status = self.attempt_recovery(
                recovery_func=recovery_func,
                check_func=check_func,
                tracker=tracker,
                on_success=on_success
            )
            
            if status == RetryStatus.SUCCESS:
                return status
            
            if status == RetryStatus.MAX_RETRIES_EXCEEDED:
                if on_max_retries:
                    on_max_retries()
                return status
        
        return self.status


def format_retry_schedule() -> str:
    """格式化重试计划表"""
    lines = ["重试计划表:", "=" * 40]
    for i, seconds in enumerate(RETRY_INTERVALS):
        minutes = seconds / 60
        if minutes >= 1:
            time_str = f"{int(minutes)}分{seconds % 60}秒"
        else:
            time_str = f"{seconds}秒"
        lines.append(f"第{i+1}次: 等待{time_str}")
    lines.append(f"第{MAX_RETRIES+1}次: 人工介入")
    return "\n".join(lines)


if __name__ == "__main__":
    # 测试
    print(format_retry_schedule())
    print()
    
    scheduler = RetryScheduler(verbose=True)
    
    # 模拟恢复函数
    call_count = 0
    def mock_recovery():
        global call_count
        call_count += 1
        if call_count < 2:
            raise Exception("模拟失败")
        return {"status": "success"}
    
    def mock_check():
        return True
    
    # 测试单次恢复
    print("\n测试单次恢复:")
    status = scheduler.attempt_recovery(mock_recovery, mock_check)
    print(f"结果: {status.value}")
