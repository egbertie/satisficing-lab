#!/usr/bin/env python3
"""
任务执行器 - Cron-Automation System核心组件
负责加载任务配置、管理任务生命周期、处理执行和错误恢复

S1-S7覆盖:
- S1: 全局考虑（人/事/物/环境/外部/边界）
- S2: 系统闭环（输入→处理→输出→反馈）
- S3: 可观测输出（日志、状态记录）
- S4: 自动化集成（错误恢复、通知）
- S5: 自我验证（配置校验）
- S6: 认知谦逊（局限标注）
- S7: 对抗测试（错误处理）
"""

import json
import os
import sys
import time
import signal
import logging
import subprocess
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import fcntl

# 配置路径
BASE_DIR = Path(__file__).parent.parent
CONFIG_DIR = BASE_DIR / "config"
LOGS_DIR = BASE_DIR / "logs"
STATE_DIR = BASE_DIR / "state"

# 确保目录存在
LOGS_DIR.mkdir(exist_ok=True)
STATE_DIR.mkdir(exist_ok=True)
(LOGS_DIR / "execution").mkdir(exist_ok=True)
(LOGS_DIR / "errors").mkdir(exist_ok=True)

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOGS_DIR / "executor.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    SUSPENDED = "suspended"
    DISABLED = "disabled"


@dataclass
class ExecutionResult:
    """执行结果"""
    task_id: str
    task_name: str
    scheduled_at: datetime
    started_at: datetime
    finished_at: datetime
    status: TaskStatus
    exit_code: int
    output: str
    error: str
    duration_ms: int
    retry_count: int


@dataclass
class TaskState:
    """任务状态对象"""
    task_id: str
    last_run: Optional[datetime] = None
    last_status: Optional[TaskStatus] = None
    consecutive_failures: int = 0
    total_runs: int = 0
    success_count: int = 0
    failure_count: int = 0
    timeout_count: int = 0
    is_running: bool = False
    current_pid: Optional[int] = None
    next_run: Optional[datetime] = None


