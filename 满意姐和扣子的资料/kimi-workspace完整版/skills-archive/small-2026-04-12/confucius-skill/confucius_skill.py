#!/usr/bin/env python3
"""
confucius_skill.py
CONFUCIUS（孔子）- 伦理与信任治理器
五路图腾之木 - 儒家伦理，文化认同，信任治理
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum


class EthicalPrinciple(Enum):
    """儒家伦理原则"""
    REN = "仁"  # 仁爱
    YI = "义"   # 义理
    LI = "礼"   # 礼仪
    ZHI = "智"  # 智慧
    XIN = "信"  # 诚信


class GovernanceLevel(Enum):
    """治理等级"""
    EXCELLENT = "优秀"
    GOOD = "良好"
    ADEQUATE = "合格"
    NEEDS_IMPROVEMENT = "需改进"
    CRITICAL = "严重"


@dataclass
class PartnerProfile:
    """合伙人档案"""
    name: str
    # 伦理维度评分 (0-10)
    benevolence: float = 5.0      # 仁
    righteousness: float = 5.0    # 义
    propriety: float = 5.0        # 礼
    wisdom: float = 5.0           # 智
    trustworthiness: float = 5.0  # 信
    
    # 文化认同
    cultural_alignment: float = 5.0  # 文化契合度
    ethical_violations: List[str] = field(default_factory=list)  # 伦理违规记录


@dataclass
class EthicalGovernanceResult:
    """伦理治理结果"""
    partner_name: str
    five_virtues_score: Dict[str, float]  # 五常得分
    overall_ethical_score: float  # 总体伦理得分
    governance_level: GovernanceLevel
    cultural_identity: float  # 文化认同度
    trustworthiness_rating: float  # 可信度评级
    recommendations: List[str]  # 治理建议
    conflict_resolution: Optional[str]  # 冲突调解方案


class ConfuciusSkill:
    """
    CONFUCIUS（孔子）- 伦理与信任治理器
    
    核心理念：儒家伦理，文化认同，信任治理
    五常：仁、义、礼、智、信
    """
    
    # 五常权重
    VIRTUE_WEIGHTS = {
        "benevolence": 0.20,      # 仁
        "righteousness": 0.20,    # 义
        "propriety": 0.20,        # 礼
        "wisdom": 0.20,           # 智
        "trustworthiness": 0.20   # 信
    }
    
    def __init__(self):
        self.name = "CONFUCIUS（孔子）"
        self.element = "木"
        self.motto = "儒家伦理，文化认同，信任治理"
    
    def evaluate_ethical_governance(self, partner: PartnerProfile) -> EthicalGovernanceResult:
        """
        评估伦理治理状态
        """
        # 计算五常得分
        five_virtues = {
            "仁(仁爱)": partner.benevolence * 10,
            "义(义理)": partner.righteousness * 10,
            "礼(礼仪)": partner.propriety * 10,
            "智(智慧)": partner.wisdom * 10,
            "信(诚信)": partner.trustworthiness * 10
        }
        
        # 计算总体伦理得分
        overall_score = sum(
            getattr(partner, virtue) * 10 * weight
            for virtue, weight in self.VIRTUE_WEIGHTS.items()
        )
        
        # 伦理违规惩罚
        violation_penalty = len(partner.ethical_violations) * 10
        overall_score = max(0, overall_score - violation_penalty)
        
        # 确定治理等级
        governance_level = self._determine_governance_level(overall_score)
        
        # 计算可信度
        trustworthiness = self._calculate_trustworthiness(partner, overall_score)
        
        # 生成治理建议
        recommendations = self._generate_recommendations(partner, five_virtues)
        
        # 冲突调解方案（如有违规）
        conflict_resolution = None
        if partner.ethical_violations:
            conflict_resolution = self._generate_conflict_resolution(partner)
        
        return EthicalGovernanceResult(
            partner_name=partner.name,
            five_virtues_score=five_virtues,
            overall_ethical_score=round(overall_score, 1),
            governance_level=governance_level,
            cultural_identity=partner.cultural_alignment * 10,
            trustworthiness_rating=trustworthiness,
            recommendations=recommendations,
            conflict_resolution=conflict_resolution
        )
    
    def _determine_governance_level(self, score: float) -> GovernanceLevel:
        """确定治理等级"""
        if score >= 85:
            return GovernanceLevel.EXCELLENT
        elif score >= 70:
            return GovernanceLevel.GOOD
        elif score >= 55:
            return GovernanceLevel.ADEQUATE
        elif score >= 40:
            return GovernanceLevel.NEEDS_IMPROVEMENT
        else:
            return GovernanceLevel.CRITICAL
    
    def _calculate_trustworthiness(self, partner: PartnerProfile, 
                                   base_score: float) -> float:
        """计算可信度评级"""
        # 基础可信度来自伦理得分
        trust = base_score
        
        # 诚信（信）权重加倍
        trust += partner.trustworthiness * 5
        
        # 文化认同加成
        trust += partner.cultural_alignment * 3
        
        # 违规记录惩罚
        trust -= len(partner.ethical_violations) * 15
        
        return max(0, min(100, trust))
    
    def _generate_recommendations(self, partner: PartnerProfile,
                                   virtues: Dict[str, float]) -> List[str]:
        """生成治理建议"""
        recommendations = []
        
        # 找出最低分项
        min_virtue = min(virtues.items(), key=lambda x: x[1])
        if min_virtue[1] < 60:
            recommendations.append(f"加强{min_virtue[0]}培养，这是当前最大短板")
        
        # 文化认同建议
        if partner.cultural_alignment < 6:
            recommendations.append("组织文化培训，提升团队文化认同")
        
        # 违规处理建议
        if partner.ethical_violations:
            recommendations.append(f"处理{len(partner.ethical_violations)}项伦理违规，重建信任")
            recommendations.append("建立伦理监督机制，防止再次发生")
        
        # 通用建议
        if partner.trustworthiness >= 8:
            recommendations.append("诚信表现优秀，可作为团队伦理榜样")
        
        if not recommendations:
            recommendations.append("伦理治理良好，继续保持")
        
        return recommendations
    
    def _generate_conflict_resolution(self, partner: PartnerProfile) -> str:
        """生成冲突调解方案"""
        steps = [
            f"1. 承认违规: {', '.join(partner.ethical_violations)}",
            "2. 道歉与承诺: 公开道歉并承诺不再发生",
            "3. 补偿行动: 根据违规程度采取补救措施",
            "4. 监督机制: 建立3-6个月观察期",
            "5. 信任重建: 通过持续良好表现逐步恢复信任"
        ]
        return "\n".join(steps)
    
    def format_report(self, result: EthicalGovernanceResult) -> str:
        """格式化治理报告"""
        lines = [
            "=" * 60,
            f"【CONFUCIUS伦理与信任治理报告】",
            f"评估对象: {result.partner_name}",
            "=" * 60,
            f"",
            f"【五常评估】",
        ]
        
        for virtue, score in result.five_virtues_score.items():
            status = "✅" if score >= 70 else ("🟡" if score >= 50 else "❌")
            lines.append(f"  {status} {virtue}: {score:.1f}/100")
        
        lines.extend([
            f"",
            f"【综合评估】",
            f"  总体伦理得分: {result.overall_ethical_score}/100",
            f"  治理等级: {result.governance_level.value}",
            f"  文化认同度: {result.cultural_identity:.1f}%",
            f"  可信度评级: {result.trustworthiness_rating:.1f}%",
        ])
        
        if result.conflict_resolution:
            lines.extend([
                f"",
                f"【冲突调解方案】",
                result.conflict_resolution,
            ])
        
        lines.extend([
            f"",
            f"【治理建议】",
        ])
        
        for i, rec in enumerate(result.recommendations, 1):
            lines.append(f"  {i}. {rec}")
        
        lines.extend([
            f"",
            "=" * 60,
            f"【五路图腾】CONFUCIUS（木）- 儒家伦理，文化认同",
            "=" * 60,
        ])
        
        return "\n".join(lines)


# 便捷函数
def ethical_governance(
    name: str,
    benevolence: float = 7.0,       # 仁 (0-10)
    righteousness: float = 7.0,     # 义 (0-10)
    propriety: float = 7.0,         # 礼 (0-10)
    wisdom: float = 7.0,            # 智 (0-10)
    trustworthiness: float = 7.0,   # 信 (0-10)
    cultural_alignment: float = 7.0,  # 文化认同 (0-10)
    ethical_violations: Optional[List[str]] = None
) -> str:
    """快速伦理评估"""
    partner = PartnerProfile(
        name=name,
        benevolence=benevolence,
        righteousness=righteousness,
        propriety=propriety,
        wisdom=wisdom,
        trustworthiness=trustworthiness,
        cultural_alignment=cultural_alignment,
        ethical_violations=ethical_violations or []
    )
    
    confucius = ConfuciusSkill()
    result = confucius.evaluate_ethical_governance(partner)
    return confucius.format_report(result)


if __name__ == "__main__":
    print("=" * 60)
    print("CONFUCIUS（孔子）- 伦理与信任治理器 测试")
    print("=" * 60)
    print()
    
    # 测试1: 优秀合伙人
    print(ethical_governance(
        name="优秀合伙人",
        benevolence=8.5,
        righteousness=8.0,
        propriety=8.5,
        wisdom=8.0,
        trustworthiness=9.0,
        cultural_alignment=8.5
    ))
    
    print()
    print("-" * 60)
    print()
    
    # 测试2: 有伦理问题
    print(ethical_governance(
        name="问题合伙人",
        benevolence=6.0,
        righteousness=5.0,
        propriety=6.5,
        wisdom=7.0,
        trustworthiness=4.0,  # 诚信低
        cultural_alignment=5.0,
        ethical_violations=["违反保密协议", "利益冲突未申报"]
    ))
