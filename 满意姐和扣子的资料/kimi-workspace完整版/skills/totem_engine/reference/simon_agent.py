"""
外援代码: 司马贺满意解决策Agent
来源: external_assistance_request_v1.0.md
状态: 保持原样，未经修改
"""
from typing import Dict, List, Any
import json


class HerbertSimonAgent:
    """
    司马贺满意解决策Agent完整实现
    特性：可解释、约束驱动、非最优化
    """
    def __init__(self):
        self.search_history = []
        self.domain_rules = self._load_domain_rules()

    def _load_domain_rules(self) -> dict:
        """领域知识：合伙人匹配领域的约束检查规则"""
        return {
            '全职投入': lambda c: c.get('availability') == 'full_time' or '全职' in str(c),
            '有产业资源': lambda c: c.get('network') in ['强', 'high'] or c.get('industry_exp', 0) > 5,
            '接受较低估值': lambda c: c.get('equity_expectation') in ['低', 'low', '中', 'medium'],
            '创业经验': lambda c: c.get('startup_exp', False) or '创业' in str(c.get('track_record', '')),
            '技术背景': lambda c: c.get('background') == 'tech' or '技术' in str(c)
        }

    def decide(self, scenario: Dict[str, Any]) -> Dict:
        """主决策入口"""
        self.search_history = []  # 重置历史
        # 1. 约束分析
        constraints = self._analyze_constraints(scenario)
        # 2. 阈值设定
        thresholds = self._set_thresholds(constraints, scenario.get('risk_preference', 'moderate'))
        # 3. 满意解搜索（带停止规则）
        candidates = scenario.get('candidates', [])
        satisfactory = []
        first_satisfactory = None
        for i, candidate in enumerate(candidates):
            eval_result = self._evaluate(candidate, constraints, thresholds)
            record = {
                'name': candidate.get('name', f'Candidate_{i}'),
                'index': i,
                'adequacy': eval_result['is_adequate'],
                'metrics': eval_result['metrics'],
                'reason': eval_result['reason']
            }
            self.search_history.append(record)
            if eval_result['is_adequate']:
                satisfactory.append(candidate)
                if first_satisfactory is None:
                    first_satisfactory = {
                        'candidate': candidate,
                        'index': i,
                        'reason': f"首个满足阈值的候选（位置{i}）"
                    }
        # 4. 生成建议
        recommendation = self._formulate_recommendation(
            satisfactory, first_satisfactory, candidates, constraints
        )
        return {
            'constraints_analysis': constraints,
            'satisficing_threshold': thresholds,
            'candidates_evaluation': self.search_history,
            'recommendation': recommendation,
            'process_metadata': {
                'search_depth': len(candidates),
                'stop_point': first_satisfactory['index'] if first_satisfactory else None,
                'satisfactory_count': len(satisfactory),
                'is_satisficing': True  # 标记为满意解模式，非最优化
            }
        }

    def _analyze_constraints(self, scenario: Dict) -> Dict:
        """约束识别与分类"""
        raw = scenario.get('constraints', [])
        profile = scenario.get('founder_profile', '')
        hard, soft, trade_off = [], [], []
        # 分类逻辑
        hard_indicators = ['必须', '全职', '法定', 'exclusive', '必须']
        soft_indicators = ['希望', '最好', 'prefer', ' ideally']
        for c in raw:
            if any(h in c for h in hard_indicators):
                hard.append({'type': 'hard', 'desc': c, 'mandatory': True})
            elif any(s in c for s in soft_indicators):
                soft.append({'type': 'soft', 'desc': c, 'weight': 1.5})
            else:
                trade_off.append({'type': 'trade_off', 'desc': c, 'negotiable': True})
        # 从画像推断隐性约束
        if '首次' in profile or 'first' in profile:
            soft.append({'type': 'soft', 'desc': '有指导经验', 'source': 'inferred', 'weight': 1.0})
        return {
            'hard_constraints': hard,
            'soft_constraints': soft,
            'trade_off_constraints': trade_off,
            'total_pressure': len(hard) * 2 + len(soft) * 1 + len(trade_off) * 0.5
        }

    def _set_thresholds(self, constraints: Dict, risk_pref: str) -> Dict:
        """基于约束压力和风险偏好设定阈值"""
        pressure = constraints['total_pressure']
        # 基础阈值
        base = {
            'hard_compliance': 1.0,  # 硬约束必须100%
            'soft_compliance': max(0.5, 1.0 - pressure * 0.1),  # 压力越大，标准越低
            'trade_off_tolerance': 0.4
        }
        # 风险偏好调整
        adjustments = {
            'conservative': {'soft_compliance': 0.2, 'trade_off_tolerance': -0.1},
            'moderate': {'soft_compliance': 0.0, 'trade_off_tolerance': 0.0},
            'aggressive': {'soft_compliance': -0.2, 'trade_off_tolerance': 0.2}
        }
        adj = adjustments.get(risk_pref, adjustments['moderate'])
        for k in base:
            base[k] += adj.get(k, 0)
            base[k] = max(0.0, min(1.0, base[k]))
        return {
            'threshold_values': base,
            'rationale': f"约束压力={pressure:.1f}, 风险偏好={risk_pref}",
            'interpretation': {
                'hard': "必须完全满足",
                'soft': f"至少满足{base['soft_compliance']:.0%}",
                'trade_off': f"允许{base['trade_off_tolerance']:.0%}的权衡偏离"
            }
        }

    def _evaluate(self, candidate: Dict, constraints: Dict, thresholds: Dict) -> Dict:
        """评估单个候选人的充分性"""
        metrics = {
            'hard_pass': True,
            'soft_met': 0,
            'soft_total': 0,
            'trade_off_deviation': 0
        }
        reasons = []
        # 硬约束检查（一票否决）
        for hc in constraints['hard_constraints']:
            check_func = self.domain_rules.get(hc['desc'], lambda c: True)
            if not check_func(candidate):
                metrics['hard_pass'] = False
                reasons.append(f"不满足硬约束: {hc['desc']}")
        if not metrics['hard_pass']:
            return {'is_adequate': False, 'metrics': metrics, 'reason': '；'.join(reasons)}
        # 软约束检查
        soft_total = len(constraints['soft_constraints'])
        soft_met = 0
        for sc in constraints['soft_constraints']:
            check_func = self.domain_rules.get(sc['desc'], lambda c: True)
            if check_func(candidate):
                soft_met += 1
        metrics['soft_met'] = soft_met
        metrics['soft_total'] = soft_total
        soft_ratio = soft_met / soft_total if soft_total > 0 else 1.0
        # 可权衡约束检查（允许偏离，但记录）
        trade_off_deviation = 0
        for tc in constraints['trade_off_constraints']:
            check_func = self.domain_rules.get(tc['desc'], lambda c: True)
            if not check_func(candidate):
                # 检查是否有补偿特性
                has_alt = self._has_alternative_strength(candidate, tc['desc'])
                if not has_alt:
                    trade_off_deviation += 0.3
        metrics['trade_off_deviation'] = trade_off_deviation
        # 满意解判定
        is_adequate = (
            soft_ratio >= thresholds['threshold_values']['soft_compliance']
            and trade_off_deviation <= thresholds['threshold_values']['trade_off_tolerance']
        )
        # 构建解释
        if soft_total > 0:
            reasons.append(f"软约束满足{soft_met}/{soft_total} ({soft_ratio:.0%})")
        if trade_off_deviation > 0:
            reasons.append(f"权衡偏离度: {trade_off_deviation:.1f}")
        return {
            'is_adequate': is_adequate,
            'metrics': metrics,
            'reason': '；'.join(reasons) if reasons else "全面满足约束"
        }

    def _has_alternative_strength(self, candidate: Dict, missing_constraint: str) -> bool:
        """检查候选人在某方面不足时是否有其他补偿优势"""
        # 简单启发规则：如缺少"产业资源"，但有"资金"或"技术专利"补偿
        alt_map = {
            '有产业资源': ['funding_access', 'patents', 'technical_depth'],
            '接受较低估值': ['exceptional_experience', 'strategic_value']
        }
        alternatives = alt_map.get(missing_constraint, [])
        return any(candidate.get(attr) for attr in alternatives)

    def _formulate_recommendation(self, satisfactory: List, first_sat: Dict,
                                   all_candidates: List, constraints: Dict) -> Dict:
        """生成最终建议（含停止规则解释）"""
        if not satisfactory:
            return {
                'action': 'expand_search',
                'stop_at': None,
                'rationale': '无满意解，建议放宽约束或扩大搜索范围',
                'fallback': '考虑降低软约束阈值10-20%'
            }
        if len(satisfactory) == 1:
            chosen = satisfactory[0]
            return {
                'action': 'accept',
                'stop_at': chosen.get('name'),
                'rationale': '唯一满意解，符合停止规则（首个即停）',
                'note': '无需继续评估后续候选（满意解特性）'
            }
        # 多个满意解：在满意集内简单比较（非全搜索空间优化）
        # 选择策略：首个满足 vs 满意集中较优
        if len(satisfactory) <= 3:
            # 满意集较小，内部选最优
            best = max(satisfactory, key=lambda c: c.get('composite_score', 0))
            return {
                'action': 'select_best_in_satisfactory',
                'stop_at': best.get('name'),
                'rationale': f"在{len(satisfactory)}个满意解中选择指标较优者，但仍非全局最优搜索",
                'satisfactory_set': [c.get('name') for c in satisfactory]
            }
        else:
            # 满意解过多，说明阈值过低，建议收紧
            return {
                'action': 'reevaluate_thresholds',
                'stop_at': first_sat['candidate'].get('name') if first_sat else None,
                'rationale': f"满意解过多({len(satisfactory)})，建议提高阈值以提升决策质量",
                'satisfactory_set': [c.get('name') for c in satisfactory[:5]]
            }
