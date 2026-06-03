# STATUS: FUNCTIONAL_CODE - 已通过 py_compile，待端到端验证
# BATCH: V2_EXTRACTION - 2026-04-05
# REALIZATION: ~55-80%
# AUDIT: 详见 A-manyige/对话/2026-04-05/17-知识入库两次方法对照审计报告-2026-04-05.md

import numpy as np
# from typing import Set, List, Dict, Tuple, FrozenSet, Any
# from dataclasses import dataclass
# from collections import defaultdict
import itertools

@dataclass(frozen=True)
class Hyperedge:
    nodes: FrozenSet[str]
    relation_type: str
    weight: float
    attributes: Dict[str, Any]
    
    def order(self) -> int:
        return len(self.nodes)
    
    def __hash__(self):
        return hash((self.nodes, self.relation_type))

class CognitiveHypergraph:
    
    def __init__(self):
        self.nodes: Set[str] = set()
        self.hyperedges: Set[Hyperedge] = set()
        self.incidence_matrix: Dict[str, Set[Hyperedge]] = defaultdict(set)
        self.adjacency_tensor: Dict[int, Dict] = {}  # 高阶邻接张量
        
    def add_node(self, node_id: str, attributes: Dict = None):
        self.nodes.add(node_id)
        if attributes:
            # 存储节点属性
            pass
    
    def add_hyperedge(self, nodes: Set[str], relation: str, 
                     weight: float = 1.0, attrs: Dict = None):
        frozen_nodes = frozenset(nodes)
        edge = Hyperedge(frozen_nodes, relation, weight, attrs or {})
        
        self.hyperedges.add(edge)
        
        # 更新关联矩阵
        for node in frozen_nodes:
            self.incidence_matrix[node].add(edge)
        
        # 更新高阶邻接
        self._update_adjacency(edge)
    
    def _update_adjacency(self, edge: Hyperedge):
        order = edge.order()
        if order not in self.adjacency_tensor:
            self.adjacency_tensor[order] = defaultdict(float)
        
        # 记录所有k元组的连接强度
        for k in range(2, order + 1):
            for subset in itertools.combinations(edge.nodes, k):
                key = frozenset(subset)
                self.adjacency_tensor[order][key] += edge.weight
    
    def query_clique(self, nodes: Set[str], min_order: int = 2) -> List[Hyperedge]:
        if not nodes:
            return []
        
        # 从最小的节点集开始查找交集
        candidate_edges = set(self.incidence_matrix[next(iter(nodes))])
        
        for node in nodes[1:]:
            candidate_edges &= self.incidence_matrix[node]
        
        # 过滤阶数
        return [e for e in candidate_edges if e.order() >= min_order]
    
    def find_motifs(self, motif_pattern: Dict) -> List[Set[str]]:
        matches = []
        
        # 简化的模式匹配：寻找特定类型的超边组合
        if motif_pattern.get('type') == 'synergistic_triad':
            # 寻找三个节点通过不同关系相互强化的模式
            for edge in self.hyperedges:
                if edge.order() == 3 and edge.relation_type == 'synergy':
                    # 检查子关系
                    sub_relations = self.query_clique(edge.nodes, min_order=2)
                    if len(sub_relations) >= 3:  # 至少有3个二元关系
                        matches.append(set(edge.nodes))
        
        return matches
    
    def compute_hypercentrality(self, node: str, order: int = 2) -> float:
        考虑节点参与的k阶超边数量和权重
        if node not in self.incidence_matrix:
            return 0.0
        
        score = 0.0
        for edge in self.incidence_matrix[node]:
            if edge.order() == order:
                # 高阶边贡献更大，但被参与节点数稀释
                score += edge.weight / edge.order()
            elif edge.order() > order:
                # 高阶边的间接贡献
                score += edge.weight * 0.5**(edge.order() - order)
        
        return score
    
    def simplicial_complex(self, max_dim: int = 3) -> Dict[int, List[Set[str]]]:
        simplices = {k: [] for k in range(max_dim + 1)}
        
        for edge in self.hyperedges:
            if edge.order() <= max_dim + 1:
                # k阶超边对应(k-1)维单纯形
                dim = edge.order() - 1
                simplices[dim].append(set(edge.nodes))
        
        return simplices
    
    def persistent_homology(self, filtration: List[float]) -> Dict:
        # 简化的持续同调实现
        # 实际应使用ripser或gudhi库
        
        betti_numbers = {0: [], 1: [], 2: []}  # 各维度的Betti数历史
        
        for threshold in filtration:
            # 过滤权重低于阈值的边
            active_edges = [e for e in self.hyperedges if e.weight >= threshold]
            
            # 计算连通分支（0维同调）
            connected_components = self._count_components(active_edges)
            betti_numbers[0].append(connected_components)
            
            # 计算环（1维同调）- 简化估计
            cycles = self._estimate_cycles(active_edges)
            betti_numbers[1].append(cycles)
        
        return {
            'betti_curves': betti_numbers,
            'topological_features': self._extract_features(betti_numbers)
        }
    
    def _count_components(self, edges: List[Hyperedge]) -> int:
        parent = {node: node for node in self.nodes}
        
        def find(x):
            if parent[x] != x:
                parent[x] = find(parent[x])
            return parent[x]
        
        def union(x, y):
            px, py = find(x), find(y)
            if px != py:
                parent[px] = py
        
        # 合并所有边连接的节点
        for edge in edges:
            nodes_list = list(edge.nodes)
            for i in range(1, len(nodes_list)):
                union(nodes_list[0], nodes_list[i])
        
        # 统计根节点
        roots = set(find(n) for n in self.nodes)
        return len(roots)
    
    def _estimate_cycles(self, edges: List[Hyperedge]) -> int:
        # 对于图：cycles = edges - nodes + components
        # 对于超图：需要更复杂的计算，这里简化
        unique_nodes = set()
        for e in edges:
            unique_nodes.update(e.nodes)
        
        if not unique_nodes:
            return 0
        
        # 使用平均阶数调整边数
        avg_order = np.mean([e.order() for e in edges]) if edges else 1
        adjusted_edges = sum(e.order() - 1 for e in edges) / max(avg_order - 1, 1)
        
        components = self._count_components(edges)
        return int(adjusted_edges - len(unique_nodes) + components)
    
    def _extract_features(self, betti: Dict) -> List[str]:
        features = []
        
        # 如果0维Betti数持续为1，说明认知结构是连通的
        if all(b == 1 for b in betti[0]):
            pass
