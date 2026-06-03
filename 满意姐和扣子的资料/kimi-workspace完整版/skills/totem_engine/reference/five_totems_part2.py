"""
外援代码: 五图腾Agent量化方案 (续)
来源: external_assistance_request_v1.0.md
状态: 保持原样，未经修改

包含:
- ConfuciusAgent: 孔子(木) - 五常伦理评估
- HuiNengAgent: 慧能(火) - 顿悟创新评估
- ConflictResolver: 基于五行的冲突消解
"""
from typing import Dict, List, Any


class ConfuciusAgent:
    """
    孔子(木)：仁义礼智信五维伦理评估
    将儒家五常转化为合伙人伦理审查清单
    """
    def evaluate(self, founder_values: List[str], candidate_profile: Dict) -> Dict:
        # 五常评估
        benevolence = self._assess_benevolence(candidate_profile)      # 仁：利他、关怀
        righteousness = self._assess_righteousness(candidate_profile, founder_values)  # 义：公平、正义
        propriety = self._assess_propriety(candidate_profile)          # 礼：规矩、礼仪
        wisdom = self._assess_wisdom(candidate_profile)                # 智：智慧、判断
        trust = self._assess_trustworthiness(candidate_profile)        # 信：信用、可靠
        # 加权综合（义在合伙中权重更高，涉及股权分配）
        weights = {
            'benevolence': 0.15,
            'righteousness': 0.3,
            'propriety': 0.15,
            'wisdom': 0.2,
            'trust': 0.2
        }
        scores = {
            'benevolence': benevolence,
            'righteousness': righteousness,
            'propriety': propriety,
            'wisdom': wisdom,
            'trust': trust
        }
        overall = sum(scores[k] * w for k, w in weights.items())
        # 伦理红线：信和义不可妥协
        if trust < 0.4 or righteousness < 0.4:
            overall *= 0.5
            flag = "伦理风险"
        elif overall > 0.7:
            flag = "积极"
        elif overall > 0.5:
            flag = "需深入沟通"
        else:
            flag = "谨慎"
        return {
            'score': round(overall, 2),
            'dimension': '伦理评估/五常',
            'analysis': f"仁{round(benevolence,1)}/义{round(righteousness,1)}/礼{round(propriety,1)}/智{round(wisdom,1)}/信{round(trust,1)}",
            'recommendation': flag,
            'details': {
                'benevolence': round(benevolence, 2),
                'righteousness': round(righteousness, 2),
                'propriety': round(propriety, 2),
                'wisdom': round(wisdom, 2),
                'trust': round(trust, 2)
            }
        }

    def _assess_benevolence(self, profile: Dict) -> float:
        """仁：利他倾向评估"""
        text = profile.get('values_expression', '') + profile.get('track_record', '')
        altruistic_terms = ['分享', '共赢', '帮助他人', '社会价值', '团队成长']
        return min(sum(1 for t in altruistic_terms if t in text) / 2, 1.0)

    def _assess_righteousness(self, profile: Dict, founder_values: List[str]) -> float:
        """义：公平正义，特别是在股权和利益分配上"""
        # 检查是否强调"快速变现"vs"长期价值"
        if '快速变现' in profile.get('values_expression', ''):
            if '长期主义' in founder_values:
                return 0.3  # 价值观冲突
        if '股权敏感' in profile.get('values_expression', ''):
            return 0.5  # 需要关注
        return 0.7

    def _assess_propriety(self, profile: Dict) -> float:
        """礼：遵守规则、尊重流程"""
        text = profile.get('collaboration_style', '')
        rule_terms = ['规范', '流程', '尊重', '边界', '职业']
        return min(sum(1 for t in rule_terms if t in text) / 2, 1.0)

    def _assess_wisdom(self, profile: Dict) -> float:
        """智：判断力、学习力"""
        exp_years = profile.get('experience', '0年')
        try:
            years = int(exp_years.split('年')[0])
        except:
            years = 5
        # 经验转化为智慧评分（饱和函数）
        return min(years / 10, 1.0)

    def _assess_trustworthiness(self, profile: Dict) -> float:
        """信：信用记录"""
        # 基于过往承诺兑现记录（简化版）
        record = profile.get('track_record', '')
        red_flags = ['失信', '纠纷', '诉讼', '撕毁协议']
        for flag in red_flags:
            if flag in record:
                return 0.3
        return 0.8


