#!/usr/bin/env python3
"""
Token预算分配器 (Allocator)
三级预算池分配管理
"""

import yaml
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple
from dataclasses import dataclass

@dataclass
class PoolStatus:
    """预算池状态"""
    name: str
    allocated: int
    used: int
    remaining: int
    usage_percent: float
    status: str  # normal, warning, critical, exhausted

class BudgetAllocator:
    """Token预算分配器"""
    
    def __init__(self, config_dir: str = None, data_dir: str = None):
        if config_dir is None:
            config_dir = Path(__file__).parent.parent / "config"
        if data_dir is None:
            data_dir = Path(__file__).parent.parent / "data"
        
        self.config_dir = Path(config_dir)
        self.data_dir = Path(data_dir)
        
        # 加载配置
        self.budget_config = self._load_yaml("budgets.yaml")
        self.threshold_config = self._load_yaml("thresholds.yaml")
        
        # 预算池
        self.pools = {}
        self._initialize_pools()
    
    def _load_yaml(self, filename: str) -> dict:
        """加载YAML配置"""
        filepath = self.config_dir / filename
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        return {}
    
    def _initialize_pools(self):
        """初始化预算池"""
        global_config = self.budget_config.get("global", {})
        daily_budget = global_config.get("daily_budget", 50000)
        
        pools_config = self.budget_config.get("budget_pools", {})
        
        for pool_name, config in pools_config.items():
            percentage = config.get("percentage", 0)
            self.pools[pool_name] = {
                "name": pool_name,
                "percentage": percentage,
                "daily_limit": int(daily_budget * percentage / 100),
                "used": 0,
                "description": config.get("description", ""),
                "approval_required": config.get("approval_required", False)
            }
    
    def get_pool_for_task(self, task_type: str) -> Tuple[str, dict]:
        """
        根据任务类型获取预算池
        返回: (pool_name, pool_config)
        """
        task_types = self.budget_config.get("task_types", {})
        task_config = task_types.get(task_type, {})
        
        pool_name = task_config.get("pool", "operational_budget")
        return pool_name, self.pools.get(pool_name, self.pools["operational_budget"])
    
    def check_availability(self, pool_name: str, amount: int) -> dict:
        """
        检查预算池是否有足够余额
        
        Returns:
            {
                "available": bool,
                "pool": str,
                "requested": int,
                "available_amount": int,
                "reason": str
            }
        """
        pool = self.pools.get(pool_name)
        if not pool:
            return {
                "available": False,
                "pool": pool_name,
                "requested": amount,
                "available_amount": 0,
                "reason": f"预算池 {pool_name} 不存在"
            }
        
        remaining = pool["daily_limit"] - pool["used"]
        
        if remaining < amount:
            return {
                "available": False,
                "pool": pool_name,
                "requested": amount,
                "available_amount": remaining,
                "reason": f"预算池 {pool_name} 余额不足 (需要{amount}, 剩余{remaining})"
            }
        
        return {
            "available": True,
            "pool": pool_name,
            "requested": amount,
            "available_amount": remaining,
            "reason": "预算充足"
        }
    
    def consume(self, pool_name: str, amount: int, task_id: str = None) -> dict:
        """
        从预算池扣减Token
        
        Returns:
            {
                "success": bool,
                "pool": str,
                "amount": int,
                "remaining": int,
                "usage_percent": float
            }
        """
        pool = self.pools.get(pool_name)
        if not pool:
            return {"success": False, "error": f"预算池 {pool_name} 不存在"}
        
        # 检查可用性
        check = self.check_availability(pool_name, amount)
        if not check["available"]:
            return {"success": False, "error": check["reason"]}
        
        # 扣减
        pool["used"] += amount
        remaining = pool["daily_limit"] - pool["used"]
        usage_percent = (pool["used"] / pool["daily_limit"]) * 100
        
        return {
            "success": True,
            "pool": pool_name,
            "amount": amount,
            "remaining": remaining,
            "usage_percent": round(usage_percent, 1)
        }
    
    def get_pool_status(self, pool_name: str = None) -> dict:
        """获取预算池状态"""
        if pool_name:
            pool = self.pools.get(pool_name)
            if not pool:
                return {"error": f"预算池 {pool_name} 不存在"}
            return self._format_pool_status(pool)
        
        return {
            name: self._format_pool_status(pool)
            for name, pool in self.pools.items()
        }
    
    def _format_pool_status(self, pool: dict) -> dict:
        """格式化预算池状态"""
        remaining = pool["daily_limit"] - pool["used"]
        usage_percent = (pool["used"] / pool["daily_limit"]) * 100 if pool["daily_limit"] > 0 else 0
        
        if usage_percent >= 100:
            status = "exhausted"
        elif usage_percent >= 90:
            status = "critical"
        elif usage_percent >= 70:
            status = "warning"
        else:
            status = "normal"
        
        return {
            "name": pool["name"],
            "allocated": pool["daily_limit"],
            "used": pool["used"],
            "remaining": remaining,
            "usage_percent": round(usage_percent, 1),
            "status": status,
            "description": pool["description"],
            "approval_required": pool["approval_required"]
        }
    
    def get_total_status(self) -> dict:
        """获取整体预算状态"""
        total_allocated = sum(p["daily_limit"] for p in self.pools.values())
        total_used = sum(p["used"] for p in self.pools.values())
        total_remaining = total_allocated - total_used
        usage_percent = (total_used / total_allocated) * 100 if total_allocated > 0 else 0
        
        return {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "total_budget": total_allocated,
            "total_used": total_used,
            "total_remaining": total_remaining,
            "usage_percent": round(usage_percent, 1),
            "pools": self.get_pool_status()
        }
    
    def transfer(self, from_pool: str, to_pool: str, amount: int, reason: str = "") -> dict:
        """
        预算池间转账（需审批）
        """
        source = self.pools.get(from_pool)
        target = self.pools.get(to_pool)
        
        if not source or not target:
            return {"success": False, "error": "预算池不存在"}
        
        source_remaining = source["daily_limit"] - source["used"]
        if source_remaining < amount:
            return {"success": False, "error": f"源预算池余额不足 (剩余{source_remaining})"}
        
        # 执行转账
        source["daily_limit"] -= amount
        target["daily_limit"] += amount
        
        return {
            "success": True,
            "from": from_pool,
            "to": to_pool,
            "amount": amount,
            "reason": reason
        }
    
    def reset_daily(self):
        """日终重置（模拟）"""
        self._initialize_pools()
        print("🔄 预算池已日终重置")


