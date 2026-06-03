#!/usr/bin/env python3
"""
Token Optimizer Module
Token优化模块 - 实现85-90% Token节省目标

功能:
- 分层审计Token预算管理
- 智能抽样与缓存
- 模型降级策略
- Token消耗统计与优化建议

Author: Kimi Claw
Version: 1.0.0
Status: WIP
"""

import json
import hashlib
import random
import time
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import threading
from collections import defaultdict


class OptimizationStrategy(Enum):
    """优化策略枚举"""
    CACHE_FIRST = "cache_first"          # 优先使用缓存
    TIER_ADAPTIVE = "tier_adaptive"      # 自适应层级
    MODEL_DEGRADE = "model_degrade"      # 模型降级
    SAMPLING_SMART = "sampling_smart"    # 智能抽样


@dataclass
class TokenUsage:
    """Token使用记录"""
    timestamp: datetime
    tier: str
    tokens_used: int
    cache_hit: bool
    text_length: int
    latency_ms: float
    

@dataclass
class OptimizationResult:
    """优化结果"""
    original_estimate: int      # 原始估算消耗
    actual_usage: int           # 实际使用
    savings: int                # 节省量
    savings_rate: float         # 节省率
    strategy_applied: List[str] # 应用的策略
    cache_hit: bool
    tier_used: str
    

class EmbeddingCache:
    """
    向量缓存系统 (Token优化核心)
    相似请求复用审计结果，节省Token消耗
    """
    
    def __init__(self, 
                 similarity_threshold: float = 0.85,
                 max_entries: int = 10000,
                 ttl_hours: int = 24):
        self.similarity_threshold = similarity_threshold
        self.max_entries = max_entries
        self.ttl_hours = ttl_hours
        
        # 缓存存储: hash -> (embedding, result, timestamp, access_count)
        self._cache: Dict[str, Tuple] = {}
        self._access_stats: Dict[str, int] = defaultdict(int)
        self._lock = threading.Lock()
        
        # 统计
        self._hits = 0
        self._misses = 0
    
    def _text_to_embedding(self, text: str) -> List[float]:
        """
        简化的文本向量化
        实际生产环境应使用BERT/Sentence-Transformer
        """
        # 使用字符级n-gram作为简化embedding
        text = text.lower()[:1000]  # 限制长度
        n_grams = set()
        
        for i in range(len(text) - 2):
            n_grams.add(text[i:i+3])
        
        # 创建简单向量
        embedding = [0.0] * 256
        for gram in n_grams:
            idx = hash(gram) % 256
            embedding[idx] += 1.0
        
        # 归一化
        norm = sum(x**2 for x in embedding) ** 0.5
        if norm > 0:
            embedding = [x / norm for x in embedding]
        
        return embedding
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """计算余弦相似度"""
        dot = sum(a * b for a, b in zip(vec1, vec2))
        return dot  # 向量已归一化，点积即余弦相似度
    
    def get(self, text: str) -> Optional[Any]:
        """
        获取缓存结果
        
        Returns:
            缓存的审计结果，或None
        """
        embedding = self._text_to_embedding(text)
        text_hash = hashlib.sha256(text.encode()).hexdigest()[:16]
        
        with self._lock:
            # 直接哈希匹配
            if text_hash in self._cache:
                cached_emb, result, timestamp, _ = self._cache[text_hash]
                
                # 检查TTL
                if datetime.now() - timestamp < timedelta(hours=self.ttl_hours):
                    self._access_stats[text_hash] += 1
                    self._hits += 1
                    return result
                else:
                    # 过期删除
                    del self._cache[text_hash]
            
            # 相似度匹配
            for key, (cached_emb, result, timestamp, _) in list(self._cache.items()):
                # 检查TTL
                if datetime.now() - timestamp > timedelta(hours=self.ttl_hours):
                    del self._cache[key]
                    continue
                
                similarity = self._cosine_similarity(embedding, cached_emb)
                if similarity >= self.similarity_threshold:
                    self._access_stats[key] += 1
                    self._hits += 1
                    return result
            
            self._misses += 1
            return None
    
    def put(self, text: str, result: Any):
        """存入缓存"""
        embedding = self._text_to_embedding(text)
        text_hash = hashlib.sha256(text.encode()).hexdigest()[:16]
        
        with self._lock:
            # LRU淘汰
            if len(self._cache) >= self.max_entries:
                # 移除最少访问的
                lru_key = min(self._access_stats, key=self._access_stats.get)
                if lru_key in self._cache:
                    del self._cache[lru_key]
                    del self._access_stats[lru_key]
            
            self._cache[text_hash] = (embedding, result, datetime.now(), 1)
            self._access_stats[text_hash] = 1
    
    def get_stats(self) -> Dict:
        """获取缓存统计"""
        total = self._hits + self._misses
        return {
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": self._hits / total if total > 0 else 0,
            "entries": len(self._cache),
            "threshold": self.similarity_threshold
        }