class HuiNengAgent:
    """
    慧能(火)：顿悟能力与突破创新评估
    核心：将"顿悟"量化为模式突破能力+逆境转化力
    """
    def evaluate(self, founder_profile: Dict, candidate_profile: Dict) -> Dict:
        # 1. 创新互补性（与创始人技术背景互补）
        innovation_comp = self._assess_innovation_complement(
            founder_profile.get('background', 'tech'),
            candidate_profile.get('innovation_ability', '')
        )
        # 2. 顿悟潜力（突破常规思维的能力）
        insight_potential = self._assess_insight(
            candidate_profile.get('problem_solving_record', ''),
            candidate_profile.get('breakthrough_cases', [])
        )
        # 3. 压力转化（将逆境转化为突破的能力）
        stress_conversion = self._assess_stress_conversion(
            candidate_profile.get('failure_experience', ''),
            candidate_profile.get('resilience_indicators', [])
        )
        # 火性评分：重视爆发力而非持续性
        overall = (innovation_comp * 0.4 + insight_potential * 0.3 + stress_conversion * 0.3)
        # 火的特性：若创新互补性极高，其他可妥协
        if innovation_comp > 0.9:
            overall = min(overall * 1.1, 1.0)  # bonus
            note = "创新互补性极强，可弥补其他短板（火之突破）"
        else:
            note = "创新维度评估"
        return {
            'score': round(overall, 2),
            'dimension': '创新突破/顿悟',
            'analysis': note,
            'recommendation': '积极' if overall > 0.7 else '可接受',
            'details': {
                'innovation_complement': round(innovation_comp, 2),
                'insight_potential': round(insight_potential, 2),
                'stress_conversion': round(stress_conversion, 2)
            }
        }

    def _assess_innovation_complement(self, founder_bg: str, cand_ability: str) -> float:
        """创新互补性：创始人技术+候选人商业/模式创新 = 高互补"""
        if 'tech' in founder_bg and ('模式创新' in cand_ability or 'business' in cand_ability):
            return 0.9
        if 'tech' in founder_bg and 'tech' in cand_ability:
            return 0.5  # 同质，创新互补性低
        return 0.7

    def _assess_insight(self, record: str, cases: List[str]) -> float:
        """顿悟潜力：基于过往突破案例"""
        # 关键词：颠覆、突破、 unconventional solution
        indicators = ['颠覆', '突破', '重新定义', '首创', 'unique', 'novel']
        text = record + " ".join(cases)
        count = sum(1 for i in indicators if i in text)
        return min(count / 2, 1.0)

    def _assess_stress_conversion(self, failures: str, resilience: List[str]) -> float:
        """压力转化：从失败中反弹的能力"""
        # 有失败经历且提及"学到"、"成长" = 高转化力
        if not failures:
            return 0.5  # 无失败记录，未知
        growth_terms = ['学到', '成长', '反思', '变得更', 'lesson', 'growth']
        has_growth = any(t in failures for t in growth_terms)
        return 0.8 if has_growth else 0.4


class ConflictResolver:
    """
    五图腾冲突消解器：基于五行相生相克关系
    优先级：土(刘禹锡) > 金(司马贺) > 水(观自在) > 木(孔子) > 火(慧能)
    但引入相克关系：当两图腾冲突时，检查克制关系决定权重
    """
    def __init__(self):
        self.dominance = {
            'water': 'fire',   # 观自在克慧能
            'fire': 'metal',   # 慧能克司马贺
            'metal': 'wood',   # 司马贺克孔子
            'wood': 'earth',   # 孔子克刘禹锡
            'earth': 'water'   # 刘禹锡克观自在
        }
        self.element_map = {
            'liuyuxi': 'earth',
            'simon': 'metal',
            'guanzizai': 'water',
            'confucius': 'wood',
            'huineng': 'fire'
        }

    def resolve(self, evaluations: Dict[str, Dict], scenario: Dict) -> Dict:
        """
        输入：五个图腾的评估结果
        输出：综合共识与冲突消解建议
        """
        scores = {k: v['score'] for k, v in evaluations.items()}
        # 1. 检测严重冲突（评分差异>0.5）
        conflicts = []
        for t1 in evaluations:
            for t2 in evaluations:
                if t1 != t2 and abs(scores[t1] - scores[t2]) > 0.5:
                    conflicts.append({
                        'between': (t1, t2),
                        'severity': abs(scores[t1] - scores[t2]),
                        'type': 'major_disagreement'
                    })
        # 2. 基于五行的冲突消解
        resolution_strategy = self._apply_dominance_rules(conflicts, evaluations)
        # 3. 加权综合评分
        final_score = self._calculate_consensus(scores, resolution_strategy)
        # 4. 生成建议
        recommendation = self._formulate_advice(evaluations, conflicts, resolution_strategy)
        return {
            'consensus_score': round(final_score, 2),
            'conflicts_detected': len(conflicts),
            'conflict_details': conflicts,
            'resolution_strategy': resolution_strategy,
            'recommendation': recommendation,
            'individual_scores': scores
        }

    def _apply_dominance_rules(self, conflicts: List[Dict], evaluations: Dict) -> Dict:
        """应用五行相克规则调整权重"""
        adjustments = {}
        for conflict in conflicts:
            t1, t2 = conflict['between']
            e1 = self.element_map.get(t1)
            e2 = self.element_map.get(t2)
            # 检查克制关系
            if self.dominance.get(e1) == e2:
                # t1 克 t2，t1权重提升
                adjustments[t1] = adjustments.get(t1, 1.0) * 1.2
                adjustments[t2] = adjustments.get(t2, 1.0) * 0.8
            elif self.dominance.get(e2) == e1:
                # t2 克 t1，t2权重提升
                adjustments[t2] = adjustments.get(t2, 1.0) * 1.2
                adjustments[t1] = adjustments.get(t1, 1.0) * 0.8
        return adjustments

    def _calculate_consensus(self, scores: Dict[str, float], adjustments: Dict[str, float]) -> float:
        """计算综合评分"""
        # 基础权重
        base_weights = {
            'liuyuxi': 0.2,
            'simon': 0.25,
            'guanzizai': 0.2,
            'confucius': 0.2,
            'huineng': 0.15
        }
        # 应用调整
        adjusted_weights = {}
        for k, w in base_weights.items():
            adjusted_weights[k] = w * adjustments.get(k, 1.0)
        # 归一化
        total = sum(adjusted_weights.values())
        normalized = {k: v/total for k, v in adjusted_weights.items()}
        # 加权计算
        return sum(scores[k] * normalized[k] for k in scores)

    def _formulate_advice(self, evaluations: Dict, conflicts: List, strategy: Dict) -> str:
        """生成冲突消解建议"""
        if not conflicts:
            return "五图腾共识一致，无冲突"
        parts = [f"检测到{len(conflicts)}处冲突，已按五行相克规则消解"]
        for c in conflicts[:2]:  # 最多显示2个
            t1, t2 = c['between']
            parts.append(f"- {t1} vs {t2}: 差异{c['severity']:.2f}")
        if strategy:
            parts.append(f"权重调整: {strategy}")
        return "；".join(parts)
