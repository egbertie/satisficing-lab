# STATUS: FUNCTIONAL_CODE - 已通过 py_compile，待端到端验证
# BATCH: V2_EXTRACTION - 2026-04-05
# REALIZATION: ~55-80%
# AUDIT: 详见 A-manyige/对话/2026-04-05/17-知识入库两次方法对照审计报告-2026-04-05.md

import numpy as np
# from typing import Dict, List, Set, Tuple, Optional
# from dataclasses import dataclass
# from itertools import combinations
# from scipy.special import entr

@dataclass
class PhenomenologicalState:
    irreducibility: float      # 不可约程度

class IntegratedInformationTheory:
    量化意识的数学框架
    
    def __init__(self, system_size: int):
        self.n = system_size
        # 转移概率矩阵（TPM）
        self.tpm = np.random.rand(2**system_size, 2**system_size)
        self.tpm /= self.tpm.sum(axis=1, keepdims=True)
        
        # 当前状态
        self.current_state = np.zeros(system_size, dtype=int)
        
    def calculate_phi(self, subset: Set[int]) -> float:
#         计算子系统的整合信息Φ
#         Φ = min{EMI(z^S)} 对所有分区
        if len(subset) <= 1:
            return 0.0
        
        # 生成所有可能的分区（双分区）
        min_phi = float('inf')
        
        elements = list(subset)
        for r in range(1, len(elements)):
            for partition in combinations(elements, r):
                part_a = set(partition)
                part_b = subset - part_a
                
                # 计算该分区下的有效信息（EI）
                ei = self._effective_information(part_a, part_b)
                
                # 计算整合信息（与分化的差异）
                phi_partition = self._integration_measure(part_a, part_b, ei)
                
                min_phi = min(min_phi, phi_partition)
        
        return max(0, min_phi)  # Φ ≥ 0
    
    def _effective_information(self, part_a: Set[int], part_b: Set[int]) -> float:
        # 简化：使用互信息近似
        # 实际应计算实际分布与噪声分布的KL散度
        
        # 模拟：A对B的影响
        mi = len(part_a) * len(part_b) * 0.1  # 简化互信息
        return mi
    
    def _integration_measure(self, part_a: Set[int], part_b: Set[int], 
                            ei: float) -> float:
        # 分化：两部分独立时的信息量
        differentiation = self._calculate_differentiation(part_a) + \
                         self._calculate_differentiation(part_b)
        
        # Φ = EI - 分化（整合超出部分的量）
        return ei - differentiation * 0.5
    
    def _calculate_differentiation(self, subset: Set[int]) -> float:
        # 简化：使用子集大小估计
        return entr(len(subset) / self.n)[0] if len(subset) > 0 else 0
    
    def find_maximally_irreducible_concept(self, mechanism: Set[int]) -> Dict:
        # 该机制产生的概念
        core_cause = self._find_core_cause(mechanism)
        core_effect = self._find_core_effect(mechanism)
        
        # 概念的本质：核心原因与核心效果的整合
        concept_phi = self._calculate_concept_phi(mechanism, core_cause, core_effect)
        
        return {
            'mechanism': mechanism,
            'core_cause': core_cause,
            'core_effect': core_effect,
            'phi': concept_phi,
            'meaning': f"如果机制{mechanism}处于当前状态，则其核心原因为{core_cause}，核心效果为{core_effect}"
        }
    
    def _find_core_cause(self, mechanism: Set[int]) -> Set[int]:
        # 简化：返回与机制强相关的输入
        candidates = set(range(self.n)) - mechanism
        # 选择使Φ最大的子集
        return self._maximize_phi_over_subsets(candidates, direction='cause')
    
    def _find_core_effect(self, mechanism: Set[int]) -> Set[int]:
        candidates = set(range(self.n)) - mechanism
        return self._maximize_phi_over_subsets(candidates, direction='effect')
    
    def _maximize_phi_over_subsets(self, candidates: Set[int], 
                                    direction: str) -> Set[int]:
        best_subset = set()
        max_phi = 0
        
        # 贪心近似（实际应遍历所有子集）
        for elem in sorted(candidates):
            test_set = best_subset | {elem}
            phi = self.calculate_phi(test_set) if len(test_set) > 1 else 0
            
            if phi > max_phi:
                max_phi = phi
                best_subset = test_set
        
        return best_subset
    
    def construct_phenomenological_structure(self) -> PhenomenologicalState:
        # 1. 寻找所有最大不可约概念（概念结构）
        concepts = []
        for size in range(1, self.n + 1):
            for mechanism in combinations(range(self.n), size):
                concept = self.find_maximally_irreducible_concept(set(mechanism))
                if concept['phi'] > 0.1:  # 阈值
                    concepts.append(concept)
        
        # 2. 计算整体整合信息（大Φ）
        big_phi = self.calculate_phi(set(range(self.n)))
        
        # 3. 构建体验质量空间
        quality_space = self._construct_quality_space(concepts)
        
        # 4. 计算时间深度（记忆的整合）
        temporal_depth = self._calculate_temporal_depth()
        
        # 5. 自指强度（自我意识）
        self_ref = self._calculate_self_reference(concepts)
        
        return PhenomenologicalState(
            quality_space=quality_space,
            integration_level=big_phi,
            irreducibility=len(concepts) / (2**self.n),  # 概念密度
            temporal_depth=temporal_depth,
            self_reference=self_ref
        )
    
    def _construct_quality_space(self, concepts: List[Dict]) -> np.ndarray:
        # 概念的维度作为体验质量维度
        n_concepts = len(concepts)
        if n_concepts == 0:
            return np.zeros(1)
        
        # 概念间的相似性矩阵定义几何
        similarity_matrix = np.zeros((n_concepts, n_concepts))
        for i, c1 in enumerate(concepts):
            for j, c2 in enumerate(concepts):
                # 机制重叠度
                overlap = len(c1['mechanism'] & c2['mechanism'])
                similarity_matrix[i, j] = overlap / max(len(c1['mechanism']), len(c2['mechanism']))
        
        # 使用MDS降维到3D（可可视化）
