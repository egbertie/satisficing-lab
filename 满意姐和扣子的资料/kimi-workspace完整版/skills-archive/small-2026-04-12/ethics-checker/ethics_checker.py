"""
伦理检查器 - Ethics Checker
核心模块: 黎红雷五规检查
版本: 1.0.0
日期: 2026-04-02
Expert_ID: 黎红雷数字替身
"""

import json
import re
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple
from enum import Enum


class EthicsLevel(Enum):
    """伦理级别"""
    EXEMPLARY = "exemplary"      # 典范
    COMPLIANT = "compliant"      # 合规
    QUESTIONABLE = "questionable" # 存疑
    VIOLATION = "violation"      # 违规


@dataclass
class EthicsCheckResult:
    """伦理检查结果"""
    rule: str                    # 规则名
    score: float                # 分数 0-1
    level: EthicsLevel          # 级别
    violations: List[str]       # 违规项
    recommendations: List[str]  # 建议


@dataclass
class EthicsReport:
    """伦理检查报告"""
    overall_score: float
    overall_level: EthicsLevel
    rule_results: List[EthicsCheckResult]
    summary: str
    actionable_items: List[str]


class EthicsChecker:
    """
    伦理检查器
    
    基于黎红雷教授儒商伦理六规（删除"智"后五规）:
    - 诚 (Integrity): 信息披露完整性
    - 信 (Trustworthiness): 承诺可兑现性
    - 义 (Righteousness): 利益冲突处理
    - 仁 (Benevolence): 利益相关者关怀
    - 礼 (Propriety): 商业伦理合规
    
    新限制声明:
    - 基于规则匹配，非深度语义理解
    - 复杂情境可能误判
    - 建议作为辅助工具，重要决策人工复核
    """
    
    def __init__(self):
        self.rules = {
            "诚_integrity": {
                "weight": 0.25,
                "description": "信息披露完整性",
                "positive_indicators": [
                    "披露", "透明", "公开", "如实", "完整",
                    "disclose", "transparent", "complete"
                ],
                "negative_indicators": [
                    "隐瞒", "隐藏", "隐瞒", "遮蔽", "不完整",
                    "conceal", "hide", "withhold"
                ]
            },
            "信_trustworthiness": {
                "weight": 0.20,
                "description": "承诺可兑现性",
                "positive_indicators": [
                    "可兑现", "可行", "可实现", "务实", "审慎",
                    "feasible", "realistic", "achievable"
                ],
                "negative_indicators": [
                    "夸大", "过度承诺", "不切实际", "空头支票",
                    "exaggerate", "overpromise", "unrealistic"
                ]
            },
            "义_righteousness": {
                "weight": 0.20,
                "description": "利益冲突处理",
                "positive_indicators": [
                    "声明", "回避", "独立", "公正", "公平",
                    "declare", "avoid", "independent", "fair"
                ],
                "negative_indicators": [
                    "利益输送", "关联交易", "暗箱操作", "偏袒",
                    "conflict", "biased", "favoritism"
                ]
            },
            "仁_benevolence": {
                "weight": 0.15,
                "description": "利益相关者关怀",
                "positive_indicators": [
                    "关怀", "保护", "平衡", "共赢", "负责任",
                    "care", "protect", "balance", "win-win"
                ],
                "negative_indicators": [
                    "伤害", "损害", "牺牲", "忽视", "剥削",
                    "harm", "damage", "exploit", "ignore"
                ]
            },
            "礼_propriety": {
                "weight": 0.20,
                "description": "商业伦理合规",
                "positive_indicators": [
                    "合规", "合法", "符合规范", "遵守", "正当",
                    "compliant", "legal", "ethical", "proper"
                ],
                "negative_indicators": [
                    "违规", "违法", "不合规", "灰色地带", "擦边球",
                    "violation", "illegal", "unethical"
                ]
            }
        }
        
        # 级别阈值
        self.thresholds = {
            EthicsLevel.EXEMPLARY: 0.90,
            EthicsLevel.COMPLIANT: 0.70,
            EthicsLevel.QUESTIONABLE: 0.50
        }
    
    def check_integrity(self, content: str) -> EthicsCheckResult:
        """检查诚 - 信息披露完整性"""
        return self._check_rule("诚_integrity", content)
    
    def check_trustworthiness(self, content: str) -> EthicsCheckResult:
        """检查信 - 承诺可兑现性"""
        return self._check_rule("信_trustworthiness", content)
    
    def check_righteousness(self, content: str) -> EthicsCheckResult:
        """检查义 - 利益冲突处理"""
        return self._check_rule("义_righteousness", content)
    
    def check_benevolence(self, content: str) -> EthicsCheckResult:
        """检查仁 - 利益相关者关怀"""
        return self._check_rule("仁_benevolence", content)
    
    def check_propriety(self, content: str) -> EthicsCheckResult:
        """检查礼 - 商业伦理合规"""
        return self._check_rule("礼_propriety", content)
    
    def full_check(self, content: str) -> EthicsReport:
        """
        完整伦理检查
        
        执行五规检查，生成综合报告
        """
        results = []
        
        results.append(self.check_integrity(content))
        results.append(self.check_trustworthiness(content))
        results.append(self.check_righteousness(content))
        results.append(self.check_benevolence(content))
        results.append(self.check_propriety(content))
        
        # 加权计算总分
        total_score = sum(
            r.score * self.rules[r.rule]["weight"]
            for r in results
        )
        
        # 确定级别
        overall_level = self._determine_level(total_score)
        
        # 汇总违规
        all_violations = []
        for r in results:
            all_violations.extend(r.violations)
        
        # 生成建议
        actionable_items = self._generate_recommendations(results)
        
        # 生成摘要
        summary = self._generate_summary(total_score, overall_level, results)
        
        return EthicsReport(
            overall_score=total_score,
            overall_level=overall_level,
            rule_results=results,
            summary=summary,
            actionable_items=actionable_items
        )
    
    def _check_rule(self, rule_name: str, content: str) -> EthicsCheckResult:
        """检查单项规则"""
        rule = self.rules[rule_name]
        
        # 计数
        positive_count = 0
        negative_count = 0
        
        for indicator in rule["positive_indicators"]:
            positive_count += len(re.findall(indicator, content, re.IGNORECASE))
        
        for indicator in rule["negative_indicators"]:
            negative_count += len(re.findall(indicator, content, re.IGNORECASE))
        
        # 计算分数
        total_signals = positive_count + negative_count
        if total_signals == 0:
            score = 0.5  # 中性
        else:
            score = positive_count / total_signals
        
        # 确定级别
        level = self._determine_level(score)
        
        # 提取违规
        violations = []
        if negative_count > 0:
            for indicator in rule["negative_indicators"]:
                if re.search(indicator, content, re.IGNORECASE):
                    violations.append(f"发现负面信号: {indicator}")
        
        # 生成建议
        recommendations = []
        if score < 0.7:
            recommendations.append(f"建议增强{rule['description']}方面的表述")
        
        return EthicsCheckResult(
            rule=rule_name,
            score=score,
            level=level,
            violations=violations[:5],  # 限制数量
            recommendations=recommendations
        )
    
    def _determine_level(self, score: float) -> EthicsLevel:
        """确定级别"""
        if score >= self.thresholds[EthicsLevel.EXEMPLARY]:
            return EthicsLevel.EXEMPLARY
        elif score >= self.thresholds[EthicsLevel.COMPLIANT]:
            return EthicsLevel.COMPLIANT
        elif score >= self.thresholds[EthicsLevel.QUESTIONABLE]:
            return EthicsLevel.QUESTIONABLE
        else:
            return EthicsLevel.VIOLATION
    
    def _generate_recommendations(self, results: List[EthicsCheckResult]) -> List[str]:
        """生成行动建议"""
        recommendations = []
        
        low_scores = [r for r in results if r.score < 0.6]
        for r in low_scores:
            rule_desc = self.rules[r.rule]["description"]
            recommendations.append(f"重点关注'{rule_desc}'，当前评分{r.score:.2f}")
        
        return recommendations
    
    def _generate_summary(
        self,
        total_score: float,
        level: EthicsLevel,
        results: List[EthicsCheckResult]
    ) -> str:
        """生成摘要"""
        rule_status = []
        for r in results:
            status = "✓" if r.score >= 0.7 else "✗"
            rule_status.append(f"{status} {r.rule}")
        
        return f"""
伦理检查摘要:
- 综合评分: {total_score:.2f}/1.0
- 伦理级别: {level.value}
- 规则检查: {', '.join(rule_status)}
- 建议: {'通过' if level in [EthicsLevel.EXEMPLARY, EthicsLevel.COMPLIANT] else '需改进'}
""".strip()