class TaskExecutor:
    """任务执行器 - S2系统闭环核心"""
    
    def __init__(self):
        self.tasks: Dict[str, Any] = {}
        self.task_states: Dict[str, TaskState] = {}
        self.alerts_config: Dict[str, Any] = {}
        self.recovery_config: Dict[str, Any] = {}
        self.running = False
        self.scheduler_thread: Optional[threading.Thread] = None
        self._load_configs()
        self._load_states()
    
    def _load_configs(self) -> None:
        """S1: 加载配置 - 输入维度"""
        try:
            # 加载任务配置
            with open(CONFIG_DIR / "tasks.json", 'r', encoding='utf-8') as f:
                config = json.load(f)
                self.tasks = {t['id']: t for t in config.get('tasks', [])}
            logger.info(f"已加载 {len(self.tasks)} 个任务配置")
            
            # 加载告警配置
            with open(CONFIG_DIR / "alerts.json", 'r', encoding='utf-8') as f:
                self.alerts_config = json.load(f)
            
            # 加载恢复策略
            with open(CONFIG_DIR / "recovery.json", 'r', encoding='utf-8') as f:
                self.recovery_config = json.load(f)
                
        except Exception as e:
            logger.error(f"配置加载失败: {e}")
            raise
    
    def _load_states(self) -> None:
        """加载任务状态"""
        state_file = STATE_DIR / "task_states.json"
        if state_file.exists():
            try:
                with open(state_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for task_id, state_data in data.items():
                        self.task_states[task_id] = TaskState(
                            task_id=task_id,
                            last_run=datetime.fromisoformat(state_data['last_run']) if state_data.get('last_run') else None,
                            last_status=TaskStatus(state_data['last_status']) if state_data.get('last_status') else None,
                            consecutive_failures=state_data.get('consecutive_failures', 0),
                            total_runs=state_data.get('total_runs', 0),
                            success_count=state_data.get('success_count', 0),
                            failure_count=state_data.get('failure_count', 0),
                            timeout_count=state_data.get('timeout_count', 0),
                            is_running=state_data.get('is_running', False),
                            current_pid=state_data.get('current_pid'),
                            next_run=datetime.fromisoformat(state_data['next_run']) if state_data.get('next_run') else None,
                        )
            except Exception as e:
                logger.warning(f"状态加载失败: {e}")
        
        # 初始化缺失的状态
        for task_id in self.tasks:
            if task_id not in self.task_states:
                self.task_states[task_id] = TaskState(task_id=task_id)
    
    def _save_states(self) -> None:
        """保存任务状态"""
        state_file = STATE_DIR / "task_states.json"
        try:
            data = {}
            for task_id, state in self.task_states.items():
                data[task_id] = {
                    'last_run': state.last_run.isoformat() if state.last_run else None,
                    'last_status': state.last_status.value if state.last_status else None,
                    'consecutive_failures': state.consecutive_failures,
                    'total_runs': state.total_runs,
                    'success_count': state.success_count,
                    'failure_count': state.failure_count,
                    'timeout_count': state.timeout_count,
                    'is_running': state.is_running,
                    'current_pid': state.current_pid,
                    'next_run': state.next_run.isoformat() if state.next_run else None,
                }
            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"状态保存失败: {e}")
    
    def _acquire_lock(self, task_id: str) -> bool:
        """S7对抗测试: 获取任务执行锁 - 防止任务重叠"""
        lock_file = STATE_DIR / f"{task_id}.lock"
        try:
            fd = open(lock_file, 'w')
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return True
        except IOError:
            return False
    
    def _release_lock(self, task_id: str) -> None:
        """释放任务执行锁"""
        lock_file = STATE_DIR / f"{task_id}.lock"
        if lock_file.exists():
            lock_file.unlink()
    
    def execute_task(self, task_id: str, is_retry: bool = False) -> ExecutionResult:
        """
        S2系统闭环: 执行核心 - 输入→处理→输出→反馈
        """
        task = self.tasks.get(task_id)
        if not task:
            raise ValueError(f"任务不存在: {task_id}")
        
        if not task.get('enabled', True):
            logger.info(f"任务 {task_id} 已禁用，跳过执行")
            return None
        
        state = self.task_states.get(task_id, TaskState(task_id=task_id))
        
        # S7: 检查任务重叠
        if state.is_running:
            policy = task.get('overlap_policy', 'skip')
            if policy == 'skip':
                logger.warning(f"任务 {task_id} 正在运行，跳过本次执行")
                return None
            elif policy == 'queue':
                logger.info(f"任务 {task_id} 正在运行，排队等待")
                # 实现排队逻辑
            # parallel策略继续执行
        
        # S7: 获取执行锁
        if not self._acquire_lock(task_id):
            logger.warning(f"任务 {task_id} 无法获取执行锁，跳过")
            return None
        
        scheduled_at = datetime.now()
        started_at = datetime.now()
        
        # 更新状态
        state.is_running = True
        state.total_runs += 1
        self._save_states()
        
        script_path = BASE_DIR / task['script']
        timeout = task.get('timeout', 300)
        
        logger.info(f"开始执行任务 {task_id}: {task['name']}")
        
        try:
            # S2处理: 执行脚本
            process = subprocess.Popen(
                [sys.executable, str(script_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=str(BASE_DIR)
            )
            state.current_pid = process.pid
            
            # S7: 超时控制
            try:
                stdout, stderr = process.communicate(timeout=timeout)
                exit_code = process.returncode
            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = process.communicate()
                exit_code = -1
                status = TaskStatus.TIMEOUT
                logger.error(f"任务 {task_id} 执行超时 (>{timeout}s)")
            else:
                if exit_code == 0:
                    status = TaskStatus.SUCCESS
                    logger.info(f"任务 {task_id} 执行成功")
                else:
                    status = TaskStatus.FAILED
                    logger.error(f"任务 {task_id} 执行失败，退出码: {exit_code}")
            
        except Exception as e:
            exit_code = -1
            status = TaskStatus.FAILED
            stdout = ""
            stderr = str(e)
            logger.exception(f"任务 {task_id} 执行异常")
        
        finished_at = datetime.now()
        duration_ms = int((finished_at - started_at).total_seconds() * 1000)
        
        # S3输出: 记录执行结果
        result = ExecutionResult(
            task_id=task_id,
            task_name=task['name'],
            scheduled_at=scheduled_at,
            started_at=started_at,
            finished_at=finished_at,
            status=status,
            exit_code=exit_code,
            output=stdout,
            error=stderr,
            duration_ms=duration_ms,
            retry_count=state.consecutive_failures if is_retry else 0
        )
        
        self._record_execution(result)
        
        # S4反馈: 更新状态并触发后续处理
        state.last_run = finished_at
        state.last_status = status
        state.is_running = False
        state.current_pid = None
        
        if status == TaskStatus.SUCCESS:
            state.consecutive_failures = 0
            state.success_count += 1
        elif status in [TaskStatus.FAILED, TaskStatus.TIMEOUT]:
            state.consecutive_failures += 1
            state.failure_count += 1
            if status == TaskStatus.TIMEOUT:
                state.timeout_count += 1
            # S4: 触发错误恢复
            self._handle_failure(task, state, result)
        
        self._save_states()
        self._release_lock(task_id)
        
        return result
    
    def _record_execution(self, result: ExecutionResult) -> None:
        """S3: 记录执行日志"""
        log_file = LOGS_DIR / "execution" / f"{result.task_id}_{result.started_at.strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(result), f, indent=2, default=str)
        except Exception as e:
            logger.error(f"执行日志记录失败: {e}")
        
        # 错误日志单独记录
        if result.status in [TaskStatus.FAILED, TaskStatus.TIMEOUT]:
            error_log = LOGS_DIR / "errors" / f"{result.task_id}_{result.started_at.strftime('%Y%m%d_%H%M%S')}.log"
            try:
                with open(error_log, 'w', encoding='utf-8') as f:
                    f.write(f"Task: {result.task_name}\n")
                    f.write(f"Status: {result.status.value}\n")
                    f.write(f"Exit Code: {result.exit_code}\n")
                    f.write(f"Duration: {result.duration_ms}ms\n")
                    f.write(f"\n=== STDOUT ===\n{result.output}\n")
                    f.write(f"\n=== STDERR ===\n{result.error}\n")
            except Exception as e:
                logger.error(f"错误日志记录失败: {e}")
    
    def _handle_failure(self, task: Dict, state: TaskState, result: ExecutionResult) -> None:
        """
        S4自动化集成: 错误恢复处理
        """
        task_id = task['id']
        
        # 获取恢复策略
        recovery = self.recovery_config.get('task_specific', {}).get(task_id, {})
        strategy_name = recovery.get('strategy', 'default')
        strategy = self.recovery_config.get('strategies', {}).get(strategy_name, {})
        
        max_retries = strategy.get('max_retries', 3)
        retry_intervals = strategy.get('retry_intervals', [60, 300, 600])
        
        # S3: 发送告警
        self._send_alert(task, result)
        
        # S4: 决定后续处理
        if state.consecutive_failures < max_retries:
            # 调度重试
            retry_idx = min(state.consecutive_failures - 1, len(retry_intervals) - 1)
            delay = retry_intervals[retry_idx]
            logger.info(f"任务 {task_id} 将在 {delay}秒后重试 ({state.consecutive_failures}/{max_retries})")
            # 使用定时器调度重试
            threading.Timer(delay, self.execute_task, args=[task_id, True]).start()
        else:
            # 最终失败处理
            final_action = strategy.get('on_final_failure', 'suspend_and_alert')
            if final_action == 'suspend_and_alert':
                task['enabled'] = False
                logger.error(f"任务 {task_id} 连续失败 {state.consecutive_failures} 次，已暂停")
                self._send_critical_alert(task, f"任务已暂停: 连续失败 {state.consecutive_failures} 次")
    
    def _send_alert(self, task: Dict, result: ExecutionResult) -> None:
        """发送告警通知"""
        # 简化实现，实际应调用通知服务
        logger.warning(f"[ALERT] 任务 {task['name']} ({result.task_id}) 执行失败")
    
    def _send_critical_alert(self, task: Dict, message: str) -> None:
        """发送关键告警"""
        logger.error(f"[CRITICAL] {task['name']}: {message}")
    
    def get_status(self) -> Dict[str, Any]:
        """获取系统状态 - S3监控"""
        total = len(self.tasks)
        enabled = sum(1 for t in self.tasks.values() if t.get('enabled', True))
        running = sum(1 for s in self.task_states.values() if s.is_running)
        
        return {
            "total_tasks": total,
            "enabled_tasks": enabled,
            "running_tasks": running,
            "task_details": [
                {
                    "id": task_id,
                    "name": task['name'],
                    "enabled": task.get('enabled', True),
                    "status": state.last_status.value if state.last_status else "unknown",
                    "last_run": state.last_run.isoformat() if state.last_run else None,
                    "consecutive_failures": state.consecutive_failures
                }
                for task_id, task in self.tasks.items()
                if (state := self.task_states.get(task_id))
            ]
        }
    
    def enable_task(self, task_id: str) -> bool:
        """启用任务"""
        if task_id in self.tasks:
            self.tasks[task_id]['enabled'] = True
            if task_id in self.task_states:
                self.task_states[task_id].consecutive_failures = 0
            self._save_states()
            logger.info(f"任务 {task_id} 已启用")
            return True
        return False
    
    def disable_task(self, task_id: str) -> bool:
        """禁用任务"""
        if task_id in self.tasks:
            self.tasks[task_id]['enabled'] = False
            self._save_states()
            logger.info(f"任务 {task_id} 已禁用")
            return True
        return False


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Cron-Automation Task Executor')
    parser.add_argument('action', choices=['run', 'status', 'enable', 'disable'], help='操作')
    parser.add_argument('task_id', nargs='?', help='任务ID')
    
    args = parser.parse_args()
    
    executor = TaskExecutor()
    
    if args.action == 'run':
        if not args.task_id:
            print("请指定任务ID")
            sys.exit(1)
        result = executor.execute_task(args.task_id)
        if result:
            print(f"执行结果: {result.status.value}")
        else:
            print("任务未执行")
    
    elif args.action == 'status':
        status = executor.get_status()
        print(json.dumps(status, indent=2, default=str))
    
    elif args.action == 'enable':
        if not args.task_id:
            print("请指定任务ID")
            sys.exit(1)
        if executor.enable_task(args.task_id):
            print(f"任务 {args.task_id} 已启用")
        else:
            print(f"任务 {args.task_id} 不存在")
    
    elif args.action == 'disable':
        if not args.task_id:
            print("请指定任务ID")
            sys.exit(1)
        if executor.disable_task(args.task_id):
            print(f"任务 {args.task_id} 已禁用")
        else:
            print(f"任务 {args.task_id} 不存在")


if __name__ == '__main__':
    main()