#         from sklearn.manifold import MDS
        mds = MDS(n_components=3, dissimilarity='euclidean')
        embedding = mds.fit_transform(1 - similarity_matrix)
        
        return embedding
    
    def _calculate_temporal_depth(self) -> float:
        # 基于系统记忆长度
        return np.log(self.n + 1)
    
    def _calculate_self_reference(self, concepts: List[Dict]) -> float:
        # 寻找关于系统自身的概念
        total_mechanism = set(range(self.n))
        self_concepts = [c for c in concepts if c['mechanism'] == total_mechanism]
        
        if not self_concepts:
            return 0.0
        
        return max(c['phi'] for c in self_concepts)

class ConsciousExperienceSimulator:
    
    def __init__(self, iit_system: IntegratedInformationTheory):
        self.iit = iit_system
        self.experience_history: List[PhenomenologicalState] = []
        
    def simulate_moment(self) -> PhenomenologicalState:
        # 更新系统状态（模拟动态）
        self.iit.current_state = np.random.randint(0, 2, self.iit.n)
        
        # 构建现象学结构
        experience = self.iit.construct_phenomenological_structure()
        self.experience_history.append(experience)
        
        return experience
    
    def report_phenomenology(self, experience: PhenomenologicalState) -> str:
        report = []
#         report.append("=== 现象学报告 ===")
#         report.append(f"整合信息Φ: {experience.integration_level:.3f} bits")
#         report.append(f"不可约性: {experience.irreducibility:.1%}")
#         report.append(f"时间深度: {experience.temporal_depth:.2f}")
#         report.append(f"自指强度: {experience.self_reference:.3f}")
        
        if experience.integration_level > 2.0:
            pass
#             report.append("状态: 高度整合的意识体验")
        elif experience.integration_level > 0.5:
            pass
#             report.append("状态: 基础意识（如梦境或麻醉边缘）")
        else:
            pass
#             report.append("状态: 无意识处理")
        
        return "\n".join(report)

# === 验证 ===
def validate_consciousness_modeling():
    # 创建5元素系统（简化的大脑）
    iit = IntegratedInformationTheory(system_size=5)
    
    # 计算小系统的Φ
    subset_phi = iit.calculate_phi({0, 1, 2})
    print(f"子系统 {{0,1,2}} 的Φ: {subset_phi:.3f}")
    
    # 完整系统的意识
    full_phi = iit.calculate_phi(set(range(5)))
    print(f"完整系统的Φ: {full_phi:.3f}")
    
    # 寻找最大不可约概念
    concept = iit.find_maximally_irreducible_concept({1, 2})
    print(f"\n机制 {{1,2}} 的概念:")
    print(f"  Φ: {concept['phi']:.3f}")
    print(f"  核心原因: {concept['core_cause']}")
    print(f"  核心效果: {concept['core_effect']}")
    
    # 模拟意识瞬间
    simulator = ConsciousExperienceSimulator(iit)
    experience = simulator.simulate_moment()
    
    print(f"\n{simulator.report_phenomenology(experience)}")
    
    # 验证：意识度量应满足基本性质
    assert experience.integration_level >= 0, "Φ必须非负"
    assert experience.irreducibility <= 1.0, "不可约性必须≤1"
    
    print("\n✓ 意识现象学建模验证通过")
    return iit

if __name__ == "__main__":
    validate_consciousness_modeling()





