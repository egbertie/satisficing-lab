"""
lizexiang_human_factor_analyzer.py
李泽湘硬科技孵化体系"人"因素研究与合伙人匹配分析器

来源: 30_李泽湘硬科技孵化体系的人因素研究_从270案例中提取合伙人匹配的成功模式与失败教训
版本: V1.0
生成时间: 2026-04-09
作者: 蓝军 Skeptor-7
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum


class TeamArchetype(Enum):
    TECH_TECH = "技术-技术型"
    TECH_BUSINESS = "技术-商业型"
    MULTI_TECH = "多元技术型"
    BUSINESS_BUSINESS = "商业-商业型"


class Outcome(Enum):
    UNICORN = "独角兽"
    SURVIVOR = "存活企业"
    RESTRUCTURE = "重组"
    FAILURE = "失败退出"


@dataclass
class FounderProfile:
    name: str
    technical_depth: float   # 0-100
    business_acumen: float   # 0-100
    resilience_score: float  # 0-100
    motivation_clarity: float  # 0-100
    collaboration_history: str = ""


@dataclass
class PartnershipMatch:
    founders: List[FounderProfile]
    archetype: TeamArchetype
    predicted_outcome: Outcome
    success_probability: float
    risk_factors: List[str] = field(default_factory=list)
    mentor_recommendations: List[str] = field(default_factory=list)


class LizexiangHumanFactorAnalyzer:
    """
    基于李泽湘 270+ 硬科技孵化案例的"人"因素分析器。
    核心假设：硬科技创业成功概率可通过对"人"的前置筛选、情境测试和导师陪伴显著提升。
    """

    # 270+ 案例宏观统计
    CASE_STATS = {
        "total_cases": 270,
        "total_valuation_bn": 350,
        "unicorns": 12,
        "survival_rate_xbotpark": 0.80,
        "unicorn_rate_xbotpark": 0.15,
        "failure_due_to_founder_conflict": 0.65,
        "failure_due_to_tech": 0.20,
        "failure_due_to_market": 0.15,
        "second_year_crisis_rate": 0.45,
    }

    # 创业浓度对比 (%)
    ENTREPRENEURIAL_CONCENTRATION = {
        "MIT_Stanford": 0.01,
        "Changzhou_University": 0.10,
        "Chongqing_Mingyue": 0.20,
        "GIDA_DaVinci": 0.60,
    }

    def __init__(self):
        self.archetype_weights = {
            TeamArchetype.TECH_BUSINESS: 0.26,   # XbotPark 转化率 10%-26% 的上限
            TeamArchetype.MULTI_TECH: 0.18,
            TeamArchetype.TECH_TECH: 0.12,
            TeamArchetype.BUSINESS_BUSINESS: 0.06,
        }

    def classify_archetype(self, founders: List[FounderProfile]) -> TeamArchetype:
        if len(founders) < 2:
            return TeamArchetype.TECH_TECH
        tech_scores = [f.technical_depth for f in founders]
        biz_scores = [f.business_acumen for f in founders]
        avg_tech = sum(tech_scores) / len(tech_scores)
        avg_biz = sum(biz_scores) / len(biz_scores)
        max_tech = max(tech_scores)
        max_biz = max(biz_scores)

        has_strong_tech = max_tech >= 75
        has_strong_biz = max_biz >= 75
        has_multi_tech = len([s for s in tech_scores if s >= 70]) >= 2

        if has_strong_tech and has_strong_biz:
            return TeamArchetype.TECH_BUSINESS
        if has_multi_tech:
            return TeamArchetype.MULTI_TECH
        if avg_biz > avg_tech:
            return TeamArchetype.BUSINESS_BUSINESS
        return TeamArchetype.TECH_TECH

    def predict_success(self, founders: List[FounderProfile],
                        mentor_involved: bool = True,
                        pressure_test_passed: bool = False) -> PartnershipMatch:
        archetype = self.classify_archetype(founders)
        base_prob = self.archetype_weights.get(archetype, 0.10)

        # 韧性均值加成
        avg_resilience = sum(f.resilience_score for f in founders) / len(founders)
        resilience_bonus = (avg_resilience - 50) * 0.003

        # 动机清晰度加成
        avg_motivation = sum(f.motivation_clarity for f in founders) / len(founders)
        motivation_bonus = (avg_motivation - 50) * 0.002

        prob = base_prob + resilience_bonus + motivation_bonus
        prob = max(0.02, min(0.95, prob))

        # 导师介入是否显著
        if mentor_involved:
            prob = min(0.95, prob * 1.35)   # 类似于存活率提升

        if pressure_test_passed:
            prob = min(0.95, prob * 1.15)

        # 映射到 outcome
        outcome = self._map_outcome(prob)
        risks = self._identify_risks(founders, archetype)
        recs = self._mentor_recommendations(founders, archetype, mentor_involved, pressure_test_passed)

        return PartnershipMatch(
            founders=founders,
            archetype=archetype,
            predicted_outcome=outcome,
            success_probability=round(prob, 4),
            risk_factors=risks,
            mentor_recommendations=recs,
        )

    def _map_outcome(self, prob: float) -> Outcome:
        if prob >= 0.20:
            return Outcome.UNICORN
        if prob >= 0.12:
            return Outcome.SURVIVOR
        if prob >= 0.06:
            return Outcome.RESTRUCTURE
        return Outcome.FAILURE

    def _identify_risks(self, founders: List[FounderProfile], archetype: TeamArchetype) -> List[str]:
        risks = []
        if archetype == TeamArchetype.BUSINESS_BUSINESS:
            risks.append("双商业背景团队技术深度不足，硬科技领域失败率高")
        if archetype == TeamArchetype.TECH_TECH:
            risks.append("双技术背景团队商业化和市场拓展能力存在结构性缺口")
        if len(founders) >= 2:
            res_scores = [f.resilience_score for f in founders]
            if min(res_scores) < 40:
                risks.append("存在低韧性合伙人，可能在第二年危机中率先退出")
        avg_motivation = sum(f.motivation_clarity for f in founders) / len(founders)
        if avg_motivation < 50:
            risks.append("创业动机清晰度偏低，属于早期筛选需重点观察项")
        if len(risks) == 0:
            risks.append("当前无明显结构性风险，建议进入情境测试阶段")
        return risks

    def _mentor_recommendations(self, founders: List[FounderProfile],
                                archetype: TeamArchetype,
                                mentor_involved: bool,
                                pressure_test_passed: bool) -> List[str]:
        recs = []
        if not mentor_involved:
            recs.append("强烈建议匹配李泽湘体系导师，早期 mentorship 可将存活率提升至 80%")
        if archetype == TeamArchetype.TECH_TECH:
            recs.append("建议安排商业导师补齐市场与融资能力")
        if not pressure_test_passed:
            recs.append("建议执行 72 小时压力测试或情境模拟，观察合伙人冲突响应模式")
        if mentor_involved and not pressure_test_passed:
            recs.append("导师已介入，下一阶段重点是通过压力测试验证躯体信号识别结果")
        if len(recs) == 0:
            recs.append("维持现有 mentor-mentee 节奏，定期复评合伙人协作状态")
        return recs

    def get_case_stats(self) -> Dict:
        return dict(self.CASE_STATS)

    def compare_concentration(self, institution: str) -> Optional[float]:
        return self.ENTREPRENEURIAL_CONCENTRATION.get(institution)

    def batch_evaluate(self, cases: List[Dict]) -> List[PartnershipMatch]:
        """批量评估接口。"""
        results = []
        for case in cases:
            founders = [FounderProfile(**f) for f in case.get("founders", [])]
            match = self.predict_success(
                founders,
                mentor_involved=case.get("mentor_involved", True),
                pressure_test_passed=case.get("pressure_test_passed", False),
            )
            results.append(match)
        return results
