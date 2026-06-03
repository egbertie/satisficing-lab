#!/usr/bin/env python3
# simon_satisficing.py - 司马贺满意解算法
# 来源: 外援团队交付文档 v1.0
# 功能: 三层决策优化系统 - 多目标优化 + 满意度量化
# 创建时间: 2026-04-04 (从交付文档补实施)
# 版本: 1.0

# import numpy as np
from typing import Dict, List, Tuple, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import json

class SatisfactionLevel(Enum):
    """满意度等级"""
    UNACCEPTABLE = 0    # 不可接受
    MINIMAL = 1         # 最低可接受
    ADEQUATE = 2        # 足够
    GOOD = 3            # 良好
    EXCELLENT = 4       # 优秀

@dataclass
class DecisionCriteria:
    """决策准则"""
    name: str
    weight: float                      # 权重
    aspiration_level: float            # 期望水平（满意解阈值）
    min_acceptable: float              # 最低可接受值
    max_possible: float                # 理论最优值
    satisfaction_function: Optional[Callable] = None  # 自定义满意度函数

@dataclass
class Alternative:
    """决策备选方案"""
    name: str
    criteria_values: Dict[str, float]  # 各准则得分
    costs: Dict[str, float] = field(default_factory=dict)  # 成本（时间/资源）
    constraints: Dict[str, bool] = field(default_factory=dict)  # 约束满足情况
    
    def calculate_satisfaction(self, criteria: List[DecisionCriteria]) -> float:
        """计算总体满意度"""
        total_weight = sum(c.weight for c in criteria)
        weighted_satisfaction = 0.0
        
        for c in criteria:
            value = self.criteria_values.get(c.name, 0)
            
            # 使用自定义函数或默认计算
            if c.satisfaction_function:
                sat = c.satisfaction_function(value, c)
            else:
                sat = self._default_satisfaction(value, c)
            
            weighted_satisfaction += c.weight * sat
        
        return weighted_satisfaction / total_weight if total_weight > 0 else 0
    
    def _default_satisfaction(self, value: float, criteria: DecisionCriteria) -> float:
        """默认满意度计算"""
        if value < criteria.min_acceptable:
            return 0.0
        elif value >= criteria.aspiration_level:
            return 1.0
        else:
            # 线性插值
            range_size = criteria.aspiration_level - criteria.min_acceptable
            if range_size > 0:
                return (value - criteria.min_acceptable) / range_size
            return 0.0
    
    def is_feasible(self) -> bool:
        """检查是否满足所有硬约束"""
        return all(self.constraints.values())

