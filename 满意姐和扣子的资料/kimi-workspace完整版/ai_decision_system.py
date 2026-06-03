#!/usr/bin/env python3
# ai_decision_system.py - AI决策系统
# 来源: 文件3 - AI决策系统设计.docx
# 功能: AI辅助合伙人匹配决策系统
# 创建时间: 2026-04-04
# 版本: 1.0

import json
import sys
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

sys.path.insert(0, '/root/.openclaw/workspace')
from defense_base_components import BaseComponent, MetricsCollector

@dataclass
class DecisionContext:
    """决策上下文"""
    founder_traits: Dict
    company_stage: str
    industry: str
    funding_status: str
    team_gaps: List[str]
    priorities: List[str]

@dataclass
class Candidate:
    """合伙人候选人"""
    id: str
    name: str
    background: str
    expertise: List[str]
    experience_years: int
    previous_exits: int
    network_score: float
    culture_fit: float

class AIDecisionSystem(BaseComponent):
    """
    AI决策系统
    辅助合伙人匹配的AI决策支持
    """
    
    def __init__(self):
        super().__init__('ai_decision')
        self.metrics = MetricsCollector('ai_decision')
        
        # 决策权重配置
        self.weights = {
            'expertise_match': 0.25,
            'experience': 0.20,
            'network': 0.15,
            'culture_fit': 0.20,
            'stage_fit': 0.20
        }
    
    def evaluate_candidate(self, 
                          candidate: Candidate,
                          context: DecisionContext) -> Dict:
        """
        评估候选人匹配度
        """
        scores = {}
        
        # 专业匹配度
        scores['expertise_match'] = self._score_expertise_match(
            candidate.expertise, context.team_gaps
        )
        
        # 经验评分
        scores['experience'] = min(candidate.experience_years / 15, 1.0)
        
        # 人脉网络
        scores['network'] = candidate.network_score
        
        # 文化契合
        scores['culture_fit'] = candidate.culture_fit
        
        # 阶段契合
        scores['stage_fit'] = self._score_stage_fit(
            candidate.previous_exits, context.company_stage
        )
        
        # 加权总分
        total_score = sum(
            scores[k] * self.weights[k] for k in self.weights.keys()
        )
        
        self.metrics.record(
            action='candidate_evaluated',
            candidate_id=candidate.id,
            score=total_score
        )
        
        return {
            'candidate_id': candidate.id,
            'candidate_name': candidate.name,
            'total_score': round(total_score, 3),
            'dimension_scores': {k: round(v, 3) for k, v in scores.items()},
            'recommendation': self._generate_recommendation(total_score, scores)
        }
    
    def _score_expertise_match(self, 
                              expertise: List[str],
                              gaps: List[str]) -> float:
        """计算专业匹配度"""
        if not gaps:
            return 0.5
        
        matches = sum(1 for e in expertise if any(g in e or e in g for g in gaps))
        return min(matches / len(gaps), 1.0)
    
    def _score_stage_fit(self, 
                        previous_exits: int,
                        company_stage: str) -> float:
        """计算阶段契合度"""
        # 早期公司更看重创业经验
        if company_stage in ['天使轮', 'Pre-A轮']:
            return min(previous_exits * 0.3 + 0.4, 1.0)
        else:
            return min(previous_exits * 0.2 + 0.6, 1.0)
    
    def _generate_recommendation(self, 
                                total_score: float,
                                scores: Dict) -> str:
        """生成推荐建议"""
        if total_score >= 0.85:
            return "强烈推荐 - 各方面匹配度优秀"
        elif total_score >= 0.70:
            return "推荐 - 主要维度匹配良好"
        elif total_score >= 0.55:
            return "可考虑 - 存在部分匹配，需进一步评估"
        else:
            return "不推荐 - 匹配度较低"
    
    def rank_candidates(self,
                       candidates: List[Candidate],
                       context: DecisionContext) -> List[Tuple[Candidate, float]]:
        """
        对候选人进行排序
        """
        rankings = []
        
        for candidate in candidates:
            result = self.evaluate_candidate(candidate, context)
            rankings.append((candidate, result['total_score']))
        
        # 按分数排序
        rankings.sort(key=lambda x: x[1], reverse=True)
        
        return rankings
    
    def generate_decision_report(self,
                                top_candidate: Candidate,
                                context: DecisionContext) -> str:
        """
        生成决策报告
        """
        result = self.evaluate_candidate(top_candidate, context)
        
        report = f"""
# 合伙人匹配决策报告

## 候选人信息
- 姓名: {top_candidate.name}
- 背景: {top_candidate.background}
- 专业领域: {', '.join(top_candidate.expertise)}

## 匹配评估
- 综合得分: {result['total_score']:.1%}
- 推荐结论: {result['recommendation']}

## 维度评分
"""
        for dim, score in result['dimension_scores'].items():
            report += f"- {dim}: {score:.1%}\n"
        
        report += f"""
## 关键洞察
基于AI分析，该候选人在以下维度表现突出：
{self._highlight_strengths(result['dimension_scores'])}

## 建议行动
{self._suggest_actions(result)}

---
生成时间: {datetime.now().isoformat()}
"""
        return report
    
    def _highlight_strengths(self, scores: Dict) -> str:
        """突出优势维度"""
        strengths = [k for k, v in scores.items() if v >= 0.8]
        if strengths:
            return "- " + "\n- ".join(strengths)
        return "- 各维度表现均衡"
    
    def _suggest_actions(self, result: Dict) -> str:
        """建议行动"""
        score = result['total_score']
        if score >= 0.85:
            return "1. 尽快安排深度面谈\n2. 准备详细的合作方案\n3. 进行背景调查"
        elif score >= 0.70:
            return "1. 安排初步接触\n2. 了解其合作意向\n3. 评估文化契合度"
        else:
            return "1. 继续寻找其他候选人\n2. 可适当降低部分要求"

# 便捷函数
def evaluate_partner_match(candidate_data: Dict, context_data: Dict) -> Dict:
    """快速评估合伙人匹配"""
    system = AIDecisionSystem()
    
    candidate = Candidate(
        id=candidate_data.get('id', ''),
        name=candidate_data.get('name', ''),
        background=candidate_data.get('background', ''),
        expertise=candidate_data.get('expertise', []),
        experience_years=candidate_data.get('experience_years', 0),
        previous_exits=candidate_data.get('previous_exits', 0),
        network_score=candidate_data.get('network_score', 0.5),
        culture_fit=candidate_data.get('culture_fit', 0.5)
    )
    
    context = DecisionContext(
        founder_traits=context_data.get('founder_traits', {}),
        company_stage=context_data.get('company_stage', ''),
        industry=context_data.get('industry', ''),
        funding_status=context_data.get('funding_status', ''),
        team_gaps=context_data.get('team_gaps', []),
        priorities=context_data.get('priorities', [])
    )
    
    return system.evaluate_candidate(candidate, context)

if __name__ == '__main__':
    # 测试
    candidate = {
        'id': 'C001',
        'name': '张三',
        'background': '前华为芯片部门总监',
        'expertise': ['芯片设计', '团队管理', '供应链'],
        'experience_years': 15,
        'previous_exits': 1,
        'network_score': 0.85,
        'culture_fit': 0.75
    }
    
    context = {
        'company_stage': 'Pre-A轮',
        'industry': '半导体',
        'team_gaps': ['芯片设计', '供应链管理'],
        'priorities': ['技术', '资源']
    }
    
    result = evaluate_partner_match(candidate, context)
    print(json.dumps(result, ensure_ascii=False, indent=2))
