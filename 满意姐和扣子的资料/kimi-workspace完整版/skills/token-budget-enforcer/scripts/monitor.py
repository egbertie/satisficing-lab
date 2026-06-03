#!/usr/bin/env python3
"""
Token消耗实时监控器 (Monitor)
S4标准: 实时监控自动触发
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, asdict
import threading

@dataclass
class MonitorAlert:
    """监控告警"""
    timestamp: str
    level: str  # info, warning, critical, emergency
    metric: str
    current_value: float
    threshold: float
    message: str
    action_taken: str

class TokenMonitor:
    """Token消耗实时监控器"""
    
    def __init__(self, data_dir: str = None, check_interval: int = 5):
        if data_dir is None:
            data_dir = Path(__file__).parent.parent / "data"
        self.data_dir = Path(data_dir)
        self.consumption_file = self.data_dir / "consumption.json"
        
        self.check_interval = check_interval  # 检查间隔(秒)
        self.running = False
        self.monitor_thread = None
        
        # 告警阈值
        self.thresholds = {
            "usage_warning": 70,
            "usage_critical": 90,
            "usage_exhausted": 100,
            "single_task_soft": 1.5,
            "single_task_hard": 2.0,
            "efficiency_drop": 0.7
        }
        
        # 告警回调
        self.alert_handlers: List[Callable] = []
        self.alert_history: List[MonitorAlert] = []
        
        # 当前状态
        self.current_usage = 0
        self.daily_budget = 50000
        self.active_tasks = {}
    
    def _load_consumption_data(self) -> dict:
        """加载消耗数据"""
        if self.consumption_file.exists():
            with open(self.consumption_file, 'r') as f:
                return json.load(f)
        return {"daily_records": {}}
    
    def register_alert_handler(self, handler: Callable):
        """注册告警处理器"""
        self.alert_handlers.append(handler)
    
    def _trigger_alert(self, alert: MonitorAlert):
        """触发告警"""
        self.alert_history.append(alert)
        
        # 调用所有处理器
        for handler in self.alert_handlers:
            try:
                handler(alert)
            except Exception as e:
                print(f"Alert handler error: {e}")
        
        # 控制台输出
        emoji = {
            "info": "ℹ️",
            "warning": "🟡",
            "critical": "🔴",
            "emergency": "🚨"
        }
        print(f"{emoji.get(alert.level, '⚠️')} [{alert.level.upper()}] {alert.message}")
        print(f"   指标: {alert.metric} = {alert.current_value:.1f}% (阈值: {alert.threshold}%)")
    
    def check_budget_usage(self) -> Optional[MonitorAlert]:
        """检查预算使用率"""
        data = self._load_consumption_data()
        today = datetime.now().strftime("%Y-%m-%d")
        
        if today in data.get("daily_records", {}):
            record = data["daily_records"][today]
            usage_pct = (record["total_used"] / record["total_budget"]) * 100
        else:
            usage_pct = 0
        
        self.current_usage = usage_pct
        
        if usage_pct >= self.thresholds["usage_exhausted"]:
            return MonitorAlert(
                timestamp=datetime.now().isoformat(),
                level="emergency",
                metric="daily_usage",
                current_value=usage_pct,
                threshold=self.thresholds["usage_exhausted"],
                message="日预算已耗尽！仅P0任务可继续",
                action_taken="block_non_p0"
            )
        elif usage_pct >= self.thresholds["usage_critical"]:
            return MonitorAlert(
                timestamp=datetime.now().isoformat(),
                level="critical",
                metric="daily_usage",
                current_value=usage_pct,
                threshold=self.thresholds["usage_critical"],
                message="预算使用超过90%，进入紧急状态",
                action_taken="alert_and_throttle"
            )
        elif usage_pct >= self.thresholds["usage_warning"]:
            return MonitorAlert(
                timestamp=datetime.now().isoformat(),
                level="warning",
                metric="daily_usage",
                current_value=usage_pct,
                threshold=self.thresholds["usage_warning"],
                message="预算使用超过70%，请注意",
                action_taken="notify"
            )
        
        return None
    
    def check_task_consumption(self, task_id: str, estimated: int, actual: int) -> Optional[MonitorAlert]:
        """检查单个任务消耗"""
        if estimated == 0:
            ratio = float('inf') if actual > 0 else 0
        else:
            ratio = actual / estimated
        
        if ratio >= self.thresholds["single_task_hard"]:
            return MonitorAlert(
                timestamp=datetime.now().isoformat(),
                level="critical",
                metric=f"task_{task_id}_consumption",
                current_value=ratio * 100,
                threshold=self.thresholds["single_task_hard"] * 100,
                message=f"任务{task_id}消耗超过预估{ratio*100:.0f}%，触发熔断",
                action_taken="circuit_breaker"
            )
        elif ratio >= self.thresholds["single_task_soft"]:
            return MonitorAlert(
                timestamp=datetime.now().isoformat(),
                level="warning",
                metric=f"task_{task_id}_consumption",
                current_value=ratio * 100,
                threshold=self.thresholds["single_task_soft"] * 100,
                message=f"任务{task_id}消耗超过预估{ratio*100:.0f}%，请注意",
                action_taken="warn"
            )
        
        return None
    
    def check_efficiency(self, efficiency_score: float) -> Optional[MonitorAlert]:
        """检查效率指标"""
        if efficiency_score < self.thresholds["efficiency_drop"]:
            return MonitorAlert(
                timestamp=datetime.now().isoformat(),
                level="warning",
                metric="efficiency_score",
                current_value=efficiency_score * 100,
                threshold=self.thresholds["efficiency_drop"] * 100,
                message=f"效率评分下降到{efficiency_score*100:.0f}%，低于阈值",
                action_taken="efficiency_audit"
            )
        return None
    
    def monitor_cycle(self):
        """单次监控循环"""
        # 检查预算使用率
        alert = self.check_budget_usage()
        if alert:
            self._trigger_alert(alert)
        
        # 检查活跃任务（模拟）
        for task_id, task_info in self.active_tasks.items():
            if task_info.get("completed"):
                alert = self.check_task_consumption(
                    task_id,
                    task_info["estimated"],
                    task_info["actual"]
                )
                if alert:
                    self._trigger_alert(alert)
    
    def start_monitoring(self):
        """启动持续监控 (S4: 实时监控自动触发)"""
        self.running = True
        
        def monitor_loop():
            while self.running:
                self.monitor_cycle()
                time.sleep(self.check_interval)
        
        self.monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitor_thread.start()
        print(f"🟢 Token监控已启动，检查间隔: {self.check_interval}秒")
    
    def stop_monitoring(self):
        """停止监控"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        print("🔴 Token监控已停止")
    
    def get_status(self) -> dict:
        """获取当前监控状态"""
        return {
            "running": self.running,
            "current_usage_percent": self.current_usage,
            "daily_budget": self.daily_budget,
            "active_tasks": len(self.active_tasks),
            "alert_count_last_hour": len([
                a for a in self.alert_history
                if (datetime.now() - datetime.fromisoformat(a.timestamp)).seconds < 3600
            ]),
            "last_check": datetime.now().isoformat()
        }
    
    def get_alert_history(self, limit: int = 50) -> List[dict]:
        """获取告警历史"""
        return [asdict(a) for a in self.alert_history[-limit:]]


def main():
    """命令行接口"""
    import sys
    
    monitor = TokenMonitor()
    
    if len(sys.argv) < 2:
        # 单次检查模式
        alert = monitor.check_budget_usage()
        if alert:
            print(f"⚠️ 告警: {alert.message}")
            print(f"   当前使用率: {alert.current_value:.1f}%")
        else:
            status = monitor.get_status()
            print(f"✅ 预算状态正常")
            print(f"   当前使用率: {status['current_usage_percent']:.1f}%")
        return 0
    
    command = sys.argv[1]
    
    if command == "start":
        # 持续监控模式
        monitor.start_monitoring()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            monitor.stop_monitoring()
    
    elif command == "status":
        status = monitor.get_status()
        print(json.dumps(status, indent=2))
    
    elif command == "alerts":
        history = monitor.get_alert_history()
        print(json.dumps(history, indent=2))
    
    else:
        print(f"Unknown command: {command}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
