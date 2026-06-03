#!/usr/bin/env python3
# prospect_theory_scorer.py - 前景理论评分器
# 来源: 文件10 - Kimi_Claw技术方案_3_.docx
# 功能: 基于卡尼曼前景理论的损失厌恶权重计算
# 创建时间: 2026-04-04
# 版本: 1.0

import math
import sys
from typing import Dict, List
from dataclasses import dataclass

sys.path.insert(0, '/root/.openclaw/workspace')
from defense_base_components import BaseComponent, MetricsCollector

@dataclass
class ProspectValue:
    """前景值"""
    attribute: str
    value: float
    is_gain: bool  # True = 收益, False = 损失
    certainty: float  # 确定性 0-1

class ProspectTheoryScorer(BaseComponent):
    """
    前景理论评分器
    
    基于丹尼尔·卡尼曼(Daniel Kahneman)和阿莫斯·特沃斯基(Amos Tversky)的前景理论：
    - 损失厌恶: 损失的痛苦 > 收益的快乐
    - 敏感性递减: 边际效用递减
    - 概率权重: 对小概率事件过度重视
    """
    
    def __init__(self):
        super().__init__('prospect_theory')
        self.metrics = MetricsCollector('prospect')
        
        # 前景理论参数 (Tversky & Kahneman, 1992)
        self.alpha = 0.88  # 价值函数曲率
        self.beta = 0.88   # 损失部分曲率
        self.lambda_ = 2.25  # 损失厌恶系数
        self.gamma = 0.61  # 概率权重函数曲率
    
    def value_function(self, x: float, is_gain: bool = True) -> float:
        """
        前景理论价值函数
        
        v(x) = x^α     if x >= 0 (收益)
        v(x) = -λ(-x)^β  if x < 0 (损失)
        """
        if is_gain:
            return math.pow(x, self.alpha) if x >= 0 else 0
        else:
            return -self.lambda_ * math.pow(abs(x), self.beta) if x < 0 else 0
    
    def probability_weight(self, p: float) -> float:
        """
        概率权重函数
        
        w(p) = p^γ / (p^γ + (1-p)^γ)^(1/γ)
        """
        if p <= 0:
            return 0
        if p >= 1:
            return 1
        
        numerator = math.pow(p, self.gamma)
        denominator = math.pow(numerator + math.pow(1-p, self.gamma), 1/self.gamma)
        
        return numerator / denominator
    
    def calculate_prospect_score(self, prospects: List[ProspectValue]) -> Dict:
        """
        计算前景总分
        
        综合考虑收益、损失和概率权重
        """
        total_value = 0
        gain_value = 0
        loss_value = 0
        
        breakdown = []
        
        for prospect in prospects:
            # 计算前景价值
            v = self.value_function(prospect.value, prospect.is_gain)
            
            # 应用概率权重
            w = self.probability_weight(prospect.certainty)
            weighted_v = v * w
            
            total_value += weighted_v
            
            if prospect.is_gain:
                gain_value += weighted_v
            else:
                loss_value += weighted_v
            
            breakdown.append({
                'attribute': prospect.attribute,
                'raw_value': prospect.value,
                'is_gain': prospect.is_gain,
                'certainty': prospect.certainty,
                'value_function': v,
                'probability_weight': w,
                'weighted_value': weighted_v
            })
        
        self.metrics.record(
            action='prospect_calculated',
            total_value=total_value,
            gain_value=gain_value,
            loss_value=loss_value
        )
        
        return {
            'total_score': total_value,
            'gain_component': gain_value,
            'loss_component': loss_value,
            'loss_aversion_ratio': abs(loss_value / gain_value) if gain_value != 0 else 0,
            'breakdown': breakdown,
            'assessment': self._assess_prospect(total_value, gain_value, loss_value)
        }
    
    def _assess_prospect(self, total: float, gain: float, loss: float) -> str:
        """评估前景结果"""
        if total > 0.5:
            return "优秀前景 - 收益显著大于损失"
        elif total > 0:
            return "良好前景 - 净收益为正"
        elif total > -0.5:
            return "一般前景 - 需权衡利弊"
        else:
            return "谨慎前景 - 潜在损失较大"
    
    def apply_to_partner_matching(self, 
                                   candidate_attributes: Dict[str, float],
                                   risk_factors: Dict[str, float]) -> Dict:
        """
        应用于合伙人匹配场景
        
        Args:
            candidate_attributes: 候选人属性得分
            risk_factors: 各属性的风险概率
        """
        prospects = []
        
        for attr, score in candidate_attributes.items():
            risk = risk_factors.get(attr, 0.1)
            
            # 将属性转化为前景值
            # 高得分 = 收益前景
            # 低得分 = 损失前景
            if score >= 0.6:
                prospect = ProspectValue(
                    attribute=attr,
                    value=score - 0.5,  # 相对基准的收益
                    is_gain=True,
                    certainty=1 - risk
                )
            else:
                prospect = ProspectValue(
                    attribute=attr,
                    value=score - 0.5,  # 相对基准的损失
                    is_gain=False,
                    certainty=risk
                )
            
            prospects.append(prospect)
        
        return self.calculate_prospect_score(prospects)
    
    def explain_prospect_theory(self) -> str:
        """解释前景理论原理"""
        return """
## 前景理论原理

前景理论描述了人们在不确定条件下的决策行为：

### 1. 损失厌恶 (Loss Aversion)
- 损失的痛苦 ≈ 2.25倍收益的快乐
- 人们对损失更敏感

### 2. 敏感性递减 (Diminishing Sensitivity)
- 边际效用递减
- 从0到100的收益 > 从1000到1100的收益

### 3. 概率权重 (Probability Weighting)
- 对小概率事件过度重视
- 对大概率事件不够重视

### 在合伙人匹配中的应用
- 候选人的"潜在风险"被加权计算
- 避免对高得分但高风险候选人过度乐观
- 更准确地评估不确定条件下的匹配价值
"""

# 便捷函数
def calculate_prospect_value(attributes: Dict[str, float], 
                             risks: Dict[str, float]) -> Dict:
    """快速计算前景值"""
    scorer = ProspectTheoryScorer()
    return scorer.apply_to_partner_matching(attributes, risks)

if __name__ == '__main__':
    # 测试
    attributes = {
        'technical_skill': 0.85,
        'management_exp': 0.70,
        'network': 0.60,
        'stability': 0.55
    }
    
    risks = {
        'technical_skill': 0.1,
        'management_exp': 0.2,
        'network': 0.3,
        'stability': 0.4
    }
    
    result = calculate_prospect_value(attributes, risks)
    print(f"前景总分: {result['total_score']:.3f}")
    print(f"评估: {result['assessment']}")
