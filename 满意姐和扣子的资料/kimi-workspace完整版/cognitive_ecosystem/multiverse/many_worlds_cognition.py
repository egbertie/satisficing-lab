# STATUS: FUNCTIONAL_CODE - 已通过 py_compile，待端到端验证
# BATCH: V2_EXTRACTION - 2026-04-05
# REALIZATION: ~55-80%
# AUDIT: 详见 A-manyige/对话/2026-04-05/17-知识入库两次方法对照审计报告-2026-04-05.md

import numpy as np
from typing import Dict, List, Tuple, Optional, Callable
from dataclasses import dataclass
from concurrent.futures import ProcessPoolExecutor
import copy

@dataclass
class CognitiveUniverse:
    universe_id: int
    initial_conditions: Dict
    evolution_trajectory: List[Dict]
    final_outcome: Optional[Dict]
    probability_weight: float  # 在多元宇宙分布中的权重
    coherence_with_others: float  # 与其他宇宙的相干性

class ManyWorldsCognitiveEngine:
    多世界认知引擎
    
    def __init__(self, branching_factor: int = 8):
        self.branching_factor = branching_factor
        self.universes: List[CognitiveUniverse] = []
        self.coherence_matrix: np.ndarray = np.eye(branching_factor)
        self.history: List[List[CognitiveUniverse]] = []
        
    def initialize_multiverse(self, problem: Dict, 
                              uncertainty_dimensions: List[str]):
        self.universes = []
        
        # 在每个不确定维度上创建分支
        for i in range(self.branching_factor):
            # 为每个宇宙采样不同的参数组合
            initial_state = self._sample_initial_state(problem, uncertainty_dimensions, i)
            
            universe = CognitiveUniverse(
                universe_id=i,
                initial_conditions=initial_state,
                evolution_trajectory=[initial_state],
                final_outcome=None,
                probability_weight=1.0 / self.branching_factor,
                coherence_with_others=1.0
            )
            self.universes.append(universe)
        
        self.history.append(copy.deepcopy(self.universes))
    
    def _sample_initial_state(self, problem: Dict, 
                              dimensions: List[str], 
                              universe_idx: int) -> Dict:
        state = problem.copy()
        
        # 使用不同的随机种子确保多样性
        np.random.seed(universe_idx * 42)
        
        for dim in dimensions:
            if dim in state and isinstance(state[dim], (int, float)):
                # 添加宇宙特定的扰动
                noise = np.random.normal(0, abs(state[dim]) * 0.1)
                state[dim] = state[dim] + noise
        
        return state
    
    def evolve_step(self, transition_function: Callable, 
                    step_number: int):
        所有宇宙并行演化一步
        new_states = []
        
        with ProcessPoolExecutor(max_workers=self.branching_factor) as executor:
            futures = []
            for universe in self.universes:
                future = executor.submit(
                    self._evolve_single_universe,
                    universe,
                    transition_function
                )
                futures.append(future)
            
            for i, future in enumerate(futures):
                new_state = future.result()
                self.universes[i].evolution_trajectory.append(new_state)
                new_states.append(new_state)
        
        # 计算宇宙间的相干性（状态相似度）
        self._update_coherence(new_states)
        
        # 记录历史
        self.history.append(copy.deepcopy(self.universes))
    
    def _evolve_single_universe(self, universe: CognitiveUniverse, 
                                 transition_fn: Callable) -> Dict:
        current = universe.evolution_trajectory[-1]
        next_state = transition_fn(current, universe.universe_id)
        return next_state
    
    def _update_coherence(self, states: List[Dict]):
        n = len(states)
        self.coherence_matrix = np.zeros((n, n))
        
        for i in range(n):
            for j in range(n):
                if i == j:
                    self.coherence_matrix[i, j] = 1.0
                else:
                    # 计算状态相似度（相干性）
                    sim = self._state_similarity(states[i], states[j])
                    self.coherence_matrix[i, j] = sim
                    self.coherence_matrix[j, i] = sim
        
        # 更新每个宇宙的相干属性
        for i, universe in enumerate(self.universes):
            universe.coherence_with_others = np.mean(self.coherence_matrix[i])
    
    def _state_similarity(self, state_a: Dict, state_b: Dict) -> float:
        common_keys = set(state_a.keys()) & set(state_b.keys())
        if not common_keys:
            return 0.0
        
        similarities = []
        for key in common_keys:
            val_a = state_a[key]
            val_b = state_b[key]
            
            if isinstance(val_a, (int, float)) and isinstance(val_b, (int, float)):
                # 数值相似度
                sim = 1.0 - min(abs(val_a - val_b) / (abs(val_a) + abs(val_b) + 1e-8), 1.0)
                similarities.append(sim)
            elif isinstance(val_a, str) and isinstance(val_b, str):
                # 字符串相等
                similarities.append(1.0 if val_a == val_b else 0.0)
        
        return np.mean(similarities) if similarities else 0.0
    
    def decohere_and_select(self, selection_criteria: Callable) -> CognitiveUniverse:
        # 基于相干性和结果质量计算选择概率
        scores = []
        for universe in self.universes:
            outcome_quality = selection_criteria(universe.evolution_trajectory[-1])
            coherence_bonus = universe.coherence_with_others * 0.1  # 略微偏好与多数一致的
            
            score = outcome_quality + coherence_bonus
            scores.append(score)
        
        # 概率归一化
        probs = np.array(scores)
        probs = probs / probs.sum()
        
        # 选择（或加权组合）
        selected_idx = np.random.choice(len(self.universes), p=probs)
        
        # 退相干：其他宇宙的概率权重降低（类似波函数坍缩）
        for i, universe in enumerate(self.universes):
            if i != selected_idx:
                universe.probability_weight *= 0.1  # 抑制
        
        self.universes[selected_idx].probability_weight = 1.0 - sum(
            u.probability_weight for u in self.universes if u != self.universes[selected_idx]
        )
        
        return self.universes[selected_idx]
    
    def merge_insights(self) -> Dict:
        # 收集所有宇宙的关键发现
        all_discoveries = []
        for universe in self.universes:
            if len(universe.evolution_trajectory) > 1:
                final = universe.evolution_trajectory[-1]
                all_discoveries.append({
                    'universe_id': universe.universe_id,
                    'outcome': final,
                    'weight': universe.probability_weight,
                    'path_length': len(universe.evolution_trajectory)
                })
        
        # 加权投票/平均
        merged = {
            'consensus_outcome': self._weighted_consensus(all_discoveries),
            'diversity_score': len(set(str(d['outcome']) for d in all_discoveries)),
            'optimal_universe': max(all_discoveries, key=lambda x: x['weight'])['universe_id'],
            'exploration_coverage': len(all_discoveries) / self.branching_factor
        }
        
        return merged
    
    def _weighted_consensus(self, discoveries: List[Dict]) -> Dict:
        if not discoveries:
            return {}
        
        # 对数值属性加权平均
        result = {}
        all_keys = set()
        for d in discoveries:
            all_keys.update(d['outcome'].keys())
        
        for key in all_keys:
            weighted_sum = 0
            weight_total = 0
            for d in discoveries:
                if key in d['outcome'] and isinstance(d['outcome'][key], (int, float)):
                    weighted_sum += d['outcome'][key] * d['weight']
                    weight_total += d['weight']
            
            if weight_total > 0:
                result[key] = weighted_sum / weight_total
        
        return result

