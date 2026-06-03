#!/usr/bin/env python3
"""
simon_skill.py
SIMON（司马贺）- 理性决策与满意解计算器
五路图腾之金 - 不求最优，但求最适；结果为本，满意为尺
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from enum import Enum
import json


class DecisionStatus(Enum):
    """决策状态"""
    RECOMMENDED = "推荐"
    ACCEPTABLE = "可接受"
    MARGINAL = "边缘"
    REJECTED = "不推荐"


@dataclass
class CandidateProfile:
    """候选人档案"""
    name: str
    liu_score: float  # LIU根基评分 (0-100)
    capability_match: float  # 能力匹配度 (0-10)
    cost_benefit: float  # 成本效益 (0-10)
    risk_controllability: float  # 风险可控性 (0-10)
    stakeholder_satisfaction: float  # 利益相关者满意度 (0-10)
    time_feasibility: float  # 时间可行性 (0-10)


@dataclass
class SatisficingResult:
    """满意解决策结果"""
    candidate_name: str
    satisficing_score: float  # 满意解得分 (0-100)
    aspiration_level: float  # 期望阈值
    gap_analysis: Dict[str, float]  # 差距分析
    decision_status: DecisionStatus
    trade_offs: List[str]  # 权衡分析
    recommendation: str


class SIMONSkill:
    """
    SIMON（司马贺）- 理性决策与满意解计算器
    
    核心理念：不求最优，但求最适；结果为本，满意为尺
    基于Herbert Simon的满意解理论，在有限信息下追求足够好的决策
    """
    
    # 决策维度权重
    WEIGHTS = {
        "capability_match": 0.25,
        "cost_benefit": 0.25,
        "risk_controllability": 0.20,
        "stakeholder_satisfaction": 0.20,
        "time_feasibility": 0.10
    }
    
    # 满意阈值（动态调整）
    DEFAULT_ASPIRATION = 70.0  # 默认70分即满意
    
    def __init__(self, aspiration_level: Optional[float] = None):
        self.name = "SIMON（司马贺）"
        self.element = "金"
        self.motto = "不求最优，但求最适；结果为本，满意为尺"
        self.aspiration_level = aspiration_level or self.DEFAULT_ASPIRATION
    
    def calculate_satisficing_score(self, candidate: CandidateProfile) -> float:
        """
        计算满意解得分
        
        算法：加权平均 + LIU根基评分修正
        """
        # 基础维度得分 (0-100)
        base_scores = {
            "capability_match": candidate.capability_match * 10,
            "cost_benefit": candidate.cost_benefit * 10,
            "risk_controllability": candidate.risk_controllability * 10,
            "stakeholder_satisfaction": candidate.stakeholder_satisfaction * 10,
            "time_feasibility": candidate.time_feasibility * 10
        }
        
        # 加权计算
        weighted_score = sum(
            base_scores[dim] * self.WEIGHTS[dim]
            for dim in self.WEIGHTS
        )
        
        # LIU根基修正（根基好可以加权，根基差大幅扣分）
        liu_factor = self._calculate_liu_factor(candidate.liu_score)
        
        final_score = weighted_score * liu_factor
        return round(final_score, 1)
    
    def _calculate_liu_factor(self, liu_score: float) -> float:
        """
        根据LIU根基评分计算修正因子
        
        根基是合作的前提，根基差则决策权重大幅降低
        """
        if liu_score >= 80:
            return 1.0  # 根基优秀，不修正
        elif liu_score >= 65:
            return 0.9  # 根基良好，轻微修正
        elif liu_score >= 50:
            return 0.75  # 根基一般，中等修正
        elif liu_score >= 35:
            return 0.55  # 根基较差，大幅修正
        else:
            return 0.3  # 根基差，严重修正
    
    def make_decision(self, candidate: CandidateProfile) -> SatisficingResult:
        """
        做出满意解决策
        
        不是寻找全局最优，而是寻找首个满足期望阈值的方案
        """
        score = self.calculate_satisficing_score(candidate)
        
        # 差距分析
        gap_analysis = self._analyze_gaps(candidate, score)
        
        # 权衡分析
        trade_offs = self._analyze_trade_offs(candidate)
        
        # 决策状态
        status = self._determine_status(score, candidate.liu_score)
        
        # 生成建议
        recommendation = self._generate_recommendation(
            candidate.name, score, status, gap_analysis
        )
        
        return SatisficingResult(
            candidate_name=candidate.name,
            satisficing_score=score,
            aspiration_level=self.aspiration_level,
            gap_analysis=gap_analysis,
            decision_status=status,
            trade_offs=trade_offs,
            recommendation=recommendation
        )
    
    def _analyze_gaps(self, candidate: CandidateProfile, 
                      final_score: float) -> Dict[str, float]:
        """分析各维度与期望的差距"""
        gaps = {}
        
        dimensions = {
            "capability_match": candidate.capability_match * 10,
            "cost_benefit": candidate.cost_benefit * 10,
            "risk_controllability": candidate.risk_controllability * 10,
            "stakeholder_satisfaction": candidate.stakeholder_satisfaction * 10,
            "time_feasibility": candidate.time_feasibility * 10,
            "liu_foundation": candidate.liu_score
        }
        
        for dim, score in dimensions.items():
            gap = self.aspiration_level - score
            gaps[dim] = round(gap, 1)
        
        return gaps
    
    def _analyze_trade_offs(self, candidate: CandidateProfile) -> List[str]:
        """分析决策中的权衡"""
        trade_offs = []
        
        scores = {
            "能力": candidate.capability_match,
            "成本效益": candidate.cost_benefit,
            "风险可控": candidate.risk_controllability,
            "利益平衡": candidate.stakeholder_satisfaction,
            "时间可行": candidate.time_feasibility
        }
        
        # 识别强项和弱项
        strengths = [k for k, v in scores.items() if v >= 8]
        weaknesses = [k for k, v in scores.items() if v <= 5]
        
        if strengths and weaknesses:
            trade_offs.append(
                f"强项（{', '.join(strengths)}）vs 弱项（{', '.join(weaknesses)}）需要权衡"
            )
        
        if candidate.capability_match >= 8 and candidate.cost_benefit <= 5:
            trade_offs.append("高能力但高成本，需评估性价比")
        
        if candidate.risk_controllability <= 5 and candidate.liu_score >= 70:
            trade_offs.append("根基好但风险高，需加强风控措施")
        
        return trade_offs
    
    def _determine_status(self, score: float, liu_score: float) -> DecisionStatus:
        """确定决策状态"""
        # 根基差直接不推荐
        if liu_score < 40:
            return DecisionStatus.REJECTED
        
        if score >= self.aspiration_level + 10:
            return DecisionStatus.RECOMMENDED
        elif score >= self.aspiration_level:
            return DecisionStatus.ACCEPTABLE
        elif score >= self.aspiration_level - 15:
            return DecisionStatus.MARGINAL
        else:
            return DecisionStatus.REJECTED
    
    def _generate_recommendation(self, name: str, score: float,
                                  status: DecisionStatus,
                                  gaps: Dict[str, float]) -> str:
        """生成决策建议"""
        lines = [
            f"【SIMON满意解决策 - {name}】",
            f"",
            f"满意解得分: {score:.1f}/100 (期望阈值: {self.aspiration_level})",
            f"决策状态: {status.value}",
        ]
        
        if status == DecisionStatus.RECOMMENDED:
            lines.append("建议: 立即合作，此为满意方案")
        elif status == DecisionStatus.ACCEPTABLE:
            lines.append("建议: 可以接受，达到期望标准")
        elif status == DecisionStatus.MARGINAL:
            lines.append("建议: 边缘可接受，需加强短板或降低期望")
        else:
            lines.append("建议: 不推荐，未达期望阈值")
        
        # 最大差距
        max_gap_dim = max(gaps.items(), key=lambda x: x[1])
        if max_gap_dim[1] > 0:
            lines.append(f"")
            lines.append(f"最大短板: {max_gap_dim[0]} (差距{max_gap_dim[1]:.1f}分)")
        
        return "\n".join(lines)
    
    def batch_evaluate(self, candidates: List[CandidateProfile]) -> List[SatisficingResult]:
        """批量评估多个候选人"""
        results = []
        for candidate in candidates:
            result = self.make_decision(candidate)
            results.append(result)
        
        # 按满意解得分排序
        results.sort(key=lambda x: x.satisficing_score, reverse=True)
        return results
    
    def format_report(self, result: SatisficingResult) -> str:
        """格式化决策报告"""
        lines = [
            "=" * 60,
            f"【SIMON理性决策报告】",
            f"评估对象: {result.candidate_name}",
            f"决策时间: 2026-03-29",
            "=" * 60,
            f"",
            f"【满意解得分】",
            f"  最终得分: {result.satisficing_score:.1f}/100",
            f"  期望阈值: {result.aspiration_level:.1f}",
            f"  决策状态: {result.decision_status.value}",
            f"",
            f"【差距分析】",
        ]
        
        for dim, gap in result.gap_analysis.items():
            status = "✅ 达标" if gap <= 0 else f"⚠️  差距{gap:.1f}"
            lines.append(f"  {dim}: {status}")
        
        if result.trade_offs:
            lines.extend([
                f"",
                f"【权衡分析】",
            ])
            for trade in result.trade_offs:
                lines.append(f"  • {trade}")
        
        lines.extend([
            f"",
            f"【决策建议】",
            result.recommendation,
            f"",
            "=" * 60,
            f"【五路图腾】SIMON（金）- 不求最优，但求最适",
            "=" * 60,
        ])
        
        return "\n".join(lines)


# 便捷函数
def satisficing_decision(name: str,
                         liu_score: float,
                         capability_match: float = 7.0,
                         cost_benefit: float = 7.0,
                         risk_controllability: float = 7.0,
                         stakeholder_satisfaction: float = 7.0,
                         time_feasibility: float = 7.0,
                         aspiration_level: Optional[float] = None) -> str:
    """
    快速满意解决策
    
    Args:
        name: 候选人姓名
        liu_score: LIU根基评分 (0-100)
        capability_match: 能力匹配度 (0-10)
        cost_benefit: 成本效益 (0-10)
        risk_controllability: 风险可控性 (0-10)
        stakeholder_satisfaction: 利益相关者满意度 (0-10)
        time_feasibility: 时间可行性 (0-10)
        aspiration_level: 期望阈值 (默认70)
    
    Returns:
        str: 格式化决策报告
    """
    candidate = CandidateProfile(
        name=name,
        liu_score=liu_score,
        capability_match=capability_match,
        cost_benefit=cost_benefit,
        risk_controllability=risk_controllability,
        stakeholder_satisfaction=stakeholder_satisfaction,
        time_feasibility=time_feasibility
    )
    
    simon = SIMONSkill(aspiration_level=aspiration_level)
    result = simon.make_decision(candidate)
    return simon.format_report(result)


if __name__ == "__main__":
    print("=" * 60)
    print("SIMON（司马贺）- 满意解决策器 测试")
    print("=" * 60)
    print()
    
    # 测试1: 优秀候选人
    print(satisficing_decision(
        name="优秀合伙人",
        liu_score=85,
        capability_match=9.0,
        cost_benefit=8.0,
        risk_controllability=8.5,
        stakeholder_satisfaction=8.0,
        time_feasibility=8.0
    ))
    
    print()
    print("-" * 60)
    print()
    
    # 测试2: 根基好但能力一般
    print(satisficing_decision(
        name="根基好能力一般",
        liu_score=80,
        capability_match=6.0,
        cost_benefit=7.0,
        risk_controllability=7.5,
        stakeholder_satisfaction=7.0,
        time_feasibility=6.5
    ))
    
    print()
    print("-" * 60)
    print()
    
    # 测试3: 根基差（直接否决）
    print(satisficing_decision(
        name="根基差候选人",
        liu_score=35,
        capability_match=9.0,
        cost_benefit=8.0,
        risk_controllability=7.0,
        stakeholder_satisfaction=8.0,
        time_feasibility=8.0
    ))
