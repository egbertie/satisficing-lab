"""
外援代码: 五图腾Agent量化方案
来源: external_assistance_request_v1.0.md
状态: 保持原样，未经修改

包含:
- FiveTotemSystem: 五图腾系统框架
- LiuYuxiAgent: 刘禹锡(土) - 德馨评估
- SimonTotemAdapter: 司马贺(金) - 满意解适配
- GuanZizaiAgent: 观自在(水) - 直觉评估
"""
from typing import Dict, List, Any
import json


class FiveTotemSystem:
    """
    五图腾决策系统：刘禹锡(土)、司马贺(金)、观自在(水)、孔子(木)、慧能(火)
    五行相生相克关系融入冲突消解逻辑
    """
    TOTEM_PROFILES = {
        'liuyuxi': {  # 土 - 凝聚、德馨
            'element': 'earth',
            'dimensions': ['品德匹配', '团队凝聚', '长期信任'],
            'metrics': ['value_alignment', 'reputation', 'collaboration_history'],
            'weight': 0.2
        },
        'simon': {  # 金 - 理性、切割
            'element': 'metal',
            'dimensions': ['理性决策', '约束分析', '满意解'],
            'metrics': ['constraint_fit', 'rational_score', 'adequacy'],
            'weight': 0.25
        },
        'guanzizai': {  # 水 - 直觉、流动
            'element': 'water',
            'dimensions': ['直觉洞察', '压力应对', '内心自由'],
            'metrics': ['intuition_match', 'stress_resilience', 'autonomy'],
            'weight': 0.2
        },
        'confucius': {  # 木 - 伦理、生长
            'element': 'wood',
            'dimensions': ['仁义礼智信', '伦理评估', '长期信任'],
            'metrics': ['benevolence', 'righteousness', 'propriety', 'wisdom', 'trust'],
            'weight': 0.2
        },
        'huineng': {  # 火 - 顿悟、变革
            'element': 'fire',
            'dimensions': ['创新突破', '压力转化', '顿悟能力'],
            'metrics': ['innovation_complement', 'breakthrough_potential', 'stress_conversion'],
            'weight': 0.15
        }
    }
    # 五行相克关系用于冲突消解（水克火、火克金等）
    DOMINANCE_RELATIONS = {
        'water': 'fire',   # 观自在克慧能（直觉压过顿悟）
        'fire': 'metal',   # 慧能克司马贺（创新破约束）
        'metal': 'wood',   # 司马贺克孔子（理性压伦理）
        'wood': 'earth',   # 孔子克刘禹锡（伦理聚人心）
        'earth': 'water'   # 刘禹锡克观自在（德馨定直觉）
    }


class LiuYuxiAgent:
    """
    刘禹锡(土)：评估品德匹配与团队凝聚潜力
    核心指标：德馨指数 = f(价值观一致性, 过往声誉, 合作稳定性)
    """
    def evaluate(self, founder_values: List[str], candidate_profile: Dict) -> Dict:
        # 1. 价值观对齐度（关键词匹配+语义扩展）
        value_alignment = self._calculate_value_alignment(
            founder_values,
            candidate_profile.get('values_expression', ''),
            candidate_profile.get('track_record', '')
        )
        # 2. 德馨指数（基于过往行为的声誉推断）
        reputation_score = self._assess_reputation(
            candidate_profile.get('track_record', ''),
            candidate_profile.get('references', [])
        )
        # 3. 团队凝聚潜力（互补性+包容性）
        cohesion_potential = self._assess_cohesion(
            founder_values,
            candidate_profile.get('collaboration_style', ''),
            candidate_profile.get('conflict_resolution', '')
        )
        # 综合评分（德馨为不可妥协项，若价值观严重冲突直接降权）
        if value_alignment < 0.3:
            overall = value_alignment * 0.5  # 严重价值观冲突惩罚
            flag = "价值观根本冲突"
        else:
            overall = (value_alignment * 0.4 + reputation_score * 0.3 + cohesion_potential * 0.3)
            flag = "可接受" if overall > 0.6 else "需观察"
        return {
            'score': round(overall, 2),
            'dimension': '品德匹配/德馨',
            'analysis': self._generate_analysis(value_alignment, reputation_score, cohesion_potential, flag),
            'recommendation': flag,
            'details': {
                'value_alignment': round(value_alignment, 2),
                'reputation_score': round(reputation_score, 2),
                'cohesion_potential': round(cohesion_potential, 2)
            }
        }

    def _calculate_value_alignment(self, founder_vals: List[str], candidate_expr: str, track_record: str) -> float:
        """价值观对齐度：关键词共现+极性判断"""
        # 简化的基于规则的匹配
        alignment_indicators = {
            '长期主义': ['长期', '耐心', '坚持', '持久', 'sustainable'],
            '技术理想': ['理想', '使命', '愿景', '改变世界', '技术驱动'],
            '公平分享': ['公平', '分享', '共赢', 'generous', 'equitable']
        }
        combined_text = (candidate_expr + " " + track_record).lower()
        scores = []
        for fv in founder_vals:
            indicators = alignment_indicators.get(fv, [fv])
            matches = sum(1 for ind in indicators if ind in combined_text)
            scores.append(min(matches / 2, 1.0))  # 饱和于1.0
        return sum(scores) / len(scores) if scores else 0.5

    def _assess_reputation(self, track_record: str, references: List[str]) -> float:
        """声誉评估：基于过往记录的模式识别"""
        positive_signals = ['成功退出', '连续创业', '知名公司', '良好口碑', '诚信']
        negative_signals = ['纠纷', '诉讼', '失信', '频繁跳槽', '冲突']
        text = track_record.lower()
        pos_count = sum(1 for s in positive_signals if s in text)
        neg_count = sum(1 for s in negative_signals if s in text)
        # 贝叶斯式评分：基础0.5 + 正信号加分 - 负信号减分
        score = 0.5 + (pos_count * 0.1) - (neg_count * 0.15)
        return max(0.0, min(1.0, score))

    def _assess_cohesion(self, founder_vals: List[str], style: str, conflict_res: str) -> float:
        """团队凝聚潜力：风格互补性"""
        # 启发式：若候选人强调"协作"、"沟通"，则凝聚潜力高
        cohesion_keywords = ['协作', '沟通', '团队', '包容', '倾听', '合作']
        text = (style + " " + conflict_res).lower()
        matches = sum(1 for k in cohesion_keywords if k in text)
        return min(matches / 3, 1.0)

    def _generate_analysis(self, val_align, rep, coh, flag):
        parts = []
        if val_align > 0.7:
            parts.append("价值观高度一致")
        elif val_align < 0.4:
            parts.append("价值观存在显著差异")
        else:
            parts.append("价值观部分匹配")
        if rep > 0.7:
            parts.append("过往声誉良好")
        elif rep < 0.4:
            parts.append("声誉记录需关注")
        if coh > 0.6:
            parts.append("具备团队凝聚潜力")
        return "，".join(parts) + f"。总体判断：{flag}"


