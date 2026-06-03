"""
扩展评估器 - Extension Evaluator
核心模块: 评估扩展技能的可能性与必要性
版本: 1.0.0
日期: 2026-04-02
"""

import json
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple
from enum import Enum


class ExtensionPriority(Enum):
    """扩展优先级"""
    HIGH = "high"       # 高优先级（立即）
    MEDIUM = "medium"   # 中优先级（近期）
    LOW = "low"         # 低优先级（远期）
    DEFER = "defer"     # 暂缓


@dataclass
class ExtensionCandidate:
    """扩展候选"""
    skill_name: str
    description: str
    priority: ExtensionPriority
    estimated_effort: str  # hours
    expected_benefit: str
    prerequisites: List[str]
    risks: List[str]


@dataclass
class ExtensionPlan:
    """扩展计划"""
    high_priority: List[ExtensionCandidate]
    medium_priority: List[ExtensionCandidate]
    low_priority: List[ExtensionCandidate]
    deferred: List[ExtensionCandidate]
    overall_recommendation: str


class ExtensionEvaluator:
    """
    扩展评估器
    
    评估整改后是否需要扩展更多技能:
    - 基于当前10步整改成果
    - 评估剩余需求
    - 给出优先级排序
    
    评估维度:
    - 必要性
    - 可行性
    - 成本效益
    - 风险
    """
    
    def __init__(self):
        # 预定义的扩展候选
        self.candidates = [
            ExtensionCandidate(
                skill_name="advanced-memory-graph",
                description="高级记忆图谱（Neo4j图数据库）",
                priority=ExtensionPriority.DEFER,
                estimated_effort="20+ hours",
                expected_benefit="更好的记忆关联和检索",
                prerequisites=["Neo4j部署", "图数据库知识"],
                risks=["技术复杂度高", "维护成本大"]
            ),
            ExtensionCandidate(
                skill_name="multi-agent-orchestrator",
                description="多Agent协调器（Claude Code方案）",
                priority=ExtensionPriority.MEDIUM,
                estimated_effort="10-15 hours",
                expected_benefit="并行处理复杂任务",
                prerequisites=["当前整改稳定运行"],
                risks=["协调复杂度", "Token消耗增加"]
            ),
            ExtensionCandidate(
                skill_name="voice-interface",
                description="语音接口（Push-to-Talk）",
                priority=ExtensionPriority.LOW,
                estimated_effort="8-12 hours",
                expected_benefit="更自然的交互方式",
                prerequisites=["语音API集成"],
                risks=["识别准确率", "隐私问题"]
            ),
            ExtensionCandidate(
                skill_name="predictive-analytics",
                description="预测性分析（Token趋势预测）",
                priority=ExtensionPriority.MEDIUM,
                estimated_effort="6-10 hours",
                expected_benefit="提前预警Token耗尽",
                prerequisites=["历史数据积累"],
                risks=["预测准确率不确定"]
            ),
            ExtensionCandidate(
                skill_name="external-api-integrations",
                description="外部API集成（飞书/企微/邮件）",
                priority=ExtensionPriority.HIGH,
                estimated_effort="5-8 hours",
                expected_benefit="打通外部系统，自动化工作流",
                prerequisites=["API密钥管理"],
                risks=["API变更", "安全风险"]
            )
        ]
    
    def evaluate_all(self) -> ExtensionPlan:
        """评估所有候选"""
        high = [c for c in self.candidates if c.priority == ExtensionPriority.HIGH]
        medium = [c for c in self.candidates if c.priority == ExtensionPriority.MEDIUM]
        low = [c for c in self.candidates if c.priority == ExtensionPriority.LOW]
        deferred = [c for c in self.candidates if c.priority == ExtensionPriority.DEFER]
        
        # 生成整体建议
        if high:
            recommendation = f"建议优先处理{len(high)}个高优先级扩展"
        elif medium:
            recommendation = f"无紧急扩展，建议处理{len(medium)}个中优先级"
        else:
            recommendation = "当前整改已足够，扩展可暂缓"
        
        return ExtensionPlan(
            high_priority=high,
            medium_priority=medium,
            low_priority=low,
            deferred=deferred,
            overall_recommendation=recommendation
        )
    
    def generate_report(self, plan: ExtensionPlan) -> str:
        """生成评估报告"""
        lines = [
            "=" * 60,
            "扩展可能性评估报告",
            "=" * 60,
            "",
            f"整体建议: {plan.overall_recommendation}",
            "",
            f"高优先级扩展 ({len(plan.high_priority)}个):"
        ]
        
        for c in plan.high_priority:
            lines.extend([
                f"  📌 {c.skill_name}",
                f"     描述: {c.description}",
                f"     工作量: {c.estimated_effort}",
                f"     预期收益: {c.expected_benefit}",
                ""
            ])
        
        if plan.medium_priority:
            lines.extend([f"中优先级扩展 ({len(plan.medium_priority)}个):"])
            for c in plan.medium_priority:
                lines.append(f"  ⚡ {c.skill_name} ({c.estimated_effort})")
            lines.append("")
        
        if plan.low_priority:
            lines.extend([f"低优先级扩展 ({len(plan.low_priority)}个):"])
            for c in plan.low_priority:
                lines.append(f"  💡 {c.skill_name} ({c.estimated_effort})")
            lines.append("")
        
        if plan.deferred:
            lines.extend([f"暂缓扩展 ({len(plan.deferred)}个):"])
            for c in plan.deferred:
                lines.append(f"  ⏸️ {c.skill_name} - {c.risks[0]}")
            lines.append("")
        
        lines.extend([
            "评估结论:",
            "当前10步整改已覆盖核心需求。",
            "建议优先稳定运行当前系统，",
            "2-4周后再评估扩展必要性。",
            "=" * 60
        ])
        
        return '\n'.join(lines)


# 便捷函数接口
def evaluate_extensions() -> ExtensionPlan:
    """便捷评估函数"""
    evaluator = ExtensionEvaluator()
    return evaluator.evaluate_all()


if __name__ == "__main__":
    # 单元测试
    print("=" * 60)
    print("扩展评估器 - 单元测试")
    print("=" * 60)
    
    evaluator = ExtensionEvaluator()
    
    # 测试1: 评估所有候选
    print("\n[测试1] 评估扩展候选...")
    plan = evaluator.evaluate_all()
    print(f"  高优先级: {len(plan.high_priority)}个")
    print(f"  中优先级: {len(plan.medium_priority)}个")
    print(f"  低优先级: {len(plan.low_priority)}个")
    print(f"  暂缓: {len(plan.deferred)}个")
    
    # 测试2: 生成报告
    print("\n[测试2] 生成评估报告...")
    report = evaluator.generate_report(plan)
    print(report)
    
    print("\n" + "=" * 60)
    print("单元测试完成")
    print("=" * 60)