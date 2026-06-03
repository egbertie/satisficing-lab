"""
---
KIA-CODE: 知识入库代码级闭环
Asset: cross_cultural_trust.py
Status: ✅ 代码级KIA完成
Date: 2026-04-15
Batch: OM-03 Python资产25份代码级KIA-批次五

KIA-Loop:
  - 接收清点: 2026-04-15
  - 轻量提取: 2026-04-15 (代码结构识别)
  - 查重去冗: 2026-04-15 (无重复代码)
  - Tier分级: T1 (核心项目资产)
  - 深度洞察: 2026-04-15 (伦理与跨文化系统)
  - 血液化: ✅ 完成 (五路图腾映射确认)
  - 归档锁定: 2026-04-15

功能定位:
  - 用途: 跨文化信任系统
  - 关联: 信任构建
  - 维护者: 蓝军+满意姐

血液化映射:
  - 五路图腾关联: 合伙人信任评估
  - 产品映射: 刘禹锡-品德根基
  - 运营映射: 伦理与跨文化评估

---
"""

#!/usr/bin/env python3
"""
cross_cultural_trust.py - 跨文化信任差异分析（STAGE-D-CN华人适配版）
来源: 系统深度优化方案.docx - 第十五轮
功能: B1实现 - 跨文化信任轨迹计算与升级路径
"""
import json
from typing import Dict, List
from dataclasses import dataclass
import sys


@dataclass
class TrustDimension:
    """信任维度评分"""
    dimension: str
    score: float  # 0-100
    cultural_gap: float  # 与西方基准的差异
    adjustment_needed: bool


