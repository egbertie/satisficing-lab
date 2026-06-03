#!/usr/bin/env python3
"""
Token消耗预估器 (Estimator)
基于任务类型和历史数据预估Token消耗
"""

import yaml
import json
import re
from pathlib import Path
from typing import Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Estimation:
    """预估结果"""
    tokens: int
    confidence: float  # 0-1
    confidence_level: str  # "high", "medium", "low"
    range_low: int
    range_high: int
    method: str
    notes: str

class TokenEstimator:
    """Token消耗预估器"""
    
    # 基础Token消耗（基于经验）
    BASE_TOKENS = 500
    
    # 任务类型关键词映射
    TASK_KEYWORDS = {
        "research_analysis": ["研究", "分析", "调研", "深度", "综合", "review", "analyze", "research"],
        "document_generation": ["报告", "文档", "总结", "撰写", "write", "report", "document"],
        "code_development": ["代码", "开发", "编程", "实现", "code", "develop", "program", "implement"],
        "data_processing": ["数据", "处理", "整理", "清洗", "data", "process", "clean"],
        "testing_experiment": ["测试", "实验", "验证", "test", "experiment", "verify"],
        "routine_operation": ["查询", "检查", "查看", "query", "check", "list"]
    }
    
    def __init__(self, config_dir: str = None):
        if config_dir is None:
            config_dir = Path(__file__).parent.parent / "config"
        self.config_dir = Path(config_dir)
        self.budget_config = self._load_yaml("budgets.yaml")
        self._load_historical_data()
    
    def _load_yaml(self, filename: str) -> dict:
        """加载YAML配置文件"""
        filepath = self.config_dir / filename
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        return {}
    
    def _load_historical_data(self):
        """加载历史消耗数据"""
        data_dir = self.config_dir.parent / "data"
        consumption_file = data_dir / "consumption.json"
        if consumption_file.exists():
            with open(consumption_file, 'r') as f:
                self.consumption_data = json.load(f)
        else:
            self.consumption_data = {"daily_records": {}}
    
    def classify_task(self, task_desc: str) -> Tuple[str, float]:
        """
        分类任务类型
        返回: (task_type, confidence)
        """
        task_desc_lower = task_desc.lower()
        scores = {}
        
        for task_type, keywords in self.TASK_KEYWORDS.items():
            score = 0
            for keyword in keywords:
                if keyword.lower() in task_desc_lower:
                    score += 1
            if score > 0:
                scores[task_type] = score
        
        if not scores:
            return "routine_operation", 0.5
        
        best_type = max(scores, key=scores.get)
        confidence = min(scores[best_type] / 2, 1.0)  # 归一化到1
        return best_type, confidence
    
    def get_task_multiplier(self, task_type: str) -> float:
        """获取任务类型的Token乘数"""
        task_types = self.budget_config.get("task_types", {})
        task_config = task_types.get(task_type, {})
        return task_config.get("base_multiplier", 1.0)
    
    def estimate(self, task_desc: str, context_length: int = 0) -> Estimation:
        """
        预估任务Token消耗
        
        Args:
            task_desc: 任务描述
            context_length: 上下文长度（token数）
            
        Returns:
            Estimation对象
        """
        # 识别任务类型
        task_type, type_confidence = self.classify_task(task_desc)
        multiplier = self.get_task_multiplier(task_type)
        
        # 基础预估
        base_estimate = int(self.BASE_TOKENS * multiplier)
        
        # 上下文调整
        context_factor = 1 + (context_length / 2000)  # 每2000token增加100%
        adjusted_estimate = int(base_estimate * context_factor)
        
        # 计算置信区间
        if type_confidence > 0.8:
            confidence_level = "high"
            deviation = 0.15
        elif type_confidence > 0.5:
            confidence_level = "medium"
            deviation = 0.30
        else:
            confidence_level = "low"
            deviation = 0.50
        
        range_low = int(adjusted_estimate * (1 - deviation))
        range_high = int(adjusted_estimate * (1 + deviation))
        
        # 生成说明
        notes = f"任务类型: {task_type}, 置信度: {confidence_level}"
        if context_length > 0:
            notes += f", 上下文: {context_length}tokens"
        
        return Estimation(
            tokens=adjusted_estimate,
            confidence=type_confidence,
            confidence_level=confidence_level,
            range_low=range_low,
            range_high=range_high,
            method="keyword_classification",
            notes=notes
        )
    
    def estimate_with_history(self, task_desc: str, similar_tasks: list = None) -> Estimation:
        """
        基于历史数据增强预估
        """
        base_estimate = self.estimate(task_desc)
        
        if similar_tasks and len(similar_tasks) >= 3:
            # 使用历史平均
            avg_consumption = sum(t['tokens'] for t in similar_tasks) / len(similar_tasks)
            historical_weight = 0.6
            blended = int(base_estimate.tokens * (1 - historical_weight) + avg_consumption * historical_weight)
            
            return Estimation(
                tokens=blended,
                confidence=min(base_estimate.confidence + 0.1, 1.0),
                confidence_level="high" if base_estimate.confidence > 0.7 else base_estimate.confidence_level,
                range_low=int(blended * 0.85),
                range_high=int(blended * 1.15),
                method="historical_blended",
                notes=f"{base_estimate.notes}, 历史数据参考: {len(similar_tasks)}条"
            )
        
        return base_estimate
    
    def batch_estimate(self, tasks: list) -> list:
        """
        批量预估多个任务
        
        Args:
            tasks: [(task_id, task_desc, context_length), ...]
            
        Returns:
            [Estimation, ...]
        """
        return [self.estimate(desc, ctx) for _, desc, ctx in tasks]
    
    def verify_accuracy(self, task_id: str, estimated: int, actual: int) -> dict:
        """
        验证预估准确性
        
        Returns:
            {"deviation": float, "accuracy": str, "within_threshold": bool}
        """
        if estimated == 0:
            deviation = float('inf') if actual > 0 else 0
        else:
            deviation = abs(actual - estimated) / estimated
        
        if deviation <= 0.2:
            accuracy = "excellent"
        elif deviation <= 0.3:
            accuracy = "good"
        elif deviation <= 0.5:
            accuracy = "fair"
        else:
            accuracy = "poor"
        
        return {
            "task_id": task_id,
            "estimated": estimated,
            "actual": actual,
            "deviation": round(deviation, 2),
            "deviation_percent": f"{deviation*100:.1f}%",
            "accuracy": accuracy,
            "within_threshold": deviation <= 0.3
        }


def main():
    """命令行接口"""
    import sys
    
    estimator = TokenEstimator()
    
    if len(sys.argv) < 2:
        print("Usage: estimator.py <task_description> [context_length]")
        return 1
    
    task_desc = sys.argv[1]
    context = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    
    result = estimator.estimate(task_desc, context)
    
    print(f"任务: {task_desc}")
    print(f"预估消耗: {result.tokens} tokens")
    print(f"置信区间: [{result.range_low}, {result.range_high}]")
    print(f"置信度: {result.confidence:.0%} ({result.confidence_level})")
    print(f"预估方法: {result.method}")
    print(f"说明: {result.notes}")
    
    return 0


if __name__ == "__main__":
    exit(main())