class TierBudgetManager:
    """
    分层预算管理器
    管理L1/L2/L3三层审计的Token预算
    """
    
    TIER_BUDGETS = {
        "L1": 100,   # 轻量
        "L2": 500,   # 标准
        "L3": 1000   # 深度
    }
    
    def __init__(self, daily_limit: int = 6000):
        self.daily_limit = daily_limit
        self.today_usage = 0
        self.tier_usage = {"L1": 0, "L2": 0, "L3": 0}
        self.last_reset = datetime.now().date()
        self._lock = threading.Lock()
    
    def _check_reset(self):
        """检查是否需要重置每日计数"""
        today = datetime.now().date()
        if today != self.last_reset:
            self.today_usage = 0
            self.tier_usage = {"L1": 0, "L2": 0, "L3": 0}
            self.last_reset = today
    
    def allocate_budget(self, tier: str, requested: int) -> Tuple[int, bool]:
        """
        分配预算
        
        Returns:
            (allocated, is_full)
        """
        with self._lock:
            self._check_reset()
            
            tier_budget = self.TIER_BUDGETS.get(tier, 500)
            max_alloc = min(tier_budget, requested)
            
            # 检查每日限额
            remaining = self.daily_limit - self.today_usage
            if remaining <= 0:
                return 0, True
            
            allocated = min(max_alloc, remaining)
            self.today_usage += allocated
            self.tier_usage[tier] = self.tier_usage.get(tier, 0) + allocated
            
            return allocated, (remaining - allocated) <= 0
    
    def get_usage_report(self) -> Dict:
        """获取使用报告"""
        with self._lock:
            self._check_reset()
            
            return {
                "daily_limit": self.daily_limit,
                "today_used": self.today_usage,
                "today_remaining": self.daily_limit - self.today_usage,
                "usage_rate": self.today_usage / self.daily_limit,
                "tier_breakdown": self.tier_usage.copy(),
                "projected_daily": self._project_daily_usage()
            }
    
    def _project_daily_usage(self) -> int:
        """预测今日总消耗"""
        if datetime.now().hour == 0:
            return self.today_usage
        
        hours_passed = datetime.now().hour + datetime.now().minute / 60
        hourly_rate = self.today_usage / hours_passed
        remaining_hours = 24 - hours_passed
        
        return int(self.today_usage + hourly_rate * remaining_hours)


class SamplingEngine:
    """
    智能抽样引擎
    30%随机抽样 + 异常触发100%
    """
    
    def __init__(self, base_rate: float = 0.30):
        self.base_rate = base_rate
        self.anomaly_detector = AnomalyDetector()
        
        # 历史抽样统计
        self.sampled_count = 0
        self.skipped_count = 0
    
    def should_sample(self, text: str, context: Optional[Dict] = None) -> Tuple[bool, str]:
        """
        决定是否抽样
        
        Returns:
            (should_sample, reason)
        """
        context = context or {}
        
        # 异常触发 (高优先级)
        is_anomaly, anomaly_type = self.anomaly_detector.detect(text)
        if is_anomaly:
            self.sampled_count += 1
            return True, f"ANOMALY_TRIGGERED:{anomaly_type}"
        
        # 上下文标记 (用户指定)
        if context.get("force_audit"):
            self.sampled_count += 1
            return True, "FORCED_BY_CONTEXT"
        
        # 随机抽样
        if random.random() < self.base_rate:
            self.sampled_count += 1
            return True, "RANDOM_SAMPLING"
        
        self.skipped_count += 1
        return False, "SKIPPED"
    
    def get_sampling_stats(self) -> Dict:
        """获取抽样统计"""
        total = self.sampled_count + self.skipped_count
        return {
            "sampled": self.sampled_count,
            "skipped": self.skipped_count,
            "sampling_rate": self.sampled_count / total if total > 0 else 0,
            "target_rate": self.base_rate,
            "estimated_savings": f"{self.skipped_count * 500} tokens"  # 假设平均节省500t
        }


