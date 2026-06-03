"""
---
KIA-CODE: 知识入库代码级闭环
Asset: intuition_calibrator.py
Status: ✅ 代码级KIA完成
Date: 2026-04-15
Batch: OM-03 Python资产25份代码级KIA-批次三

KIA-Loop:
  - 接收清点: 2026-04-15
  - 轻量提取: 2026-04-15 (代码结构识别)
  - 查重去冗: 2026-04-15 (无重复代码)
  - Tier分级: T1 (核心项目资产)
  - 深度洞察: 2026-04-15 (案例库与决策系统)
  - 血液化: ✅ 完成 (五路图腾映射确认)
  - 归档锁定: 2026-04-15

功能定位:
  - 用途: 直觉校准器
  - 关联: 感知力训练
  - 维护者: 蓝军+满意姐

血液化映射:
  - 五路图腾关联: 右脑直觉
  - 产品映射: 六祖慧能-顿悟
  - 运营映射: 案例库与决策支持

---
"""

#!/usr/bin/env python3
# intuition_calibrator.py - 直觉校准器
# 来源: 文件10 - Kimi_Claw技术方案_3_.docx
# 功能: 直觉感知力校准与置信度评估
# 创建时间: 2026-04-04
# 版本: 1.0

import sys
import statistics
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

sys.path.insert(0, '/root/.openclaw/workspace')
from defense_base_components import BaseComponent, MetricsCollector

@dataclass
class IntuitionSignal:
    """直觉信号"""
    source: str  # 信号来源
    type: str    # 信号类型
    intensity: float  # 强度 0-1
    confidence: float  # 置信度 0-1
    timestamp: datetime = field(default_factory=datetime.now)
    context: Dict = field(default_factory=dict)

