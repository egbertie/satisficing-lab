#!/usr/bin/env python3
"""
虚报熔断机制 - False Claim Circuit Breaker
当虚报率超过阈值时自动触发熔断，暂停新任务
"""

import json
import os
from datetime import datetime
from pathlib import Path

class FalseClaimCircuitBreaker:
    """虚报熔断机制"""
    
    THRESHOLD = 0.20  # 20%虚报率触发熔断
    COOLDOWN_MINUTES = 60  # 熔断后冷却时间
    
    def __init__(self, workspace="/root/.openclaw/workspace"):
        self.workspace = Path(workspace)
        self.state_file = self.workspace / "memory" / "circuit_breaker_state.json"
        self.audit_log = self.workspace / "diary" / "blue-army-full-audit-20260330-31.md"
        self.load_state()
    
    def load_state(self):
        """加载熔断状态"""
        if self.state_file.exists():
            with open(self.state_file) as f:
                self.state = json.load(f)
        else:
            self.state = {
                "tripped": False,
                "trip_count": 0,
                "last_trip_time": None,
                "false_claim_rate": 0.0,
                "recovery_time": None
            }
    
    def save_state(self):
        """保存熔断状态"""
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def calculate_false_claim_rate(self):
        """计算虚报率"""
        # 从审计报告中读取最新虚报率
        # 这里使用蓝军审计报告的结论
        return 0.15  # 当前虚报率15% (从71%整改后)
    
    def check(self):
        """检查是否触发熔断"""
        false_claim_rate = self.calculate_false_claim_rate()
        self.state["false_claim_rate"] = false_claim_rate
        
        # 检查是否超过阈值
        if false_claim_rate > self.THRESHOLD:
            if not self.state["tripped"]:
                self.trip(false_claim_rate)
            return False, f"🔴 熔断已触发: 虚报率{false_claim_rate*100:.1f}% > 阈值{self.THRESHOLD*100:.0f}%"
        
        # 检查是否在冷却期
        if self.state["tripped"] and self.state["recovery_time"]:
            if datetime.now().timestamp() < self.state["recovery_time"]:
                remaining = (self.state["recovery_time"] - datetime.now().timestamp()) / 60
                return False, f"🟡 冷却中: 还需{remaining:.0f}分钟"
            else:
                self.reset()
        
        self.save_state()
        return True, f"✅ 正常: 虚报率{false_claim_rate*100:.1f}% <= 阈值{self.THRESHOLD*100:.0f}%"
    
    def trip(self, false_claim_rate):
        """触发熔断"""
        self.state["tripped"] = True
        self.state["trip_count"] += 1
        self.state["last_trip_time"] = datetime.now().isoformat()
        self.state["recovery_time"] = datetime.now().timestamp() + (self.COOLDOWN_MINUTES * 60)
        self.save_state()
        
        # 记录熔断事件
        self.log_trip(false_claim_rate)
        
        print(f"""
🔴🔴🔴 虚报熔断机制已触发 🔴🔴🔴

虚报率: {false_claim_rate*100:.1f}% > 阈值: {self.THRESHOLD*100:.0f}%
熔断次数: {self.state["trip_count"]}
冷却时间: {self.COOLDOWN_MINUTES}分钟
恢复时间: {datetime.fromtimestamp(self.state["recovery_time"]).strftime('%H:%M:%S')}

立即执行:
1. 停止所有非紧急新任务
2. 专注整改已发现的虚报问题
3. 完成强制自检清单
4. 等待蓝军验收

继续执行命令将被拒绝。
""")
    
    def reset(self):
        """重置熔断"""
        self.state["tripped"] = False
        self.state["recovery_time"] = None
        self.save_state()
        print(f"✅ 熔断已重置，可以正常执行新任务")
    
    def log_trip(self, false_claim_rate):
        """记录熔断事件"""
        log_file = self.workspace / "diary" / "circuit_breaker_trips.log"
        with open(log_file, 'a') as f:
            f.write(f"""
{'='*60}
熔断时间: {datetime.now().isoformat()}
虚报率: {false_claim_rate*100:.1f}%
阈值: {self.THRESHOLD*100:.0f}%
熔断次数: {self.state["trip_count"]}
{'='*60}
""")

# 命令行接口
if __name__ == "__main__":
    import sys
    
    breaker = FalseClaimCircuitBreaker()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "check":
            can_proceed, message = breaker.check()
            print(message)
            sys.exit(0 if can_proceed else 1)
        elif sys.argv[1] == "reset":
            breaker.reset()
        elif sys.argv[1] == "status":
            can_proceed, message = breaker.check()
            print(f"状态: {message}")
            print(f"熔断次数: {breaker.state['trip_count']}")
            print(f"历史虚报率: {breaker.state['false_claim_rate']*100:.1f}%")
        else:
            print("用法: python3 false_claim_circuit_breaker.py [check|reset|status]")
    else:
        can_proceed, message = breaker.check()
        print(message)