class AnomalyDetector:
    """异常检测器"""
    
    HIGH_RISK_PATTERNS = [
        "危险", "警告", "敏感", "机密", "违法",
        "诈骗", "欺诈", "暴力", "色情", "恐怖"
    ]
    
    CONFIDENCE_PATTERNS = [
        "绝对", "一定", "必然", "毫无疑问",
        "100%", "百分之百", "肯定", "保证"
    ]
    
    LENGTH_THRESHOLDS = {
        "VERY_SHORT": (0, 50),
        "VERY_LONG": (5000, float('inf'))
    }
    
    def detect(self, text: str) -> Tuple[bool, str]:
        """
        检测异常
        
        Returns:
            (is_anomaly, anomaly_type)
        """
        text_lower = text.lower()
        
        # 高风险内容
        for pattern in self.HIGH_RISK_PATTERNS:
            if pattern in text_lower:
                return True, f"HIGH_RISK:{pattern}"
        
        # 过度自信
        conf_count = sum(1 for p in self.CONFIDENCE_PATTERNS if p in text_lower)
        if conf_count >= 2:
            return True, "OVER_CONFIDENCE"
        
        # 异常长度
        if len(text) < 50:
            return True, "TOO_SHORT"
        if len(text) > 5000:
            return True, "TOO_LONG"
        
        # 特殊字符比例
        special_ratio = sum(1 for c in text if not c.isalnum()) / max(len(text), 1)
        if special_ratio > 0.3:
            return True, "HIGH_SPECIAL_CHARS"
        
        return False, ""


class ModelDegradationStrategy:
    """
    模型降级策略
    GPT-4 -> GPT-3.5 -> 本地规则
    """
    
    MODEL_COSTS = {
        "gpt-4": 1.0,           # 基准成本
        "gpt-3.5-turbo": 0.1,   # 1/10成本
        "local_rules": 0.01     # 几乎零成本
    }
    
    def __init__(self, budget_manager: TierBudgetManager):
        self.budget_manager = budget_manager
        self.degradation_threshold = 0.8  # 80%预算时开始降级
    
    def select_model(self, tier: str, risk_score: float) -> Tuple[str, float]:
        """
        选择模型
        
        Returns:
            (model_name, cost_ratio)
        """
        usage = self.budget_manager.get_usage_report()
        usage_rate = usage["usage_rate"]
        
        # 高预算使用 + 高风险内容: 保持GPT-4
        if usage_rate < self.degradation_threshold and risk_score > 70:
            return "gpt-4", self.MODEL_COSTS["gpt-4"]
        
        # 中等预算或中风险: 使用GPT-3.5
        if usage_rate < 0.95:
            return "gpt-3.5-turbo", self.MODEL_COSTS["gpt-3.5-turbo"]
        
        # 低预算: 使用本地规则
        return "local_rules", self.MODEL_COSTS["local_rules"]
    
    def should_degrade_for_speed(self, latency_budget_ms: float) -> bool:
        """是否应该为速度降级"""
        return latency_budget_ms < 200  # <200ms强制使用轻量级


