#!/usr/bin/env python3
# totem_multi_agent_council.py - 五路图腾多智能体系统
# 来源: 文件13 - AI决策系统设计.docx (认知层)
# 功能: 五图腾协同决策的多智能体系统
# 创建时间: 2026-04-04
# 版本: 1.0

import sys
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

sys.path.insert(0, '/root/.openclaw/workspace')
from defense_base_components import BaseComponent, MetricsCollector

class ElementType(Enum):
    """五行元素"""
    METAL = "金"      # 司马贺 - 理性
    EARTH = "土"      # 刘禹锡 - 德馨
    WATER = "水"      # 观自在 - 洞察
    WOOD = "木"       # 孔子 - 伦理
    FIRE = "火"       # 慧能 - 突破

@dataclass
class AgentPerspective:
    """Agent视角分析结果"""
    agent_name: str
    element: ElementType
    analysis: str
    confidence: float
    weight: float
    key_points: List[str]

@dataclass
class DecisionInput:
    """决策输入"""
    scenario: str
    context: Dict
    constraints: List[str]
    decision_type: str  # partner_matching, investment, strategy, etc.

class TotemMultiAgentCouncil(BaseComponent):
    """
    五路图腾多智能体系统
    
    基于文档需求的认知层实现：
    - 五图腾Agent协同分析
    - 动态权重调整
    - 视角冲突结构化呈现
    """
    
    def __init__(self):
        super().__init__('totem_council')
        self.metrics = MetricsCollector('council')
        
        # 五图腾Agent配置
        self.totem_agents = {
            'simon': {
                'name': '司马贺',
                'element': ElementType.METAL,
                'focus': ['边界分析', '满意解算法', '理性决策'],
                'default_weight': 0.25
            },
            'liuyuxi': {
                'name': '刘禹锡',
                'element': ElementType.EARTH,
                'focus': ['长期价值', '根基评估', '团队凝聚'],
                'default_weight': 0.20
            },
            'guanzizai': {
                'name': '观自在',
                'element': ElementType.WATER,
                'focus': ['直觉感知', '风险洞察', '定力判断'],
                'default_weight': 0.20
            },
            'confucius': {
                'name': '孔子',
                'element': ElementType.WOOD,
                'focus': ['五常评估', '伦理审视', '教化视角'],
                'default_weight': 0.20
            },
            'huineng': {
                'name': '慧能',
                'element': ElementType.FIRE,
                'focus': ['创新破执', '顿悟触发', '直觉突破'],
                'default_weight': 0.15
            }
        }
        
        # 决策类型权重调整规则
        self.decision_weights = {
            'partner_matching': {
                'confucius': 0.30,  # 合伙人匹配提高伦理权重
                'simon': 0.25,
                'guanzizai': 0.20,
                'liuyuxi': 0.15,
                'huineng': 0.10
            },
            'investment': {
                'simon': 0.30,      # 投资提高理性权重
                'guanzizai': 0.25,  # 风险洞察
                'liuyuxi': 0.20,
                'confucius': 0.15,
                'huineng': 0.10
            },
            'crisis': {
                'huineng': 0.30,    # 危机提高突破权重
                'guanzizai': 0.25,
                'simon': 0.20,
                'confucius': 0.15,
                'liuyuxi': 0.10
            },
            'team_building': {
                'liuyuxi': 0.35,    # 团队建设提高德馨权重
                'confucius': 0.25,
                'simon': 0.15,
                'guanzizai': 0.15,
                'huineng': 0.10
            }
        }
    
    def get_dynamic_weights(self, decision_type: str) -> Dict[str, float]:
        """获取动态权重"""
        if decision_type in self.decision_weights:
            return self.decision_weights[decision_type]
        
        # 默认权重
        return {k: v['default_weight'] for k, v in self.totem_agents.items()}
    
    def council_deliberation(self, 
                            decision_input: DecisionInput) -> Dict:
        """
        五图腾协同审议
        
        模拟五图腾从不同视角分析同一决策场景
        """
        print(f"🔷 五路图腾审议: {decision_input.scenario}")
        print(f"   决策类型: {decision_input.decision_type}")
        print()
        
        # 获取动态权重
        weights = self.get_dynamic_weights(decision_input.decision_type)
        
        perspectives = []
        
        # 每个图腾给出分析
        for agent_id, agent_info in self.totem_agents.items():
            print(f"  🎯 {agent_info['name']} ({agent_info['element'].value}) 分析中...")
            
            perspective = self._get_agent_perspective(
                agent_id, agent_info, decision_input, weights[agent_id]
            )
            perspectives.append(perspective)
        
        # 记录指标
        self.metrics.record(
            action='council_deliberation',
            decision_type=decision_input.decision_type,
            agent_count=len(perspectives)
        )
        
        return {
            'scenario': decision_input.scenario,
            'decision_type': decision_input.decision_type,
            'perspectives': perspectives,
            'weights_used': weights,
            'conflicts': self._identify_conflicts(perspectives),
            'synthesis_ready': True
        }
    
    def _get_agent_perspective(self,
                               agent_id: str,
                               agent_info: Dict,
                               decision_input: DecisionInput,
                               weight: float) -> AgentPerspective:
        """获取单个Agent的分析视角"""
        
        # 基于Agent特性生成分析框架
        focus_areas = agent_info['focus']
        
        # 模拟分析过程（实际应用中调用对应的System Prompt）
        analysis = self._simulate_agent_analysis(
            agent_info['name'], focus_areas, decision_input
        )
        
        return AgentPerspective(
            agent_name=agent_info['name'],
            element=agent_info['element'],
            analysis=analysis,
            confidence=0.7 + weight * 0.3,  # 权重影响置信度
            weight=weight,
            key_points=focus_areas
        )
    
    def _simulate_agent_analysis(self,
                                 agent_name: str,
                                 focus_areas: List[str],
                                 decision_input: DecisionInput) -> str:
        """模拟Agent分析（实际应调用LLM）"""
        focus_str = '、'.join(focus_areas)
        return f"从{focus_str}角度分析：该决策需要重点考虑{focus_areas[0]}维度"
    
    def _identify_conflicts(self, 
                           perspectives: List[AgentPerspective]) -> List[Dict]:
        """识别视角冲突"""
        conflicts = []
        
        # 检查理性vs直觉的冲突
        rational_agents = [p for p in perspectives 
                         if p.element in [ElementType.METAL, ElementType.WOOD]]
        intuitive_agents = [p for p in perspectives 
                          if p.element in [ElementType.WATER, ElementType.FIRE]]
        
        if rational_agents and intuitive_agents:
            conflicts.append({
                'type': 'rational_vs_intuitive',
                'description': '理性分析 vs 直觉感知',
                'agents_a': [p.agent_name for p in rational_agents],
                'agents_b': [p.agent_name for p in intuitive_agents],
                'resolution_suggestion': '在数据充分时信任理性，在信息不完整时参考直觉'
            })
        
        # 检查短期vs长期的冲突
        short_term = [p for p in perspectives if p.element == ElementType.FIRE]
        long_term = [p for p in perspectives if p.element == ElementType.EARTH]
        
        if short_term and long_term:
            conflicts.append({
                'type': 'short_vs_long_term',
                'description': '短期突破 vs 长期根基',
                'agents_a': [p.agent_name for p in short_term],
                'agents_b': [p.agent_name for p in long_term],
                'resolution_suggestion': '评估时间窗口，紧急选突破，稳健选根基'
            })
        
        return conflicts
    
    def generate_council_report(self, 
                               deliberation_result: Dict) -> str:
        """生成审议报告"""
        report = f"""
# 五路图腾审议报告

## 决策场景
{deliberation_result['scenario']}

## 决策类型
{deliberation_result['decision_type']}

## 五维分析

"""
        for p in deliberation_result['perspectives']:
            report += f"### {p.agent_name} ({p.element.value}) - 权重{p.weight:.0%}\n"
            report += f"- 分析视角: {', '.join(p.key_points)}\n"
            report += f"- 置信度: {p.confidence:.1%}\n\n"
        
        if deliberation_result['conflicts']:
            report += "## 视角冲突\n\n"
            for c in deliberation_result['conflicts']:
                report += f"### {c['description']}\n"
                report += f"- 冲突方: {', '.join(c['agents_a'])} vs {', '.join(c['agents_b'])}\n"
                report += f"- 建议: {c['resolution_suggestion']}\n\n"
        
        return report

# 便捷函数
def council_decide(scenario: str, 
                  decision_type: str = "general",
                  context: Dict = None) -> Dict:
    """快速五图腾审议"""
    council = TotemMultiAgentCouncil()
    
    decision_input = DecisionInput(
        scenario=scenario,
        context=context or {},
        constraints=[],
        decision_type=decision_type
    )
    
    return council.council_deliberation(decision_input)

if __name__ == '__main__':
    # 测试
    result = council_decide(
        scenario="评估一位潜在的合伙人候选人",
        decision_type="partner_matching"
    )
    
    print("\n" + "="*70)
    print("审议结果")
    print("="*70)
    for p in result['perspectives']:
        print(f"{p.agent_name} ({p.element.value}): 权重{p.weight:.0%}")
