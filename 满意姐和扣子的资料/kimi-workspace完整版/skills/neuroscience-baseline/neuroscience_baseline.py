"""
神经科学基线检查器 - Neuroscience Baseline Checker
核心模块: 方翊沣博士数字替身能力验证
版本: 1.0.0
日期: 2026-04-02
Expert_ID: 方博士数字替身
"""

import json
import re
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple
from enum import Enum


class BaselineLevel(Enum):
    """基线级别"""
    OPTIMAL = "optimal"       # 最优
    NORMAL = "normal"         # 正常
    SUBOPTIMAL = "suboptimal" # 亚优
    CRITICAL = "critical"     # 临界


@dataclass
class BaselineCheck:
    """基线检查项"""
    dimension: str            # 维度
    score: float             # 分数 0-1
    level: BaselineLevel     # 级别
    details: Dict            # 详情


@dataclass
class BaselineReport:
    """基线检查报告"""
    overall_score: float
    overall_level: BaselineLevel
    dimensions: List[BaselineCheck]
    recommendations: List[str]
    sleep_optimization: Dict


class NeuroscienceBaselineChecker:
    """
    神经科学基线检查器
    
    基于方翊沣博士神经科学专业知识:
    - 决策压力评估
    - 认知负荷检测
    - 睡眠优化建议
    - 脑机接口(BCI)兼容性检查
    
    新限制声明:
    - 基于文本分析，非生理信号测量
    - 建议仅供参考，不构成医疗建议
    - 睡眠分析基于自我报告，非客观监测
    """
    
    def __init__(self):
        self.dimensions = {
            "cognitive_load": {
                "name": "认知负荷",
                "weight": 0.25,
                "indicators": {
                    "high": ["复杂", "多任务", "信息过载", "难以决策", "混乱"],
                    "low": ["清晰", "简单", "明确", "有序", "专注"]
                }
            },
            "decision_pressure": {
                "name": "决策压力",
                "weight": 0.25,
                "indicators": {
                    "high": ["紧急", " deadline", "必须", "压力", "焦虑"],
                    "low": ["从容", "时间充裕", " relaxed", "冷静"]
                }
            },
            "sleep_quality": {
                "name": "睡眠质量",
                "weight": 0.20,
                "indicators": {
                    "poor": ["熬夜", "失眠", "睡眠不足", "困倦", "疲劳"],
                    "good": ["充足睡眠", "休息好", "精力充沛", "睡眠质量高"]
                }
            },
            "bci_readiness": {
                "name": "BCI准备度",
                "weight": 0.15,
                "indicators": {
                    "ready": ["神经反馈", "脑电", "专注", "冥想"],
                    "not_ready": ["分心", "烦躁", "注意力不集中"]
                }
            },
            "intuition_calibration": {
                "name": "直觉校准",
                "weight": 0.15,
                "indicators": {
                    "calibrated": ["直觉", "感知", "洞察", "第六感"],
                    "not_calibrated": ["怀疑", "不确定", "犹豫"]
                }
            }
        }
        
        self.thresholds = {
            BaselineLevel.OPTIMAL: 0.85,
            BaselineLevel.NORMAL: 0.65,
            BaselineLevel.SUBOPTIMAL: 0.45
        }
    
    def check_cognitive_load(self, content: str) -> BaselineCheck:
        """检查认知负荷"""
        return self._check_dimension("cognitive_load", content)
    
    def check_decision_pressure(self, content: str) -> BaselineCheck:
        """检查决策压力"""
        return self._check_dimension("decision_pressure", content)
    
    def check_sleep_quality(self, content: str) -> BaselineCheck:
        """检查睡眠质量"""
        return self._check_dimension("sleep_quality", content)
    
    def check_bci_readiness(self, content: str) -> BaselineCheck:
        """检查BCI准备度"""
        return self._check_dimension("bci_readiness", content)
    
    def check_intuition_calibration(self, content: str) -> BaselineCheck:
        """检查直觉校准"""
        return self._check_dimension("intuition_calibration", content)
    
    def full_check(self, content: str) -> BaselineReport:
        """完整基线检查"""
        dimensions = []
        
        dimensions.append(self.check_cognitive_load(content))
        dimensions.append(self.check_decision_pressure(content))
        dimensions.append(self.check_sleep_quality(content))
        dimensions.append(self.check_bci_readiness(content))
        dimensions.append(self.check_intuition_calibration(content))
        
        # 加权计算
        total_score = sum(
            d.score * self.dimensions[d.dimension]["weight"]
            for d in dimensions
        )
        
        overall_level = self._determine_level(total_score)
        
        # 生成建议
        recommendations = self._generate_recommendations(dimensions)
        
        # 睡眠优化建议
        sleep_opt = self._generate_sleep_optimization(dimensions)
        
        return BaselineReport(
            overall_score=total_score,
            overall_level=overall_level,
            dimensions=dimensions,
            recommendations=recommendations,
            sleep_optimization=sleep_opt
        )
    
    def _check_dimension(self, dim_key: str, content: str) -> BaselineCheck:
        """检查单项维度"""
        dim = self.dimensions[dim_key]
        indicators = dim["indicators"]
        
        positive_count = 0
        negative_count = 0
        
        # 根据维度类型确定正负指标
        if "high" in indicators and "low" in indicators:
            # 高=负面，低=正面（如认知负荷）
            for ind in indicators["high"]:
                negative_count += len(re.findall(ind, content, re.IGNORECASE))
            for ind in indicators["low"]:
                positive_count += len(re.findall(ind, content, re.IGNORECASE))
        elif "poor" in indicators and "good" in indicators:
            # poor=负面，good=正面（如睡眠质量）
            for ind in indicators["poor"]:
                negative_count += len(re.findall(ind, content, re.IGNORECASE))
            for ind in indicators["good"]:
                positive_count += len(re.findall(ind, content, re.IGNORECASE))
        elif "ready" in indicators and "not_ready" in indicators:
            # ready=正面，not_ready=负面
            for ind in indicators["ready"]:
                positive_count += len(re.findall(ind, content, re.IGNORECASE))
            for ind in indicators["not_ready"]:
                negative_count += len(re.findall(ind, content, re.IGNORECASE))
        elif "calibrated" in indicators:
            # calibrated=正面，not_calibrated=负面
            for ind in indicators["calibrated"]:
                positive_count += len(re.findall(ind, content, re.IGNORECASE))
            for ind in indicators["not_calibrated"]:
                negative_count += len(re.findall(ind, content, re.IGNORECASE))
        
        # 计算分数
        total = positive_count + negative_count
        if total == 0:
            score = 0.5
        else:
            score = positive_count / total
        
        # 构建详情
        details = {
            "positive_signals": positive_count,
            "negative_signals": negative_count,
            "dimension_name": dim["name"]
        }
        
        return BaselineCheck(
            dimension=dim_key,
            score=score,
            level=self._determine_level(score),
            details=details
        )
    
    def _determine_level(self, score: float) -> BaselineLevel:
        """确定级别"""
        if score >= self.thresholds[BaselineLevel.OPTIMAL]:
            return BaselineLevel.OPTIMAL
        elif score >= self.thresholds[BaselineLevel.NORMAL]:
            return BaselineLevel.NORMAL
        elif score >= self.thresholds[BaselineLevel.SUBOPTIMAL]:
            return BaselineLevel.SUBOPTIMAL
        else:
            return BaselineLevel.CRITICAL
    
    def _generate_recommendations(self, dimensions: List[BaselineCheck]) -> List[str]:
        """生成神经科学建议"""
        recommendations = []
        
        # 认知负荷过高
        cog_load = next((d for d in dimensions if d.dimension == "cognitive_load"), None)
        if cog_load and cog_load.score < 0.5:
            recommendations.append("认知负荷较高，建议进行任务分解或休息")
        
        # 决策压力过大
        pressure = next((d for d in dimensions if d.dimension == "decision_pressure"), None)
        if pressure and pressure.score < 0.5:
            recommendations.append("决策压力较大，建议采用满意解而非最优解")
        
        # 睡眠质量差
        sleep = next((d for d in dimensions if d.dimension == "sleep_quality"), None)
        if sleep and sleep.score < 0.5:
            recommendations.append("睡眠不足可能影响决策质量，建议优先保障睡眠")
        
        # BCI准备度
        bci = next((d for d in dimensions if d.dimension == "bci_readiness"), None)
        if bci and bci.score >= 0.7:
            recommendations.append("BCI准备度良好，可考虑神经反馈训练")
        
        return recommendations
    
    def _generate_sleep_optimization(self, dimensions: List[BaselineCheck]) -> Dict:
        """生成睡眠优化建议（方博士专业）"""
        sleep = next((d for d in dimensions if d.dimension == "sleep_quality"), None)
        
        if not sleep:
            return {}
        
        if sleep.score >= 0.8:
            return {
                "status": "optimal",
                "recommendation": "保持当前睡眠习惯",
                "sleep_hygiene": ["规律作息", "睡前远离屏幕"]
            }
        elif sleep.score >= 0.5:
            return {
                "status": "suboptimal",
                "recommendation": "建议优化睡眠",
                "sleep_hygiene": [
                    "固定就寝时间",
                    "睡前1小时避免蓝光",
                    "保持卧室凉爽黑暗",
                    "避免午后咖啡因"
                ]
            }
        else:
            return {
                "status": "poor",
                "recommendation": "睡眠严重不足，优先改善睡眠",
                "sleep_hygiene": [
                    "立即调整作息，保证7-8小时睡眠",
                    "建立睡前仪式",
                    "必要时咨询睡眠专家",
                    "避免睡前高强度脑力活动"
                ],
                "warning": "睡眠不足严重影响认知功能和决策质量"
            }