class TokenOptimizer:
    """
    Token优化器主类
    协调所有优化策略，实现85-90% Token节省目标
    """
    
    def __init__(self, 
                 daily_budget: int = 6000,
                 sampling_rate: float = 0.30,
                 cache_similarity: float = 0.85):
        """
        初始化Token优化器
        
        Args:
            daily_budget: 每日Token预算 (默认6000)
            sampling_rate: 抽样率 (默认30%)
            cache_similarity: 缓存相似度阈值 (默认0.85)
        """
        self.daily_budget = daily_budget
        self.sampling_rate = sampling_rate
        
        # 子组件
        self.cache = EmbeddingCache(
            similarity_threshold=cache_similarity,
            max_entries=10000
        )
        self.budget_manager = TierBudgetManager(daily_budget)
        self.sampling_engine = SamplingEngine(sampling_rate)
        self.degradation_strategy = ModelDegradationStrategy(self.budget_manager)
        
        # 历史记录
        self.usage_history: List[TokenUsage] = []
        self._lock = threading.Lock()
        
        # 统计
        self.original_estimate_total = 0
        self.actual_total = 0
        
        print(f"[TokenOptimizer] 初始化完成")
        print(f"  - 每日预算: {daily_budget} tokens")
        print(f"  - 抽样率: {sampling_rate*100}%")
        print(f"  - 缓存相似度: {cache_similarity}")
        print(f"  - 目标节省: 85-90%")
    
    def optimize_and_audit(self, 
                          text: str,
                          audit_func: Callable,
                          context: Optional[Dict] = None) -> Dict:
        """
        优化并审计
        
        Args:
            text: 待审计文本
            audit_func: 审计函数
            context: 上下文
        
        Returns:
            包含优化信息的审计结果
        """
        context = context or {}
        start_time = time.time()
        
        # 估算原始消耗 (假设无优化时需要L2审计)
        original_estimate = 500
        
        strategies_applied = []
        cache_hit = False
        
        # 1. 缓存检查 (Token优化策略1: 结果缓存)
        cached_result = self.cache.get(text)
        if cached_result:
            cache_hit = True
            strategies_applied.append("CACHE_REUSE")
            actual_usage = 0  # 缓存命中无消耗
            
            self._record_usage(
                tier="CACHED",
                tokens=0,
                cache_hit=True,
                text_len=len(text),
                latency=(time.time() - start_time) * 1000
            )
            
            return {
                "result": cached_result,
                "optimization": OptimizationResult(
                    original_estimate=original_estimate,
                    actual_usage=actual_usage,
                    savings=original_estimate,
                    savings_rate=1.0,
                    strategy_applied=strategies_applied,
                    cache_hit=True,
                    tier_used="CACHED"
                ).__dict__,
                "latency_ms": (time.time() - start_time) * 1000
            }
        
        # 2. 智能抽样 (Token优化策略2: 30%抽样)
        should_sample, reason = self.sampling_engine.should_sample(text, context)
        if not should_sample:
            strategies_applied.append(f"SAMPLING_SKIP:{reason}")
            
            return {
                "result": {"action": "PASS", "reason": "SAMPLING_SKIPPED"},
                "optimization": OptimizationResult(
                    original_estimate=original_estimate,
                    actual_usage=0,
                    savings=original_estimate,
                    savings_rate=1.0,
                    strategy_applied=strategies_applied,
                    cache_hit=False,
                    tier_used="NONE"
                ).__dict__,
                "latency_ms": (time.time() - start_time) * 1000
            }
        
        # 3. 模型降级选择 (Token优化策略3: GPT-3.5审计)
        risk_score = self._calculate_risk_score(text)
        model, cost_ratio = self.degradation_strategy.select_model("L2", risk_score)
        
        if model == "gpt-3.5-turbo":
            strategies_applied.append("MODEL_DEGRADE_GPT35")
            tier = "L2_LIGHT"
        elif model == "local_rules":
            strategies_applied.append("MODEL_DEGRADE_LOCAL")
            tier = "L1"
        else:
            tier = "L2"
        
        # 4. 分配预算
        allocated, budget_exhausted = self.budget_manager.allocate_budget(
            tier, 500 if tier.startswith("L2") else 100
        )
        
        if budget_exhausted:
            strategies_applied.append("EMERGENCY_MODE")
            tier = "L1"
            allocated = 100
        
        # 5. 执行审计
        audit_result = audit_func(text, tier=tier, max_tokens=allocated)
        actual_usage = audit_result.get("tokens_used", allocated)
        
        # 6. 缓存结果
        self.cache.put(text, audit_result)
        
        # 7. 记录
        self._record_usage(
            tier=tier,
            tokens=actual_usage,
            cache_hit=False,
            text_len=len(text),
            latency=(time.time() - start_time) * 1000
        )
        
        # 计算节省
        savings = original_estimate - actual_usage
        savings_rate = savings / original_estimate if original_estimate > 0 else 0
        
        # 更新总计
        with self._lock:
            self.original_estimate_total += original_estimate
            self.actual_total += actual_usage
        
        return {
            "result": audit_result,
            "optimization": OptimizationResult(
                original_estimate=original_estimate,
                actual_usage=actual_usage,
                savings=savings,
                savings_rate=savings_rate,
                strategy_applied=strategies_applied,
                cache_hit=cache_hit,
                tier_used=tier
            ).__dict__,
            "latency_ms": (time.time() - start_time) * 1000,
            "model_used": model
        }
    
    def _calculate_risk_score(self, text: str) -> float:
        """计算风险评分"""
        score = 0.0
        text_lower = text.lower()
        
        # 简单风险评分逻辑
        risk_keywords = ["危险", "警告", "错误", "敏感"]
        for kw in risk_keywords:
            if kw in text_lower:
                score += 20
        
        return min(score, 100)
    
    def _record_usage(self, tier: str, tokens: int, cache_hit: bool,
                     text_len: int, latency: float):
        """记录使用"""
        usage = TokenUsage(
            timestamp=datetime.now(),
            tier=tier,
            tokens_used=tokens,
            cache_hit=cache_hit,
            text_length=text_len,
            latency_ms=latency
        )
        
        with self._lock:
            self.usage_history.append(usage)
            # 保留最近1000条
            if len(self.usage_history) > 1000:
                self.usage_history = self.usage_history[-1000:]
    
    def get_optimization_report(self) -> Dict:
        """
        生成优化报告 (S5自我验证)
        """
        with self._lock:
            total_original = self.original_estimate_total
            total_actual = self.actual_total
        
        # 各策略贡献
        cache_stats = self.cache.get_stats()
        sampling_stats = self.sampling_engine.get_sampling_stats()
        budget_report = self.budget_manager.get_usage_report()
        
        # 计算各策略节省
        cache_savings = cache_stats["hits"] * 500  # 假设每次缓存节省500t
        sampling_savings = sampling_stats["skipped"] * 500
        
        total_savings = cache_savings + sampling_savings
        if total_original > 0:
            overall_savings_rate = total_savings / total_original
        else:
            overall_savings_rate = 0
        
        return {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_requests": cache_stats["hits"] + cache_stats["misses"],
                "total_original_estimate": total_original,
                "total_actual_usage": total_actual,
                "total_savings": total_savings,
                "overall_savings_rate": overall_savings_rate,
                "target_met": overall_savings_rate >= 0.85
            },
            "strategy_breakdown": {
                "cache": {
                    "hits": cache_stats["hits"],
                    "hit_rate": cache_stats["hit_rate"],
                    "estimated_savings": cache_savings
                },
                "sampling": {
                    "rate": sampling_stats["sampling_rate"],
                    "skipped": sampling_stats["skipped"],
                    "estimated_savings": sampling_savings
                },
                "model_degradation": {
                    "cost_ratio_gpt35": 0.1,  # GPT-3.5是GPT-4的1/10成本
                    "description": "使用GPT-3.5执行审计"
                }
            },
            "budget_status": budget_report,
            "validation": {
                "target_savings_rate": "85-90%",
                "actual_savings_rate": f"{overall_savings_rate*100:.1f}%",
                "meets_target": overall_savings_rate >= 0.85,
                "note": "目标节省率基于原始40K tokens/日 vs 优化后6K tokens/日"
            }
        }
    
    def get_optimization_suggestions(self) -> List[str]:
        """获取优化建议"""
        suggestions = []
        
        cache_stats = self.cache.get_stats()
        if cache_stats["hit_rate"] < 0.6:
            suggestions.append(
                f"缓存命中率仅{cache_stats['hit_rate']*100:.1f}%，"
                "建议降低相似度阈值或扩大缓存容量"
            )
        
        budget_report = self.budget_manager.get_usage_report()
        if budget_report["projected_daily"] > self.daily_budget * 0.9:
            suggestions.append(
                f"预测今日消耗{budget_report['projected_daily']}，"
                "接近预算上限，建议调整抽样率"
            )
        
        sampling_stats = self.sampling_engine.get_sampling_stats()
        if abs(sampling_stats["sampling_rate"] - self.sampling_rate) > 0.05:
            suggestions.append(
                f"实际抽样率{sampling_stats['sampling_rate']*100:.1f}% "
                f"偏离目标{self.sampling_rate*100:.1f}%，需校准"
            )
        
        return suggestions


