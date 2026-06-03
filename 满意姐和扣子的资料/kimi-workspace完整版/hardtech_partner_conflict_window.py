"""
hardtech_partner_conflict_window.py
硬科技创业合伙人冲突关键窗口期评估与干预机制

来源: 32硬科技创业合伙人冲突的关键窗口期与干预机制研究
版本: V1.0
生成时间: 2026-04-09
作者: 蓝军 Skeptor-7 (基于用户研究文档规则化生成)
"""

from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from enum import Enum


class ConflictStage(Enum):
    LATENCY = "潜伏期"          # 0-12 个月
    MANIFESTATION = "显现期"    # 12-24 个月 (第二年危机)
    OUTBREAK = "爆发/治理期"    # 24 个月以后


class RiskLevel(Enum):
    GREEN = "绿色"
    YELLOW = "黄色"
    RED = "红色"


@dataclass
class TeamSignal:
    metric: str
    value: float
    threshold_green: float
    threshold_yellow: float
    threshold_red: float
    unit: str = ""

    def level(self) -> RiskLevel:
        if self.value <= self.threshold_green:
            return RiskLevel.GREEN
        elif self.value <= self.threshold_yellow:
            return RiskLevel.YELLOW
        else:
            return RiskLevel.RED


@dataclass
class ConflictAssessment:
    company_name: str
    founded_months: int
    stage: ConflictStage
    signals: List[TeamSignal] = field(default_factory=list)
    overall_risk: RiskLevel = RiskLevel.GREEN
    intervention_urgency: str = ""
    recommended_actions: List[str] = field(default_factory=list)


class HardtechPartnerConflictWindow:
    """
    硬科技创业合伙人冲突关键窗口期评估器。
    基于 Wasserman 研究与 XbotPark 实证数据，识别 "第二年危机" (12-24 个月)。
    """

    STAGE_THRESHOLDS = {
        ConflictStage.LATENCY: (0, 12),
        ConflictStage.MANIFESTATION: (12, 24),
        ConflictStage.OUTBREAK: (24, 120),
    }

    def __init__(self):
        self.intervention_effectiveness = {
            "seed_stage": 0.65,   # 早期介入效应约为晚期的 2 倍以上
            "late_stage": 0.30,
        }

    def determine_stage(self, months: int) -> ConflictStage:
        if months < 12:
            return ConflictStage.LATENCY
        elif months < 24:
            return ConflictStage.MANIFESTATION
        return ConflictStage.OUTBREAK

    def build_default_signals(self, tech_route_disputes_monthly: float,
                              communication_frequency_weekly: float,
                              equity_change_count: int,
                              funding_deviation_rate: float) -> List[TeamSignal]:
        """
        构建早期预警指标信号。
        核心指标：技术路线分歧次数/月、创始人沟通频率/周、股权变更记录次数、融资进度偏离度。
        """
        return [
            TeamSignal("技术路线分歧次数/月", tech_route_disputes_monthly, 0.5, 1.5, 3.0, "次"),
            TeamSignal("创始人沟通频率/周", communication_frequency_weekly, 3.0, 1.5, 0.5, "次"),
            TeamSignal("股权变更记录次数", float(equity_change_count), 0.0, 1.0, 2.0, "次"),
            TeamSignal("融资进度偏离度", funding_deviation_rate, 0.10, 0.25, 0.40, "%"),
        ]

    def assess(self,
               company_name: str,
               founded_months: int,
               tech_route_disputes_monthly: float = 0.0,
               communication_frequency_weekly: float = 3.0,
               equity_change_count: int = 0,
               funding_deviation_rate: float = 0.0,
               mentor_involved: bool = False,
               mentor_stage: str = "") -> ConflictAssessment:
        stage = self.determine_stage(founded_months)
        signals = self.build_default_signals(
            tech_route_disputes_monthly,
            communication_frequency_weekly,
            equity_change_count,
            funding_deviation_rate,
        )

        red_count = sum(1 for s in signals if s.level() == RiskLevel.RED)
        yellow_count = sum(1 for s in signals if s.level() == RiskLevel.YELLOW)

        if red_count >= 2:
            overall = RiskLevel.RED
        elif red_count == 1 or yellow_count >= 2:
            overall = RiskLevel.YELLOW
        else:
            overall = RiskLevel.GREEN

        actions = self._recommend_actions(stage, overall, mentor_involved, mentor_stage)
        urgency = self._urgency_label(stage, overall)

        return ConflictAssessment(
            company_name=company_name,
            founded_months=founded_months,
            stage=stage,
            signals=signals,
            overall_risk=overall,
            intervention_urgency=urgency,
            recommended_actions=actions,
        )

    def _recommend_actions(self, stage: ConflictStage, risk: RiskLevel,
                           mentor_involved: bool, mentor_stage: str) -> List[str]:
        actions = []
        if stage == ConflictStage.MANIFESTATION and risk in (RiskLevel.YELLOW, RiskLevel.RED):
            actions.append("启动导师深度介入（建议在显现期 12-18 个月内），可将解体风险降低 30-40%")
        if risk == RiskLevel.RED:
            actions.append("执行合伙人一对一深度沟通，技术路线分歧须形成书面决议")
            actions.append("引入外部独立董事或顾问进行冲突调解")
        if not mentor_involved and stage != ConflictStage.LATENCY:
            actions.append("建议尽快匹配导师资源，晚期介入效应显著低于种子期")
        if mentor_stage == "late" and mentor_involved:
            actions.append("当前导师介入偏晚，建议增加介入频率并聚焦冲突化解")
        if len(actions) == 0:
            actions.append("维持常规合伙人沟通机制，定期复评")
        return actions

    def _urgency_label(self, stage: ConflictStage, risk: RiskLevel) -> str:
        if stage == ConflictStage.MANIFESTATION and risk == RiskLevel.RED:
            return "P0-紧急：处于第二年危机高峰窗口，须立即干预"
        if stage == ConflictStage.OUTBREAK and risk in (RiskLevel.YELLOW, RiskLevel.RED):
            return "P1-高优先级：冲突已进入爆发/治理期"
        if risk == RiskLevel.YELLOW:
            return "P2-关注：存在预警信号，建议 2 周内复查"
        return "P3-常规：风险可控"

    def did_effect(self, mentor_involved: bool, intervention_timing: str) -> Dict[str, float]:
        """
        导师介入的因果效应估计 (DID)。
        intervention_timing: 'seed_stage' | 'late_stage'
        """
        base_effect = self.intervention_effectiveness.get(intervention_timing, 0.30)
        return {
            "hazard_ratio": 0.65 if mentor_involved else 1.0,
            "risk_reduction": base_effect if mentor_involved else 0.0,
            "effect_significance": "p<0.05" if mentor_involved else "N/A",
        }

    def export_checklist(self, assessment: ConflictAssessment) -> Dict:
        """导出《合伙人冲突早期预警清单》结构化数据。"""
        return {
            "company": assessment.company_name,
            "founded_months": assessment.founded_months,
            "stage": assessment.stage.value,
            "overall_risk": assessment.overall_risk.value,
            "urgency": assessment.intervention_urgency,
            "signals": [
                {
                    "metric": s.metric,
                    "value": s.value,
                    "level": s.level().value,
                    "unit": s.unit,
                }
                for s in assessment.signals
            ],
            "actions": assessment.recommended_actions,
        }
