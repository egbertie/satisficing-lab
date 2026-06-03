# STATUS: FUNCTIONAL_CODE - 已通过 py_compile，待端到端验证
# BATCH: V2_EXTRACTION - 2026-04-05
# REALIZATION: ~55-80%
# AUDIT: 详见 A-manyige/对话/2026-04-05/17-知识入库两次方法对照审计报告-2026-04-05.md

import numpy as np
from typing import Dict, List, Tuple, Optional, Callable
from dataclasses import dataclass
from scipy.integrate import odeint
import matplotlib.pyplot as plt

@dataclass
class ThermodynamicCognitiveState:
    steady_state_distance: float     # 距离稳态的距离

class DissipativeCognitiveStructure:
    基于Prigogine的最小熵产生原理
    
    def __init__(self, n_processes: int = 5):
        self.n = n_processes
        # 热力学力（化学势差、温度差等）
        self.affinities = np.zeros(n_processes)
        # 流（认知活动的速率）
        self.fluxes = np.zeros(n_processes)
        # 熵产生矩阵（Onsager系数）
        self.L_matrix = np.eye(n_processes) * 0.1  # 线性响应系数
        # 内部状态变量
        self.state = np.ones(n_processes) / n_processes  # 归一化
        self.history = []
        
    def calculate_entropy_production(self) -> float:
#         计算熵产生率 σ = Σ J_i X_i
        sigma = np.dot(self.fluxes, self.affinities)
        return max(sigma, 0)  # 熵产生必须非负（热力学第二定律）
    
    def onsager_relations(self) -> np.ndarray:
#         Onsager互反关系：J = L·X
        L是对称正定的Onsager矩阵
        # 确保L对称正定
        L_sym = (self.L_matrix + self.L_matrix.T) / 2
        eigenvalues = np.linalg.eigvalsh(L_sym)
        if np.any(eigenvalues <= 0):
            # 调整为正定
            L_sym += np.eye(self.n) * (abs(np.min(eigenvalues)) + 0.01)
        
        self.fluxes = L_sym @ self.affinities
        return self.fluxes
    
    def evolve_to_steady_state(self, 
                                external_constraints: Dict[int, float],
                                time_span: np.ndarray) -> List[ThermodynamicCognitiveState]:
        def dynamics(state, t):
            # 动态方程：d(state)/dt = -Γ·∇F + noise
            # 其中F是自由能，Γ是衰减系数
            
            # 计算自由能梯度（简化：二次势）
            free_energy_grad = state - 0.2  # 假设稳态在0.2
            
            # 热噪声（涨落-耗散定理）
            noise = np.random.normal(0, 0.01, self.n)
            
            # 外部约束（固定某些认知过程）
            for idx, val in external_constraints.items():
                if 0 <= idx < self.n:
                    state[idx] = val
            
            dsdt = -0.1 * free_energy_grad + noise
            
            # 确保归一化（概率守恒）
            dsdt -= np.mean(dsdt)
            
            return dsdt
        
        trajectory = odeint(dynamics, self.state, time_span)
        
        states = []
        for i, s in enumerate(trajectory):
            self.state = s
            
            # 更新亲和力和流
            self.affinities = s - 0.1  # 偏离参考态的差
            self.onsager_relations()
            
            sigma = self.calculate_entropy_production()
            
            tc_state = ThermodynamicCognitiveState(
                internal_entropy=-np.sum(s * np.log(s + 1e-10)),
                external_entropy_production=sigma,
                free_energy=-np.sum(s * np.log(s + 1e-10)) + 0.5 * np.sum(s**2),
                affinity=self.affinities.copy(),
                fluxes=self.fluxes.copy(),
                steady_state_distance=np.linalg.norm(s - 0.2)
            )
            states.append(tc_state)
        
        self.history.extend(states)
        return states
    
    def minimize_entropy_production(self, 
                                     target_constraints: Dict[int, Tuple[float, float]]) -> np.ndarray:
        from scipy.optimize import minimize
        
        def objective(x):
            # 目标：最小化熵产生
            affinities = x - 0.2
            fluxes = self.L_matrix @ affinities
            sigma = np.dot(fluxes, affinities)
            return sigma
        
        # 约束条件
        constraints = []
        for idx, (lb, ub) in target_constraints.items():
            constraints.append({'type': 'ineq', 'fun': lambda x, i=idx: x[i] - lb})
            constraints.append({'type': 'ineq', 'fun': lambda x, i=idx: ub - x[i]})
        
        # 归一化约束
        constraints.append({'type': 'eq', 'fun': lambda x: np.sum(x) - 1.0})
        
        result = minimize(objective, self.state, method='SLSQP', 
                         constraints=constraints)
        
        return result.x
    
    def calculate_exergy(self, environment_state: np.ndarray) -> float:
        # 㶲 = U - U_env + P_env(V - V_env) - T_env(S - S_env)
        # 简化：基于状态差异
        exergy = np.sum((self.state - environment_state)**2)
        return exergy
    
    def detect_bifurcation(self, parameter_range: np.ndarray) -> List[float]:
        bifurcation_points = []
        prev_state = None
        
        for param in parameter_range:
            # 改变控制参数（如外部信息流入速率）
            self.L_matrix[0, 0] = param
            
            # 寻找稳态
            steady = self.minimize_entropy_production({})
            
            if prev_state is not None:
                # 检测突变（大变化）
                if np.linalg.norm(steady - prev_state) > 0.3:
                    bifurcation_points.append(param)
            
            prev_state = steady
        
        return bifurcation_points
    
    def export_entropy_to_environment(self, entropy_amount: float) -> bool:
        维持内部低熵的必要操作
        current_internal = -np.sum(self.state * np.log(self.state + 1e-10))
        
        # 模拟熵导出：重置某些状态
        if entropy_amount > 0:
            # "遗忘"低概率状态
            threshold = 0.1
            self.state[self.state < threshold] = 0
            # 重归一化
            if np.sum(self.state) > 0:
                self.state /= np.sum(self.state)
        
        new_internal = -np.sum(self.state * np.log(self.state + 1e-10))
        
        return new_internal < current_internal  # 成功降低熵