class IntuitionCalibrator(BaseComponent):
    """
    直觉校准器
    
    基于观自在理念，实现直觉感知力的校准和评估：
    - 异常检测: 识别不符合常规的微妙信号
    - 置信度校准: 评估直觉信号的可靠性
    - 人机协同: 算法辅助但不替代直觉判断
    """
    
    def __init__(self):
        super().__init__('intuition_calibrator')
        self.metrics = MetricsCollector('intuition')
        
        # 历史校准数据
        self.calibration_history = []
        
        # 信号阈值
        self.signal_threshold = 0.6
        self.confidence_threshold = 0.7
    
    def detect_anomaly(self, 
                      data_point: Dict,
                      baseline: Dict) -> Dict:
        """
        异常检测
        
        识别与基线存在显著偏差的信号
        """
        anomalies = []
        anomaly_scores = []
        
        for key, value in data_point.items():
            if key in baseline:
                baseline_value = baseline[key]
                
                # 计算偏差
                if isinstance(value, (int, float)) and isinstance(baseline_value, (int, float)):
                    deviation = abs(value - baseline_value) / (abs(baseline_value) + 0.001)
                    
                    if deviation > 0.3:  # 30%偏差视为异常
                        anomaly_scores.append(deviation)
                        anomalies.append({
                            'attribute': key,
                            'value': value,
                            'baseline': baseline_value,
                            'deviation': deviation,
                            'severity': 'high' if deviation > 0.5 else 'medium'
                        })
        
        # 计算总体异常度
        anomaly_score = max(anomaly_scores) if anomaly_scores else 0
        
        self.metrics.record(
            action='anomaly_detected',
            score=anomaly_score,
            count=len(anomalies)
        )
        
        return {
            'has_anomaly': len(anomalies) > 0,
            'anomaly_score': anomaly_score,
            'anomalies': anomalies,
            'attention_required': anomaly_score > 0.5
        }
    
    def calibrate_confidence(self, 
                           intuition_signals: List[IntuitionSignal],
   historical_accuracy: Optional[float] = None) -> Dict:
        """
        校准直觉置信度
        
        基于信号一致性、历史准确性等因素调整置信度
        """
        if not intuition_signals:
            return {
                'calibrated_confidence': 0.5,
                'reliability': 'unknown',
                'recommendation': '无直觉信号，建议依赖数据分析'
            }
        
        # 1. 信号一致性
        confidences = [s.confidence for s in intuition_signals]
        consistency = 1 - statistics.stdev(confidences) if len(confidences) > 1 else 1.0
        
        # 2. 信号强度
        avg_intensity = sum(s.intensity for s in intuition_signals) / len(intuition_signals)
        
        # 3. 历史准确性
        history_factor = historical_accuracy if historical_accuracy else 0.7
        
        # 4. 综合校准
        raw_confidence = sum(confidences) / len(confidences)
        calibrated = raw_confidence * 0.4 + consistency * 0.3 + avg_intensity * 0.2 + history_factor * 0.1
        
        # 确定可靠性等级
        if calibrated >= 0.8:
            reliability = "高可靠性"
        elif calibrated >= 0.6:
            reliability = "中等可靠性"
        elif calibrated >= 0.4:
            reliability = "需谨慎验证"
        else:
            reliability = "不建议依赖"
        
        self.metrics.record(
            action='confidence_calibrated',
            raw=raw_confidence,
            calibrated=calibrated
        )
        
        return {
            'calibrated_confidence': calibrated,
            'reliability': reliability,
            'consistency': consistency,
            'avg_intensity': avg_intensity,
            'signal_count': len(intuition_signals),
            'recommendation': self._generate_recommendation(calibrated)
        }
    
    def _generate_recommendation(self, confidence: float) -> str:
        """生成建议"""
        if confidence >= 0.8:
            return "直觉信号强烈且可靠，可作为重要参考"
        elif confidence >= 0.6:
            return "直觉信号可信，建议与数据分析结合"
        elif confidence >= 0.4:
            return "直觉信号较弱，需更多验证"
        else:
            return "直觉信号不可靠，建议依赖客观分析"
    
    def collect_intuition_signals(self, 
                                  observation_context: Dict) -> List[IntuitionSignal]:
        """
        收集直觉信号
        
        基于观察上下文提取潜在的直觉信号
        """
        signals = []
        
        # 示例信号检测（实际应有更复杂的逻辑）
        if 'gut_feeling' in observation_context:
            signals.append(IntuitionSignal(
                source='user_intuition',
                type='gut_feeling',
                intensity=observation_context.get('feeling_strength', 0.5),
                confidence=0.6,
                context=observation_context
            ))
        
        if 'pattern_recognition' in observation_context:
            signals.append(IntuitionSignal(
                source='pattern_match',
                type='similarity',
                intensity=observation_context.get('similarity_score', 0.5),
                confidence=observation_context.get('pattern_confidence', 0.5),
                context=observation_context
            ))
        
        return signals
    
    def integrate_intuition_and_analysis(self,
                                        intuition_result: Dict,
                                        analysis_result: Dict) -> Dict:
        """
        整合直觉与分析结果
        
        实现观自在理念：人机协同，直觉与理性并重
        """
        intuition_conf = intuition_result.get('calibrated_confidence', 0.5)
        analysis_conf = analysis_result.get('confidence', 0.7)
        
        # 权重分配
        if intuition_conf >= 0.8:
            # 高可靠直觉，给予更高权重
            i_weight, a_weight = 0.4, 0.6
        elif intuition_conf >= 0.5:
            # 中等直觉，平衡权重
            i_weight, a_weight = 0.25, 0.75
        else:
            # 低可靠直觉，主要依赖分析
            i_weight, a_weight = 0.1, 0.9
        
        # 综合评分
        intuition_score = intuition_result.get('intuition_score', 0.5)
        analysis_score = analysis_result.get('score', 0.5)
        
        integrated_score = intuition_score * i_weight + analysis_score * a_weight
        
        return {
            'integrated_score': integrated_score,
            'intuition_weight': i_weight,
            'analysis_weight': a_weight,
            'decision_mode': '协同决策' if intuition_conf >= 0.5 else '分析主导',
            'rationale': f"直觉置信度{intuition_conf:.1%}，分析置信度{analysis_conf:.1%}，采用{int(i_weight*100)}%:{int(a_weight*100)}%权重分配"
        }
    
    def get_calibration_status(self) -> Dict:
        """获取校准系统状态"""
        return {
            'calibration_count': len(self.calibration_history),
            'signal_threshold': self.signal_threshold,
            'confidence_threshold': self.confidence_threshold,
            'system_ready': True
        }

# 便捷函数
def calibrate_intuition_signals(signals: List[Dict]) -> Dict:
    """快速校准直觉信号"""
    calibrator = IntuitionCalibrator()
    
    intuition_signals = [
        IntuitionSignal(
            source=s['source'],
            type=s['type'],
            intensity=s['intensity'],
            confidence=s['confidence']
        )
        for s in signals
    ]
    
    return calibrator.calibrate_confidence(intuition_signals)

if __name__ == '__main__':
    # 测试
    signals = [
        {'source': 'pattern', 'type': 'similarity', 'intensity': 0.8, 'confidence': 0.7},
        {'source': 'gut', 'type': 'feeling', 'intensity': 0.6, 'confidence': 0.6}
    ]
    
    result = calibrate_intuition_signals(signals)
    print(f"校准置信度: {result['calibrated_confidence']:.1%}")
    print(f"可靠性: {result['reliability']}")
