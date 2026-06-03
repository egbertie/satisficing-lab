#!/usr/bin/env python3
# style_integration_agent.py - 整合Agent (冲突消解与综合洞察)
# 来源: 文件13 - AI决策系统设计.docx (认知层)
# 功能: 整合五图腾视角，消解冲突，生成综合洞察
# 创建时间: 2026-04-04
# 版本: 1.0

import sys
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

sys.path.insert(0, '/root/.openclaw/workspace')
from defense_base_components import BaseComponent, MetricsCollector
from totem_multi_agent_council import TotemMultiAgentCouncil, DecisionInput

@dataclass
class IntegratedInsight:
    """综合洞察"""
    recommendation: str
    confidence: float
    supporting_agents: List[str]
    dissenting_agents: List[str]
    risk_factors: List[str]
    action_items: List[str]

class StyleIntegrationAgent(BaseComponent):
    """
    整合Agent
    
    基于文档需求的认知层实现：
    - 冲突消解与综合洞察
    - 多视角融合算法
    - 生成统一建议
    """
    
    def __init__(self):
        super().__init__('style_integrator')
        self.metrics = MetricsCollector('integration')
        
        # 冲突消解策略
        self.conflict_resolution_strategies = {
            'rational_vs_intuitive': self._resolve_rational_intuitive,
            'short_vs_long_term': self._resolve_short_long,
            'risk_averse_vs_risk_seeking': self._resolve_risk_preference,
            'individual_vs_collective': self._resolve_scope
        }
    
    def integrate(self, 
                 council_result: Dict) -> IntegratedInsight:
        """
        整合五图腾视角
        
        消解冲突，生成综合洞察
        """
        print("🔀 整合Agent: 多视角融合...")
        
        perspectives = council_result.get('perspectives', [])
        conflicts = council_result.get('conflicts', [])
        
        # 1. 冲突消解
        resolved_conflicts = []
        for conflict in conflicts:
            strategy = self.conflict_resolution_strategies.get(
                conflict['type'], 
                self._default_resolution
            )
            resolution = strategy(conflict, perspectives)
            resolved_conflicts.append(resolution)
        
        # 2. 生成综合建议
        recommendation = self._synthesize_recommendation(
            perspectives, resolved_conflicts
        )
        
        # 3. 识别支持/反对Agent
        supporting, dissenting = self._identify_stance(perspectives, recommendation)
        
        # 4. 提取风险因素
        risk_factors = self._extract_risks(perspectives, resolved_conflicts)
        
        # 5. 生成行动项
        action_items = self._generate_actions(recommendation, risk_factors)
        
        # 计算综合置信度
        confidence = self._calculate_confidence(perspectives, resolved_conflicts)
        
        self.metrics.record(
            action='integration_completed',
            confidence=confidence,
            conflict_count=len(conflicts)
        )
        
        return IntegratedInsight(
            recommendation=recommendation,
            confidence=confidence,
            supporting_agents=supporting,
            dissenting_agents=dissenting,
            risk_factors=risk_factors,
            action_items=action_items
        )
    
    def _resolve_rational_intuitive(self, 
                                   conflict: Dict,
                                   perspectives: List) -> Dict:
        """消解理性vs直觉冲突"""
        rational_weight = sum(p.weight for p in perspectives 
                            if p.agent_name in conflict['agents_a'])
        intuitive_weight = sum(p.weight for p in perspectives 
                             if p.agent_name in conflict['agents_b'])
        
        if rational_weight > intuitive_weight * 1.2:
            resolution = "数据充分，采用理性分析结论"
        elif intuitive_weight > rational_weight * 1.2:
            resolution = "信息不完整，参考直觉判断"
        else:
            resolution = "理性和直觉并重，需要更多信息"
        
        return {**conflict, 'resolution': resolution}
    
    def _resolve_short_long(self, 
                           conflict: Dict,
                           perspectives: List) -> Dict:
        """消解短期vs长期冲突"""
        resolution = "评估时间窗口：紧急优先短期，稳健优先长期"
        return {**conflict, 'resolution': resolution}
    
    def _resolve_risk_preference(self, 
                                 conflict: Dict,
                                 perspectives: List) -> Dict:
        """消解风险偏好冲突"""
        resolution = "根据承受能力选择：保守者选低风险，进取者选高回报"
        return {**conflict, 'resolution': resolution}
    
    def _resolve_scope(self, 
                      conflict: Dict,
                      perspectives: List) -> Dict:
        """消解范围冲突"""
        resolution = "平衡个人与集体利益，寻求共赢方案"
        return {**conflict, 'resolution': resolution}
    
    def _default_resolution(self, 
                           conflict: Dict,
                           perspectives: List) -> Dict:
        """默认冲突消解"""
        return {**conflict, 'resolution': '综合各方意见，寻求平衡'}
    
    def _synthesize_recommendation(self,
                                  perspectives: List,
                                  resolved_conflicts: List) -> str:
        """合成综合建议"""
        # 按权重排序
        sorted_perspectives = sorted(perspectives, key=lambda p: p.weight, reverse=True)
        
        # 提取高权重Agent的核心观点
        top_agents = sorted_perspectives[:3]
        agent_names = [p.agent_name for p in top_agents]
        
        # 生成建议
        recommendation = f"综合{'、'.join(agent_names)}等视角，建议："
        
        # 添加冲突消解结论
        if resolved_conflicts:
            for rc in resolved_conflicts:
                recommendation += f"\n- 关于{rc['description']}：{rc['resolution']}"
        
        return recommendation
    
    def _identify_stance(self,
                        perspectives: List,
                        recommendation: str) -> Tuple[List[str], List[str]]:
        """识别支持/反对Agent"""
        # 简化逻辑：高置信度视为支持
        supporting = [p.agent_name for p in perspectives if p.confidence >= 0.8]
        dissenting = [p.agent_name for p in perspectives if p.confidence < 0.7]
        
        return supporting, dissenting
    
    def _extract_risks(self,
                      perspectives: List,
                      resolved_conflicts: List) -> List[str]:
        """提取风险因素"""
        risks = []
        
        # 从冲突中提取风险
        for conflict in resolved_conflicts:
            if '冲突' in conflict.get('description', ''):
                risks.append(f"{conflict['description']}可能导致决策偏差")
        
        # 从低置信度视角提取风险
        for p in perspectives:
            if p.confidence < 0.75:
                risks.append(f"{p.agent_name}视角置信度较低({p.confidence:.0%})")
        
        return risks if risks else ["暂无显著风险因素"]
    
    def _generate_actions(self,
                         recommendation: str,
                         risk_factors: List[str]) -> List[str]:
        """生成行动项"""
        actions = [
            "基于综合建议制定具体执行方案",
            "监控风险因素并准备应对措施"
        ]
        
        if len(risk_factors) > 1:
            actions.append("针对识别的风险点制定预案")
        
        return actions
    
    def _calculate_confidence(self,
                             perspectives: List,
                             resolved_conflicts: List) -> float:
        """计算综合置信度"""
        # 基于各Agent置信度的加权平均
        total_confidence = sum(p.confidence * p.weight for p in perspectives)
        total_weight = sum(p.weight for p in perspectives)
        
        avg_confidence = total_confidence / total_weight if total_weight > 0 else 0.5
        
        # 冲突惩罚
        conflict_penalty = len(resolved_conflicts) * 0.05
        
        return max(0.3, min(0.95, avg_confidence - conflict_penalty))
    
    def generate_integration_report(self, 
                                   insight: IntegratedInsight) -> str:
        """生成整合报告"""
        report = f"""
# 整合Agent报告

## 综合建议
{insight.recommendation}

## 置信度
{insight.confidence:.1%}

## 支持Agent
{', '.join(insight.supporting_agents) if insight.supporting_agents else '无明确支持'}

## 保留意见
{', '.join(insight.dissenting_agents) if insight.dissenting_agents else '无明确反对'}

## 风险因素
"""
        for risk in insight.risk_factors:
            report += f"- {risk}\n"
        
        report += "\n## 行动项\n"
        for i, action in enumerate(insight.action_items, 1):
            report += f"{i}. {action}\n"
        
        return report

# 便捷函数
def integrate_council_result(council_result: Dict) -> IntegratedInsight:
    """快速整合"""
    integrator = StyleIntegrationAgent()
    return integrator.integrate(council_result)

if __name__ == '__main__':
    # 测试
    from totem_multi_agent_council import council_decide
    
    council_result = council_decide(
        scenario="评估一位潜在的合伙人候选人",
        decision_type="partner_matching"
    )
    
    insight = integrate_council_result(council_result)
    
    print("\n" + "="*70)
    print(insight.recommendation)
    print(f"\n置信度: {insight.confidence:.1%}")
    print(f"支持: {', '.join(insight.supporting_agents)}")
