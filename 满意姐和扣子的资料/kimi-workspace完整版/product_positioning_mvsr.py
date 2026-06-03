#!/usr/bin/env python3
"""
product_positioning_mvsr.py - 产品定位与MVSR组织评估（B6/B7）
来源: 系统深度优化方案.docx - 第十四轮
功能: Egbertie产品定位战略 + 最小可行满意解组织评估
"""
import json
from typing import Dict, List, Tuple
from dataclasses import dataclass
import sys


@dataclass
class PositioningStrategy:
    """产品定位策略"""
    path_name: str
    score: float
    rationale: str
    risks: List[str]
    resource_requirements: Dict[str, float]


class ProductPositioningAssistant:
    """
    B6实现：Egbertie产品定位战略（A/B/C路径分析）
    """

    def __init__(self):
        self.positioning_matrix = {
            'path_a_premium': {
                'name': 'A路径：高端精品',
                'market_requirement': 'high_growth',
                'resource_need': {'capital': 0.8, 'talent': 0.9, 'time': 0.6},
                'time_window': 'long',
                'risk_profile': 'low_execution_high_market'
            },
            'path_b_mass': {
                'name': 'B路径：规模覆盖',
                'market_requirement': 'large_tam',
                'resource_need': {'capital': 0.9, 'talent': 0.6, 'time': 0.7},
                'time_window': 'medium',
                'risk_profile': 'high_competition'
            },
            'path_c_niche': {
                'name': 'C路径：垂直深耕',
                'market_requirement': 'specialized',
                'resource_need': {'capital': 0.4, 'talent': 0.8, 'time': 0.4},
                'time_window': 'short',
                'risk_profile': 'low_market_high_execution'
            }
        }

    def evaluate_positioning(self, market_space: Dict, resources: Dict,
                             time_window: str) -> Dict:
        scores = {}
        for path_id, path_def in self.positioning_matrix.items():
            score = self._calculate_path_fit(path_def, market_space, resources, time_window)
            scores[path_id] = PositioningStrategy(
                path_name=path_def['name'],
                score=score,
                rationale=self._generate_rationale(path_def, score),
                risks=self._identify_risks(path_def, market_space),
                resource_requirements=path_def['resource_need']
            )
        sorted_paths = sorted(scores.values(), key=lambda x: x.score, reverse=True)
        recommended = sorted_paths[0]
        return {
            'recommended_path': recommended.path_name,
            'confidence': 'HIGH' if recommended.score > 0.8 else 'MEDIUM',
            'all_paths': [
                {
                    'name': p.path_name,
                    'score': round(p.score * 100, 1),
                    'fit': '优秀' if p.score > 0.8 else '良好' if p.score > 0.6 else '一般'
                } for p in sorted_paths
            ],
            'implementation_roadmap': self._generate_roadmap(recommended),
            'pivot_triggers': self._define_pivot_triggers(sorted_paths[1])
        }

    def _calculate_path_fit(self, path_def: Dict, market: Dict,
                            resources: Dict, time_window: str) -> float:
        scores = []
        market_fit = 0.7
        if path_def['market_requirement'] == 'high_growth' and market.get('growth_rate', 0) > 0.3:
            market_fit = 1.0
        elif path_def['market_requirement'] == 'large_tam' and market.get('tam', 0) > 100:
            market_fit = 1.0
        elif path_def['market_requirement'] == 'specialized' and market.get('niche_depth', 0) > 0.7:
            market_fit = 1.0
        scores.append(market_fit)
        resource_fit = sum(
            min(resources.get(k, 0), v) for k, v in path_def['resource_need'].items()
        ) / sum(path_def['resource_need'].values())
        scores.append(resource_fit)
        time_fit = 1.0 if path_def['time_window'] == time_window else 0.7 if time_window == 'flexible' else 0.5
        scores.append(time_fit)
        return sum(scores) / len(scores)

    def _generate_rationale(self, path_def: Dict, score: float) -> str:
        if score > 0.8:
            return f"{path_def['name']}与当前条件高度匹配，建议全力投入"
        elif score > 0.6:
            return f"{path_def['name']}基本可行，但需关注资源配置"
        else:
            return f"{path_def['name']}存在较大缺口，建议调整前提条件或选择其他路径"

    def _identify_risks(self, path_def: Dict, market: Dict) -> List[str]:
        risks = []
        if path_def['risk_profile'] == 'high_competition':
            risks.append("规模市场竞争激烈，需准备充足营销预算")
        elif path_def['risk_profile'] == 'low_market_high_execution':
            risks.append("细分市场容量有限，必须做到技术绝对领先")
        return risks

    def _generate_roadmap(self, strategy: PositioningStrategy) -> List[str]:
        if 'A路径' in strategy.path_name:
            return ['建立技术壁垒', '获取标杆客户', '逐步溢价']
        elif 'B路径' in strategy.path_name:
            return ['快速渠道铺设', '标准化产品', '规模化获客']
        else:
            return ['深度场景验证', '专家背书', '垂直渗透']

    def _define_pivot_triggers(self, alternative: PositioningStrategy) -> List[str]:
        return [
            f"若3个月内产品市场 fit < 0.5，考虑转向{alternative.path_name}",
            "若竞品推出同质化产品，立即评估差异化深度",
            "若融资进度滞后，启动轻量版MVP验证"
        ]


