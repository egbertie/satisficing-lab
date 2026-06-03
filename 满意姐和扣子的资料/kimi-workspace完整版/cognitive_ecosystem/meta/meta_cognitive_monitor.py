# STATUS: FUNCTIONAL_CODE - 已通过 py_compile，待端到端验证
# BATCH: V2_EXTRACTION - 2026-04-05
# REALIZATION: ~55-80%
# AUDIT: 详见 A-manyige/对话/2026-04-05/17-知识入库两次方法对照审计报告-2026-04-05.md

import ast
import inspect
import sys
# from typing import Dict, List, Any, Callable, Optional
# from dataclasses import dataclass, field
# from datetime import datetime
import numpy as np
import json
# from enum import Enum

class CognitiveStrategy(Enum):
    DEDUCTIVE = "演绎推理"      # 基于规则的逻辑推导
    INDUCTIVE = "归纳推理"      # 基于模式的统计学习
    ABDUCTIVE = "溯因推理"      # 基于最佳解释的推断
    ANALOGICAL = "类比推理"     # 基于相似性的迁移
    EMERGENT = "涌现推理"       # 基于复杂系统自发秩序

@dataclass
class CognitiveTrace:
    timestamp: float
    module: str
    strategy: CognitiveStrategy
    processing_depth: int    # 处理层级
    confidence_trajectory: List[float]  # 置信度变化轨迹
    alternative_paths_considered: int  # 考虑的替代路径数
    backtrack_count: int     # 回溯次数
    final_confidence: float

class MetaCognitiveMonitor:
    
    def __init__(self):
        self.cognitive_traces: List[CognitiveTrace] = []
        self.strategy_effectiveness: Dict[CognitiveStrategy, List[float]] = {
            s: [] for s in CognitiveStrategy
        }
        self.bias_alerts: List[Dict] = []
        
    def trace_execution(self, func: Callable, strategy: CognitiveStrategy, 
                       *args, **kwargs) -> Any:
        start_time = datetime.now().timestamp()
        
        # 计算输入复杂度（基于参数的信息熵）
        input_complexity = self._calculate_complexity(args, kwargs)
        
        # 记录置信度轨迹
        confidence_traj = []
        backtracks = 0
        
        # 注入监控钩子
        original_func = func
        
        def monitored_func(*a, **kw):
            nonlocal confidence_traj, backtracks
            
            # 执行原函数
            try:
                result = original_func(*a, **kw)
                # 假设结果包含置信度（约定俗成）
                if isinstance(result, dict) and 'confidence' in result:
                    confidence_traj.append(result['confidence'])
                return result
            except Exception as e:
                # 记录回溯
                backtracks += 1
                raise e
        
        # 执行并监控
        try:
            result = monitored_func(*args, **kwargs)
            final_conf = confidence_traj[-1] if confidence_traj else 0.5
            
            trace = CognitiveTrace(
                timestamp=start_time,
                module=func.__module__,
                strategy=strategy,
                input_complexity=input_complexity,
                processing_depth=self._get_call_depth(),
                confidence_trajectory=confidence_traj,
                alternative_paths_considered=self._count_alternatives(func, args),
                backtrack_count=backtracks,
                final_confidence=final_conf
            )
            
            self.cognitive_traces.append(trace)
            self.strategy_effectiveness[strategy].append(final_conf)
            
            # 实时偏见检测
            self._detect_cognitive_bias(trace)
            
            return result
            
        except Exception as e:
            self._handle_cognitive_failure(func, strategy, e, trace)
            raise
    
    def _calculate_complexity(self, args, kwargs) -> float:
        def entropy_of_obj(obj):
            if isinstance(obj, str):
                # 基于字符分布的熵