class CognitiveThermodynamicsOrchestrator:
    
    def __init__(self):
        self.structures: Dict[str, DissipativeCognitiveStructure] = {}
        self.heat_reservoirs: Dict[str, float] = {}  # 热库（环境熵容量）
        
    def register_cognitive_process(self, name: str, n_subprocesses: int):
        self.structures[name] = DissipativeCognitiveStructure(n_subprocesses)
        self.heat_reservoirs[name] = 100.0  # 初始熵容量
    
    def orchestrate_cognitive_flow(self, 
                                     information_input_rate: float) -> Dict:
        total_entropy_budget = 0
        
        for name, structure in self.structures.items():
            # 信息输入增加亲和力（热力学力）
            structure.affinities[0] = information_input_rate
            
            # 计算新的稳态
            steady_state = structure.minimize_entropy_production({})
            
            # 计算该过程产生的熵
            sigma = structure.calculate_entropy_production()
            
            # 检查环境是否有足够熵容量
            if self.heat_reservoirs[name] >= sigma:
                self.heat_reservoirs[name] -= sigma
                total_entropy_budget += sigma
            else:
                # 熵饱和：认知过载
                return {
                    'status': 'cognitive_overload',
                    'process': name,
                    'entropy_production': sigma,
                    'remaining_capacity': self.heat_reservoirs[name]
                }
            
            # 周期性熵清理（睡眠/遗忘机制）
            if self.heat_reservoirs[name] < 20:
                structure.export_entropy_to_environment(10.0)
                self.heat_reservoirs[name] += 10.0
        
        return {
            'status': 'optimal',
            'total_entropy_production': total_entropy_budget,
            'efficiency': 1.0 / (1.0 + total_entropy_budget)
        }

# === 验证 ===
def validate_thermodynamic_cognition():
    thermo = DissipativeCognitiveStructure(n_processes=3)
    
    # 模拟认知演化
    time_span = np.linspace(0, 10, 100)
    external_constraints = {0: 0.5}  # 固定第一个认知过程
    
    trajectory = thermo.evolve_to_steady_state(external_constraints, time_span)
    
    print("=== 热力学认知演化 ===")
    print(f"初始熵产生: {trajectory[0].external_entropy_production:.4f}")
    print(f"稳态熵产生: {trajectory[-1].external_entropy_production:.4f}")
    print(f"稳态距离: {trajectory[-1].steady_state_distance:.4f}")
    
    # 验证：熵产生应趋向最小（Prigogine原理）
    entropies = [s.external_entropy_production for s in trajectory]
    assert entropies[-1] <= entropies[0] * 1.1, "熵产生应最小化或稳定"
    
    # 最小熵产生优化
    optimal = thermo.minimize_entropy_production({
        0: (0.3, 0.7),
        1: (0.1, 0.5)
    })
    print(f"\n最优认知配置: {optimal.round(3)}")
    print(f"最优状态熵: {-np.sum(optimal * np.log(optimal + 1e-10)):.4f}")
    
    # 检测分叉（认知相变）
    bifurcations = thermo.detect_bifurcation(np.linspace(0.01, 1.0, 50))
    print(f"\n检测到的认知分叉点数: {len(bifurcations)}")
    
    # 编排器测试
    orchestrator = CognitiveThermodynamicsOrchestrator()
    orchestrator.register_cognitive_process("perception", 4)
    orchestrator.register_cognitive_process("reasoning", 5)
    
    result = orchestrator.orchestrate_cognitive_flow(information_input_rate=0.8)
    print(f"\n编排结果: {result['status']}")
    if result['status'] == 'optimal':
        print(f"总熵产生: {result['total_entropy_production']:.4f}")
        print(f"认知效率: {result['efficiency']:.2%}")
    
    print("\n✓ 热力学认知系统验证通过")
    return thermo

if __name__ == "__main__":
    validate_thermodynamic_cognition()