class SimonTotemAdapter:
    """将满意解算法包装为司马贺图腾评估器"""
    def __init__(self):
        from .simon_agent import HerbertSimonAgent
        self.engine = HerbertSimonAgent()

    def evaluate(self, scenario: Dict, candidate: Dict) -> Dict:
        # 单候选人评估模式（在满意解基础上评分）
        constraints = self.engine._analyze_constraints(scenario)
        thresholds = self.engine._set_thresholds(constraints, 'moderate')
        result = self.engine._evaluate(candidate, constraints, thresholds)
        # 转换为图腾评分格式
        score = 0.9 if result['is_adequate'] else max(0.3, result['metrics']['soft_met'] / 5)
        return {
            'score': round(score, 2),
            'dimension': '理性匹配/满意解',
            'analysis': result['reason'],
            'recommendation': '可接受' if result['is_adequate'] else '需再评估',
            'constraint_details': result['metrics']
        }


class GuanZizaiAgent:
    """
    观自在(水)：直觉洞察与压力应对评估
    核心：将"直觉"量化为模式识别速度+非共识决策能力
    """
    def evaluate(self, founder_profile: Dict, candidate_profile: Dict) -> Dict:
        # 1. 直觉匹配（决策风格相似性）
        intuition_match = self._assess_decision_style_match(
            founder_profile.get('decision_style', 'analytical'),
            candidate_profile.get('decision_style', 'analytical')
        )
        # 2. 压力应对兼容性（压力下行为模式）
        stress_compatibility = self._assess_stress_compatibility(
            founder_profile.get('stress_response', 'steady'),
            candidate_profile.get('stress_response', 'steady')
        )
        # 3. 内心自由度（自主性，避免过度控制）
        autonomy_fit = self._assess_autonomy(
            founder_profile.get('management_style', 'hands_on'),
            candidate_profile.get('autonomy_need', 'medium')
        )
        # 综合（水为流动，重视兼容性而非绝对最优）
        overall = (intuition_match * 0.4 + stress_compatibility * 0.4 + autonomy_fit * 0.2)
        # 特别处理：若压力应对差异大，大幅降权（水火不容）
        if stress_compatibility < 0.3:
            overall *= 0.6
            note = "压力应对方式冲突，可能引发协作困难"
        else:
            note = "直觉层面兼容"
        return {
            'score': round(overall, 2),
            'dimension': '直觉洞察/压力应对',
            'analysis': note,
            'recommendation': '谨慎' if overall < 0.5 else '积极',
            'details': {
                'intuition_match': round(intuition_match, 2),
                'stress_compatibility': round(stress_compatibility, 2),
                'autonomy_fit': round(autonomy_fit, 2)
            }
        }

    def _assess_decision_style_match(self, founder_style: str, candidate_style: str) -> float:
        """决策风格匹配：直觉型vs分析型"""
        # 匹配矩阵：直觉-直觉(1.0), 分析-分析(0.9), 直觉-分析(0.5)
        if founder_style == candidate_style:
            return 0.9
        elif 'intuitive' in founder_style and 'analytical' in candidate_style:
            return 0.5  # 差异较大但可互补
        else:
            return 0.7

    def _assess_stress_compatibility(self, founder_resp: str, candidate_resp: str) -> float:
        """压力应对兼容性：平稳型vs急躁型"""
        # 关键：若候选人是"急躁型"而创始人是"平稳型"，兼容性低
        incompatible_pairs = [('steady', 'aggressive'), ('calm', 'irritable')]
        for f, c in incompatible_pairs:
            if f in founder_resp and c in candidate_resp:
                return 0.3
        return 0.8

    def _assess_autonomy(self, mgmt_style: str, autonomy_need: str) -> float:
        """自主性匹配：创始人管理风格 vs 候选人自主需求"""
        # 微观管理 vs 高自主需求 = 冲突
        if 'hands_on' in mgmt_style and 'high' in autonomy_need:
            return 0.4
        if 'hands_off' in mgmt_style and 'low' in autonomy_need:
            return 0.6  # 创始人放手但候选人需要指导，轻微错配
        return 0.9
