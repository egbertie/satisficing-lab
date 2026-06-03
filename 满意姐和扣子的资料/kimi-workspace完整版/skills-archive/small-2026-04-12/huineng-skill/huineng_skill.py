#!/usr/bin/env python3
"""
huineng_skill.py
HUINENG（六祖慧能）- 顿悟与行动转化器
五路图腾之火 - 顿悟突破，行动转化，从知到行
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable
from enum import Enum


class ActionPriority(Enum):
    """行动优先级"""
    CRITICAL = "关键"
    HIGH = "高"
    MEDIUM = "中"
    LOW = "低"
    DEFERRED = "延后"


class ActionStatus(Enum):
    """行动状态"""
    PENDING = "待执行"
    IN_PROGRESS = "执行中"
    COMPLETED = "已完成"
    BLOCKED = "阻塞"
    ABORTED = "已中止"


@dataclass
class InsightItem:
    """洞察项"""
    source: str  # 来源（LIU/SIMON/GUANYIN/CONFUCIUS）
    insight: str  # 洞察内容
    confidence: float  # 置信度 (0-100)
    urgency: float  # 紧迫性 (0-10)


@dataclass
class ActionItem:
    """行动项"""
    id: str
    name: str
    description: str
    priority: ActionPriority
    estimated_effort: float  # 预计投入（小时）
    dependencies: List[str] = field(default_factory=list)
    status: ActionStatus = ActionStatus.PENDING


@dataclass
class HuinengActionPlan:
    """HUINENG行动计划"""
    overall_insight: str  # 综合顿悟洞察
    critical_breakthrough: Optional[str]  # 关键突破点
    action_sequence: List[ActionItem]  # 行动序列
    total_effort: float  # 总投入估算
    success_probability: float  # 成功概率
    risk_mitigation: List[str]  # 风险缓解措施


class HuinengSkill:
    """
    HUINENG（六祖慧能）- 顿悟与行动转化器
    
    核心理念：顿悟突破，行动转化，从知到行
    火的特性：点燃、转化、释放能量、照亮前路
    """
    
    def __init__(self):
        self.name = "HUINENG（六祖慧能）"
        self.element = "火"
        self.motto = "顿悟突破，行动转化，从知到行"
    
    def synthesize_insights(self, insights: List[InsightItem]) -> str:
        """
        综合各路洞察，生成顿悟
        
        从LIU、SIMON、GUANYIN、CONFUCIUS的洞察中提取关键信息，
        形成综合性的"顿悟"洞察
        """
        # 按置信度和紧迫性排序
        sorted_insights = sorted(
            insights,
            key=lambda x: (x.confidence * x.urgency),
            reverse=True
        )
        
        # 提取关键洞察
        key_points = []
        for item in sorted_insights[:3]:  # 取前3个最重要的
            key_points.append(f"【{item.source}】{item.insight} (置信{item.confidence:.0f}%)")
        
        # 生成综合顿悟
        synthesis = "综合顿悟:\n" + "\n".join(f"  • {p}" for p in key_points)
        
        return synthesis
    
    def identify_breakthrough(self, insights: List[InsightItem]) -> Optional[str]:
        """
        识别关键突破点
        
        从洞察中寻找"顿悟时刻"——关键的转折点或突破机会
        """
        # 高紧迫性+高置信度的洞察可能成为突破点
        breakthrough_candidates = [
            i for i in insights
            if i.urgency >= 8 and i.confidence >= 75
        ]
        
        if breakthrough_candidates:
            # 取最紧迫的
            top = max(breakthrough_candidates, key=lambda x: x.urgency)
            return f"关键突破: {top.insight} (来源:{top.source}, 紧迫性:{top.urgency}/10)"
        
        return None
    
    def generate_action_plan(self, 
                            insights: List[InsightItem],
                            constraints: Optional[Dict] = None) -> HuinengActionPlan:
        """
        生成行动计划
        
        将洞察转化为可执行的行动序列
        """
        # 综合洞察
        overall = self.synthesize_insights(insights)
        
        # 识别突破点
        breakthrough = self.identify_breakthrough(insights)
        
        # 生成行动序列
        actions = self._generate_actions(insights, constraints)
        
        # 计算总投入
        total_effort = sum(a.estimated_effort for a in actions)
        
        # 评估成功概率
        success_prob = self._calculate_success_probability(insights, actions)
        
        # 风险缓解
        risk_mitigation = self._generate_risk_mitigation(insights)
        
        return HuinengActionPlan(
            overall_insight=overall,
            critical_breakthrough=breakthrough,
            action_sequence=actions,
            total_effort=total_effort,
            success_probability=success_prob,
            risk_mitigation=risk_mitigation
        )
    
    def _generate_actions(self, insights: List[InsightItem],
                         constraints: Optional[Dict]) -> List[ActionItem]:
        """生成行动序列"""
        actions = []
        
        # 基于洞察生成行动
        for i, insight in enumerate(insights[:5]):  # 最多5个行动
            priority = self._determine_priority(insight)
            effort = self._estimate_effort(insight)
            
            action = ActionItem(
                id=f"ACT-{i+1:03d}",
                name=f"响应洞察: {insight.source}",
                description=insight.insight[:50] + "...",
                priority=priority,
                estimated_effort=effort
            )
            actions.append(action)
        
        # 按优先级排序
        priority_order = {
            ActionPriority.CRITICAL: 0,
            ActionPriority.HIGH: 1,
            ActionPriority.MEDIUM: 2,
            ActionPriority.LOW: 3,
            ActionPriority.DEFERRED: 4
        }
        actions.sort(key=lambda x: priority_order[x.priority])
        
        return actions
    
    def _determine_priority(self, insight: InsightItem) -> ActionPriority:
        """确定行动优先级"""
        score = insight.confidence * insight.urgency / 10
        
        if score >= 70:
            return ActionPriority.CRITICAL
        elif score >= 50:
            return ActionPriority.HIGH
        elif score >= 30:
            return ActionPriority.MEDIUM
        elif score >= 15:
            return ActionPriority.LOW
        else:
            return ActionPriority.DEFERRED
    
    def _estimate_effort(self, insight: InsightItem) -> float:
        """估算投入"""
        # 基于紧迫性和复杂度估算
        base_effort = 4.0  # 基础4小时
        
        # 高紧迫性可能需要更多资源
        if insight.urgency >= 8:
            base_effort *= 1.5
        
        # 高置信度意味着更清晰的执行路径，可能更快
        if insight.confidence >= 80:
            base_effort *= 0.8
        
        return round(base_effort, 1)
    
    def _calculate_success_probability(self, insights: List[InsightItem],
                                       actions: List[ActionItem]) -> float:
        """计算成功概率"""
        if not insights:
            return 50.0
        
        # 基于平均置信度
        avg_confidence = sum(i.confidence for i in insights) / len(insights)
        
        # 行动数量影响（过多行动降低成功率）
        action_penalty = min(len(actions) * 2, 15)
        
        success_prob = avg_confidence - action_penalty
        return max(30, min(95, success_prob))
    
    def _generate_risk_mitigation(self, insights: List[InsightItem]) -> List[str]:
        """生成风险缓解措施"""
        measures = []
        
        # 低置信度洞察的风险
        low_confidence = [i for i in insights if i.confidence < 60]
        if low_confidence:
            measures.append("对低置信度洞察进行进一步验证")
        
        # 高紧迫性风险
        high_urgency = [i for i in insights if i.urgency >= 8]
        if high_urgency:
            measures.append("为高紧迫性行动准备应急预案")
        
        # 通用措施
        measures.extend([
            "建立定期回顾机制，及时调整计划",
            "保持与利益相关者的沟通",
            "准备Plan B应对意外情况"
        ])
        
        return measures
    
    def format_report(self, plan: HuinengActionPlan) -> str:
        """格式化行动计划报告"""
        lines = [
            "=" * 60,
            f"【HUINENG顿悟与行动计划】",
            f"转化时间: 2026-03-29",
            "=" * 60,
            f"",
            f"【综合顿悟】",
            plan.overall_insight,
        ]
        
        if plan.critical_breakthrough:
            lines.extend([
                f"",
                f"【关键突破点】",
                f"  🔥 {plan.critical_breakthrough}",
            ])
        
        lines.extend([
            f"",
            f"【行动序列】",
            f"  总投入估算: {plan.total_effort:.1f}小时",
            f"  成功概率: {plan.success_probability:.0f}%",
            f"",
        ])
        
        for i, action in enumerate(plan.action_sequence, 1):
            icon = {"关键": "🔴", "高": "🟠", "中": "🟡", "低": "🟢", "延后": "⚪"}.get(
                action.priority.value, "⚪"
            )
            lines.append(f"  {icon} {action.id} [{action.priority.value}] {action.name}")
            lines.append(f"      {action.description} (预计{action.estimated_effort}h)")
        
        lines.extend([
            f"",
            f"【风险缓解】",
        ])
        
        for i, measure in enumerate(plan.risk_mitigation, 1):
            lines.append(f"  {i}. {measure}")
        
        lines.extend([
            f"",
            "=" * 60,
            f"【五路图腾】HUINENG（火）- 顿悟突破，行动转化",
            "=" * 60,
        ])
        
        return "\n".join(lines)


# 便捷函数
def huineng_transform(
    liu_insight: str = "",
    simon_insight: str = "",
    guanyin_insight: str = "",
    confucius_insight: str = ""
) -> str:
    """
    快速转化函数
    
    将四路洞察转化为行动计划
    """
    insights = []
    
    if liu_insight:
        insights.append(InsightItem("LIU", liu_insight, 80, 7))
    if simon_insight:
        insights.append(InsightItem("SIMON", simon_insight, 75, 6))
    if guanyin_insight:
        insights.append(InsightItem("GUANYIN", guanyin_insight, 70, 8))
    if confucius_insight:
        insights.append(InsightItem("CONFUCIUS", confucius_insight, 85, 5))
    
    huineng = HuinengSkill()
    plan = huineng.generate_action_plan(insights)
    return huineng.format_report(plan)


if __name__ == "__main__":
    print("=" * 60)
    print("HUINENG（六祖慧能）- 顿悟与行动转化器 测试")
    print("=" * 60)
    print()
    
    # 测试：综合四路洞察
    print(huineng_transform(
        liu_insight="候选人根基优秀，价值观一致，可信任",
        simon_insight="满意解得分85，建议立即合作",
        guanyin_insight="市场机会良好，建议加速推进",
        confucius_insight="五常得分高，伦理治理优秀"
    ))