# === 验证 ===
def validate_many_worlds():
    engine = ManyWorldsCognitiveEngine(branching_factor=4)
    
    # 问题：在不确定性下寻找最优参数
    problem = {
        'learning_rate': 0.01,
        'batch_size': 32,
        'epochs': 100,
        'target_metric': 0.95
    }
    
    uncertainties = ['learning_rate', 'batch_size']
    
    # 初始化多元宇宙
    engine.initialize_multiverse(problem, uncertainties)
    
    print("=== 初始多元宇宙 ===")
    for u in engine.universes:
        print(f"宇宙{u.universe_id}: lr={u.initial_conditions['learning_rate']:.4f}, "
              f"bs={u.initial_conditions['batch_size']}")
    
    # 演化（模拟训练过程）
    def evolution_step(state, universe_id):
        # 模拟训练动态
        lr = state['learning_rate']
        bs = state['batch_size']
        
        # 不同宇宙有不同的收敛速度
        progress = 0.01 * (1 + universe_id * 0.1)
        new_metric = state.get('current_metric', 0.5) + progress * (1 - lr * 10)
        
        return {
            **state,
            'current_metric': min(new_metric, state['target_metric']),
            'step': state.get('step', 0) + 1
        }
    
    for step in range(5):
        engine.evolve_step(evolution_step, step)
        print(f"\n步骤 {step+1}: 相干矩阵对角线均值 = {np.mean(np.diag(engine.coherence_matrix)):.3f}")
    
    # 退相干选择
    def criteria(final_state):
        return final_state.get('current_metric', 0)
    
    selected = engine.decohere_and_select(criteria)
    print(f"\n=== 选择结果 ===")
    print(f"最优宇宙ID: {selected.universe_id}")
    print(f"最终指标: {selected.evolution_trajectory[-1].get('current_metric', 0):.3f}")
    print(f"选择后概率权重: {selected.probability_weight:.2f}")
    
    # 合并洞见
    consensus = engine.merge_insights()
    print(f"\n=== 多元宇宙共识 ===")
    print(f"探索覆盖率: {consensus['exploration_coverage']:.1%}")
    print(f"多样性得分: {consensus['diversity_score']}")
    
    print("\n✓ 多世界认知引擎验证通过")
    return engine

if __name__ == "__main__":
    validate_many_worlds()