def main():
    """命令行接口"""
    import sys
    
    allocator = BudgetAllocator()
    
    if len(sys.argv) < 2:
        # 显示整体状态
        status = allocator.get_total_status()
        print(json.dumps(status, indent=2))
        return 0
    
    command = sys.argv[1]
    
    if command == "status":
        if len(sys.argv) > 2:
            pool_name = sys.argv[2]
            status = allocator.get_pool_status(pool_name)
        else:
            status = allocator.get_total_status()
        print(json.dumps(status, indent=2))
    
    elif command == "check":
        if len(sys.argv) < 4:
            print("Usage: allocator.py check <pool_name> <amount>")
            return 1
        pool_name = sys.argv[2]
        amount = int(sys.argv[3])
        result = allocator.check_availability(pool_name, amount)
        print(json.dumps(result, indent=2))
    
    elif command == "consume":
        if len(sys.argv) < 4:
            print("Usage: allocator.py consume <pool_name> <amount> [task_id]")
            return 1
        pool_name = sys.argv[2]
        amount = int(sys.argv[3])
        task_id = sys.argv[4] if len(sys.argv) > 4 else None
        result = allocator.consume(pool_name, amount, task_id)
        print(json.dumps(result, indent=2))
    
    elif command == "transfer":
        if len(sys.argv) < 5:
            print("Usage: allocator.py transfer <from_pool> <to_pool> <amount>")
            return 1
        from_pool = sys.argv[2]
        to_pool = sys.argv[3]
        amount = int(sys.argv[4])
        result = allocator.transfer(from_pool, to_pool, amount)
        print(json.dumps(result, indent=2))
    
    else:
        print(f"Unknown command: {command}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