class SimonSatisficing:
    """
    司马贺满意解算法
    核心理念：在有限理性约束下，寻找"足够好"的解决方案而非理论最优
    
    三层架构：
    1. 约束层：硬约束筛选（可行性检查）
    2. 满意层：期望水平匹配（满意解搜索）
    3. 优化层：满意解中的优化选择
    """
    
    def __init__(self, search_depth: int = 3, time_limit: float = 10.0):
        self.search_depth = search_depth      # 搜索深度
        self.time_limit = time_limit          # 时间限制（秒）
        self.decision_log = []
        
    def decide(self, 
               alternatives: List[Alternative],
               criteria: List[DecisionCriteria],
               context: Dict = None) -> Dict:
        """
        主决策流程
        
        Args:
            alternatives: 备选方案列表
            criteria: 决策准则列表
            context: 决策上下文（时间压力、资源限制等）
        
        Returns:
            决策结果字典
        """
        start_time = datetime.now()
        context = context or {}
        
        # 第一层：约束筛选（硬约束检查）
        feasible_alternatives = self._constraint_filter(alternatives)
        
        if not feasible_alternatives:
            return {
                'status': 'INFEASIBLE',
                'message': '没有满足硬约束的方案',
                'recommendation': '放宽约束或寻找新方案'
            }
        
        # 第二层：满意解搜索
        satisficing_alternatives = self._satisficing_search(
            feasible_alternatives, criteria
        )
        
        if not satisficing_alternatives:
            # 降低期望，扩大搜索
            lowered_criteria = self._lower_aspirations(criteria, factor=0.8)
            satisficing_alternatives = self._satisficing_search(
                feasible_alternatives, lowered_criteria
            )
            
            if not satisficing_alternatives:
                return {
                    'status': 'NO_SATISFICING',
                    'message': '即使在降低期望后仍无满意解',
                    'recommendation': '重新设计备选方案'
                }
        
        # 第三层：满意解中的优化选择
        best_choice = self._optimize_among_satisficing(
            satisficing_alternatives, criteria, context
        )
        
        elapsed = (datetime.now() - start_time).total_seconds()
        
        # 记录决策
        self._log_decision(
            alternatives, criteria, best_choice, elapsed, context
        )
        
        return {
            'status': 'SUCCESS',
            'selected': best_choice.name,
            'satisfaction_score': best_choice.calculate_satisfaction(criteria),
            'search_stats': {
                'total_alternatives': len(alternatives),
                'feasible': len(feasible_alternatives),
                'satisficing': len(satisficing_alternatives),
                'search_time': elapsed
            },
            'alternative_details': [
                {
                    'name': alt.name,
                    'satisfaction': alt.calculate_satisfaction(criteria),
                    'is_satisficing': alt in satisficing_alternatives
                }
                for alt in alternatives
            ]
        }
    
    def _constraint_filter(self, alternatives: List[Alternative]) -> List[Alternative]:
        """第一层：硬约束筛选"""
        return [alt for alt in alternatives if alt.is_feasible()]
    
    def _satisficing_search(self, 
                           alternatives: List[Alternative],
                           criteria: List[DecisionCriteria]) -> List[Alternative]:
        """第二层：满意解搜索"""
        satisficing = []
        
        for alt in alternatives:
            satisfaction = alt.calculate_satisfaction(criteria)
            # 满意度 >= 0.8 视为满意解
            if satisfaction >= 0.8:
                satisficing.append(alt)
        
        return satisficing
    
    def _optimize_among_satisficing(self,
                                   satisficing: List[Alternative],
                                   criteria: List[DecisionCriteria],
                                   context: Dict) -> Alternative:
        """第三层：满意解中的优化"""
        # 简单策略：选择满意度最高的
        # 复杂策略可考虑多目标优化、鲁棒性等
        
        best = max(satisficing, 
                  key=lambda alt: alt.calculate_satisfaction(criteria))
        
        return best
    
    def _lower_aspirations(self, 
                          criteria: List[DecisionCriteria],
                          factor: float = 0.8) -> List[DecisionCriteria]:
        """降低期望水平"""
        lowered = []
        for c in criteria:
            new_c = DecisionCriteria(
                name=c.name,
                weight=c.weight,
                aspiration_level=c.aspiration_level * factor,
                min_acceptable=c.min_acceptable,
                max_possible=c.max_possible,
                satisfaction_function=c.satisfaction_function
            )
            lowered.append(new_c)
        return lowered
    
    def _log_decision(self, 
                     alternatives: List[Alternative],
                     criteria: List[DecisionCriteria],
                     selected: Alternative,
                     elapsed: float,
                     context: Dict):
        """记录决策日志"""
        self.decision_log.append({
            'timestamp': datetime.now().isoformat(),
            'num_alternatives': len(alternatives),
            'num_criteria': len(criteria),
            'selected': selected.name,
            'satisfaction': selected.calculate_satisfaction(criteria),
            'time_seconds': elapsed,
            'context': context
        })
    
    def analyze_tradeoffs(self, 
                         alternatives: List[Alternative],
                         criteria: List[DecisionCriteria]) -> Dict:
        """分析权衡关系"""
        analysis = {
            'pareto_frontier': [],
            'tradeoff_matrix': {},
            'dominance_relations': []
        }
        
        # 找出帕累托前沿
        for i, alt1 in enumerate(alternatives):
            is_dominated = False
            for j, alt2 in enumerate(alternatives):
                if i != j:
                    if self._dominates(alt2, alt1, criteria):
                        is_dominated = True
                        analysis['dominance_relations'].append({
                            'dominator': alt2.name,
                            'dominated': alt1.name
                        })
                        break
            if not is_dominated:
                analysis['pareto_frontier'].append(alt1.name)
        
        return analysis
    
    def _dominates(self, 
                  alt1: Alternative, 
                  alt2: Alternative,
                  criteria: List[DecisionCriteria]) -> bool:
        """检查alt1是否支配alt2"""
        better_in_at_least_one = False
        
        for c in criteria:
            v1 = alt1.criteria_values.get(c.name, 0)
            v2 = alt2.criteria_values.get(c.name, 0)
            
            if v1 < v2:
                return False
            elif v1 > v2:
                better_in_at_least_one = True
        
        return better_in_at_least_one
    
    def get_decision_stats(self) -> Dict:
        """获取决策统计"""
        if not self.decision_log:
            return {'total_decisions': 0}
        
        total = len(self.decision_log)
        avg_time = sum(d['time_seconds'] for d in self.decision_log) / total
        avg_satisfaction = sum(d['satisfaction'] for d in self.decision_log) / total
        
        return {
            'total_decisions': total,
            'avg_decision_time': avg_time,
            'avg_satisfaction': avg_satisfaction,
            'satisficing_rate': sum(1 for d in self.decision_log 
                                   if d['satisfaction'] >= 0.8) / total
        }

# 便捷函数
def make_decision(alternatives_data: List[Dict],
                 criteria_data: List[Dict]) -> Dict:
    """快速决策接口"""
    # 构造Alternative对象
    alternatives = []
    for data in alternatives_data:
        alt = Alternative(
            name=data['name'],
            criteria_values=data.get('criteria_values', {}),
            costs=data.get('costs', {}),
            constraints=data.get('constraints', {})
        )
        alternatives.append(alt)
    
    # 构造Criteria对象
    criteria = []
    for data in criteria_data:
        crit = DecisionCriteria(
            name=data['name'],
            weight=data.get('weight', 1.0),
            aspiration_level=data.get('aspiration_level', 0.8),
            min_acceptable=data.get('min_acceptable', 0.5),
            max_possible=data.get('max_possible', 1.0)
        )
        criteria.append(crit)
    
    # 执行决策
    simon = SimonSatisficing()
    return simon.decide(alternatives, criteria)

if __name__ == '__main__':
    # 测试案例：投资决策
    alternatives_data = [
        {
            'name': '保守型A',
            'criteria_values': {'收益': 0.6, '风险': 0.9, '流动性': 0.8},
            'constraints': {'最低门槛': True}
        },
        {
            'name': '平衡型B',
            'criteria_values': {'收益': 0.75, '风险': 0.7, '流动性': 0.7},
            'constraints': {'最低门槛': True}
        },
        {
            'name': '激进型C',
            'criteria_values': {'收益': 0.9, '风险': 0.4, '流动性': 0.5},
            'constraints': {'最低门槛': True}
        }
    ]
    
    criteria_data = [
        {'name': '收益', 'weight': 0.4, 'aspiration_level': 0.7},
        {'name': '风险', 'weight': 0.35, 'aspiration_level': 0.6},
        {'name': '流动性', 'weight': 0.25, 'aspiration_level': 0.6}
    ]
    
    result = make_decision(alternatives_data, criteria_data)
    print(json.dumps(result, ensure_ascii=False, indent=2))
