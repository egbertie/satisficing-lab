#!/usr/bin/env python3
"""
Partner Matching Engine - 合伙人匹配引擎
基于赫伯特·西蒙满意解理论 + 儒商五维评估 + 前景理论风险模型

核心算法:
1. SatisficingMatcher - 满意解匹配（非最大化，阈值截止）
2. ComplementarityScorer - 能力互补性评估
3. ConfucianEthicsEvaluator - 儒商伦理五维评估
4. ProspectTheoryRiskScorer - 前景理论风险兼容
5. ExplanationGenerator - 可解释性生成

Author: 满意解研究所
Version: 1.0.0
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Literal, Any
from enum import Enum
import json
import uuid
from datetime import datetime


# ═══════════════════════════════════════════════════════════════
# 数据模型定义
# ═══════════════════════════════════════════════════════════════

class CapabilityDimension(str, Enum):
    """能力维度"""
    TECHNICAL_DEPTH = "technical_depth"
    BUSINESS_ACUMEN = "business_acumen"
    FINANCIAL_MANAGEMENT = "financial_management"
    TEAM_BUILDING = "team_building"
    INDUSTRY_NETWORK = "industry_network"
    FUNDRAISING = "fundraising"
    OPERATIONS = "operations"
    SALES_MARKETING = "sales_marketing"


class RiskTolerance(str, Enum):
    """风险容忍度"""
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"


class PartnerType(str, Enum):
    """合伙人类型"""
    BUSINESS = "商业合伙人"
    TECHNICAL = "技术合伙人"
    OPERATION = "运营合伙人"
    FINANCE = "财务合伙人"
    STRATEGIC = "战略合伙人"


class Outcome(str, Enum):
    """匹配结果"""
    SUCCESS = "成功"
    FAILURE = "失败"
    PENDING = "待定"
    ONGOING = "进行中"


@dataclass
class ValueDimension:
    """价值观维度评估（仁义礼智信）"""
    score: float = field(default=0.5)  # 0-1标准化分数
    evidence: List[str] = field(default_factory=list)  # 支撑证据
    confidence: float = field(default=0.8)  # 置信度 0-1
    
    def to_dict(self) -> Dict[str, Any]:
        return {"score": self.score, "evidence": self.evidence, "confidence": self.confidence}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ValueDimension':
        return cls(
            score=data.get("score", 0.5),
            evidence=data.get("evidence", []),
            confidence=data.get("confidence", 0.8)
        )


@dataclass
class RiskIndicators:
    """风险指标"""
    employment_status: Literal["full_time", "part_time_available", "advisory_only"] = "full_time"
    location_flexibility: Literal["local", "remote_ok", "hybrid_required"] = "local"
    equity_expectation: float = 0.25  # 期望股权比例 0-1
    non_compete_status: Literal["cleared", "pending", "restricted"] = "cleared"
    pending_litigations: List[str] = field(default_factory=list)
    financial_safety_need: Literal["high", "medium", "low"] = "medium"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "employment_status": self.employment_status,
            "location_flexibility": self.location_flexibility,
            "equity_expectation": self.equity_expectation,
            "non_compete_status": self.non_compete_status,
            "pending_litigations": self.pending_litigations,
            "financial_safety_need": self.financial_safety_need
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RiskIndicators':
        return cls(
            employment_status=data.get("employment_status", "full_time"),
            location_flexibility=data.get("location_flexibility", "local"),
            equity_expectation=data.get("equity_expectation", 0.25),
            non_compete_status=data.get("non_compete_status", "cleared"),
            pending_litigations=data.get("pending_litigations", []),
            financial_safety_need=data.get("financial_safety_need", "medium")
        )


@dataclass
class TrackRecord:
    """职业履历记录"""
    role: str = ""
    company_name: Optional[str] = None
    exit_valuation: Optional[int] = None  # 退出估值（人民币）
    exit_type: Optional[Literal["IPO", "Acquisition", "Shutdown"]] = None
    duration_months: int = 0
    lessons_learned: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "role": self.role,
            "company_name": self.company_name,
            "exit_valuation": self.exit_valuation,
            "exit_type": self.exit_type,
            "duration_months": self.duration_months,
            "lessons_learned": self.lessons_learned
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TrackRecord':
        return cls(
            role=data.get("role", ""),
            company_name=data.get("company_name"),
            exit_valuation=data.get("exit_valuation"),
            exit_type=data.get("exit_type"),
            duration_months=data.get("duration_months", 0),
            lessons_learned=data.get("lessons_learned")
        )


@dataclass
class FounderProfile:
    """创始人画像"""
    id: str = ""
    name: str = ""
    industry: str = ""  # 硬科技细分领域
    stage: Literal["idea", "pre_seed", "seed", "pre_a", "a_round", "growth"] = "pre_a"
    company_age_months: int = 0
    
    # 能力矩阵 1-10分自评
    capability_matrix: Dict[str, int] = field(default_factory=dict)
    
    # 价值观系统
    value_system: Dict[str, float] = field(default_factory=dict)
    
    # 风险偏好
    risk_profile: Dict[str, Any] = field(default_factory=dict)
    
    # 合伙人需求
    partner_requirements: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.id:
            self.id = f"founder_{uuid.uuid4().hex[:8]}"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "industry": self.industry,
            "stage": self.stage,
            "company_age_months": self.company_age_months,
            "capability_matrix": self.capability_matrix,
            "value_system": self.value_system,
            "risk_profile": self.risk_profile,
            "partner_requirements": self.partner_requirements
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FounderProfile':
        founder = cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            industry=data.get("industry", ""),
            stage=data.get("stage", "pre_a"),
            company_age_months=data.get("company_age_months", 0),
            capability_matrix=data.get("capability_matrix", {}),
            value_system=data.get("value_system", {}),
            risk_profile=data.get("risk_profile", {}),
            partner_requirements=data.get("partner_requirements", {})
        )
        return founder


@dataclass
class CandidateProfile:
    """候选人画像"""
    id: str = ""
    name: str = ""
    current_role: str = ""
    
    # 能力矩阵 1-10分
    capability_matrix: Dict[str, int] = field(default_factory=dict)
    
    # 价值观对齐证据（仁义礼智信五维）
    value_alignment_evidence: Dict[str, ValueDimension] = field(default_factory=dict)
    
    # 风险指标
    risk_indicators: RiskIndicators = field(default_factory=RiskIndicators)
    
    # 职业履历
    track_records: List[TrackRecord] = field(default_factory=list)
    
    # 推荐信
    references: List[Dict[str, Any]] = field(default_factory=list)
    
    def __post_init__(self):
        if not self.id:
            self.id = f"candidate_{uuid.uuid4().hex[:8]}"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "current_role": self.current_role,
            "capability_matrix": self.capability_matrix,
            "value_alignment_evidence": {
                k: v.to_dict() for k, v in self.value_alignment_evidence.items()
            },
            "risk_indicators": self.risk_indicators.to_dict(),
            "track_records": [t.to_dict() for t in self.track_records],
            "references": self.references
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CandidateProfile':
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            current_role=data.get("current_role", ""),
            capability_matrix=data.get("capability_matrix", {}),
            value_alignment_evidence={
                k: ValueDimension.from_dict(v) 
                for k, v in data.get("value_alignment_evidence", {}).items()
            },
            risk_indicators=RiskIndicators.from_dict(data.get("risk_indicators", {})),
            track_records=[TrackRecord.from_dict(t) for t in data.get("track_records", [])],
            references=data.get("references", [])
        )


@dataclass
class DimensionScores:
    """多维度评分结果"""
    complementarity: float = 0.0  # 能力互补性 0-100
    values_alignment: float = 0.0  # 价值观对齐 0-100
    risk_compatibility: float = 0.0  # 风险兼容性 0-100
    growth_potential: float = 0.0  # 成长潜力 0-100
    
    @property
    def average(self) -> float:
        return (self.complementarity + self.values_alignment + 
                self.risk_compatibility + self.growth_potential) / 4
    
    def to_dict(self) -> Dict[str, float]:
        return {
            "complementarity": self.complementarity,
            "values_alignment": self.values_alignment,
            "risk_compatibility": self.risk_compatibility,
            "growth_potential": self.growth_potential,
            "average": self.average
        }


@dataclass
class SatisficingThresholds:
    """满意解阈值设定"""
    complementarity: float = 70.0
    values_alignment: float = 75.0
    risk_compatibility: float = 70.0
    growth_potential: float = 60.0
    
    def to_dict(self) -> Dict[str, float]:
        return {
            "complementarity": self.complementarity,
            "values_alignment": self.values_alignment,
            "risk_compatibility": self.risk_compatibility,
            "growth_potential": self.growth_potential
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, float]) -> 'SatisficingThresholds':
        return cls(
            complementarity=data.get("complementarity", 70.0),
            values_alignment=data.get("values_alignment", 75.0),
            risk_compatibility=data.get("risk_compatibility", 70.0),
            growth_potential=data.get("growth_potential", 60.0)
        )


@dataclass
class MatchResult:
    """匹配结果"""
    candidate_id: str = ""
    candidate_name: str = ""
    overall_score: float = 0.0  # 综合得分 0-100
    confidence: float = 0.0  # 置信度 0-1
    dimension_scores: DimensionScores = field(default_factory=DimensionScores)
    satisficing_met: bool = False  # 是否满足满意解
    red_flags: List[str] = field(default_factory=list)  # 警示信号
    deal_breakers: List[str] = field(default_factory=list)  # 一票否决项
    recommendation: Literal["strong_match", "conditional_match", "reject"] = "reject"
    explanation: Dict[str, Any] = field(default_factory=dict)  # 解释详情
    next_steps: List[str] = field(default_factory=list)  # 后续建议
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "candidate_name": self.candidate_name,
            "overall_score": self.overall_score,
            "confidence": self.confidence,
            "dimension_scores": self.dimension_scores.to_dict(),
            "satisficing_met": self.satisficing_met,
            "red_flags": self.red_flags,
            "deal_breakers": self.deal_breakers,
            "recommendation": self.recommendation,
            "explanation": self.explanation,
            "next_steps": self.next_steps
        }


# ═══════════════════════════════════════════════════════════════
# 核心算法实现
# ═══════════════════════════════════════════════════════════════

class SatisficingMatcher:
    """
    满意解匹配引擎
    
    基于赫伯特·西蒙的满意解理论:
    - 非最大化：不追求最优解，追求"足够好"
    - 阈值截止：设定可接受阈值，首个满足即停止搜索
    - 搜索成本：考虑搜索的认知和时间成本
    """
    
    def __init__(self, thresholds: Optional[SatisficingThresholds] = None):
        self.thresholds = thresholds or SatisficingThresholds()
        self.evaluated_count = 0
    
    def match_all(self, founder: FounderProfile, candidates: List[CandidateProfile],
                  max_search: Optional[int] = None) -> List[MatchResult]:
        """评估所有候选人，返回完整排序结果"""
        results = []
        search_limit = max_search or len(candidates)
        
        for idx, candidate in enumerate(candidates[:search_limit]):
            self.evaluated_count += 1
            result = self._evaluate_single(founder, candidate, idx)
            results.append(result)
        
        # 按综合得分降序排序
        results.sort(key=lambda x: x.overall_score, reverse=True)
        
        # 标记首个满足满意解条件的
        for r in results:
            if r.satisficing_met and not r.deal_breakers:
                r.recommendation = "strong_match"
                break
        
        return results
    
    def find_satisficing(self, founder: FounderProfile, 
                         candidates: List[CandidateProfile],
                         max_search: Optional[int] = None) -> Optional[MatchResult]:
        """
        严格满意解算法：找到首个满足所有阈值的候选人立即返回
        这是西蒙满意解理论的核心实现
        """
        search_limit = max_search or len(candidates)
        
        for idx, candidate in enumerate(candidates[:search_limit]):
            self.evaluated_count += 1
            
            # 1. 一票否决检查
            deal_breakers = self._check_deal_breakers(founder, candidate)
            if deal_breakers:
                continue
            
            # 2. 多维度评估
            dim_scores = self._calculate_dimensions(founder, candidate)
            
            # 3. 阈值检查（满意解核心）
            meets_thresholds = (
                dim_scores.complementarity >= self.thresholds.complementarity and
                dim_scores.values_alignment >= self.thresholds.values_alignment and
                dim_scores.risk_compatibility >= self.thresholds.risk_compatibility and
                dim_scores.growth_potential >= self.thresholds.growth_potential
            )
            
            if meets_thresholds:
                # 满意解找到！立即停止搜索（西蒙理论核心）
                return self._create_result(
                    candidate, dim_scores,
                    satisficing=True,
                    search_cost=self._calculate_search_cost(idx + 1),
                    deal_breakers=[]
                )
        
        # 无满意解，返回最佳替代
        return self._find_best_alternative(founder, candidates)
    
    def _check_deal_breakers(self, founder: FounderProfile,
                            candidate: CandidateProfile) -> List[str]:
        """一票否决逻辑（硬约束）"""
        deal_breakers = []
        
        # 1. 法律风险
        if candidate.risk_indicators.pending_litigations:
            deal_breakers.append("存在未决诉讼")
        
        if candidate.risk_indicators.non_compete_status == "restricted":
            deal_breakers.append("竞业限制未解除")
        
        # 2. 股权期望超限
        max_offer = founder.partner_requirements.get('max_equity_offer', 0.40)
        if candidate.risk_indicators.equity_expectation > max_offer:
            deal_breakers.append(
                f"股权期望({candidate.risk_indicators.equity_expectation:.0%})"
                f"超过可接受范围({max_offer:.0%})"
            )
        
        # 3. 价值观底线（儒商五维中任何一项低于0.5）
        for dim, evidence in candidate.value_alignment_evidence.items():
            if evidence.score < 0.5:
                deal_breakers.append(f"{dim}维度价值观得分过低({evidence.score:.2f})")
        
        # 4. 全职承诺要求
        if "full_time_commitment" in founder.partner_requirements.get('deal_breakers', []):
            if candidate.risk_indicators.employment_status != "full_time":
                deal_breakers.append("无法满足全职承诺要求")
        
        return deal_breakers
    
    def _calculate_dimensions(self, founder: FounderProfile,
                             candidate: CandidateProfile) -> DimensionScores:
        """计算四个核心维度得分"""
        
        # 1. 互补性（40%权重）
        comp_score = self._calc_complementarity(
            founder.capability_matrix,
            candidate.capability_matrix,
            founder.partner_requirements.get('must_have_capabilities', [])
        )
        
        # 2. 价值观对齐（30%权重）
        values_score = self._calc_values_alignment(
            candidate.value_alignment_evidence,
            founder.value_system
        )
        
        # 3. 风险兼容（20%权重）
        risk_score = self._calc_risk_compatibility(
            founder.risk_profile,
            candidate.risk_indicators
        )
        
        # 4. 成长潜力（10%权重）
        growth_score = self._calc_growth_potential(candidate)
        
        return DimensionScores(
            complementarity=comp_score,
            values_alignment=values_score,
            risk_compatibility=risk_score,
            growth_potential=growth_score
        )
    
    def _calc_complementarity(self, founder_caps: Dict[str, int],
                              candidate_caps: Dict[str, int],
                              must_haves: List[str]) -> float:
        """
        互补性算法：
        - 差距>=5视为互补（加分）
        - 双方均>=6视为重叠（减分）
        - 必须能力覆盖（硬性要求）
        """
        complementarity_points = 0.0
        overlap_penalty = 0.0
        coverage_score = 0.0
        
        all_dims = set(founder_caps.keys()) | set(candidate_caps.keys())
        if not all_dims:
            return 50.0  # 默认值
        
        for dim in all_dims:
            f_score = founder_caps.get(dim, 0)
            c_score = candidate_caps.get(dim, 0)
            gap = abs(f_score - c_score)
            
            # 互补条件：一方强(>=7)一方弱(<=3)，差距>=5
            if gap >= 5 and max(f_score, c_score) >= 7:
                complementarity_points += gap / 2
            
            # 重叠惩罚：双方都强(>=6)
            if f_score >= 6 and c_score >= 6:
                overlap_penalty += (f_score + c_score - 12) / 4
        
        # 必须能力覆盖检查
        for need in must_haves:
            if candidate_caps.get(need, 0) >= 7:
                coverage_score += 20  # 每项必须能力+20分
        
        base_score = (complementarity_points / len(all_dims)) * 10
        final_score = base_score + coverage_score - overlap_penalty
        
        return max(0.0, min(100.0, final_score))
    
    def _calc_values_alignment(self, candidate_values: Dict[str, ValueDimension],
                               founder_values: Dict[str, float]) -> float:
        """
        儒商五维评估 + 长期主义对齐
        """
        if not candidate_values:
            return 50.0  # 默认值
        
        # 五维权重
        weights = {
            'ren': 0.20,   # 仁：利他
            'yi': 0.25,    # 义：底线（高权重，一票否决相关）
            'li': 0.15,    # 礼：契约
            'zhi': 0.20,   # 智：学习
            'xin': 0.20    # 信：信用
        }
        
        weighted_sum = 0.0
        for dim, weight in weights.items():
            if dim in candidate_values:
                weighted_sum += candidate_values[dim].score * weight
        
        # 长期主义对齐加成
        founder_long_term = founder_values.get('long_term_orientation', 0.5)
        candidate_ren = candidate_values.get('ren', ValueDimension(score=0.5))
        alignment_bonus = 10 if abs(founder_long_term - candidate_ren.score) < 0.2 else 0
        
        return min(100.0, weighted_sum * 100 + alignment_bonus)
    
    def _calc_risk_compatibility(self, founder_risk: Dict[str, Any],
                                 candidate_risk: RiskIndicators) -> float:
        """
        前景理论应用：
        - 退出时间一致性
        - 股权稀释容忍度
        """
        score = 100.0
        
        # 退出时间差异（权重30%）
        f_exit = founder_risk.get('exit_timeline_years', 5)
        c_exit = 5  # 简化处理
        exit_diff = abs(f_exit - c_exit)
        score -= exit_diff * 5  # 每年差异扣5分
        
        # 股权稀释容忍度（权重40%）
        f_dilution = founder_risk.get('equity_dilution_tolerance', 0.30)
        c_expectation = candidate_risk.equity_expectation
        dilution_gap = abs(f_dilution - c_expectation)
        score -= dilution_gap * 100  # 转换为百分比扣分
        
        # 风险态度（权重30%）- 简化处理
        # 实际应通过candidate的历史track_record分析
        
        return max(0.0, min(100.0, score))
    
    def _calc_growth_potential(self, candidate: CandidateProfile) -> float:
        """成长潜力评估：学习敏捷性 + 失败经历价值"""
        base_score = 50.0
        
        # 学习敏捷性（通过智维证据）
        zhi_evidence = candidate.value_alignment_evidence.get('zhi')
        if zhi_evidence:
            base_score += zhi_evidence.score * 30
        
        # 失败经历（有价值的失败加分）
        for record in candidate.track_records:
            if record.exit_type == "Shutdown" and record.lessons_learned:
                base_score += 10  # 有教训的失败是资产
        
        # 推荐信质量
        high_cred_refs = len([r for r in candidate.references
                              if r.get('credibility') == 'high'])
        base_score += high_cred_refs * 5
        
        return min(100.0, base_score)
    
    def _calculate_search_cost(self, evaluated_count: int) -> Dict[str, Any]:
        """计算搜索成本（认知负荷模拟）"""
        return {
            "evaluated_candidates": evaluated_count,
            "cognitive_load": evaluated_count * 0.1,
            "time_cost_minutes": evaluated_count * 15,
            "satisficing_efficiency": 1.0 / evaluated_count if evaluated_count > 0 else 0
        }
    
    def _create_result(self, candidate: CandidateProfile,
                      dim_scores: DimensionScores,
                      satisficing: bool,
                      search_cost: Dict[str, Any],
                      deal_breakers: List[str]) -> MatchResult:
        """创建匹配结果对象"""
        
        # 综合得分（加权）
        weights = {
            'complementarity': 0.40,
            'values_alignment': 0.30,
            'risk_compatibility': 0.20,
            'growth_potential': 0.10
        }
        
        overall = sum(
            getattr(dim_scores, dim) * weight
            for dim, weight in weights.items()
        )
        
        # 置信度计算（基于证据完整度）
        evidence_count = len([e for e in candidate.value_alignment_evidence.values()
                              if e.evidence])
        confidence = min(0.95, 0.6 + evidence_count * 0.05)
        
        return MatchResult(
            candidate_id=candidate.id,
            candidate_name=candidate.name,
            overall_score=round(overall, 2),
            confidence=round(confidence, 2),
            dimension_scores=dim_scores,
            satisficing_met=satisficing,
            red_flags=[],
            deal_breakers=deal_breakers,
            recommendation="strong_match" if satisficing else "conditional_match",
            explanation={},
            next_steps=self._generate_next_steps(satisficing, deal_breakers)
        )
    
    def _generate_next_steps(self, satisficing: bool,
                            deal_breakers: List[str]) -> List[str]:
        """生成后续行动建议"""
        if deal_breakers:
            return ["终止接触：存在不可接受的风险因素", "寻找替代候选人"]
        
        if satisficing:
            return [
                "1. 深度尽职调查：验证所有证据材料",
                "2. 压力测试面试：设计3个冲突场景测试反应",
                "3. 试用期机制：建议3-6个月合作试用期",
                "4. 股权架构设计：协商动态股权兑现方案"
            ]
        else:
            return [
                "1. 差距分析：明确不满足的具体维度",
                "2. 条件谈判：尝试通过协议条款弥补短板",
                "3. 备选方案：同时评估其他候选人"
            ]
    
    def _find_best_alternative(self, founder: FounderProfile,
                              candidates: List[CandidateProfile]) -> Optional[MatchResult]:
        """无满意解时，返回最接近阈值的候选人"""
        best_score = -1.0
        best_result = None
        
        for candidate in candidates:
            deal_breakers = self._check_deal_breakers(founder, candidate)
            if deal_breakers:
                continue
            
            dim_scores = self._calculate_dimensions(founder, candidate)
            total = (dim_scores.complementarity + dim_scores.values_alignment +
                    dim_scores.risk_compatibility + dim_scores.growth_potential)
            
            if total > best_score:
                best_score = total
                best_result = self._create_result(
                    candidate, dim_scores,
                    satisficing=False,
                    search_cost=self._calculate_search_cost(len(candidates)),
                    deal_breakers=[]
                )
        
        return best_result
    
    def _evaluate_single(self, founder: FounderProfile,
                        candidate: CandidateProfile,
                        idx: int) -> MatchResult:
        """评估单个候选人"""
        deal_breakers = self._check_deal_breakers(founder, candidate)
        dim_scores = self._calculate_dimensions(founder, candidate)
        
        # 检查是否满足满意解
        satisficing = (
            not deal_breakers and
            dim_scores.complementarity >= self.thresholds.complementarity and
            dim_scores.values_alignment >= self.thresholds.values_alignment and
            dim_scores.risk_compatibility >= self.thresholds.risk_compatibility and
            dim_scores.growth_potential >= self.thresholds.growth_potential
        )
        
        return self._create_result(
            candidate, dim_scores,
            satisficing=satisficing,
            search_cost=self._calculate_search_cost(idx + 1),
            deal_breakers=deal_breakers
        )


class ExplanationGenerator:
    """可解释性生成器 - 生成类人可理解的匹配解释"""
    
    DIMENSION_NAMES = {
        'complementarity': '能力互补性',
        'values_alignment': '价值观对齐',
        'risk_compatibility': '风险兼容性',
        'growth_potential': '成长潜力'
    }
    
    def generate(self, result: MatchResult, founder: FounderProfile,
                candidate: CandidateProfile) -> Dict[str, Any]:
        """生成完整解释报告"""
        explanation = {
            "executive_summary": self._generate_summary(result),
            "detailed_analysis": self._analyze_dimensions(
                result.dimension_scores, founder, candidate
            ),
            "risk_assessment": self._assess_risks(result, candidate),
            "analogy": self._generate_analogy(result),
            "claw_recommended_questions": self._generate_questions(
                result, founder, candidate
            )
        }
        return explanation
    
    def _generate_summary(self, result: MatchResult) -> str:
        """生成执行摘要"""
        if result.satisficing_met:
            return (
                f"**{result.candidate_name}** 满足所有最低阈值，是合格的满意解。"
                f"综合匹配度{result.overall_score:.1f}分，建议进入深度尽调阶段。"
                f"核心优势在{self._get_strongest_dimension(result.dimension_scores)}维度。"
            )
        else:
            return (
                f"**{result.candidate_name}** 未达到全部阈值，但为当前候选集中的最优替代。"
                f"需重点关注{self._get_weakest_dimension(result.dimension_scores)}维度的差距。"
            )
    
    def _analyze_dimensions(self, scores: DimensionScores,
                           founder: FounderProfile,
                           candidate: CandidateProfile) -> List[Dict[str, Any]]:
        """逐维度详细分析"""
        analysis = []
        dimensions = {
            'complementarity': scores.complementarity,
            'values_alignment': scores.values_alignment,
            'risk_compatibility': scores.risk_compatibility,
            'growth_potential': scores.growth_potential
        }
        
        for dim_key, score in dimensions.items():
            item = {
                "dimension": self.DIMENSION_NAMES[dim_key],
                "score": score,
                "level": self._score_level(score),
                "interpretation": self._interpret_dimension(dim_key, score),
                "suggestions": self._dimension_suggestions(dim_key, score)
            }
            analysis.append(item)
        
        return analysis
    
    def _assess_risks(self, result: MatchResult,
                     candidate: CandidateProfile) -> Dict[str, Any]:
        """风险评估"""
        risks = []
        
        # 股权期望风险
        if candidate.risk_indicators.equity_expectation > 0.30:
            risks.append({
                "type": "股权稀释",
                "level": "medium",
                "description": f"候选人期望{candidate.risk_indicators.equity_expectation:.0%}股权，可能导致控制权稀释",
                "mitigation": "设计分期兑现方案，设置业绩里程碑"
            })
        
        # 兼职风险
        if candidate.risk_indicators.employment_status == "part_time_available":
            risks.append({
                "type": "时间投入",
                "level": "high",
                "description": "候选人只能兼职投入，可能与创业高强度要求冲突",
                "mitigation": "明确最低时间承诺，设置关键节点到场要求"
            })
        
        # 价值观风险
        low_values = [k for k, v in candidate.value_alignment_evidence.items()
                      if v.score < 0.7]
        if low_values:
            risks.append({
                "type": "价值观偏差",
                "level": "medium" if len(low_values) < 2 else "high",
                "description": f"在{', '.join(low_values)}维度存在价值观差异",
                "mitigation": "通过具体场景测试验证实际行为模式"
            })
        
        return {
            "total_risks": len(risks),
            "risk_items": risks,
            "overall_risk_level": "high" if any(r.get('level') == 'high' for r in risks) else "medium"
        }
    
    def _generate_analogy(self, result: MatchResult) -> str:
        """生成类比说明"""
        score = result.overall_score
        
        if score >= 85:
            return "如同刘备得诸葛亮：能力互补且价值观高度契合，具备长期合作基础。"
        elif score >= 70:
            return "如同唐僧收孙悟空：虽有紧箍咒（约束机制）风险，但能力互补性强。"
        elif score >= 60:
            return "如同宋江与李逵：短期战斗力强，但长期价值观风险需关注。"
        else:
            return "如同项羽与范增：表面互补，实则决策冲突风险极高。"
    
    def _generate_questions(self, result: MatchResult,
                           founder: FounderProfile,
                           candidate: CandidateProfile) -> List[Dict[str, Any]]:
        """生成Claw应追问的关键问题"""
        questions = []
        
        # 能力验证
        if result.dimension_scores.complementarity < 80:
            questions.append({
                "category": "能力验证",
                "question": f"候选人声称在关键领域有丰富经验，能否要求其提供具体项目案例并进行背景核实？",
                "purpose": "验证能力真实性",
                "priority": "high"
            })
        
        # 压力测试
        questions.append({
            "category": "压力测试",
            "question": "如果公司现金流只能维持6个月，候选人建议优先裁员50%还是全员降薪共渡难关？这与创始人的选择是否一致？",
            "purpose": "验证危机决策价值观",
            "priority": "critical"
        })
        
        # 股权期望
        if candidate.risk_indicators.equity_expectation > 0.25:
            questions.append({
                "category": "期望管理",
                "question": f"候选人期望{candidate.risk_indicators.equity_expectation:.0%}股权，其认知基础是什么（市场对比/过往经历/价值贡献预期）？",
                "purpose": "校准股权期望合理性",
                "priority": "high"
            })
        
        # 直觉校准
        questions.append({
            "category": "直觉验证",
            "question": "创始人在与候选人的交流中，是否有任何'微妙的违和感'或'过于完美的不真实感'？",
            "purpose": "激活右脑直觉判断",
            "priority": "critical"
        })
        
        return questions
    
    def _get_strongest_dimension(self, scores: DimensionScores) -> str:
        dims = {
            '能力互补性': scores.complementarity,
            '价值观对齐': scores.values_alignment,
            '风险兼容性': scores.risk_compatibility,
            '成长潜力': scores.growth_potential
        }
        return max(dims, key=dims.get)
    
    def _get_weakest_dimension(self, scores: DimensionScores) -> str:
        dims = {
            '能力互补性': scores.complementarity,
            '价值观对齐': scores.values_alignment,
            '风险兼容性': scores.risk_compatibility,
            '成长潜力': scores.growth_potential
        }
        return min(dims, key=dims.get)
    
    def _score_level(self, score: float) -> str:
        if score >= 80:
            return "优秀"
        if score >= 70:
            return "良好"
        if score >= 60:
            return "及格"
        return "需改进"
    
    def _interpret_dimension(self, dim_key: str, score: float) -> str:
        interpretations = {
            'complementarity': "候选人在关键领域与创始人形成能力互补",
            'values_alignment': f"儒商五维评估显示{'高度' if score > 80 else '基本'}一致",
            'risk_compatibility': f"退出预期和风险态度{'高度' if score > 80 else '部分'}匹配",
            'growth_potential': f"学习敏捷性和失败经历价值转化能力评估为{self._score_level(score)}"
        }
        return interpretations.get(dim_key, "")
    
    def _dimension_suggestions(self, dim_key: str, score: float) -> List[str]:
        if score >= 80:
            return ["保持现状，建议通过协议固化优势"]
        
        suggestions = {
            'complementarity': ["考虑聘请顾问弥补能力缺口", "设计能力补足的时间表"],
            'values_alignment': ["增加3-6个月价值观磨合期", "明确价值观冲突时的决策机制"],
            'risk_compatibility': ["设计动态股权调整机制", "建立风险共担的财务安排"],
            'growth_potential': ["设定学习目标和资源支持计划", "安排导师辅助成长"]
        }
        return suggestions.get(dim_key, ["需人工深度评估"])


# ═══════════════════════════════════════════════════════════════
# 数据持久化
# ═══════════════════════════════════════════════════════════════

import sqlite3
from pathlib import Path


class MatchingResultStore:
    """匹配结果存储"""
    
    def __init__(self, db_path: str = "./data/matching_results.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创始人表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS founders (
                id TEXT PRIMARY KEY,
                name TEXT,
                industry TEXT,
                stage TEXT,
                profile_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 候选人表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS candidates (
                id TEXT PRIMARY KEY,
                name TEXT,
                current_role TEXT,
                profile_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 匹配结果表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS matching_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                founder_id TEXT,
                candidate_id TEXT,
                overall_score REAL,
                satisficing_met BOOLEAN,
                recommendation TEXT,
                dimension_scores_json TEXT,
                deal_breakers_json TEXT,
                explanation_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (founder_id) REFERENCES founders(id),
                FOREIGN KEY (candidate_id) REFERENCES candidates(id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def save_founder(self, founder: FounderProfile) -> str:
        """保存创始人"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO founders (id, name, industry, stage, profile_json)
            VALUES (?, ?, ?, ?, ?)
        """, (
            founder.id,
            founder.name,
            founder.industry,
            founder.stage,
            json.dumps(founder.to_dict(), ensure_ascii=False)
        ))
        
        conn.commit()
        conn.close()
        return founder.id
    
    def save_candidate(self, candidate: CandidateProfile) -> str:
        """保存候选人"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO candidates (id, name, current_role, profile_json)
            VALUES (?, ?, ?, ?)
        """, (
            candidate.id,
            candidate.name,
            candidate.current_role,
            json.dumps(candidate.to_dict(), ensure_ascii=False)
        ))
        
        conn.commit()
        conn.close()
        return candidate.id
    
    def save_result(self, founder_id: str, candidate_id: str,
                   result: MatchResult) -> int:
        """保存匹配结果"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO matching_results 
            (founder_id, candidate_id, overall_score, satisficing_met, 
             recommendation, dimension_scores_json, deal_breakers_json, explanation_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            founder_id,
            candidate_id,
            result.overall_score,
            result.satisficing_met,
            result.recommendation,
            json.dumps(result.dimension_scores.to_dict()),
            json.dumps(result.deal_breakers),
            json.dumps(result.explanation)
        ))
        
        result_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return result_id
    
    def get_results_by_founder(self, founder_id: str) -> List[Dict[str, Any]]:
        """获取创始人的所有匹配结果"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT mr.*, c.name as candidate_name
            FROM matching_results mr
            JOIN candidates c ON mr.candidate_id = c.id
            WHERE mr.founder_id = ?
            ORDER BY mr.overall_score DESC
        """, (founder_id,))
        
        columns = [desc[0] for desc in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return results


# ═══════════════════════════════════════════════════════════════
# CLI入口
# ═══════════════════════════════════════════════════════════════

import click


@click.group()
def cli():
    """合伙人匹配引擎 - 基于满意解理论的智能匹配系统"""
    pass


@cli.command()
@click.option('--founder-file', '-f', required=True, help='创始人画像JSON文件路径')
@click.option('--candidates-file', '-c', required=True, help='候选人列表JSON文件路径')
@click.option('--output', '-o', default='matching_results.json', help='输出结果文件')
def match(founder_file, candidates_file, output):
    """执行匹配评估"""
    # 加载数据
    with open(founder_file, 'r', encoding='utf-8') as f:
        founder_data = json.load(f)
    founder = FounderProfile.from_dict(founder_data)
    
    with open(candidates_file, 'r', encoding='utf-8') as f:
        candidates_data = json.load(f)
    candidates = [CandidateProfile.from_dict(c) for c in candidates_data]
    
    # 执行匹配
    matcher = SatisficingMatcher()
    results = matcher.match_all(founder, candidates)
    
    # 生成解释
    explainer = ExplanationGenerator()
    for result in results:
        candidate = next(c for c in candidates if c.id == result.candidate_id)
        result.explanation = explainer.generate(result, founder, candidate)
    
    # 保存结果
    output_data = {
        "founder": founder.to_dict(),
        "candidates_count": len(candidates),
        "evaluated_count": matcher.evaluated_count,
        "matches": [r.to_dict() for r in results]
    }
    
    with open(output, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    click.echo(f"✅ 匹配完成，评估了 {matcher.evaluated_count} 位候选人")
    click.echo(f"📁 结果已保存至: {output}")
    
    # 输出满意解
    satisficing = [r for r in results if r.satisficing_met]
    if satisficing:
        click.echo(f"🎯 找到 {len(satisficing)} 位满足满意解的候选人")
        for r in satisficing[:3]:
            click.echo(f"   - {r.candidate_name}: {r.overall_score:.1f}分")
    else:
        click.echo("⚠️ 未找到满足满意解的候选人，已返回最优替代")


@cli.command()
@click.option('--result-file', '-r', required=True, help='匹配结果JSON文件路径')
@click.option('--candidate-id', '-c', required=True, help='候选人ID')
def explain(result_file, candidate_id):
    """查看详细解释报告"""
    with open(result_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    matches = data.get('matches', [])
    result = next((m for m in matches if m['candidate_id'] == candidate_id), None)
    
    if not result:
        click.echo(f"❌ 未找到候选人 {candidate_id} 的匹配结果")
        return
    
    click.echo("\n" + "=" * 60)
    click.echo(f"📊 匹配解释报告: {result['candidate_name']}")
    click.echo("=" * 60)
    
    expl = result.get('explanation', {})
    click.echo(f"\n{expl.get('executive_summary', '')}")
    
    click.echo(f"\n📈 维度得分:")
    dims = result.get('dimension_scores', {})
    for dim, name in ExplanationGenerator.DIMENSION_NAMES.items():
        score = dims.get(dim, 0)
        bar = "█" * int(score / 5) + "░" * (20 - int(score / 5))
        click.echo(f"  {name}: {score:.1f} [{bar}]")
    
    click.echo(f"\n🎯 推荐: {result.get('recommendation', 'unknown')}")
    
    click.echo(f"\n💡 后续建议:")
    for step in result.get('next_steps', []):
        click.echo(f"  • {step}")
    
    click.echo(f"\n🔍 追问清单:")
    questions = expl.get('claw_recommended_questions', [])
    for q in questions[:3]:
        click.echo(f"  [{q.get('priority', 'normal')}] {q.get('question', '')}")


@cli.command()
def demo():
    """运行示例匹配演示"""
    click.echo("🚀 运行合伙人匹配演示...\n")
    
    # 创建示例创始人
    founder = FounderProfile(
        name="张创始人",
        industry="AI芯片",
        stage="pre_a",
        capability_matrix={
            "technical_depth": 3,
            "business_acumen": 4,
            "financial_management": 3,
            "fundraising": 2,
            "industry_network": 5,
            "team_building": 5
        },
        value_system={
            "long_term_orientation": 0.8,
            "control_preference": 0.7
        },
        risk_profile={
            "exit_timeline_years": 7,
            "equity_dilution_tolerance": 0.30
        },
        partner_requirements={
            "must_have_capabilities": ["fundraising", "business_acumen"],
            "max_equity_offer": 0.35
        }
    )
    
    # 创建示例候选人
    candidates = [
        CandidateProfile(
            name="李CTO",
            current_role="前芯片公司技术总监",
            capability_matrix={
                "technical_depth": 9,
                "business_acumen": 5,
                "financial_management": 4,
                "fundraising": 3
            },
            value_alignment_evidence={
                "ren": ValueDimension(score=0.8, evidence=["团队评价良好"]),
                "yi": ValueDimension(score=0.9, evidence=["无诉讼记录"]),
                "li": ValueDimension(score=0.7, evidence=["合同履约记录"]),
                "zhi": ValueDimension(score=0.85, evidence=["持续学习记录"]),
                "xin": ValueDimension(score=0.9, evidence=["征信良好"])
            },
            risk_indicators=RiskIndicators(
                equity_expectation=0.25,
                employment_status="full_time"
            )
        ),
        CandidateProfile(
            name="王CFO",
            current_role="前上市公司CFO",
            capability_matrix={
                "technical_depth": 2,
                "business_acumen": 8,
                "financial_management": 9,
                "fundraising": 8
            },
            value_alignment_evidence={
                "ren": ValueDimension(score=0.7, evidence=["公益记录"]),
                "yi": ValueDimension(score=0.8, evidence=["合规历史"]),
                "li": ValueDimension(score=0.9, evidence=["财务规范"]),
                "zhi": ValueDimension(score=0.8, evidence=["CFA/CPA证书"]),
                "xin": ValueDimension(score=0.85, evidence=["无违约记录"])
            },
            risk_indicators=RiskIndicators(
                equity_expectation=0.30,
                employment_status="full_time"
            )
        )
    ]
    
    # 执行匹配
    matcher = SatisficingMatcher()
    results = matcher.match_all(founder, candidates)
    
    # 显示结果
    click.echo(f"创始人: {founder.name} ({founder.industry})")
    click.echo(f"评估候选人: {len(candidates)} 位\n")
    
    for i, result in enumerate(results, 1):
        status = "✅" if result.satisficing_met else "⚠️"
        click.echo(f"{status} #{i} {result.candidate_name}: {result.overall_score:.1f}分 "
                  f"(互补:{result.dimension_scores.complementarity:.0f} "
                  f"价值观:{result.dimension_scores.values_alignment:.0f})")
        if result.deal_breakers:
            click.echo(f"   一票否决: {', '.join(result.deal_breakers)}")
    
    click.echo("\n" + "=" * 60)
    click.echo("满意解匹配演示完成")


if __name__ == '__main__':
    cli()
