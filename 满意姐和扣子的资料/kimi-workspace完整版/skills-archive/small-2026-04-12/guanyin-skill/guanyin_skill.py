#!/usr/bin/env python3
"""
guanyin_skill.py
GUANYIN（观自在）- 洞察与应变决策器
五路图腾之水 - 居方寸之地，以价值致远
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum
from datetime import datetime
import json


class EnvironmentSignal(Enum):
    """环境信号类型"""
    MARKET_SHIFT = "市场变化"
    TEAM_DYNAMIC = "团队动态"
    RISK_ALERT = "风险预警"
    OPPORTUNITY = "机会出现"
    RESOURCE_CHANGE = "资源变化"


class ResponseStrategy(Enum):
    """应变策略"""
    ADAPT = "适应调整"
    PIVOT = "策略转向"
    HOLD = "保持定力"
    ACCELERATE = "加速推进"
    RETREAT = "策略收缩"


@dataclass
class EnvironmentData:
    """环境数据"""
    market_trend: float = 5.0  # 市场趋势 (0-10, 5=中性)
    team_morale: float = 5.0   # 团队士气 (0-10)
    risk_level: float = 5.0    # 风险等级 (0-10)
    opportunity_score: float = 5.0  # 机会评分 (0-10)
    resource_availability: float = 5.0  # 资源可用性 (0-10)
    
    # 信号列表
    signals: List[Tuple[EnvironmentSignal, str, float]] = field(default_factory=list)
    # (信号类型, 描述, 强度0-10)


@dataclass
class GuanyinInsight:
    """GUANYIN洞察结果"""
    overall_situation: str  # 整体形势判断
    key_signals: List[str]  # 关键信号
    recommended_strategy: ResponseStrategy
    confidence: float  # 置信度 (0-100)
    action_plan: List[str]  # 行动计划
    light_asset_advice: str  # 轻资产建议


class GuanyinSkill:
    """
    GUANYIN（观自在）- 洞察与应变决策器
    
    核心理念：居方寸之地，以价值致远
    水的智慧：随形就势，润物无声，以柔克刚，居低不争
    """
    
    def __init__(self):
        self.name = "GUANYIN（观自在）"
        self.element = "水"
        self.motto = "居方寸之地，以价值致远"
    
    def sense_environment(self, data: EnvironmentData) -> GuanyinInsight:
        """
        感知环境并生成洞察
        
        基于环境数据，识别关键信号，推荐应变策略
        """
        # 分析整体形势
        situation = self._analyze_situation(data)
        
        # 提取关键信号
        key_signals = self._extract_signals(data)
        
        # 推荐策略
        strategy = self._recommend_strategy(data)
        
        # 计算置信度
        confidence = self._calculate_confidence(data)
        
        # 生成行动计划
        action_plan = self._generate_action_plan(strategy, data)
        
        # 轻资产建议
        light_asset_advice = self._generate_light_asset_advice(data, strategy)
        
        return GuanyinInsight(
            overall_situation=situation,
            key_signals=key_signals,
            recommended_strategy=strategy,
            confidence=confidence,
            action_plan=action_plan,
            light_asset_advice=light_asset_advice
        )
    
    def _analyze_situation(self, data: EnvironmentData) -> str:
        """分析整体形势"""
        # 综合评分
        avg_score = (
            data.market_trend + data.team_morale + data.resource_availability -
            data.risk_level + data.opportunity_score
        ) / 5
        
        if avg_score >= 7:
            return "形势有利，适合积极行动"
        elif avg_score >= 5:
            return "形势中性，保持灵活应变"
        elif avg_score >= 3:
            return "形势挑战，需要谨慎应对"
        else:
            return "形势严峻，建议策略收缩"
    
    def _extract_signals(self, data: EnvironmentData) -> List[str]:
        """提取关键信号"""
        signals = []
        
        # 分析各维度异常
        if data.market_trend >= 8:
            signals.append("📈 市场趋势强劲，存在增长机会")
        elif data.market_trend <= 3:
            signals.append("📉 市场下行，需收缩风险敞口")
        
        if data.team_morale <= 4:
            signals.append("😔 团队士气低落，需关注内部状态")
        elif data.team_morale >= 8:
            signals.append("😊 团队士气高涨，可加大投入")
        
        if data.risk_level >= 7:
            signals.append("⚠️  高风险警报，需立即采取风控措施")
        
        if data.opportunity_score >= 8:
            signals.append("💎 重大机会出现，建议快速响应")
        
        if data.resource_availability <= 4:
            signals.append("📦 资源紧张，需轻资产运营")
        
        # 添加显式信号
        for signal_type, desc, intensity in data.signals:
            if intensity >= 6:
                signals.append(f"[{signal_type.value}] {desc} (强度:{intensity})")
        
        return signals if signals else ["📊 无明显异常信号，维持现状"]
    
    def _recommend_strategy(self, data: EnvironmentData) -> ResponseStrategy:
        """推荐应变策略"""
        # 计算各维度综合得分
        opportunity = data.opportunity_score + data.market_trend
        risk = data.risk_level * 2  # 风险权重更高
        resource = data.resource_availability + data.team_morale
        
        # 决策逻辑
        if opportunity >= 15 and risk <= 10 and resource >= 10:
            return ResponseStrategy.ACCELERATE
        elif data.risk_level >= 8 or data.resource_availability <= 3:
            return ResponseStrategy.RETREAT
        elif data.market_trend <= 3 and data.opportunity_score <= 4:
            return ResponseStrategy.PIVOT
        elif abs(data.market_trend - 5) <= 1 and data.risk_level <= 6:
            return ResponseStrategy.HOLD
        else:
            return ResponseStrategy.ADAPT
    
    def _calculate_confidence(self, data: EnvironmentData) -> float:
        """计算洞察置信度"""
        # 基于数据完整性和一致性
        base_confidence = 70.0
        
        # 信号越多，置信度越高（但不超过95）
        signal_bonus = min(len(data.signals) * 3, 15)
        
        # 极端值降低置信度（可能数据不准）
        extreme_count = sum([
            1 for v in [data.market_trend, data.team_morale, data.risk_level]
            if v >= 9 or v <= 1
        ])
        extreme_penalty = extreme_count * 5
        
        confidence = base_confidence + signal_bonus - extreme_penalty
        return max(50, min(95, confidence))
    
    def _generate_action_plan(self, strategy: ResponseStrategy, 
                             data: EnvironmentData) -> List[str]:
        """生成行动计划"""
        plans = {
            ResponseStrategy.ACCELERATE: [
                "加大资源投入，抓住机会",
                "快速扩展团队，提升执行力",
                "增加市场投入，抢占先机"
            ],
            ResponseStrategy.PIVOT: [
                "重新评估核心假设",
                "调整产品/服务方向",
                "寻找新市场或新模式"
            ],
            ResponseStrategy.HOLD: [
                "维持当前策略，观察变化",
                "优化内部效率，降低成本",
                "储备资源，等待时机"
            ],
            ResponseStrategy.ADAPT: [
                "微调策略，适应环境",
                "加强风险监控",
                "保持灵活性，快速响应"
            ],
            ResponseStrategy.RETREAT: [
                "收缩非核心业务",
                "减少固定成本",
                "保存实力，等待复苏"
            ]
        }
        
        base_plan = plans.get(strategy, ["保持观察"])
        
        # 根据具体情况添加定制化建议
        if data.risk_level >= 6:
            base_plan.insert(0, "⚠️ 优先处理高风险项")
        
        if data.resource_availability <= 5:
            base_plan.append("💡 采用轻资产模式，减少固定投入")
        
        return base_plan
    
    def _generate_light_asset_advice(self, data: EnvironmentData,
                                    strategy: ResponseStrategy) -> str:
        """生成轻资产建议"""
        advice_parts = []
        
        # 资源紧张时的轻资产策略
        if data.resource_availability <= 5:
            advice_parts.append("资源紧张，优先采用合作、外包等轻资产方式")
        
        # 高机会时的杠杆策略
        if data.opportunity_score >= 7:
            advice_parts.append("机会良好，可通过资源整合放大杠杆效应")
        
        # 高风险时的保守策略
        if data.risk_level >= 6:
            advice_parts.append("风险较高，减少固定资产投入，保持现金储备")
        
        # 根据策略调整
        if strategy == ResponseStrategy.ACCELERATE:
            advice_parts.append("加速期可采用战略联盟，共享资源而非独自投入")
        elif strategy == ResponseStrategy.RETREAT:
            advice_parts.append("收缩期优先变现非核心资产，保持轻资产运营")
        
        if not advice_parts:
            advice_parts.append("保持轻资产心态，以最小投入验证最大价值")
        
        return "；".join(advice_parts)
    
    def format_report(self, insight: GuanyinInsight) -> str:
        """格式化洞察报告"""
        lines = [
            "=" * 60,
            f"【GUANYIN洞察与应变报告】",
            f"洞察时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "=" * 60,
            f"",
            f"【整体形势】",
            f"  {insight.overall_situation}",
            f"  洞察置信度: {insight.confidence:.0f}%",
            f"",
            f"【关键信号】",
        ]
        
        for signal in insight.key_signals:
            lines.append(f"  {signal}")
        
        lines.extend([
            f"",
            f"【推荐策略】",
            f"  🎯 {insight.recommended_strategy.value}",
            f"",
            f"【行动计划】",
        ])
        
        for i, action in enumerate(insight.action_plan, 1):
            lines.append(f"  {i}. {action}")
        
        lines.extend([
            f"",
            f"【轻资产建议】",
            f"  💡 {insight.light_asset_advice}",
            f"",
            "=" * 60,
            f"【五路图腾】GUANYIN（水）- 居方寸之地，以价值致远",
            "=" * 60,
        ])
        
        return "\n".join(lines)


# 便捷函数
def guanyin_insight(
    market_trend: float = 5.0,
    team_morale: float = 5.0,
    risk_level: float = 5.0,
    opportunity_score: float = 5.0,
    resource_availability: float = 5.0,
    signals: Optional[List[Tuple[EnvironmentSignal, str, float]]] = None
) -> str:
    """
    快速洞察函数
    
    Args:
        market_trend: 市场趋势 (0-10)
        team_morale: 团队士气 (0-10)
        risk_level: 风险等级 (0-10)
        opportunity_score: 机会评分 (0-10)
        resource_availability: 资源可用性 (0-10)
        signals: 显式信号列表 [(类型, 描述, 强度)]
    
    Returns:
        str: 格式化洞察报告
    """
    env_data = EnvironmentData(
        market_trend=market_trend,
        team_morale=team_morale,
        risk_level=risk_level,
        opportunity_score=opportunity_score,
        resource_availability=resource_availability
    )
    
    if signals:
        env_data.signals = [
            (EnvironmentSignal(sig[0]), sig[1], sig[2])
            for sig in signals
        ]
    
    guanyin = GuanyinSkill()
    insight = guanyin.sense_environment(env_data)
    return guanyin.format_report(insight)


if __name__ == "__main__":
    print("=" * 60)
    print("GUANYIN（观自在）- 洞察与应变决策器 测试")
    print("=" * 60)
    print()
    
    # 测试1: 形势大好
    print(guanyin_insight(
        market_trend=8.5,
        team_morale=8.0,
        risk_level=3.0,
        opportunity_score=9.0,
        resource_availability=7.0
    ))
    
    print()
    print("-" * 60)
    print()
    
    # 测试2: 形势挑战
    print(guanyin_insight(
        market_trend=3.5,
        team_morale=4.0,
        risk_level=8.0,
        opportunity_score=3.0,
        resource_availability=4.0,
        signals=[
            (EnvironmentSignal.RISK_ALERT, "核心供应商出现问题", 8),
            (EnvironmentSignal.TEAM_DYNAMIC, "关键人员离职", 7)
        ]
    ))
