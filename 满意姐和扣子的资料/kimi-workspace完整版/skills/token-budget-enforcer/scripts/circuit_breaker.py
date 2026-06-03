#!/usr/bin/env python3
"""
Token预算熔断器 (Circuit Breaker)
S2标准: 预算执行（监控→预警→熔断→调整→报告）
"""

import json
import time
from datetime import datetime
from pathlib import Path
from enum import Enum
from typing import Dict, Optional, List
from dataclasses import dataclass, asdict

class CircuitState(Enum):
    """熔断器状态"""
    CLOSED = "closed"       # 正常 - 允许通过
    OPEN = "open"          # 熔断 - 阻断
    HALF_OPEN = "half_open" # 半开 - 试探性允许

@dataclass
class CircuitBreakerRecord:
    """熔断记录"""
    timestamp: str
    task_id: str
    reason: str
    state_before: str
    state_after: str
    estimated: int
    actual: int
    resolution: Optional[str] = None
    resolved_at: Optional[str] = None

class TokenCircuitBreaker:
    """Token预算熔断器"""
    
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            data_dir = Path(__file__).parent.parent / "data"
        self.data_dir = Path(data_dir)
        self.records_file = self.data_dir / "circuit_breaker_records.json"
        
        # 熔断阈值
        self.soft_limit = 1.5   # 150% 预警
        self.hard_limit = 2.0   # 200% 熔断
        self.emergency_limit = 3.0  # 300% P0可覆盖
        
        # 状态
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.cooldown_seconds = 300  # 冷却时间5分钟
        
        # 记录
        self.records: List[CircuitBreakerRecord] = []
        self._load_records()
    
    def _load_records(self):
        """加载历史熔断记录"""
        if self.records_file.exists():
            with open(self.records_file, 'r') as f:
                data = json.load(f)
                self.records = [CircuitBreakerRecord(**r) for r in data.get("records", [])]
    
    def _save_records(self):
        """保存熔断记录"""
        self.records_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.records_file, 'w') as f:
            json.dump({
                "records": [asdict(r) for r in self.records]
            }, f, indent=2)
    
    def check(self, task_id: str, estimated: int, actual: int, is_p0: bool = False) -> dict:
        """
        检查是否需要熔断
        
        Returns:
            {
                "allowed": bool,
                "state": str,
                "action": str,
                "reason": str
            }
        """
        if estimated == 0:
            ratio = float('inf') if actual > 0 else 0
        else:
            ratio = actual / estimated
        
        # 检查当前状态
        if self.state == CircuitState.OPEN:
            # 检查是否过了冷却期
            if self.last_failure_time:
                elapsed = (datetime.now() - datetime.fromisoformat(self.last_failure_time)).seconds
                if elapsed > self.cooldown_seconds:
                    self.state = CircuitState.HALF_OPEN
                    print(f"🔓 熔断器进入半开状态，允许试探性任务")
                else:
                    remaining = self.cooldown_seconds - elapsed
                    # 即使在熔断状态，P0任务超过emergency_limit也应该被阻断
                    if is_p0 and ratio >= self.emergency_limit:
                        return {
                            "allowed": False,
                            "state": self.state.value,
                            "action": "block_p0_exceeds_emergency",
                            "reason": f"P0任务消耗({actual})超过预估({estimated})的{self.emergency_limit*100:.0f}% ({ratio*100:.0f}%)，即使P0也被阻断！"
                        }
                    return {
                        "allowed": is_p0,  # P0任务可以覆盖
                        "state": self.state.value,
                        "action": "block" if not is_p0 else "allow_p0_override",
                        "reason": f"熔断器开启中，冷却时间剩余{remaining}秒"
                    }
        
        # 判断是否需要熔断
        if ratio >= self.hard_limit:
            if is_p0 and ratio < self.emergency_limit:
                # P0任务可以覆盖硬限制（但不能超过紧急限制）
                self._record_circuit_event(task_id, "hard_limit_p0_override", estimated, actual)
                return {
                    "allowed": True,
                    "state": self.state.value,
                    "action": "allow_with_audit",
                    "reason": f"P0任务覆盖熔断（{ratio*100:.0f}%），已审计"
                }
            
            # 触发熔断
            self._trip_circuit(task_id, "hard_limit_exceeded", estimated, actual)
            return {
                "allowed": False,
                "state": self.state.value,
                "action": "circuit_breaker_triggered",
                "reason": f"消耗{actual}超过预估{estimated}的{self.hard_limit*100:.0f}% ({ratio*100:.0f}%)，熔断！"
            }
        
        elif ratio >= self.soft_limit:
            # 软限制，预警但不熔断
            return {
                "allowed": True,
                "state": self.state.value,
                "action": "warn",
                "reason": f"消耗{actual}超过预估{estimated}的{self.soft_limit*100:.0f}% ({ratio*100:.0f}%)，请注意"
            }
        
        # 正常通过
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= 3:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                print(f"✅ 熔断器关闭，恢复正常")
        
        return {
            "allowed": True,
            "state": self.state.value,
            "action": "allow",
            "reason": "正常通过"
        }
    
    def _trip_circuit(self, task_id: str, reason: str, estimated: int, actual: int):
        """触发熔断"""
        old_state = self.state
        self.state = CircuitState.OPEN
        self.failure_count += 1
        self.last_failure_time = datetime.now().isoformat()
        self.success_count = 0
        
        record = CircuitBreakerRecord(
            timestamp=datetime.now().isoformat(),
            task_id=task_id,
            reason=reason,
            state_before=old_state.value,
            state_after=self.state.value,
            estimated=estimated,
            actual=actual
        )
        self.records.append(record)
        self._save_records()
        
        print(f"🚨 熔断器触发！任务{task_id}被阻断")
        print(f"   原因: {reason}")
        print(f"   预估: {estimated}, 实际: {actual}")
    
    def _record_circuit_event(self, task_id: str, reason: str, estimated: int, actual: int):
        """记录熔断事件（非阻断）"""
        record = CircuitBreakerRecord(
            timestamp=datetime.now().isoformat(),
            task_id=task_id,
            reason=reason,
            state_before=self.state.value,
            state_after=self.state.value,
            estimated=estimated,
            actual=actual
        )
        self.records.append(record)
        self._save_records()
    
    def reset(self, reason: str = "manual"):
        """手动重置熔断器"""
        old_state = self.state
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        print(f"🔄 熔断器手动重置 ({reason})")
        print(f"   原状态: {old_state.value} -> 现状态: closed")
    
    def get_status(self) -> dict:
        """获取熔断器状态"""
        return {
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "last_failure": self.last_failure_time,
            "total_records": len(self.records),
            "thresholds": {
                "soft_limit": f"{self.soft_limit*100:.0f}%",
                "hard_limit": f"{self.hard_limit*100:.0f}%",
                "emergency_limit": f"{self.emergency_limit*100:.0f}%"
            }
        }
    
    def get_records(self, limit: int = 20) -> List[dict]:
        """获取熔断记录"""
        return [asdict(r) for r in self.records[-limit:]]
    
    def can_execute(self, pool_usage_percent: float) -> dict:
        """
        检查预算池是否可以执行
        S2: 预算执行监控
        """
        if pool_usage_percent >= 100:
            return {
                "can_execute": False,
                "reason": "预算池已耗尽",
                "suggestion": "等待次日重置或申请战略储备"
            }
        elif pool_usage_percent >= 90:
            return {
                "can_execute": True,
                "reason": "预算池紧急状态，谨慎执行",
                "suggestion": "考虑使用极简模式或分批执行"
            }
        elif pool_usage_percent >= 70:
            return {
                "can_execute": True,
                "reason": "预算池注意状态",
                "suggestion": "监控消耗"
            }
        else:
            return {
                "can_execute": True,
                "reason": "预算池状态正常",
                "suggestion": "正常执行"
            }


def main():
    """命令行接口"""
    import sys
    
    cb = TokenCircuitBreaker()
    
    if len(sys.argv) < 2:
        # 显示状态
        status = cb.get_status()
        print(json.dumps(status, indent=2))
        return 0
    
    command = sys.argv[1]
    
    if command == "check":
        if len(sys.argv) < 5:
            print("Usage: circuit_breaker.py check <task_id> <estimated> <actual> [--p0]")
            return 1
        
        task_id = sys.argv[2]
        estimated = int(sys.argv[3])
        actual = int(sys.argv[4])
        is_p0 = "--p0" in sys.argv
        
        result = cb.check(task_id, estimated, actual, is_p0)
        print(json.dumps(result, indent=2))
    
    elif command == "reset":
        reason = sys.argv[2] if len(sys.argv) > 2 else "manual"
        cb.reset(reason)
    
    elif command == "status":
        status = cb.get_status()
        print(json.dumps(status, indent=2))
    
    elif command == "records":
        records = cb.get_records()
        print(json.dumps(records, indent=2))
    
    else:
        print(f"Unknown command: {command}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
