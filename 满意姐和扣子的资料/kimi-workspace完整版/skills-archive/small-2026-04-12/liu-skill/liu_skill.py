#!/usr/bin/env python3
"""
liu_skill.py
LIU（刘禹锡）- 根基与信任评估器
五路图腾之土 - 聚贤才为伍，引智士同行
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum
import json


class TrustLevel(Enum):
    """信任等级 L1-L5"""
    L1_UNTRUSTED = "L1"
    L2_CAUTIOUS = "L2"
    L3_NEUTRAL = "L3"
    L4_TRUSTED = "L4"
    L5_FULL_TRUST = "L5"


class Recommendation(Enum):
    """合作建议"""
    RECOMMEND = "推荐"
    CAUTIOUS = "谨慎"
    NOT_RECOMMEND = "不推荐"


@dataclass
class CandidateData:
    """候选人数据"""
    name: str
    # 价值观问卷（1-10分）
    values_alignment: float = 0.0  # 价值观一致性
    integrity_history: float = 0.0  # 历史诚信
    long_term_commitment: float = 0.0  # 长期承诺
    cultural_fit: float = 0.0  # 文化契合
    reputation_score: float = 0.0  # 人品口碑
    
    # 其他信息
    past_collaborations: List[Dict] = field(default_factory=list)
    references: List[str] = field(default_factory=list)
    red_flags: List[str] = field(default_factory=list)


@dataclass
class LIUEvaluationResult:
    """LIU评估结果"""
    candidate_name: str
    total_score: float  # 0-100
    trust_level: TrustLevel
    recommendation: Recommendation
    dimension_scores: Dict[str, float]
    risk_warnings: List[str]
    reasoning: str


class LIUSkill:
    """
    LIU（刘禹锡）- 根基与信任评估器
    
    核心理念：聚贤才为伍，引智士同行
    如同山之稳固，是长期合作的基石
    """
    
    # 评估维度权重
    WEIGHTS = {
        "values_alignment": 0.30,
        "integrity_history": 0.25,
        "long_term_commitment": 0.20,
        "cultural_fit": 0.15,
        "reputation_score": 0.10
    }
    
    def __init__(self):
        self.name = "LIU（刘禹锡）"
        self.element = "土"
        self.motto = "聚贤才为伍，引智士同行"
    
    def evaluate_partner(self, candidate: CandidateData) -> LIUEvaluationResult:
        """
        评估候选人根基与信任worthiness
        
        Args:
            candidate: 候选人数据
            
        Returns:
            LIUEvaluationResult: 评估结果
        """
        # 计算各维度得分（输入是0-10，转为0-100）
        dimension_scores = {
            "values_alignment": candidate.values_alignment * 10,
            "integrity_history": candidate.integrity_history * 10,
            "long_term_commitment": candidate.long_term_commitment * 10,
            "cultural_fit": candidate.cultural_fit * 10,
            "reputation_score": candidate.reputation_score * 10
        }
        
        # 计算加权总分
        total_score = sum(
            dimension_scores[dim] * self.WEIGHTS[dim]
            for dim in self.WEIGHTS
        )
        
        # 确定信任等级
        trust_level = self._determine_trust_level(total_score)
        
        # 生成合作建议
        recommendation = self._generate_recommendation(
            total_score, trust_level, candidate.red_flags
        )
        
        # 生成风险预警
        risk_warnings = self._generate_risk_warnings(candidate, dimension_scores)
        
        # 生成推理说明
        reasoning = self._generate_reasoning(
            candidate.name, total_score, trust_level, dimension_scores
        )
        
        return LIUEvaluationResult(
            candidate_name=candidate.name,
            total_score=round(total_score, 1),
            trust_level=trust_level,
            recommendation=recommendation,
            dimension_scores=dimension_scores,
            risk_warnings=risk_warnings,
            reasoning=reasoning
        )
    
    def _determine_trust_level(self, score: float) -> TrustLevel:
        """根据总分确定信任等级"""
        if score >= 85:
            return TrustLevel.L5_FULL_TRUST
        elif score >= 70:
            return TrustLevel.L4_TRUSTED
        elif score >= 55:
            return TrustLevel.L3_NEUTRAL
        elif score >= 40:
            return TrustLevel.L2_CAUTIOUS
        else:
            return TrustLevel.L1_UNTRUSTED
    
    def _generate_recommendation(self, score: float, 
                                  trust_level: TrustLevel,
                                  red_flags: List[str]) -> Recommendation:
        """生成合作建议"""
        # 有严重red flags直接不推荐
        if len(red_flags) >= 2:
            return Recommendation.NOT_RECOMMEND
        
        if trust_level in [TrustLevel.L5_FULL_TRUST, TrustLevel.L4_TRUSTED]:
            return Recommendation.RECOMMEND
        elif trust_level == TrustLevel.L3_NEUTRAL:
            if red_flags:
                return Recommendation.CAUTIOUS
            return Recommendation.RECOMMEND
        elif trust_level == TrustLevel.L2_CAUTIOUS:
            return Recommendation.CAUTIOUS
        else:
            return Recommendation.NOT_RECOMMEND
    
    def _generate_risk_warnings(self, candidate: CandidateData,
                                 scores: Dict[str, float]) -> List[str]:
        """生成风险预警"""
        warnings = []
        
        # 基于各维度得分生成预警
        if scores["values_alignment"] < 50:
            warnings.append("价值观一致性较低，可能存在理念冲突")
        
        if scores["integrity_history"] < 50:
            warnings.append("历史诚信记录不足，建议深入背调")
        
        if scores["long_term_commitment"] < 50:
            warnings.append("长期承诺度低，可能中途退出")
        
        if scores["cultural_fit"] < 50:
            warnings.append("文化契合度低，团队融入可能困难")
        
        # 添加red flags
        for flag in candidate.red_flags:
            warnings.append(f"Red Flag: {flag}")
        
        return warnings
    
    def _generate_reasoning(self, name: str, score: float,
                           trust_level: TrustLevel,
                           scores: Dict[str, float]) -> str:
        """生成评估推理说明"""
        lines = [
            f"【LIU评估 - {name}】",
            f"",
            f"总分: {score:.1f}/100 | 信任等级: {trust_level.value}",
            f"",
            f"维度分析:",
            f"  • 价值观一致性: {scores['values_alignment']:.1f}/100 (权重30%)",
            f"  • 历史诚信: {scores['integrity_history']:.1f}/100 (权重25%)",
            f"  • 长期承诺: {scores['long_term_commitment']:.1f}/100 (权重20%)",
            f"  • 文化契合: {scores['cultural_fit']:.1f}/100 (权重15%)",
            f"  • 人品口碑: {scores['reputation_score']:.1f}/100 (权重10%)",
            f"",
            f"结论: {trust_level.name}",
        ]
        
        return "\n".join(lines)
    
    def format_report(self, result: LIUEvaluationResult) -> str:
        """格式化评估报告"""
        lines = [
            "=" * 50,
            f"【LIU根基与信任评估报告】",
            f"评估对象: {result.candidate_name}",
            f"评估时间: 2026-03-29",
            "=" * 50,
            f"",
            f"【综合评分】",
            f"  总分: {result.total_score}/100",
            f"  信任等级: {result.trust_level.value}",
            f"  合作建议: {result.recommendation.value}",
            f"",
            f"【维度得分】",
        ]
        
        for dim, score in result.dimension_scores.items():
            weight = self.WEIGHTS[dim] * 100
            lines.append(f"  {dim}: {score:.1f}/100 (权重{weight:.0f}%)")
        
        if result.risk_warnings:
            lines.extend([
                f"",
                f"【风险预警】",
            ])
            for warning in result.risk_warnings:
                lines.append(f"  ⚠️  {warning}")
        
        lines.extend([
            f"",
            f"【评估依据】",
            result.reasoning,
            f"",
            "=" * 50,
            f"【五路图腾】LIU（土）- 聚贤才为伍，引智士同行",
            "=" * 50,
        ])
        
        return "\n".join(lines)


# 便捷函数
def evaluate_partner(name: str, 
                     values_alignment: float = 5.0,
                     integrity_history: float = 5.0,
                     long_term_commitment: float = 5.0,
                     cultural_fit: float = 5.0,
                     reputation_score: float = 5.0,
                     red_flags: Optional[List[str]] = None) -> str:
    """
    快速评估函数
    
    Args:
        name: 候选人姓名
        values_alignment: 价值观一致性 (0-10)
        integrity_history: 历史诚信 (0-10)
        long_term_commitment: 长期承诺 (0-10)
        cultural_fit: 文化契合 (0-10)
        reputation_score: 人品口碑 (0-10)
        red_flags: 风险标记列表
    
    Returns:
        str: 格式化评估报告
    """
    candidate = CandidateData(
        name=name,
        values_alignment=values_alignment,
        integrity_history=integrity_history,
        long_term_commitment=long_term_commitment,
        cultural_fit=cultural_fit,
        reputation_score=reputation_score,
        red_flags=red_flags or []
    )
    
    liu = LIUSkill()
    result = liu.evaluate_partner(candidate)
    return liu.format_report(result)


if __name__ == "__main__":
    # 测试用例
    print("=" * 60)
    print("LIU（刘禹锡）- 根基与信任评估器 测试")
    print("=" * 60)
    print()
    
    # 优秀候选人
    print(evaluate_partner(
        name="张三",
        values_alignment=9.0,
        integrity_history=8.5,
        long_term_commitment=8.0,
        cultural_fit=8.5,
        reputation_score=9.0
    ))
    
    print()
    print("-" * 60)
    print()
    
    # 有风险候选人
    print(evaluate_partner(
        name="李四",
        values_alignment=6.0,
        integrity_history=4.0,
        long_term_commitment=5.0,
        cultural_fit=5.5,
        reputation_score=4.5,
        red_flags=["有历史合同纠纷记录"]
    ))
