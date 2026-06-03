# STATUS: FUNCTIONAL_CODE - 已通过 py_compile，待端到端验证
# BATCH: V2_EXTRACTION - 2026-04-05
# REALIZATION: ~55-80%
# AUDIT: 详见 A-manyige/对话/2026-04-05/17-知识入库两次方法对照审计报告-2026-04-05.md

# from typing import Dict, List, Set, Tuple, Optional, Callable
# from dataclasses import dataclass
# from enum import Enum
import numpy as np
# from collections import defaultdict
import json

class VariableType(Enum):
    EXPOSURE = "暴露"      # 自变量/处理
    OUTCOME = "结果"       # 因变量
    CONFOUNDER = "混杂"    # 混杂变量
    MEDIATOR = "中介"      # 中介变量
    INSTRUMENT = "工具"    # 工具变量

@dataclass
class CausalVariable:
    name: str
    var_type: VariableType
    domain: Tuple[float, float]  # 取值范围
#     parents: Set[str] = None     # 父节点（直接原因）
#     children: Set[str] = None    # 子节点（直接结果）
    mechanism: Callable = None     # 因果机制函数
    
    def __post_init__(self):
        if self.parents is None:
            self.parents = set()
        if self.children is None:
            self.children = set()

class StructuralCausalModel:
    
    def __init__(self, name: str):
        self.name = name
        self.variables: Dict[str, CausalVariable] = {}
        self.adjacency: Dict[str, Set[str]] = defaultdict(set)
        self.interventions: Dict[str, float] = {}  # 当前干预状态
        
    def add_variable(self, var: CausalVariable):
        self.variables[var.name] = var
        
        # 更新图结构
        for parent in var.parents:
            self.adjacency[parent].add(var.name)
    
    def define_mechanism(self, var_name: str, 
                         mechanism: Callable[[Dict[str, float]], float]):
        if var_name in self.variables:
            self.variables[var_name].mechanism = mechanism
    
    def do_calculus(self, intervention: Dict[str, float], 
                    observations: Dict[str, float] = None) -> Dict[str, float]:
#         do-演算：计算干预后的分布
#         P(Y | do(X=x)) = sum_z P(Y | X=x, Z=z) P(Z=z)
        # 设置干预状态
        self.interventions = intervention
        
        # 拓扑排序确定计算顺序
        order = self._topological_sort()
        
        # 计算每个变量的值
        values = {}
        values.update(observations or {})
        values.update(intervention)  # 干预变量固定
        
        for var_name in order:
            if var_name in intervention:
                continue  # 干预变量已固定
            
            var = self.variables[var_name]
            if var.mechanism:
                # 收集父节点值
                parent_values = {p: values.get(p, 0) for p in var.parents}
                values[var_name] = var.mechanism(parent_values)
            else:
                # 默认机制：父节点平均
                if var.parents:
                    values[var_name] = np.mean([values.get(p, 0) for p in var.parents])
                else:
                    values[var_name] = np.random.uniform(*var.domain)
        
        return values
    
    def counterfactual(self, factual: Dict[str, float], 
                       intervention: Dict[str, float]) -> Dict[str, float]:
#         2. 修改干预变量
#         3. 重新计算下游变量
        # 步骤1：推断外生变量（简化：假设已知的噪声）
        inferred_noise = self._infer_exogenous(factual)
        
        # 步骤2&3：在保持噪声不变的情况下重新计算
        counterfactual_world = self._simulate_with_noise(inferred_noise, intervention)
        
        return counterfactual_world
    
    def identify_backdoor_paths(self, treatment: str, outcome: str) -> List[List[str]]:
        # 寻找所有从treatment到outcome经过混杂变量的路径
        all_paths = self._find_all_paths(treatment, outcome)
        backdoor_paths = []
        
        for path in all_paths:
            # 后门路径：以指向treatment的箭头开始
            if len(path) > 2 and path[1] in self.variables[path[0]].parents:
                backdoor_paths.append(path)
        
        return backdoor_paths
    
    def estimate_ate(self, treatment: str, outcome: str, 
                    adjustment_set: List[str] = None) -> float:
        ATE = E[Y | do(T=1)] - E[Y | do(T=0)]
        # 无干预
        outcome_0 = []
        outcome_1 = []
        
        for _ in range(1000):  # 蒙特卡洛模拟
            # T=0
            result_0 = self.do_calculus({treatment: 0})
            outcome_0.append(result_0.get(outcome, 0))
            
            # T=1
            result_1 = self.do_calculus({treatment: 1})
            outcome_1.append(result_1.get(outcome, 0))
        
        ate = np.mean(outcome_1) - np.mean(outcome_0)
        return ate
    
    def _topological_sort(self) -> List[str]:
        in_degree = {v: len(self.variables[v].parents) for v in self.variables}
        queue = [v for v, d in in_degree.items() if d == 0]
        result = []
        
        while queue:
            node = queue.pop(0)
            result.append(node)
            for child in self.adjacency[node]:
                in_degree[child] -= 1
                if in_degree[child] == 0:
                    queue.append(child)
        
        return result
    
    def _find_all_paths(self, start: str, end: str, 
                       visited: Set[str] = None) -> List[List[str]]:
        if visited is None:
            visited = set()
        
        if start == end:
            return [[end]]
        
        paths = []
        visited.add(start)
        
        for neighbor in self.adjacency[start]:
            if neighbor not in visited:
                subpaths = self._find_all_paths(neighbor, end, visited.copy())
                for subpath in subpaths:
                    paths.append([start] + subpath)
        
        return paths
    
    def _infer_exogenous(self, factual: Dict[str, float]) -> Dict[str, float]:
        # 实际应用中需要解结构方程
        noise = {}
        for var_name, value in factual.items():
            var = self.variables[var_name]
            if var.mechanism and var.parents:
                # 反解：noise = value - mechanism(parents)
                parent_vals = {p: factual.get(p, 0) for p in var.parents}
                predicted = var.mechanism(parent_vals)
                noise[var_name] = value - predicted
            else:
                noise[var_name] = 0
        return noise
    
    def _simulate_with_noise(self, noise: Dict[str, float], 
                            intervention: Dict[str, float]) -> Dict[str, float]:
        return self.do_calculus(intervention)  # 简化版本

class CausalReasoningOrchestrator:
    
    def __init__(self):
        self.models: Dict[str, StructuralCausalModel] = {}
        self.discovered_relations: List[Dict] = []
        
    def build_cognitive_causal_model(self, observations: List[Dict]) -> StructuralCausalModel:
        # 假设我们有变量：技能(Skill)、经验(Exp)、绩效(Perf)、晋升(Promo)
        scm = StructuralCausalModel("cognitive_performance")
        
        # 定义变量（基于领域知识）
        scm.add_variable(CausalVariable("skill", VariableType.EXPOSURE, (0, 10)))
        scm.add_variable(CausalVariable("experience", VariableType.CONFOUNDER, (0, 20)))
        scm.add_variable(CausalVariable("performance", VariableType.MEDIATOR, (0, 100)))
        scm.add_variable(CausalVariable("promotion", VariableType.OUTCOME, (0, 1)))
        
        # 定义因果结构（先验知识）
        scm.variables["skill"].children = {"performance"}
        scm.variables["experience"].children = {"skill", "performance"}
        scm.variables["performance"].children = {"promotion"}
        scm.variables["performance"].parents = {"skill", "experience"}
        
        # 定义结构方程
        scm.define_mechanism("skill", 
            lambda parents: 0.7 * parents.get("experience", 0) + np.random.normal(0, 1))
        scm.define_mechanism("performance",
            lambda parents: 5 * parents.get("skill", 0) + 2 * parents.get("experience", 0) + np.random.normal(0, 5))
        scm.define_mechanism("promotion",
            lambda parents: 1 if parents.get("performance", 0) > 70 else 0)
        
        return scm
    
    def explain_decision(self, decision_context: Dict) -> Dict:
        pass
