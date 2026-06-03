#!/usr/bin/env python3
# continual_learning_engine.py - 持续学习引擎
# 来源: 文件10深度重审 (段落15,000-20,000)
# 功能: 基于案例的持续学习与模型进化
# 创建时间: 2026-04-04 (蓝军整改补实施)
# 版本: 1.0

import json
import sys
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

sys.path.insert(0, '/root/.openclaw/workspace')
from defense_base_components import BaseComponent, MetricsCollector

@dataclass
class LearningEpisode:
    """学习样本"""
    case_id: str
    features: Dict
    outcome: float  # 实际结果 (0-1)
    prediction: float  # 模型预测
    timestamp: datetime
    feedback: str  # 用户反馈

class ContinualLearningEngine(BaseComponent):
    """
    持续学习引擎
    
    实现增量学习，无需重训练即可进化：
    - 案例反馈收集
    - 权重在线调整
    - 知识蒸馏
    - 遗忘控制
    """
    
    def __init__(self):
        super().__init__('continual_learning')
        self.metrics = MetricsCollector('learning')
        
        self.data_path = f"{self.workspace}/continual_learning"
        Path(self.data_path).mkdir(parents=True, exist_ok=True)
        
        # 学习历史
        self.episodes: List[LearningEpisode] = []
        
        # 当前权重 (可学习调整)
        self.current_weights = {
            'satisficing': 0.30,
            'prospect': 0.20,
            'ethics': 0.25,
            'intuition': 0.15,
            'diligence': 0.10
        }
        
        # 学习率
        self.learning_rate = 0.01
        
        # 加载历史
        self._load_episodes()
    
    def _load_episodes(self):
        """加载学习历史"""
        data_file = f"{self.data_path}/episodes.json"
        if Path(data_file).exists():
            try:
                with open(data_file, 'r') as f:
                    data = json.load(f)
                    self.episodes = [
                        LearningEpisode(
                            case_id=e['case_id'],
                            features=e['features'],
                            outcome=e['outcome'],
                            prediction=e['prediction'],
                            timestamp=datetime.fromisoformat(e['timestamp']),
                            feedback=e['feedback']
                        )
                        for e in data.get('episodes', [])
                    ]
                    self.current_weights = data.get('weights', self.current_weights)
            except:
                pass
    
    def _save_episodes(self):
        """保存学习历史"""
        data_file = f"{self.data_path}/episodes.json"
        data = {
            'episodes': [
                {
                    'case_id': e.case_id,
                    'features': e.features,
                    'outcome': e.outcome,
                    'prediction': e.prediction,
                    'timestamp': e.timestamp.isoformat(),
                    'feedback': e.feedback
                }
                for e in self.episodes[-1000:]  # 只保留最近1000条
            ],
            'weights': self.current_weights,
            'last_update': datetime.now().isoformat()
        }
        
        with open(data_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def record_outcome(self, 
                      case_id: str,
                      features: Dict,
                      prediction: float,
                      actual_outcome: float,
                      feedback: str = ""):
        """
        记录案例结果
        """
        episode = LearningEpisode(
            case_id=case_id,
            features=features,
            outcome=actual_outcome,
            prediction=prediction,
            timestamp=datetime.now(),
            feedback=feedback
        )
        
        self.episodes.append(episode)
        
        # 触发权重调整
        self._adjust_weights(episode)
        
        # 保存
        self._save_episodes()
        
        self.metrics.record(
            action='outcome_recorded',
            case_id=case_id,
            error=abs(prediction - actual_outcome)
        )
    
    def _adjust_weights(self, episode: LearningEpisode):
        """
        在线权重调整
        
        基于预测误差调整各维度权重
        """
        error = episode.prediction - episode.outcome
        
        # 分析各特征对预测的影响 (简化版)
        feature_impacts = episode.features
        
        for dimension in self.current_weights:
            if dimension in feature_impacts:
                # 如果该维度预测偏高，降低权重
                if error > 0.1:  # 预测过高
                    self.current_weights[dimension] -= self.learning_rate * 0.5
                elif error < -0.1:  # 预测过低
                    self.current_weights[dimension] += self.learning_rate * 0.5
                
                # 确保权重在合理范围内
                self.current_weights[dimension] = max(0.05, min(0.5, self.current_weights[dimension]))
        
        # 归一化
        total = sum(self.current_weights.values())
        self.current_weights = {k: v/total for k, v in self.current_weights.items()}
    
    def get_improved_weights(self) -> Dict:
        """
        获取优化后的权重
        """
        return self.current_weights.copy()
    
    def analyze_learning_progress(self) -> Dict:
        """
        分析学习进度
        """
        if len(self.episodes) < 10:
            return {
                'status': 'insufficient_data',
                'episodes': len(self.episodes),
                'message': '数据不足，继续收集案例'
            }
        
        # 计算最近10个案例的误差
        recent_errors = [
            abs(e.prediction - e.outcome)
            for e in self.episodes[-10:]
        ]
        
        # 计算早期10个案例的误差
        if len(self.episodes) >= 20:
            early_errors = [
                abs(e.prediction - e.outcome)
                for e in self.episodes[-20:-10]
            ]
            
            improvement = sum(early_errors) / len(early_errors) - sum(recent_errors) / len(recent_errors)
        else:
            improvement = 0
        
        return {
            'status': 'learning',
            'total_episodes': len(self.episodes),
            'recent_avg_error': sum(recent_errors) / len(recent_errors),
            'improvement': improvement,
            'current_weights': self.current_weights,
            'trend': 'improving' if improvement > 0.01 else ('stable' if improvement > -0.01 else 'degrading')
        }
    
    def generate_learning_report(self) -> str:
        """生成学习报告"""
        progress = self.analyze_learning_progress()
        
        report = f"""
# 持续学习报告

## 学习概况
- 学习样本数: {progress.get('total_episodes', 0)}
- 学习状态: {progress.get('status', 'unknown')}

## 性能趋势
- 近期平均误差: {progress.get('recent_avg_error', 0):.3f}
- 改进幅度: {progress.get('improvement', 0):+.3f}
- 趋势: {progress.get('trend', 'unknown')}

## 优化后权重
"""
        weights = progress.get('current_weights', {})
        for dim, weight in weights.items():
            report += f"- {dim}: {weight:.3f}\n"
        
        report += """
## 学习建议
- 继续收集案例反馈以优化权重
- 关注误差较大的维度
- 定期审查权重合理性
"""
        return report

# 便捷函数
def record_case_outcome(case_id: str, 
                       features: Dict,
                       prediction: float,
                       actual: float):
    """快速记录案例结果"""
    engine = ContinualLearningEngine()
    engine.record_outcome(case_id, features, prediction, actual)
    return engine.get_improved_weights()

if __name__ == '__main__':
    # 测试
    engine = ContinualLearningEngine()
    
    # 模拟记录几个案例
    for i in range(5):
        engine.record_outcome(
            case_id=f'CASE_{i}',
            features={'satisficing': 0.8, 'ethics': 0.7},
            prediction=0.75,
            actual_outcome=0.85
        )
    
    print(engine.generate_learning_report())