# 便捷函数接口
def check_neuroscience_baseline(content: str) -> BaselineReport:
    """便捷基线检查函数"""
    checker = NeuroscienceBaselineChecker()
    return checker.full_check(content)


if __name__ == "__main__":
    # 单元测试
    print("=" * 60)
    print("神经科学基线检查器 - 单元测试")
    print("=" * 60)
    
    checker = NeuroscienceBaselineChecker()
    
    # 测试1: 良好状态
    print("\n[测试1] 良好状态检查...")
    good_content = """
    今天状态不错，睡眠充足，精力充沛。
    任务清晰简单，压力不大，时间充裕。
    专注度很高，可以进行深度思考。
    直觉很准，感知力在线。
    """
    result = checker.full_check(good_content)
    print(f"  综合评分: {result.overall_score:.2f}")
    print(f"  基线级别: {result.overall_level.value}")
    print(f"  建议数: {len(result.recommendations)}")
    
    # 测试2: 疲劳状态
    print("\n[测试2] 疲劳状态检查...")
    tired_content = """
    昨晚又熬夜了，睡眠不足，感觉很疲劳。
    任务很复杂，多任务并行，信息过载。
    压力很大， deadline 很紧，很焦虑。
    注意力无法集中，分心严重。
    """
    result = checker.full_check(tired_content)
    print(f"  综合评分: {result.overall_score:.2f}")
    print(f"  基线级别: {result.overall_level.value}")
    print(f"  睡眠优化: {result.sleep_optimization.get('status', 'N/A')}")
    
    # 测试3: 各维度检查
    print("\n[测试3] 各维度检查...")
    for dim_key in checker.dimensions.keys():
        check = checker._check_dimension(dim_key, good_content)
        print(f"  {checker.dimensions[dim_key]['name']}: {check.score:.2f}")
    
    print("\n" + "=" * 60)
    print("单元测试完成")
    print("=" * 60)
    print("\n注意: 本检查器基于文本分析，仅供参考")
    print("      睡眠问题建议咨询专业医生")