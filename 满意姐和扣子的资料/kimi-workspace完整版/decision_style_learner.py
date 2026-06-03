#!/usr/bin/env python3
# decision_style_learner.py - 决策风格习得引擎
# 来源: 文件13 - AI决策系统设计.docx (学习层)
# 功能: 让AI习得Egbertie的决策风格
# 创建时间: 2026-04-04
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
class DecisionLog:
    """决策日志"""
    log_id: str
    scenario: str
    thought_process: str  # 思考路径而非仅结论
    decision: str
    outcome: Optional[str]
    timestamp: datetime
    feedback: Optional[str] = None

@dataclass
class StylePattern:
    """决策风格模式"""
    pattern_name: str
    description: str
    examples: List[str]
    frequency: float

class DecisionStyleLearner(BaseComponent):
    """
    决策风格习得引擎
    
    基于文档需求的学习层实现：
    - 决策过程追踪
    - 对比学习
    - 风格模式提取
    """
    
    def __init__(self):
        super().__init__('style_learner')
        self.metrics = MetricsCollector('style_learning')
        
        self.data_path = f"{self.workspace}/style_learning"
        Path(self.data_path).mkdir(parents=True, exist_ok=True)
        
        # 决策日志库
        self.decision_logs: List[DecisionLog] = []
        
        # 学习到的风格模式
        self.style_patterns: List[StylePattern] = []
        
        # 风格偏好权重
        self.style_weights = {
            'rational_vs_intuitive': 0.5,  # 0=纯理性, 1=纯直觉
            'short_vs_long_term': 0.5,     # 0=纯短期, 1=纯长期
            'risk_averse_vs_seeking': 0.5, # 0=风险规避, 1=风险追求
            'individual_vs_collective': 0.5 # 0=个人, 1=集体
        }
        
        # 加载历史
        self._load_logs()
        self._extract_patterns()
    
    def _load_logs(self):
        """加载历史决策日志"""
        log_file = f"{self.data_path}/decision_logs.json"
        if Path(log_file).exists():
            try:
                with open(log_file, 'r') as f:
                    data = json.load(f)
                    self.decision_logs = [
                        DecisionLog(
                            log_id=d['log_id'],
                            scenario=d['scenario'],
                            thought_process=d['thought_process'],
                            decision=d['decision'],
                            outcome=d.get('outcome'),
                            timestamp=datetime.fromisoformat(d['timestamp']),
                            feedback=d.get('feedback')
                        )
                        for d in data.get('logs', [])
                    ]
            except:
                pass
    
    def _save_logs(self):
        """保存决策日志"""
        log_file = f"{self.data_path}/decision_logs.json"
        data = {
            'logs': [
                {
                    'log_id': d.log_id,
                    'scenario': d.scenario,
                    'thought_process': d.thought_process,
                    'decision': d.decision,
                    'outcome': d.outcome,
                    'timestamp': d.timestamp.isoformat(),
                    'feedback': d.feedback
                }
                for d in self.decision_logs[-500:]  # 保留最近500条
            ]
        }
        with open(log_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def record_decision(self,
                       scenario: str,
                       thought_process: str,
                       decision: str,
                       outcome: Optional[str] = None) -> str:
        """
        记录决策过程
        
        关键：记录"思考路径"而非仅结论
        """
        log_id = f"DEC_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        log = DecisionLog(
            log_id=log_id,
            scenario=scenario,
            thought_process=thought_process,
            decision=decision,
            outcome=outcome,
            timestamp=datetime.now()
        )
        
        self.decision_logs.append(log)
        self._save_logs()
        
        # 触发模式更新
        if len(self.decision_logs) % 10 == 0:
            self._extract_patterns()
        
        self.metrics.record(action='decision_recorded', log_id=log_id)
        
        return log_id
    
    def provide_feedback(self,
                        log_id: str,
                        feedback: str,
                        is_aligned: bool):
        """
        提供风格反馈
        
        用户只需标注"符合/不符合我的风格"
        """
        for log in self.decision_logs:
            if log.log_id == log_id:
                log.feedback = feedback
                break
        
        self._save_logs()
        
        # 根据反馈调整风格权重
        if is_aligned:
            self._reinforce_style(log_id)
        else:
            self._adjust_style(log_id)
        
        self.metrics.record(
            action='feedback_provided',
            log_id=log_id,
            aligned=is_aligned
        )
    
    def _extract_patterns(self):
        """提取决策风格模式"""
        if len(self.decision_logs) < 5:
            return
        
        patterns = []
        
        # 模式1: 思考路径特征
        thought_keywords = self._extract_keywords(
            [d.thought_process for d in self.decision_logs]
        )
        
        if thought_keywords:
            patterns.append(StylePattern(
                pattern_name='思考路径偏好',
                description=f'倾向于使用{thought_keywords[0]}等方式思考',
                examples=thought_keywords[:3],
                frequency=0.7
            ))
        
        # 模式2: 决策维度偏好
        dimension_keywords = self._extract_decision_dimensions(
            [d.decision for d in self.decision_logs]
        )
        
        if dimension_keywords:
            patterns.append(StylePattern(
                pattern_name='决策维度偏好',
                description=f'决策时重视{dimension_keywords[0]}等维度',
                examples=dimension_keywords[:3],
                frequency=0.6
            ))
        
        self.style_patterns = patterns
    
    def _extract_keywords(self, texts: List[str]) -> List[str]:
        """提取关键词"""
        # 简化的关键词提取
        common_words = ['风险', '收益', '长期', '短期', '团队', '个人', '伦理', '效率']
        found = []
        for text in texts:
            for word in common_words:
                if word in text and word not in found:
                    found.append(word)
        return found
    
    def _extract_decision_dimensions(self, decisions: List[str]) -> List[str]:
        """提取决策维度"""
        dimensions = ['价值观', '利益', '风险', '伦理', '效率', '公平']
        found = []
        for decision in decisions:
            for dim in dimensions:
                if dim in decision and dim not in found:
                    found.append(dim)
        return found
    
    def _reinforce_style(self, log_id: str):
        """强化学习到的风格"""
        # 找到对应的日志
        log = next((d for d in self.decision_logs if d.log_id == log_id), None)
        if not log:
            return
        
        # 根据决策内容调整风格权重
        if '直觉' in log.thought_process or '感觉' in log.thought_process:
            self.style_weights['rational_vs_intuitive'] += 0.05
        if '长期' in log.decision:
            self.style_weights['short_vs_long_term'] += 0.05
        
        # 确保在范围内
        for key in self.style_weights:
            self.style_weights[key] = max(0.0, min(1.0, self.style_weights[key]))
    
    def _adjust_style(self, log_id: str):
        """调整风格（不符合反馈时）"""
        # 反向调整
        log = next((d for d in self.decision_logs if d.log_id == log_id), None)
        if not log:
            return
        
        if '直觉' in log.thought_process:
            self.style_weights['rational_vs_intuitive'] -= 0.05
        if '长期' in log.decision:
            self.style_weights['short_vs_long_term'] -= 0.05
        
        for key in self.style_weights:
            self.style_weights[key] = max(0.0, min(1.0, self.style_weights[key]))
    
    def get_learned_style(self) -> Dict:
        """获取学习到的风格"""
        return {
            'style_weights': self.style_weights,
            'patterns': [
                {
                    'name': p.pattern_name,
                    'description': p.description,
                    'frequency': p.frequency
                }
                for p in self.style_patterns
            ],
            'total_logs': len(self.decision_logs),
            'learning_status': 'learning' if len(self.decision_logs) >= 10 else 'insufficient_data'
        }
    
    def generate_style_report(self) -> str:
        """生成风格学习报告"""
        style = self.get_learned_style()
        
        report = f"""
# 决策风格学习报告

## 学习概况
- 决策样本数: {style['total_logs']}
- 学习状态: {style['learning_status']}

## 风格偏好
- 理性 ↔ 直觉: {style['style_weights']['rational_vs_intuitive']:.2f} (0.5=平衡)
- 短期 ↔ 长期: {style['style_weights']['short_vs_long_term']:.2f}
- 风险规避 ↔ 风险追求: {style['style_weights']['risk_averse_vs_seeking']:.2f}
- 个人 ↔ 集体: {style['style_weights']['individual_vs_collective']:.2f}

## 识别的模式
"""
        for p in style['patterns']:
            report += f"- {p['name']}: {p['description']} (频率{p['frequency']:.0%})\n"
        
        return report

# 便捷函数
def record_decision(scenario: str,
                   thought_process: str,
                   decision: str) -> str:
    """快速记录决策"""
    learner = DecisionStyleLearner()
    return learner.record_decision(scenario, thought_process, decision)

if __name__ == '__main__':
    # 测试
    learner = DecisionStyleLearner()
    
    # 模拟记录几个决策
    for i in range(5):
        learner.record_decision(
            scenario=f'决策场景{i}',
            thought_process='从风险维度切入，考虑长期价值',
            decision='选择稳健方案'
        )
    
    print(learner.generate_style_report())
