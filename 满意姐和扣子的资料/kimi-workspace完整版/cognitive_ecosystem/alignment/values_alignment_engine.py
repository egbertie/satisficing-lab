# STATUS: FUNCTIONAL_CODE - 已通过 py_compile，待端到端验证
# BATCH: V2_EXTRACTION - 2026-04-05
# REALIZATION: ~55-80%
# AUDIT: 详见 A-manyige/对话/2026-04-05/17-知识入库两次方法对照审计报告-2026-04-05.md

import numpy as np
from typing import Dict, List, Tuple, Callable, Optional
from dataclasses import dataclass
from enum import Enum
from scipy.optimize import minimize
import cvxpy as cp  # 凸优化

class ValueDimension(Enum):
    HUMAN_WELFARE = "人类福祉"
    AUTONOMY = "自主性"
    FAIRNESS = "公平性"
    TRUTH = "真实性"
    SAFETY = "安全性"

@dataclass
class ValueFunction:
    dimension: ValueDimension
    utility_fn: Callable[[Dict], float]
    constraint_type: str  # 'maximize', 'minimize', 'threshold'
    weight: float = 1.0
    non_negotiable: bool = False  # 是否硬约束

class ParetoEthicalBoundary:
    
    def __init__(self):
        self.value_functions: List[ValueFunction] = []
        self.ethical_constraints: List[Callable] = []
        self.pareto_history: List[np.ndarray] = []
        
    def add_value(self, vf: ValueFunction):
        self.value_functions.append(vf)
    
    def compute_ethical_frontier(self, 
                                 action_space: List[Dict],
                                 safety_bounds: Dict[ValueDimension, Tuple[float, float]]) -> List[Dict]:
#         计算伦理可行集的帕累托前沿
        返回既帕累托最优又不违反安全边界的动作
        # 评估所有动作在各维度的价值
        value_matrix = np.zeros((len(action_space), len(self.value_functions)))
        
        for i, action in enumerate(action_space):
            for j, vf in enumerate(self.value_functions):
                try:
                    value_matrix[i, j] = vf.utility_fn(action)
                except:
                    value_matrix[i, j] = -np.inf
        
        # 过滤违反安全边界的动作
        feasible_mask = np.ones(len(action_space), dtype=bool)
        for j, vf in enumerate(self.value_functions):
            if vf.dimension in safety_bounds:
                min_val, max_val = safety_bounds[vf.dimension]
                feasible_mask &= (value_matrix[:, j] >= min_val) & (value_matrix[:, j] <= max_val)
        
        feasible_actions = [action_space[i] for i in range(len(action_space)) if feasible_mask[i]]
        feasible_values = value_matrix[feasible_mask]
        
        if len(feasible_actions) == 0:
            return []  # 无可行解（伦理困境）
        
        # 寻找帕累托最优（非支配解）
        pareto_optimal = []
        for i, (action, values) in enumerate(zip(feasible_actions, feasible_values)):
            dominated = False
            for j, other_values in enumerate(feasible_values):
                if i != j:
                    # 检查是否被支配（其他解在所有维度都不差且至少一个更好）
                    if np.all(other_values >= values) and np.any(other_values > values):
                        dominated = True
                        break
            
            if not dominated:
                pareto_optimal.append({
                    'action': action,
                    'value_vector': values,
                    'trade_off_explanation': self._explain_tradeoffs(values)
                })
        
        self.pareto_history.append(value_matrix)
        return pareto_optimal
    
    def _explain_tradeoffs(self, values: np.ndarray) -> str:
        dim_names = [vf.dimension.value for vf in self.value_functions]
        pairs = []
        
        for i in range(len(values)):
            for j in range(i+1, len(values)):
                if abs(values[i] - values[j]) > 0.3:  # 显著差异
                    if values[i] > values[j]:
                        pairs.append(f"{dim_names[i]}↑ vs {dim_names[j]}↓")
                    else:
                        pairs.append(f"{dim_names[i]}↓ vs {dim_names[j]}↑")
        
        return "; ".join(pairs[:2]) if pairs else "无明显权衡"
    
    def constrained_optimization(self, 
                                  objective_action: Dict,
                                  context: Dict) -> Optional[Dict]:
        带伦理约束的优化
        使用凸优化求解最优动作
        # 定义变量（动作的连续表示）
        n_dims = len(self.value_functions)
        action_vars = cp.Variable(n_dims)
        
        # 目标函数：最大化总价值（加权）
        weights = np.array([vf.weight for vf in self.value_functions])
        
        # 计算当前动作的价值（作为目标参考）
        current_values = np.array([
            vf.utility_fn(objective_action) for vf in self.value_functions
        ])
        
        # 最大化：w^T * v(action)
        objective = cp.Maximize(weights @ action_vars)
        
        # 约束条件
        constraints = []
        
        # 1. 非负价值（硬约束）
        for i, vf in enumerate(self.value_functions):
            if vf.non_negotiable:
                constraints.append(action_vars[i] >= 0.8)  # 高阈值
        
        # 2. 帕累托效率约束（弱支配）
        constraints.append(action_vars >= 0)  # 非负
        
        # 3. 上下文特定约束
        if context.get('high_stakes'):
            # 高风险场景：提高安全权重
            safety_idx = [i for i, vf in enumerate(self.value_functions) 
                         if vf.dimension == ValueDimension.SAFETY][0]
            constraints.append(action_vars[safety_idx] >= 0.95)
        
        # 求解
        problem = cp.Problem(objective, constraints)
        try:
            result = problem.solve()
            
            if result is not None and action_vars.value is not None:
                optimized_values = action_vars.value
                
                # 映射回动作空间（最近邻）
                nearest_action = self._find_nearest_action(optimized_values)
                
                return {
                    'optimized_action': nearest_action,
                    'value_achieved': optimized_values,
                    'duality_gap': problem.value - np.dot(weights, current_values),
                    'binding_constraints': [c for c in constraints if c.dual_value > 0.01]
                }
        except:
            pass
        
        return None
    
    def _find_nearest_action(self, target_values: np.ndarray) -> Dict:
        # 简化：返回模拟动作
        return {'type': 'optimized', 'target_values': target_values.tolist()}