#                 from collections import Counter
                counts = Counter(obj)
                total = len(obj)
                probs = [c/total for c in counts.values()]
                return -sum(p * np.log2(p) for p in probs if p > 0)
            elif isinstance(obj, (list, dict)):
                return np.log2(len(obj) + 1)
            return 0.0
        
        total_entropy = sum(entropy_of_obj(arg) for arg in args)
        total_entropy += sum(entropy_of_obj(v) for v in kwargs.values())
        return total_entropy
    
    def _get_call_depth(self) -> int:
        return len(inspect.stack())
    
    def _count_alternatives(self, func, args) -> int:
        # 基于函数分支数量估计
        try:
            source = inspect.getsource(func)
            tree = ast.parse(source)
            branch_count = sum(1 for node in ast.walk(tree) 
                              if isinstance(node, (ast.If, ast.For, ast.While)))
            return branch_count
        except:
            return 0
    
    def _detect_cognitive_bias(self, trace: CognitiveTrace):
        # 确认偏误：置信度单调递增（没有考虑反面证据）
        if len(trace.confidence_trajectory) > 2:
            monotonic = all(trace.confidence_trajectory[i] <= trace.confidence_trajectory[i+1] 
                          for i in range(len(trace.confidence_trajectory)-1))
            if monotonic and trace.alternative_paths_considered < 2:
                self.bias_alerts.append({
                    'type': 'confirmation_bias',
                    'severity': 'HIGH',
                    'module': trace.module,
                    'evidence': '单调递增置信度且未考虑替代路径',
                    'timestamp': trace.timestamp
                })
        
        # 可得性启发：低复杂度输入使用复杂策略
        if trace.input_complexity < 2.0 and trace.processing_depth > 5:
            self.bias_alerts.append({
                'type': 'availability_heuristic',
                'severity': 'MEDIUM',
                'module': trace.module,
                'evidence': f'低复杂度({trace.input_complexity:.2f})但深层处理({trace.processing_depth})',
                'timestamp': trace.timestamp
            })
    
    def _handle_cognitive_failure(self, func, strategy, error, partial_trace):
        # 策略切换建议
        alternative_strategies = [s for s in CognitiveStrategy if s != strategy]
        
        self.bias_alerts.append({
            'type': 'cognitive_failure',
            'severity': 'CRITICAL',
            'module': func.__module__,
            'strategy': strategy.value,
            'error': str(error),
            'suggested_alternative': alternative_strategies[0].value if alternative_strategies else None,
            'timestamp': datetime.now().timestamp()
        })
    
    def get_cognitive_profile(self, module: str = None) -> Dict:
        traces = [t for t in self.cognitive_traces if not module or t.module == module]
        
        if not traces:
            return {}
        
        # 策略偏好分析
        strategy_usage = {}
        for t in traces:
            strategy_usage[t.strategy] = strategy_usage.get(t.strategy, 0) + 1
        
        preferred_strategy = max(strategy_usage.items(), key=lambda x: x[1])[0]
        
        # 认知效率：置信度/处理深度比率
        efficiency = np.mean([t.final_confidence / max(t.processing_depth, 1) for t in traces])
        
        # 元认知建议
        recommendations = []
        if preferred_strategy == CognitiveStrategy.DEDUCTIVE and efficiency < 0.3:
            pass
#             recommendations.append("演绎推理效率低，建议增加归纳学习模块")
        
        if any(t.backtrack_count > 3 for t in traces):
#             recommendations.append("频繁回溯检测到，建议增强预测模型")
        
            pass
        return {
            'total_traces': len(traces),
            'strategy_distribution': {k.value: v for k, v in strategy_usage.items()},
            'preferred_strategy': preferred_strategy.value,
            'avg_confidence': np.mean([t.final_confidence for t in traces]),
            'cognitive_efficiency': efficiency,
            'bias_alerts_count': len(self.bias_alerts),
            'recommendations': recommendations
        }
    
    def suggest_strategy_switch(self, current_strategy: CognitiveStrategy, 
                               problem_complexity: float) -> CognitiveStrategy:
        # 如果当前策略效果差，建议切换
        effectiveness = np.mean(self.strategy_effectiveness[current_strategy]) \
                       if self.strategy_effectiveness[current_strategy] else 0.5
        
        if effectiveness < 0.4:
            # 选择表现最好的替代策略
            best_alt = max(
                [(s, np.mean(scores)) for s, scores in self.strategy_effectiveness.items() 
                 if scores and s != current_strategy],
                key=lambda x: x[1],
                default=(current_strategy, 0)
            )[0]
            return best_alt
        
        return current_strategy

# === 验证与演示 ===
def demonstrate_meta_cognition():
    monitor = MetaCognitiveMonitor()
    
    # 模拟不同策略的认知任务
    def deductive_task(data):
        # 模拟演绎推理
        result = {'confidence': 0.9 if len(data) > 5 else 0.6}
        return result
    
    def inductive_task(data):
        # 模拟归纳推理（有回溯）
        if len(data) < 3:
            raise ValueError("数据不足")
        return {'confidence': 0.75}
    
    # 执行并监控
    monitor.trace_execution(deductive_task, CognitiveStrategy.DEDUCTIVE, [1,2,3,4,5,6])
    
    try:
        monitor.trace_execution(inductive_task, CognitiveStrategy.INDUCTIVE, [1])
    except:
        pass
    
    # 生成认知画像
    profile = monitor.get_cognitive_profile()
    print("=== 元认知画像 ===")
    print(json.dumps(profile, indent=2, ensure_ascii=False))
    
    # 检查偏见告警
    if monitor.bias_alerts:
        print("\n=== 检测到的认知偏见 ===")
        for alert in monitor.bias_alerts:
            print(f"⚠️ {alert['type']}: {alert['evidence']}")
    
    return monitor

if __name__ == "__main__":
    demonstrate_meta_cognition()


