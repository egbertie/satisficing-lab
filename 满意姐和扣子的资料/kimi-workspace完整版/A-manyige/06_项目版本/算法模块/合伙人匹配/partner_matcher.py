#!/usr/bin/env python3
# partner_matcher.py - 合伙人匹配引擎
# 来源: 文件10 - Kimi_Claw技术方案_3_.docx
# 功能: 整合四大理论的合伙人匹配引擎
# 创建时间: 2026-04-04
# 版本: 1.0

import sys
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

sys.path.insert(0, '/root/.openclaw/workspace')
from defense_base_components import BaseComponent, MetricsCollector
from satisficing_matcher import SatisficingMatcher
from prospect_theory_scorer import ProspectTheoryScorer
from confucian_ethics_evaluator import ConfucianEthicsEvaluator, ConfucianDimension, EthicsEvidence
from intuition_calibrator import IntuitionCalibrator, IntuitionSignal

@dataclass
class PartnerCandidate:
    """合伙人候选人"""
    id: str
    name: str
    attributes: Dict[str, float]  # 各维度得分
    risk_factors: Dict[str, float]  # 风险因子
    ethics_evidence: Dict[str, List[Dict]]  # 伦理证据
    intuition_signals: List[Dict]  # 直觉信号

class PartnerMatcher(BaseComponent):
    """
    合伙人匹配引擎
    
    整合四大理论的综合匹配系统：
    1. 西蒙满意解理论 - 寻找"足够好"的合伙人
    2. 前景理论 - 考虑损失厌恶的风险评估
    3. 儒商五维 - 伦理道德评估
    4. 观自在 - 直觉感知力校准
    """
    
    def __init__(self):
        super().__init__('partner_matcher')
        self.metrics = MetricsCollector('partner_matching')
        
        # 初始化各理论模块
        self.satisficing = SatisficingMatcher()
        self.prospect = ProspectTheoryScorer()
        self.ethics = ConfucianEthicsEvaluator()
        self.intuition = IntuitionCalibrator()
        
        # 权重配置
        self.weights = {
            'satisficing': 0.30,
            'prospect': 0.20,
            'ethics': 0.25,
            'intuition': 0.15,
            'analytical': 0.10
        }
    
    def comprehensive_match(self, candidate: PartnerCandidate) -> Dict:
        """
        综合匹配评估
        
        从四个维度全面评估候选人
        """
        results = {}
        
        # 1. 满意解评估
        print("  📊 满意解评估...")
        results['satisficing'] = self.satisficing.evaluate_candidate(
            candidate.attributes
        )
        
        # 2. 前景理论评估
        print("  📊 前景理论评估...")
        results['prospect'] = self.prospect.apply_to_partner_matching(
            candidate.attributes,
            candidate.risk_factors
        )
        
        # 3. 儒商伦理评估
        print("  📊 儒商伦理评估...")
        # 转换伦理证据格式
        ethics_evidence = {}
        for dim_name, evidence_list in candidate.ethics_evidence.items():
            try:
                dim = ConfucianDimension[dim_name]
                ethics_evidence[dim] = [
                    EthicsEvidence(
                        dimension=dim,
                        evidence_type=e['type'],
                        description=e['desc'],
                        confidence=e['confidence']
                    )
                    for e in evidence_list
                ]
            except:
                pass
        
        results['ethics'] = self.ethics.comprehensive_evaluate(ethics_evidence)
        
        # 4. 直觉校准
        print("  📊 直觉信号校准...")
        intuition_signals = [
            IntuitionSignal(
                source=s['source'],
                type=s['type'],
                intensity=s['intensity'],
                confidence=s['confidence']
            )
            for s in candidate.intuition_signals
        ]
        results['intuition'] = self.intuition.calibrate_confidence(intuition_signals)
        
        # 5. 计算综合得分
        composite_score = self._calculate_composite_score(results)
        
        # 6. 生成综合建议
        recommendation = self._generate_comprehensive_recommendation(results, composite_score)
        
        self.metrics.record(
            action='candidate_matched',
            candidate_id=candidate.id,
            composite_score=composite_score
        )
        
        return {
            'candidate_id': candidate.id,
            'candidate_name': candidate.name,
            'composite_score': composite_score,
            'dimension_scores': {
                'satisficing': results['satisficing'].get('satisfaction_rate', 0),
                'prospect': results['prospect'].get('total_score', 0),
                'ethics': results['ethics'].get('total_score', 0),
                'intuition': results['intuition'].get('calibrated_confidence', 0)
            },
            'detailed_results': results,
            'recommendation': recommendation,
            'decision': self._make_decision(results, composite_score)
        }
    
    def _calculate_composite_score(self, results: Dict) -> float:
        """计算综合得分"""
        scores = {
            'satisficing': results['satisficing'].get('satisfaction_rate', 0),
            'prospect': results['prospect'].get('total_score', 0) / 2 + 0.5,  # 归一化
            'ethics': results['ethics'].get('total_score', 0),
            'intuition': results['intuition'].get('calibrated_confidence', 0)
        }
        
        composite = sum(
            scores.get(k, 0) * self.weights[k] 
            for k in ['satisficing', 'prospect', 'ethics', 'intuition']
        )
        
        return composite
    
    def _generate_comprehensive_recommendation(self, results: Dict, score: float) -> str:
        """生成综合建议"""
        parts = []
        
        # 满意解方面
        if results['satisficing'].get('is_satisficing'):
            parts.append("满足基本能力要求")
        else:
            parts.append("部分能力维度未达标")
        
        # 伦理方面
        ethics_level = results['ethics'].get('ethics_level', '')
        if '君子' in ethics_level or '贤人' in ethics_level:
            parts.append("伦理素养优秀")
        
        # 直觉方面
        if results['intuition'].get('calibrated_confidence', 0) >= 0.7:
            parts.append("直觉信号良好")
        
        return "；".join(parts) if parts else "需进一步考察"
    
    def _make_decision(self, results: Dict, score: float) -> str:
        """做出决策建议"""
        # 必须满足满意解
        if not results['satisficing'].get('is_satisficing'):
            return "不推荐 - 未满足基本能力要求"
        
        # 伦理底线
        ethics_score = results['ethics'].get('total_score', 0)
        if ethics_score < 0.5:
            return "不推荐 - 伦理风险"
        
        # 综合判断
        if score >= 0.80:
            return "强烈推荐"
        elif score >= 0.65:
            return "推荐"
        elif score >= 0.50:
            return "可考虑"
        else:
            return "不推荐"
    
    def rank_candidates(self, candidates: List[PartnerCandidate]) -> List[Tuple[PartnerCandidate, float]]:
        """
        对候选池进行排序
        """
        rankings = []
        
        print(f"\n🔍 评估 {len(candidates)} 位候选人...")
        
        for i, candidate in enumerate(candidates, 1):
            print(f"\n[{i}/{len(candidates)}] 评估: {candidate.name}")
            result = self.comprehensive_match(candidate)
            rankings.append((candidate, result['composite_score'], result))
        
        # 按综合得分排序
        rankings.sort(key=lambda x: x[1], reverse=True)
        
        return rankings
    
    def generate_match_report(self, top_candidate: PartnerCandidate) -> str:
        """生成匹配报告"""
        result = self.comprehensive_match(top_candidate)
        
        report = f"""
# 合伙人匹配综合报告

## 候选人信息
- 姓名: {result['candidate_name']}
- ID: {result['candidate_id']}

## 综合评估
- **综合得分**: {result['composite_score']:.1%}
- **决策建议**: {result['decision']}
- **关键优势**: {result['recommendation']}

## 四维分析

### 1. 满意解评估 (西蒙理论)
- 满意率: {result['dimension_scores']['satisficing']:.1%}
- 判定: {'满足标准' if result['detailed_results']['satisficing'].get('is_satisficing') else '未达标'}

### 2. 前景评估 (卡尼曼理论)
- 前景得分: {result['dimension_scores']['prospect']:.3f}
- 评估: {result['detailed_results']['prospect'].get('assessment', 'N/A')}

### 3. 伦理评估 (儒商五维)
- 伦理等级: {result['detailed_results']['ethics'].get('ethics_level', 'N/A')}
- 综合得分: {result['dimension_scores']['ethics']:.1%}

### 4. 直觉校准 (观自在)
- 校准置信度: {result['dimension_scores']['intuition']:.1%}
- 可靠性: {result['detailed_results']['intuition'].get('reliability', 'N/A')}

---
*报告生成时间: 2026年*
*方法论: 满意解 × 前景理论 × 儒商伦理 × 观自在直觉*
"""
        return report

