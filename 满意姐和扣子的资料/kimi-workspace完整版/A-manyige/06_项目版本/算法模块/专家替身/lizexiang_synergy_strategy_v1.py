"""
lizexiang_synergy_strategy_v1.py
满意解研究所与李泽湘体系协同策略分析器 V1.0

来源: 满意解研究所与李泽湘体系协同策略研究报告1.0
版本: V1.0
生成时间: 2026-04-09
作者: 蓝军 Skeptor-7
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum


class SynergyDomain(Enum):
    TALENT_PIPELINE = "人才管道"
    PROJECT_CO_INVESTMENT = "项目联合投资"
    MENTOR_NETWORK = "导师网络共享"
    REGIONAL_EXPANSION = "区域扩张复制"
    RESEARCH_COLLAB = "研究协作"


class PartnerProfile(Enum):
    STARTUP = "硬科技初创企业"
    INCUBATOR = "孵化器/加速器"
    UNIVERSITY = "高校教改班"
    GOVERNMENT = "地方政府/园区"
    INVESTOR = "投资机构"


@dataclass
class SynergyAssessment:
    domain: SynergyDomain
    readiness_score: float   # 0-100
    synergy_value: str
    recommended_actions: List[str] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)


class LizexiangSynergyStrategyV1:
    """
    满意解研究所 × 李泽湘体系（XbotPark）协同策略评估与建议引擎。
    基于"基地+基金+学院"三位一体模式与区域扩展数据。
    """

    XBOTPARK_STATS = {
        "total_incubated": 270,
        "total_valuation_bn": 350,
        "unicorns": 12,
        "songshanhu_companies": 70,
        "songshanhu_unicorns": 6,
        "overall_survival_rate": 0.80,
        "unicorn_rate": 0.15,
        "regional_bases": ["东莞松山湖", "深圳科创学院", "宁波基地", "常州基地", "重庆明月湖", "香港基地"],
    }

    REGIONAL_FOCUS = {
        "深圳科创学院": "AI硬件 + 半小时创新圈",
        "宁波基地": "工业互联网与智能制造",
        "重庆明月湖": "西部硬科技 + 青年创新创业人才孵化",
        "香港基地": "香港研发 + 内地转化 跨境协同",
        "常州基地": "新工科教育改革 + 创业浓度提升",
    }

    CONCENTRATION_BENCHMARKS = {
        "MIT_Stanford": 0.01,
        "常州大学教改班": 0.10,
        "重庆大学明月班": 0.20,
        "广州美院达芬奇创新学院": 0.60,
    }

    def __init__(self):
        self.domain_weights = {
            SynergyDomain.TALENT_PIPELINE: 0.25,
            SynergyDomain.PROJECT_CO_INVESTMENT: 0.20,
            SynergyDomain.MENTOR_NETWORK: 0.20,
            SynergyDomain.REGIONAL_EXPANSION: 0.20,
            SynergyDomain.RESEARCH_COLLAB: 0.15,
        }

    def assess_partner_fit(self, partner_type: PartnerProfile,
                           region: Optional[str] = None,
                           has_talent_pool: bool = False,
                           has_capital: bool = False) -> List[SynergyAssessment]:
        """根据合作伙伴画像输出协同策略评估。"""
        results = []

        # Domain 1: 人才管道
        if partner_type in (PartnerProfile.UNIVERSITY, PartnerProfile.INCUBATOR, PartnerProfile.GOVERNMENT):
            actions = ["接入李泽湘‘新工科’课程体系，提升创业浓度"] if has_talent_pool else ["共建人才筛选与培养前置基地"]
            risks = [] if has_talent_pool else ["缺乏系统化新工科课程，人才筛选成本较高"]
            results.append(SynergyAssessment(
                domain=SynergyDomain.TALENT_PIPELINE,
                readiness_score=85.0 if has_talent_pool else 55.0,
                synergy_value="高" if has_talent_pool else "中",
                recommended_actions=actions,
                risks=risks,
            ))

        # Domain 2: 项目联合投资
        if partner_type in (PartnerProfile.INVESTOR, PartnerProfile.INCUBATOR, PartnerProfile.GOVERNMENT):
            actions = ["参与清水湾基金二期，共享270+项目池"] if has_capital else ["引入李泽湘基金作为领投方，降低早期尽职调查成本"]
            risks = [] if has_capital else ["资金规模不足时，联合投资话语权受限"]
            results.append(SynergyAssessment(
                domain=SynergyDomain.PROJECT_CO_INVESTMENT,
                readiness_score=80.0 if has_capital else 60.0,
                synergy_value="高" if has_capital else "中",
                recommended_actions=actions,
                risks=risks,
            ))

        # Domain 3: 导师网络共享
        actions = ["引入李泽湘体系导师参与合伙人匹配与冲突调解",
                   "将满意解研究所的CBIIP感知力训练嵌入XbotPark孵化流程"]
        results.append(SynergyAssessment(
            domain=SynergyDomain.MENTOR_NETWORK,
            readiness_score=75.0,
            synergy_value="高",
            recommended_actions=actions,
            risks=["导师时间稀缺，需设计分层 mentorship 机制"],
        ))

        # Domain 4: 区域扩张复制
        if region and region in self.REGIONAL_FOCUS:
            focus = self.REGIONAL_FOCUS[region]
            results.append(SynergyAssessment(
                domain=SynergyDomain.REGIONAL_EXPANSION,
                readiness_score=90.0,
                synergy_value="高",
                recommended_actions=[f"在{region}落地协同节点，聚焦{focus}"],
                risks=["区域产业政策变化可能影响基地运营稳定性"],
            ))
        elif partner_type == PartnerProfile.GOVERNMENT:
            results.append(SynergyAssessment(
                domain=SynergyDomain.REGIONAL_EXPANSION,
                readiness_score=70.0,
                synergy_value="中",
                recommended_actions=["协助地方政府设计‘1校+1地+1平台+1园区’复制方案"],
                risks=["缺乏本地产业配套时，复制存活率可能下降"],
            ))

        # Domain 5: 研究协作
        results.append(SynergyAssessment(
            domain=SynergyDomain.RESEARCH_COLLAB,
            readiness_score=80.0,
            synergy_value="高",
            recommended_actions=[
                "联合发布《硬科技合伙人匹配白皮书》",
                "将270+案例数据与满意解决策引擎对接，验证预测模型"
            ],
            risks=["数据脱敏与商业机密保护须提前约定"],
        ))

        return results

    def generate_entry_strategy(self, partner_type: PartnerProfile, region: Optional[str] = None) -> Dict:
        """生成进入策略建议书。"""
        assessments = self.assess_partner_fit(partner_type, region)
        total_score = sum(a.readiness_score * self.domain_weights.get(a.domain, 0.20) for a in assessments)

        strategy_map = {
            PartnerProfile.STARTUP: {
                "entry_point": "申请入驻XbotPark基地 + 接受CBIIP感知力评估",
                "value_prop": "获得导师网络、供应链资源与联合投资机会",
            },
            PartnerProfile.INCUBATOR: {
                "entry_point": "导入满意解合伙人匹配工具与李泽湘 mentor 资源",
                "value_prop": "提升孵化存活率与独角兽产出率",
            },
            PartnerProfile.UNIVERSITY: {
                "entry_point": "共建新工科教改班，植入创业能力培养课程",
                "value_prop": "将学生创业浓度从<1%提升至10%-20%",
            },
            PartnerProfile.GOVERNMENT: {
                "entry_point": "引入XbotPark模式进行区域产业孵化顶层设计",
                "value_prop": "快速形成硬科技产业集群与高估值企业储备",
            },
            PartnerProfile.INVESTOR: {
                "entry_point": "联合清水湾基金对早期项目进行跟投或联合领投",
                "value_prop": "降低尽调成本，提升 early-stage Deal flow 质量",
            },
        }

        base = strategy_map.get(partner_type, {})
        return {
            "partner_type": partner_type.value,
            "region": region or "全国",
            "weighted_readiness_score": round(total_score, 2),
            "entry_point": base.get("entry_point", "定制化对接"),
            "value_proposition": base.get("value_prop", "双向赋能"),
            "domain_assessments": [
                {
                    "domain": a.domain.value,
                    "readiness": a.readiness_score,
                    "value": a.synergy_value,
                    "actions": a.recommended_actions,
                    "risks": a.risks,
                }
                for a in assessments
            ],
        }

    def get_xbotpark_stats(self) -> Dict:
        return dict(self.XBOTPARK_STATS)

    def get_regional_focus(self, region: str) -> Optional[str]:
        return self.REGIONAL_FOCUS.get(region)

    def benchmark_concentration(self, institution: str) -> Optional[float]:
        return self.CONCENTRATION_BENCHMARKS.get(institution)
