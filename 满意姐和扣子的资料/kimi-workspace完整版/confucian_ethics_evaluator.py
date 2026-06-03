#!/usr/bin/env python3
# confucian_ethics_evaluator.py - 儒商伦理评估器
# 来源: 文件10 - Kimi_Claw技术方案_3_.docx
# 功能: 基于儒商五维伦理的合伙人评估
# 创建时间: 2026-04-04
# 版本: 1.0

import sys
from typing import Dict, List
from dataclasses import dataclass
from enum import Enum

sys.path.insert(0, '/root/.openclaw/workspace')
from defense_base_components import BaseComponent, MetricsCollector

class ConfucianDimension(Enum):
    """儒商五维"""
    REN = "仁"  # 仁爱
    YI = "义"   # 道义
    LI = "礼"   # 礼仪
    ZHI = "智"  # 智慧
    XIN = "信"  # 诚信

@dataclass
class EthicsEvidence:
    """伦理证据"""
    dimension: ConfucianDimension
    evidence_type: str
    description: str
    confidence: float  # 置信度 0-1

class ConfucianEthicsEvaluator(BaseComponent):
    """
    儒商伦理评估器
    
    基于黎红雷教授儒商哲学，评估候选人在五个维度的伦理表现：
    - 仁: 仁爱精神，对人的关怀
    - 义: 道义担当，正确行事
    - 礼: 礼仪规范，行为得体
    - 智: 智慧决策，明辨是非
    - 信: 诚信守诺，言行一致
    """
    
    def __init__(self):
        super().__init__('confucian_ethics')
        self.metrics = MetricsCollector('ethics')
        
        # 五维权重
        self.dimension_weights = {
            ConfucianDimension.REN: 0.25,
            ConfucianDimension.YI: 0.20,
            ConfucianDimension.LI: 0.15,
            ConfucianDimension.ZHI: 0.20,
            ConfucianDimension.XIN: 0.20
        }
    
    def evaluate_dimension(self, 
                          dimension: ConfucianDimension,
                          evidence_list: List[EthicsEvidence]) -> Dict:
        """
        评估单个伦理维度
        """
        if not evidence_list:
            return {
                'dimension': dimension.value,
                'score': 0.5,
                'confidence': 0.0,
                'evidence_count': 0
            }
        
        # 计算加权得分
        total_confidence = sum(e.confidence for e in evidence_list)
        weighted_score = sum(
            e.confidence * self._score_evidence(e) 
            for e in evidence_list
        ) / total_confidence if total_confidence > 0 else 0.5
        
        # 置信度基于证据数量和质量
        confidence = min(total_confidence / len(evidence_list), 1.0)
        
        return {
            'dimension': dimension.value,
            'score': weighted_score,
            'confidence': confidence,
            'evidence_count': len(evidence_list),
            'key_evidence': [e.description for e in evidence_list[:3]]
        }
    
    def _score_evidence(self, evidence: EthicsEvidence) -> float:
        """对单个证据打分"""
        # 这里简化处理，实际应有更复杂的评分逻辑
        base_scores = {
            'historical_record': 0.9,  # 历史记录
            'third_party_testimonial': 0.8,  # 第三方证言
            'self_reported': 0.6,  # 自我陈述
            'indirect_indicator': 0.5  # 间接指标
        }
        return base_scores.get(evidence.evidence_type, 0.5)
    
    def comprehensive_evaluate(self, 
                              all_evidence: Dict[ConfucianDimension, List[EthicsEvidence]]) -> Dict:
        """
        综合伦理评估
        """
        dimension_scores = {}
        total_score = 0
        
        for dimension in ConfucianDimension:
            evidence = all_evidence.get(dimension, [])
            result = self.evaluate_dimension(dimension, evidence)
            dimension_scores[dimension.value] = result
            
            # 加权总分
            weight = self.dimension_weights[dimension]
            total_score += result['score'] * weight
        
        # 伦理等级
        ethics_level = self._determine_ethics_level(total_score)
        
        self.metrics.record(
            action='ethics_evaluated',
            total_score=total_score,
            level=ethics_level
        )
        
        return {
            'total_score': total_score,
            'ethics_level': ethics_level,
            'dimension_scores': dimension_scores,
            'overall_assessment': self._generate_assessment(dimension_scores, total_score),
            'recommendation': self._generate_recommendation(total_score)
        }
    
    def _determine_ethics_level(self, score: float) -> str:
        """确定伦理等级"""
        if score >= 0.85:
            return "君子级"  # 儒家理想人格
        elif score >= 0.70:
            return "贤人级"  # 有德行者
        elif score >= 0.55:
            return "善人级"  # 基本伦理达标
        else:
            return "待修养级"  # 需提升
    
    def _generate_assessment(self, 
                            dimension_scores: Dict, 
                            total: float) -> str:
        """生成总体评估"""
        # 找出强项和弱项
        scores = [(d, s['score']) for d, s in dimension_scores.items()]
        scores.sort(key=lambda x: x[1], reverse=True)
        
        strengths = [d for d, s in scores[:2]]
        weaknesses = [d for d, s in scores[-2:]]
        
        return f"""
儒商伦理评估:
- 强项: {'、'.join(strengths)}
- 待提升: {'、'.join(weaknesses)}
- 综合得分: {total:.1%}
"""
    
    def _generate_recommendation(self, score: float) -> str:
        """生成建议"""
        if score >= 0.85:
            return "伦理素养优秀，可作为企业道德标杆"
        elif score >= 0.70:
            return "伦理基础良好，值得信任合作"
        elif score >= 0.55:
            return "基本伦理达标，需在日常合作中观察"
        else:
            return "建议加强伦理考察，谨慎合作"
    
    def create_ethics_report(self, candidate_name: str, 
                            evaluation: Dict) -> str:
        """
        生成儒商伦理评估报告
        """
        report = f"""
# 儒商伦理评估报告

**评估对象**: {candidate_name}
**评估时间**: 2026年
**评估方法**: 基于黎红雷教授儒商哲学五维模型

## 总体评价

**伦理等级**: {evaluation['ethics_level']}
**综合得分**: {evaluation['total_score']:.1%}

## 五维分析

"""
        for dim, result in evaluation['dimension_scores'].items():
            report += f"""
### {dim}
- 得分: {result['score']:.1%}
- 置信度: {result['confidence']:.1%}
- 关键证据: {', '.join(result['key_evidence']) if result['key_evidence'] else '暂无'}
"""
        
        report += f"""
## 建议

{evaluation['recommendation']}

---
*评估基于公开信息和可验证证据，仅供参考*
"""
        return report