# 便捷函数
def match_partner(candidate_data: Dict) -> Dict:
    """快速匹配评估"""
    matcher = PartnerMatcher()
    
    candidate = PartnerCandidate(
        id=candidate_data.get('id', ''),
        name=candidate_data.get('name', ''),
        attributes=candidate_data.get('attributes', {}),
        risk_factors=candidate_data.get('risk_factors', {}),
        ethics_evidence=candidate_data.get('ethics_evidence', {}),
        intuition_signals=candidate_data.get('intuition_signals', [])
    )
    
    return matcher.comprehensive_match(candidate)

if __name__ == '__main__':
    # 测试
    candidate = {
        'id': 'C001',
        'name': '张三',
        'attributes': {
            'industry_experience': 0.75,
            'management_capability': 0.70,
            'resource_network': 0.65,
            'cultural_fit': 0.80,
            'commitment_level': 0.85
        },
        'risk_factors': {
            'industry_experience': 0.1,
            'management_capability': 0.15,
            'resource_network': 0.2,
            'cultural_fit': 0.1,
            'commitment_level': 0.1
        },
        'ethics_evidence': {
            'REN': [{'type': 'testimonial', 'desc': '关心团队', 'confidence': 0.8}],
            'YI': [{'type': 'record', 'desc': '决策公正', 'confidence': 0.9}],
            'LI': [{'type': 'observation', 'desc': '礼仪得体', 'confidence': 0.7}],
            'ZHI': [{'type': 'record', 'desc': '战略明智', 'confidence': 0.85}],
            'XIN': [{'type': 'record', 'desc': '履约良好', 'confidence': 0.9}]
        },
        'intuition_signals': [
            {'source': 'pattern', 'type': 'similarity', 'intensity': 0.8, 'confidence': 0.7}
        ]
    }
    
    result = match_partner(candidate)
    print(f"\n综合得分: {result['composite_score']:.1%}")
    print(f"决策建议: {result['decision']}")