# 便捷函数接口
def check_ethics(content: str) -> EthicsReport:
    """便捷伦理检查函数"""
    checker = EthicsChecker()
    return checker.full_check(content)


if __name__ == "__main__":
    # 单元测试
    print("=" * 60)
    print("伦理检查器 - 单元测试")
    print("=" * 60)
    
    checker = EthicsChecker()
    
    # 测试1: 正面内容
    print("\n[测试1] 正面内容检查...")
    positive_content = """
    我们将透明披露所有信息，确保公平决策。
    承诺可兑现，务实推进。
    已声明利益冲突，独立评估。
    关怀利益相关者，追求共赢。
    严格遵守商业伦理和法规。
    """
    result = checker.full_check(positive_content)
    print(f"  综合评分: {result.overall_score:.2f}")
    print(f"  伦理级别: {result.overall_level.value}")
    print(f"  建议数: {len(result.actionable_items)}")
    
    # 测试2: 负面内容
    print("\n[测试2] 负面内容检查...")
    negative_content = """
    隐瞒关键信息，隐藏真实数据。
    过度承诺，无法兑现。
    利益输送，关联交易。
    忽视利益相关者，造成损害。
    违规操作，打擦边球。
    """
    result = checker.full_check(negative_content)
    print(f"  综合评分: {result.overall_score:.2f}")
    print(f"  伦理级别: {result.overall_level.value}")
    print(f"  违规项: {sum(len(r.violations) for r in result.rule_results)}")
    
    # 测试3: 单项检查
    print("\n[测试3] 单项规则检查...")
    for rule_name in checker.rules.keys():
        result = checker._check_rule(rule_name, positive_content)
        print(f"  {rule_name}: {result.score:.2f} ({result.level.value})")
    
    print("\n" + "=" * 60)
    print("单元测试完成")
    print("=" * 60)
    print("\n注意: 本检查器基于规则匹配，复杂情境建议人工复核")