def mock_audit_function(text: str, tier: str, max_tokens: int) -> Dict:
    """模拟审计函数"""
    time.sleep(0.01)  # 模拟处理时间
    
    tier_tokens = {"L1": 100, "L2": 500, "L2_LIGHT": 300, "L3": 1000}
    tokens_used = min(tier_tokens.get(tier, 500), max_tokens)
    
    return {
        "action": "PASS",
        "score": random.randint(85, 98),
        "tier": tier,
        "tokens_used": tokens_used,
        "issues": []
    }


def main():
    """示例运行"""
    print("=" * 60)
    print("Token Optimizer Module")
    print("Token优化模块 - 5标准化实现")
    print("=" * 60)
    
    # 初始化优化器
    optimizer = TokenOptimizer(
        daily_budget=6000,
        sampling_rate=0.30
    )
    
    # 模拟请求
    test_texts = [
        "这是一个正常的AI响应内容。",
        "这是一个正常的AI响应内容。",  # 重复用于测试缓存
        "危险内容警告！包含敏感信息。",
        "短文本。",
        "这是一个非常长的文本" + "..." * 1000,
    ] * 10  # 生成50个请求
    
    print(f"\n[模拟 {len(test_texts)} 个请求]\n")
    
    for i, text in enumerate(test_texts):
        result = optimizer.optimize_and_audit(
            text=text,
            audit_func=mock_audit_function,
            context={}
        )
        
        if i < 5:  # 只打印前5个
            opt = result["optimization"]
            print(f"请求 {i+1}:")
            print(f"  原始估算: {opt['original_estimate']}t")
            print(f"  实际使用: {opt['actual_usage']}t")
            print(f"  节省率: {opt['savings_rate']*100:.1f}%")
            print(f"  策略: {', '.join(opt['strategy_applied'])}")
            print(f"  缓存命中: {opt['cache_hit']}")
            print()
    
    # 输出优化报告
    print("\n[优化报告]\n")
    report = optimizer.get_optimization_report()
    
    print("摘要:")
    print(f"  总请求: {report['summary']['total_requests']}")
    print(f"  原始估算: {report['summary']['total_original_estimate']}t")
    print(f"  实际使用: {report['summary']['total_actual_usage']}t")
    print(f"  节省率: {report['summary']['overall_savings_rate']*100:.1f}%")
    print(f"  达标: {'✅' if report['summary']['target_met'] else '❌'}")
    
    print("\n策略分解:")
    for strategy, data in report['strategy_breakdown'].items():
        print(f"  {strategy}: {data}")
    
    print("\n验证:")
    print(f"  目标: {report['validation']['target_savings_rate']}")
    print(f"  实际: {report['validation']['actual_savings_rate']}")
    
    # 优化建议
    print("\n[优化建议]\n")
    suggestions = optimizer.get_optimization_suggestions()
    if suggestions:
        for s in suggestions:
            print(f"  • {s}")
    else:
        print("  当前配置运行良好，无需调整。")


if __name__ == "__main__":
    main()
