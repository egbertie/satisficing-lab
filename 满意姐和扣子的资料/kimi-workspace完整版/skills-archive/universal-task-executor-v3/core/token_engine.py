"""
Universal Task Executor V3.0 - Token优化引擎
基于架构设计实现L1-L5五级Token档位管理
"""

import logging
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from .structures import (
    TokenLevel, TokenBudget, TokenConsumption, TokenLevelConfig,
    Task, TaskPriority, TaskStatus
)

logger = logging.getLogger(__name__)


class TokenLevelChangedEvent:
    """Token档位变化事件"""
    def __init__(self, old_level: TokenLevel, new_level: TokenLevel, 
                 budget: TokenBudget, reason: str = ""):
        self.old_level = old_level
        self.new_level = new_level
        self.budget = budget
        self.reason = reason
        self.timestamp = datetime.now()


class TokenEngine:
    """
    Token优化引擎 - 全局Token管理
    
    核心职责:
    1. 管理Token预算和消耗
    2. 自动切换L1-L5档位
    3. 根据档位决定执行策略
    4. 通知观察者档位变化
    """
    
    def __init__(self, total_budget: int = 100000, reserve_ratio: float = 0.1):
        """
        初始化Token引擎
        
        Args:
            total_budget: 总Token预算
            reserve_ratio: 保留比例（用于恢复/报告）
        """
        reserved = int(total_budget * reserve_ratio)
        self.budget = TokenBudget(total=total_budget, reserved=reserved)
        self._observers: List[Callable[[TokenLevelChangedEvent], None]] = []
        self._level_configs: Dict[TokenLevel, TokenLevelConfig] = {}
        self._consumption_history: List[TokenConsumption] = []
        self._current_level = TokenLevel.L5_FULL
        self._last_check_time = datetime.now()
        
        # 初始化档位配置
        self._init_level_configs()
        
        logger.info(f"TokenEngine initialized: budget={total_budget}, reserved={reserved}")
    
    def _init_level_configs(self):
        """初始化档位配置"""
        for config in TokenLevelConfig.default_configs():
            self._level_configs[config.level] = config
    
    def add_observer(self, observer: Callable[[TokenLevelChangedEvent], None]) -> None:
        """
        添加Token档位变化观察者
        
        Args:
            observer: 回调函数，接收TokenLevelChangedEvent参数
        """
        self._observers.append(observer)
        logger.debug(f"Observer added, total={len(self._observers)}")
    
    def remove_observer(self, observer: Callable[[TokenLevelChangedEvent], None]) -> None:
        """移除观察者"""
        if observer in self._observers:
            self._observers.remove(observer)
    
    def consume(self, tokens: int, context: str = "") -> TokenLevel:
        """
        消费Token，返回当前档位
        
        Args:
            tokens: 消耗的Token数量
            context: 消费上下文（用于记录）
            
        Returns:
            当前Token档位
        """
        old_level = self._current_level
        
        # 更新预算
        self.budget.consumed += tokens
        
        # 记录消耗
        consumption = TokenConsumption(
            task_id=context,
            tokens=tokens,
            operation="consume",
            context=context
        )
        self._consumption_history.append(consumption)
        
        # 检查档位变化
        new_level = self.budget.get_level()
        self._current_level = new_level
        
        # 通知观察者
        if new_level != old_level:
            event = TokenLevelChangedEvent(
                old_level=old_level,
                new_level=new_level,
                budget=self.budget,
                reason=f"Token consumed: {tokens}"
            )
            self._notify_observers(event)
            logger.warning(f"Token level changed: {old_level.value} -> {new_level.value}, "
                          f"available={self.budget.available}")
        
        return new_level
    
    def _notify_observers(self, event: TokenLevelChangedEvent) -> None:
        """通知所有观察者"""
        for observer in self._observers:
            try:
                observer(event)
            except Exception as e:
                logger.error(f"Observer notification failed: {e}")
    
    def should_execute(self, category: str, priority: str) -> bool:
        """
        根据档位判断是否应该执行任务
        
        Args:
            category: 任务类别
            priority: 任务优先级 (p0/p1/p2/p3)
            
        Returns:
            是否应该执行
        """
        level = self._current_level
        config = self._level_configs.get(level)
        
        if not config:
            logger.error(f"Unknown token level: {level}")
            return False
        
        # L1_HALT: 暂停所有任务
        if level == TokenLevel.L1_HALT:
            logger.warning(f"Token level is L1_HALT, task execution blocked: {category}/{priority}")
            return False
        
        # 检查优先级是否在允许列表中
        should_run = priority in config.allowed_priorities
        
        if not should_run:
            logger.info(f"Task blocked by token level: {level.value}, "
                       f"allowed={config.allowed_priorities}, got={priority}")
        
        return should_run
    
    def get_execution_strategy(self, category: str, priority: str) -> Dict[str, Any]:
        """
        获取执行策略
        
        Args:
            category: 任务类别
            priority: 任务优先级
            
        Returns:
            执行策略字典
        """
        level = self._current_level
        config = self._level_configs.get(level)
        
        if not config:
            return {
                "should_execute": False,
                "max_concurrency": 0,
                "reason": "Unknown token level"
            }
        
        should_execute = self.should_execute(category, priority)
        
        return {
            "should_execute": should_execute,
            "token_level": level.value,
            "max_concurrency": config.max_concurrency if should_execute else 0,
            "allowed": should_execute,
            "available_tokens": self.budget.available,
            "usage_ratio": self.budget.usage_ratio,
            "description": config.description
        }
    
    def get_max_concurrency(self) -> int:
        """获取当前档位允许的最大并发数"""
        config = self._level_configs.get(self._current_level)
        return config.max_concurrency if config else 0
    
    def reserve_tokens(self, amount: int, reason: str = "") -> bool:
        """
        预留Token（用于恢复/报告等）
        
        Args:
            amount: 预留数量
            reason: 预留原因
            
        Returns:
            是否预留成功
        """
        if self.budget.available < amount:
            logger.warning(f"Cannot reserve {amount} tokens, available={self.budget.available}")
            return False
        
        self.budget.reserved += amount
        logger.info(f"Reserved {amount} tokens for: {reason}")
        return True
    
    def release_reserved(self, amount: int) -> None:
        """释放预留的Token"""
        self.budget.reserved = max(0, self.budget.reserved - amount)
        logger.debug(f"Released {amount} reserved tokens")
    
    def get_consumption_stats(self) -> Dict[str, Any]:
        """获取Token消耗统计"""
        total_consumed = self.budget.consumed
        total_available = self.budget.total
        
        # 按context统计
        context_stats: Dict[str, int] = {}
        for c in self._consumption_history:
            context_stats[c.context] = context_stats.get(c.context, 0) + c.tokens
        
        return {
            "total_budget": total_available,
            "consumed": total_consumed,
            "available": self.budget.available,
            "reserved": self.budget.reserved,
            "usage_ratio": self.budget.usage_ratio,
            "current_level": self._current_level.value,
            "by_context": context_stats,
            "history_count": len(self._consumption_history)
        }
    
    def estimate_task_cost(self, task: Task) -> int:
        """
        估算任务Token成本
        
        基于任务类型和优先级进行估算
        """
        base_cost = 1000  # 基础成本
        
        # 根据类别调整
        category_multipliers = {
            "category_1": 1.0,   # 治理体系完善
            "category_2": 0.8,   # 周期性任务部署
            "category_3": 1.2,   # 系统能力建设
            "category_4": 0.9,   # 历史数据治理
            "category_5": 0.5,   # 杂项清理
            "category_6": 1.5,   # 全量任务审计（最高）
        }
        
        # 根据优先级调整
        priority_multipliers = {
            "p0": 1.5,  # P0需要更仔细的处理
            "p1": 1.2,
            "p2": 1.0,
            "p3": 0.8,
        }
        
        category_mult = category_multipliers.get(task.category, 1.0)
        priority_mult = priority_multipliers.get(task.priority.value, 1.0)
        
        estimated = int(base_cost * category_mult * priority_mult)
        
        return estimated
    
    def can_afford(self, task: Task) -> bool:
        """检查是否有足够Token执行任务"""
        estimated_cost = self.estimate_task_cost(task)
        return self.budget.can_consume(estimated_cost)
    
    def reset_budget(self, new_total: int, reserve_ratio: float = 0.1) -> None:
        """
        重置预算
        
        Args:
            new_total: 新的总预算
            reserve_ratio: 新的保留比例
        """
        old_total = self.budget.total
        self.budget.total = new_total
        self.budget.consumed = 0
        self.budget.reserved = int(new_total * reserve_ratio)
        
        # 更新档位
        old_level = self._current_level
        self._current_level = self.budget.get_level()
        
        logger.info(f"Budget reset: {old_total} -> {new_total}, level={self._current_level.value}")
        
        # 通知档位变化
        if self._current_level != old_level:
            event = TokenLevelChangedEvent(
                old_level=old_level,
                new_level=self._current_level,
                budget=self.budget,
                reason="Budget reset"
            )
            self._notify_observers(event)
    
    def get_level_description(self) -> str:
        """获取当前档位描述"""
        config = self._level_configs.get(self._current_level)
        return config.description if config else "Unknown"
    
    def is_critical(self) -> bool:
        """检查是否处于临界状态（L2或更低）"""
        return self._current_level in [TokenLevel.L2_CRITICAL, TokenLevel.L1_HALT]
    
    def is_halted(self) -> bool:
        """检查是否已暂停（L1）"""
        return self._current_level == TokenLevel.L1_HALT