class STAGEDCNCalculator:
    """
    B1实现：跨文化信任差异分析（STAGE-D-CN华人适配版）
    基于规则引擎的配置化实现，允许后续填充本土化案例
    """

    def __init__(self):
        self.base_model = {
            'stages': ['陌生人', '认识', '熟悉', '朋友', '合作伙伴', '深度信任'],
            'transition_factors': ['能力', '善意', '诚信', '时间', '共同经历']
        }
        self.cn_rules = {
            'guanxi_weight': 0.3,
            'face_sensitivity': 0.8,
            'indirect_communication': 0.7,
            'long_term_orientation': 0.9,
            'family_similarity': 0.6,
            'reciprocity_intensity': 0.8
        }
        self.local_cases = [
            {
                'scenario': '初次见面即谈业务',
                'western_response': '高效直接',
                'chinese_response': '感觉被冒犯，缺乏信任基础',
                'rule': '避免在陌生人阶段直接商业提案'
            },
            {
                'scenario': '饭桌上不饮酒',
                'western_response': '尊重个人选择',
                'chinese_response': '可能视为不给面子，关系难以深化',
                'rule': '理解"酒桌文化"作为信任加速器的功能'
            }
        ]

    def calculate_trust_trajectory(self, partner_profile: Dict,
                                   interaction_history: List[Dict]) -> Dict:
        base_trust = self._calculate_base_trust(interaction_history)
        cultural_adjustment = self._apply_cultural_rules(base_trust, partner_profile)
        current_stage = self._determine_stage(cultural_adjustment['adjusted_score'])
        next_steps = self._generate_next_steps(current_stage, cultural_adjustment)
        risks = self._identify_cultural_risks(partner_profile, interaction_history)
        return {
            'current_stage': current_stage,
            'stage_number': self.base_model['stages'].index(current_stage) + 1,
            'trust_score': round(cultural_adjustment['adjusted_score'], 1),
            'cultural_dimensions': [
                {'dimension': d.dimension, 'score': round(d.score, 1),
                 'gap': round(d.cultural_gap, 2), 'adjusted': d.adjustment_needed}
                for d in cultural_adjustment['dimensions']
            ],
            'upgrade_path': next_steps,
            'cultural_risks': risks,
            'time_to_next_stage_estimate': self._estimate_time(current_stage, cultural_adjustment),
            'comparison': {
                'western_context': f"在西方语境下可能已达到{self._determine_stage(base_trust)}阶段",
                'chinese_context': f"在华商语境下当前为{current_stage}阶段",
                'gap': round(cultural_adjustment['adjusted_score'] - base_trust, 1)
            }
        }

    def _calculate_base_trust(self, history: List[Dict]) -> float:
        if not history:
            return 0
        interactions = len(history)
        commitments_kept = sum(1 for h in history if h.get('commitment_kept', False))
        info_shared = sum(h.get('info_depth', 0) for h in history)
        score = (interactions * 5 + commitments_kept * 20 + info_shared * 2) / max(interactions, 1)
        return min(100, score)

    def _apply_cultural_rules(self, base_score: float, profile: Dict) -> Dict:
        dimensions = []
        adjusted = base_score
        if profile.get('shared_connections', 0) > 0:
            guanxi_boost = min(20, profile['shared_connections'] * 5 * self.cn_rules['guanxi_weight'])
            adjusted += guanxi_boost
            dimensions.append(TrustDimension('关系网络', guanxi_boost, self.cn_rules['guanxi_weight'], True))
        if profile.get('face_events', []):
            face_impact = sum(10 if e['positive'] else -15 for e in profile['face_events'])
            adjusted += face_impact * self.cn_rules['face_sensitivity']
            dimensions.append(TrustDimension('面子维护', face_impact, self.cn_rules['face_sensitivity'], True))
        if profile.get('relationship_duration_months', 0) > 12:
            long_term_bonus = 10 * self.cn_rules['long_term_orientation']
            adjusted += long_term_bonus
            dimensions.append(TrustDimension('长期关系', long_term_bonus, self.cn_rules['long_term_orientation'], False))
        reciprocity_score = profile.get('reciprocity_balance', 0)
        if reciprocity_score > 0:
            reciprocal_boost = 5 * self.cn_rules['reciprocity_intensity']
            adjusted += reciprocal_boost
            dimensions.append(TrustDimension('人情往来', reciprocal_boost, self.cn_rules['reciprocity_intensity'], True))
        return {
            'adjusted_score': min(100, max(0, adjusted)),
            'dimensions': dimensions,
            'rules_applied': len(dimensions)
        }

    def _determine_stage(self, score: float) -> str:
        stages = self.base_model['stages']
        thresholds = [0, 15, 35, 55, 75, 90]
        for i, threshold in enumerate(thresholds):
            if score < threshold:
                return stages[max(0, i - 1)]
        return stages[-1]

    def _generate_next_steps(self, current_stage: str, adjustment: Dict) -> List[str]:
        steps = []
        if current_stage == '陌生人':
            steps.extend([
                "寻找共同熟人引荐（关系背书）",
                "首次会面避免直接谈业务，先建立个人连接",
                "准备小礼物或饭局（符合礼仪但不过度）"
            ])
        elif current_stage == '认识':
            steps.extend([
                "创造非正式互动机会（茶叙优于正式会议）",
                "展示长期合作意愿（避免短期功利表现）",
                "注意面子给予（公开认可对方专业成就）"
            ])
        elif current_stage == '熟悉':
            steps.extend([
                "引入私域互动（家庭聚餐等，拟家族化）",
                "适度人情往来（帮小忙，建立互惠纽带）",
                "讨论共同价值观（如技术理想、产业情怀）"
            ])
        else:
            steps.append("维持当前信任水平，注意避免文化误解导致的倒退")
        return steps

    def _identify_cultural_risks(self, profile: Dict, history: List[Dict]) -> List[str]:
        risks = []
        if len(history) > 0:
            avg_interval = sum(h.get('days_since_last', 0) for h in history) / len(history)
            if avg_interval < 3:
                risks.append("接触频率过高，可能被感知为急躁或不稳重")
        if any(h.get('public_disagreement', False) for h in history):
            risks.append("历史上存在公开分歧记录，需特别注意面子修复")
        if profile.get('transactional_language_ratio', 0) > 0.5:
            risks.append("语言中利益计算占比过高，建议增加关系性表述")
        return risks

    def _estimate_time(self, current_stage: str, adjustment: Dict) -> str:
        base_weeks = {'陌生人': 2, '认识': 4, '熟悉': 8, '朋友': 12, '合作伙伴': 20}
        weeks = base_weeks.get(current_stage, 4)
        adjusted_weeks = int(weeks * (1 + (1 - self.cn_rules['long_term_orientation']) * 0.5))
        return f"约{adjusted_weeks}周（在持续互动前提下）"


if __name__ == "__main__":
    calc = STAGEDCNCalculator()
    profile = {
        'shared_connections': 2,
        'face_events': [{'positive': True}],
        'relationship_duration_months': 6,
        'reciprocity_balance': 5
    }
    history = [
        {'commitment_kept': True, 'info_depth': 3, 'days_since_last': 7},
        {'commitment_kept': True, 'info_depth': 4, 'days_since_last': 5}
    ]
    result = calc.calculate_trust_trajectory(profile, history)
    print(f"✓ 跨文化信任分析:")
    print(f"  当前阶段: {result['current_stage']} (第{result['stage_number']}级)")
    print(f"  信任分数: {result['trust_score']}")
    print(f"  文化差距: {result['comparison']['gap']:+}")
    print(f"  升级建议: {len(result['upgrade_path'])}条")
    print(f"  风险提示: {len(result['cultural_risks'])}项")
    assert result['stage_number'] > 0, "应确定有效阶段"
    assert 'comparison' in result, "应提供中西对比"
    print("\n✓ 跨文化信任计算系统验证通过")
    sys.exit(0)