# 便捷函数
def evaluate_ethics(evidence_dict: Dict[str, List[Dict]]) -> Dict:
    """快速评估伦理"""
    evaluator = ConfucianEthicsEvaluator()
    
    # 转换证据格式
    all_evidence = {}
    for dim_name, evidence_list in evidence_dict.items():
        dim = ConfucianDimension[dim_name]
        all_evidence[dim] = [
            EthicsEvidence(
                dimension=dim,
                evidence_type=e['type'],
                description=e['desc'],
                confidence=e['confidence']
            )
            for e in evidence_list
        ]
    
    return evaluator.comprehensive_evaluate(all_evidence)

if __name__ == '__main__':
    # 测试
    evidence = {
        'REN': [{'type': 'third_party_testimonial', 'desc': '关心员工福祉', 'confidence': 0.8}],
        'YI': [{'type': 'historical_record', 'desc': '商业决策公正', 'confidence': 0.9}],
        'LI': [{'type': 'indirect_indicator', 'desc': '社交礼仪得体', 'confidence': 0.7}],
        'ZHI': [{'type': 'historical_record', 'desc': '战略决策明智', 'confidence': 0.85}],
        'XIN': [{'type': 'historical_record', 'desc': '合同履约记录良好', 'confidence': 0.9}]
    }
    
    result = evaluate_ethics(evidence)
    print(f"伦理等级: {result['ethics_level']}")
    print(f"综合得分: {result['total_score']:.1%}")


# ===== 蓝军整改: 儒商五维学术引用深化 =====
"""
## 黎红雷教授儒商哲学学术框架 (新增)

### 理论基础
本实现基于黎红雷教授《儒商管理学》的核心理论:

1. 仁 (Ren/Benevolence)
   - 理论基础: 仁者爱人 (《论语·颜渊》)
   - 商业应用: 以人为本的管理理念，关爱员工、客户、社会
   - 评估维度: 员工关怀记录、社会责任实践、利益相关者满意度

2. 义 (Yi/Righteousness)
   - 理论基础: 见利思义 (《论语·宪问》)
   - 商业应用: 正确的义利观，取之有道
   - 评估维度: 商业决策的道德考量、合规记录、公平竞争

3. 礼 (Li/Propriety)
   - 理论基础: 不学礼，无以立 (《论语·季氏》)
   - 商业应用: 商业礼仪、企业治理规范
   - 评估维度: 商业交往礼仪、企业治理透明度、合同履约

4. 智 (Zi/Wisdom)
   - 理论基础: 知者不惑 (《论语·子罕》)
   - 商业应用: 战略智慧、创新思维
   - 评估维度: 战略决策成功率、创新能力、学习成长

5. 信 (Xin/Integrity)
   - 理论基础: 民无信不立 (《论语·颜渊》)
   - 商业应用: 诚信经营、契约精神
   - 评估维度: 合同履约率、信用评级、利益相关者信任度

### 理论创新点
- 将传统儒家伦理转化为可量化的商业评估指标
- 结合现代管理学与东方智慧
- 强调义利合一而非义利对立

参考: 黎红雷.《儒商管理学》. 人民出版社, 2018.
"""

# 学术引用版本标记
CONFUCIAN_ETHICS_VERSION = "1.1_academic_enhanced"