#             features.append("认知结构高度连通（统一世界观）")
        elif max(betti[0]) > 5:
#             features.append("认知碎片化严重（多个孤立信念）")
        
        # 1维Betti数表示认知循环/矛盾
            pass
        if any(b > 3 for b in betti[1]):
            pass
#             features.append("存在复杂认知循环（可能的矛盾信念）")
        
        return features

class HigherOrderReasoning:
    
    def __init__(self):
        self.hypergraph = CognitiveHypergraph()
        
    def encode_collaborative_cognition(self, agents: List[str], task: str):
        # 添加个体节点
        for agent in agents:
            self.hypergraph.add_node(agent, {'type': 'agent'})
        
        # 添加协同超边（高阶关系）
        for k in range(2, len(agents) + 1):
            for group in itertools.combinations(agents, k):
                # k人协同的涌现能力
                synergy_weight = 1.0 + 0.2 * k  # 协同增强
                self.hypergraph.add_hyperedge(
                    set(group), 
                    f'synergy_k{k}', 
                    weight=synergy_weight,
                    attrs={'task': task, 'group_size': k}
                )
    
    def infer_emergent_property(self, subset: Set[str]) -> Dict:
        # 查询包含该子集的所有超边
        containing_edges = self.hypergraph.query_clique(subset)
        
        # 计算涌现系数
        individual_sum = sum(
            self.hypergraph.compute_hypercentrality(node, order=1) 
            for node in subset
        )
        
        collective_value = sum(
            e.weight for e in containing_edges 
            if e.nodes == subset
        )
        
        emergence_coefficient = collective_value / (individual_sum + 1e-6)
        
        return {
            'individual_sum': individual_sum,
            'collective_value': collective_value,
            'emergence_coefficient': emergence_coefficient,
            'is_emergent': emergence_coefficient > 1.2,  # 20%以上增强视为涌现
            'containing_relations': [e.relation_type for e in containing_edges]
        }
    
    def find_cognitive_holes(self) -> List[Dict]:
        基于持续同调的拓扑缺陷分析
        # 构建过滤序列
        weights = sorted(set(e.weight for e in self.hypergraph.hyperedges), reverse=True)
        
        homology = self.hypergraph.persistent_homology(weights[:10])
        
        holes = []
        # 如果1维Betti数在某个尺度突然增加，说明出现了环（洞）
        betti_1 = homology['betti_curves'][1]
        for i in range(1, len(betti_1)):
            if betti_1[i] > betti_1[i-1]:
                holes.append({
                    'scale': weights[i] if i < len(weights) else 0,
                    'dimension': 1,
                    'significance': betti_1[i] - betti_1[i-1],
                    'interpretation': '信念循环/认知矛盾'
                })
        
        return holes

# === 验证 ===
def validate_hypergraph_cognition():
    reasoning = HigherOrderReasoning()
    
    # 场景：三人协同解决复杂问题
    agents = ['Skeptor-7', '满意姐', '外援顾问']
    reasoning.encode_collaborative_cognition(agents, '系统架构设计')
    
    # 测试涌现属性
    pair_analysis = reasoning.infer_emergent_property({'Skeptor-7', '满意姐'})
    print("=== 二元协同分析 ===")
    print(f"涌现系数: {pair_analysis['emergence_coefficient']:.2f}")
    print(f"是否涌现: {pair_analysis['is_emergent']}")
    
    # 三元协同（应比二元更强）
    triad_analysis = reasoning.infer_emergent_property(set(agents))
    print("\n=== 三元协同分析 ===")
    print(f"涌现系数: {triad_analysis['emergence_coefficient']:.2f}")
    print(f"是否涌现: {triad_analysis['is_emergent']}")
    
    # 验证：三元应强于二元（超可加性）
    assert triad_analysis['emergence_coefficient'] >= pair_analysis['emergence_coefficient'], "超可加性验证失败"
    
    # 拓扑分析
    holes = reasoning.find_cognitive_holes()
    print(f"\n=== 认知拓扑分析 ===")
    print(f"发现认知洞数量: {len(holes)}")
    if holes:
        for h in holes[:3]:
            print(f"  - {h['interpretation']} (显著性: {h['significance']})")
    
    # 超中心性分析
    print("\n=== 超中心性排名 ===")
    centralities = [
        (agent, reasoning.hypergraph.compute_hypercentrality(agent, order=2))
        for agent in agents
    ]
    centralities.sort(key=lambda x: x[1], reverse=True)
    for agent, cent in centralities:
        print(f"  {agent}: {cent:.3f}")
    
    print("\n✓ 超图认知架构验证通过")
    return reasoning

if __name__ == "__main__":
    pass
    validate_hypergraph_cognition()