class TokenAwareScheduler:
    """
    Token感知调度器
    
    根据Token档位动态调整任务调度策略
    """
    
    def __init__(self, token_engine: TokenEngine):
        self.token_engine = token_engine
        self.execution_stats = {
            "executed": 0,
            "skipped": 0,
            "deferred": 0,
            "blocked": 0
        }
        logger.info("TokenAwareScheduler initialized")
    
    def schedule_task(self, task: Task) -> Dict[str, Any]:
        """
        调度单个任务
        
        Args:
            task: 待调度任务
            
        Returns:
            调度结果
        """
        strategy = self.token_engine.get_execution_strategy(
            task.category, task.priority.value
        )
        
        if not strategy["should_execute"]:
            self.execution_stats["blocked"] += 1
            return {
                "action": "block",
                "reason": f"Token level {strategy['token_level']} blocks {task.priority.value} tasks",
                "strategy": strategy
            }
        
        # 检查Token预算
        if not self.token_engine.can_afford(task):
            self.execution_stats["deferred"] += 1
            return {
                "action": "defer",
                "reason": "Insufficient token budget",
                "estimated_cost": self.token_engine.estimate_task_cost(task),
                "available": self.token_engine.budget.available,
                "strategy": strategy
            }
        
        self.execution_stats["executed"] += 1
        return {
            "action": "execute",
            "max_concurrency": strategy["max_concurrency"],
            "strategy": strategy
        }
    
    def schedule_batch(self, tasks: List[Task]) -> List[Dict[str, Any]]:
        """
        批量调度任务
        
        Args:
            tasks: 待调度任务列表
            
        Returns:
            每个任务的调度结果
        """
        results = []
        for task in tasks:
            result = self.schedule_task(task)
            results.append({
                "task_id": task.task_id,
                "category": task.category,
                "priority": task.priority.value,
                "decision": result
            })
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """获取调度统计"""
        return {
            **self.execution_stats,
            "token_stats": self.token_engine.get_consumption_stats()
        }
    
    def reset_stats(self) -> None:
        """重置统计"""
        self.execution_stats = {
            "executed": 0,
            "skipped": 0,
            "deferred": 0,
            "blocked": 0
        }