class MVSREvaluator:
    """
    B7实现：最小可行满意解组织评估（MVSR）
    """

    def __init__(self):
        self.mvsr_principles = [
            {'id': 'MVSR-1', 'name': '决策权集中', 'description': '关键决策有明确负责人，非集体共识',
             'check': lambda team: team.get('decision_maker') is not None},
            {'id': 'MVSR-2', 'name': '信息流动快', 'description': '关键信息24小时内到达决策层',
             'check': lambda team: team.get('info_latency_hours', 48) < 24},
            {'id': 'MVSR-3', 'name': '反馈闭环短', 'description': '行动-反馈周期<2周',
             'check': lambda team: team.get('feedback_cycle_days', 30) < 14},
            {'id': 'MVSR-4', 'name': '容忍不完美', 'description': '接受80分方案快速迭代，非追求100分',
             'check': lambda team: team.get('perfectionism_score', 10) < 5},
            {'id': 'MVSR-5', 'name': '反脆弱结构', 'description': '关键岗位有备份，单点故障风险低',
             'check': lambda team: team.get('backup_ratio', 0) > 0.3},
            {'id': 'MVSR-6', 'name': '客户亲近度', 'description': '核心团队每周直接客户接触>4小时',
             'check': lambda team: team.get('customer_contact_hours', 0) > 4},
            {'id': 'MVSR-7', 'name': '资源冗余度', 'description': '关键资源（现金/人才）有20%缓冲',
             'check': lambda team: team.get('resource_buffer', 0) > 0.2},
            {'id': 'MVSR-8', 'name': '退出清晰', 'description': '合伙人退出机制已书面约定',
             'check': lambda team: team.get('exit_clause_signed', False)},
            {'id': 'MVSR-9', 'name': '目标满意化', 'description': '目标设定为"足够好"区间，非最大化',
             'check': lambda team: team.get('target_type') == 'satisficing'},
            {'id': 'MVSR-10', 'name': '学习机制', 'description': '每月有结构化复盘和改进动作',
             'check': lambda team: team.get('monthly_retrospective', False)}
        ]

    def assess_organization(self, team_structure: Dict) -> Dict:
        results = []
        passed = 0
        for principle in self.mvsr_principles:
            passed_check = principle['check'](team_structure)
            results.append({
                'id': principle['id'],
                'name': principle['name'],
                'passed': passed_check,
                'description': principle['description']
            })
            if passed_check:
                passed += 1
        compliance_rate = passed / len(self.mvsr_principles)
        return {
            'compliance_rate': round(compliance_rate * 100, 1),
            'grade': 'A' if compliance_rate > 0.9 else 'B' if compliance_rate > 0.8 else 'C' if compliance_rate > 0.6 else 'D',
            'details': results,
            'improvement_steps': self._generate_improvements(results),
            'satisficing_readiness': compliance_rate > 0.8
        }

    def _generate_improvements(self, results: List[Dict]) -> List[str]:
        failed = [r for r in results if not r['passed']]
        steps = []
        for f in failed[:3]:
            if f['id'] == 'MVSR-1':
                steps.append("明确指定各决策域的最终负责人（建议本周完成）")
            elif f['id'] == 'MVSR-2':
                steps.append("建立每日站会机制，压缩信息传递层级")
            elif f['id'] == 'MVSR-3':
                steps.append("将月度计划拆分为双周迭代，建立快速反馈节奏")
            elif f['id'] == 'MVSR-8':
                steps.append("立即起草合伙人协议，明确Good/Bad Leaver条款")
        return steps


if __name__ == "__main__":
    ppa = ProductPositioningAssistant()
    result = ppa.evaluate_positioning(
        market_space={'growth_rate': 0.4, 'niche_depth': 0.8},
        resources={'capital': 0.5, 'talent': 0.9, 'time': 0.4},
        time_window='short'
    )
    assert 'recommended_path' in result
    assert len(result['all_paths']) == 3
    print(f"✓ 产品定位: 推荐{result['recommended_path']}，置信度{result['confidence']}")

    mvsr = MVSREvaluator()
    team = {
        'decision_maker': 'CEO',
        'info_latency_hours': 12,
        'feedback_cycle_days': 7,
        'perfectionism_score': 3,
        'backup_ratio': 0.4,
        'customer_contact_hours': 6,
        'resource_buffer': 0.25,
        'exit_clause_signed': True,
        'target_type': 'satisficing',
        'monthly_retrospective': True
    }
    assessment = mvsr.assess_organization(team)
    print(f"✓ MVSR评估: 合规度{assessment['compliance_rate']}%，等级{assessment['grade']}")
    assert assessment['compliance_rate'] > 80

    print("\n✓ 产品定位与MVSR系统验证通过")
    sys.exit(0)