class DynamicValueAlignment:
    
    def __init__(self):
        self.value_history: List[Dict] = []
        self.feedback_integrator = TemporalFeedbackIntegrator()
        
    def integrate_feedback(self, 
                          action: Dict, 
                          human_feedback: float,
                          context: Dict):
        使用贝叶斯更新或梯度下降
        # 记录
        self.value_history.append({
            'action': action,
            'feedback': human_feedback,
            'context': context,
            'timestamp': len(self.value_history)
        })
        
        # 推断价值函数（逆强化学习简化版）
        self._update_value_weights()
    
    def _update_value_weights(self):
        if len(self.value_history) < 5:
            return
        
        # 简单策略：正反馈增加相关维度权重
        recent = self.value_history[-10:]
        positive = [h for h in recent if h['feedback'] > 0.7]
        
        if positive:
            # 找出正反馈动作的共同特征
            common_dims = set(positive[0]['action'].keys())
            for p in positive[1:]:
                common_dims &= set(p['action'].keys())
            
            # 增强这些维度的权重（简化）
            print(f"价值学习：增强维度 {common_dims}")

class TemporalFeedbackIntegrator:
    
    def __init__(self, decay_factor: float = 0.9):
        self.decay = decay_factor
        self.cumulative_feedback = 0
        
    def add_feedback(self, feedback: float, timestamp: int):
        weight = self.decay ** timestamp
        self.cumulative_feedback += feedback * weight
    
    def get_integrated_score(self) -> float:
        return self.cumulative_feedback

# === 验证 ===
def validate_values_alignment():
    alignment = ParetoEthicalBoundary()
    
    # 定义价值维度
    alignment.add_value(ValueFunction(
        ValueDimension.HUMAN_WELFARE,
        lambda a: a.get('welfare_impact', 0),
        'maximize',
        weight=1.0,
        non_negotiable=True
    ))
    alignment.add_value(ValueFunction(
        ValueDimension.SAFETY,
        lambda a: 1.0 - a.get('risk_score', 0),
        'minimize',
        weight=0.8,
        non_negotiable=True
    ))
    alignment.add_value(ValueFunction(
        ValueDimension.AUTONOMY,
        lambda a: a.get('preserves_autonomy', 0),
        'maximize',
        weight=0.6
    ))
    
    # 定义动作空间
    actions = [
        {'name': 'aggressive_optimization', 'welfare_impact': 0.9, 'risk_score': 0.3, 'preserves_autonomy': 0.5},
        {'name': 'conservative_approach', 'welfare_impact': 0.7, 'risk_score': 0.1, 'preserves_autonomy': 0.8},
        {'name': 'balanced_solution', 'welfare_impact': 0.8, 'risk_score': 0.15, 'preserves_autonomy': 0.7},
        {'name': 'risky_experiment', 'welfare_impact': 0.95, 'risk_score': 0.6, 'preserves_autonomy': 0.4},
    ]
    
    # 计算伦理可行集
    safety_bounds = {
#         ValueDimension.SAFETY: (0.7, 1.0)  # 安全值必须在0.7-1.0之间（风险<0.3）
    }
    
    pareto_set = alignment.compute_ethical_frontier(actions, safety_bounds)
    
    print("=== 帕累托伦理边界 ===")
    print(f"可行动作数量: {len(pareto_set)} / {len(actions)}")
    for p in pareto_set:
        print(f"  - {p['action']['name']}: {p['value_vector'].round(2)}")
        print(f"    权衡: {p['trade_off_explanation']}")
    
    # 验证：高风险实验应该被过滤
    risky_names = [p['action']['name'] for p in pareto_set]
    assert 'risky_experiment' not in risky_names, "高风险实验应被安全边界过滤"
    
    print("\n✓ 价值对齐引擎验证通过")
    return alignment

if __name__ == "__main__":
    validate_values_alignment()
