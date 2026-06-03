"""
案例分析器 - Case Analyzer
核心模块: 硬科技合伙人决策案例深度分析
版本: 1.0.0
日期: 2026-04-02
Expert_ID: CASE-ANALYZER
"""

import json
import re
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple
from enum import Enum


class CaseType(Enum):
    """案例类型"""
    PARTNER_CONFLICT = "partner_conflict"    # 合伙人冲突
    EQUITY_DISPUTE = "equity_dispute"       # 股权纠纷
    SUCCESS = "success"                      # 成功案例
    FAILURE = "failure"                      # 失败案例


@dataclass
class CaseFactor:
    """案例因子"""
    factor_name: str
    present: bool              # 是否存在
    impact: str                # 影响: positive/negative/neutral
    severity: int              # 严重程度 1-5


@dataclass
class CaseAnalysis:
    """案例分析结果"""
    case_id: str
    case_type: CaseType
    factors: List[CaseFactor]
    key_lessons: List[str]
    red_flags: List[str]
    recommendations: List[str]
    pattern_match: str         # 匹配的历史模式


class CaseAnalyzer:
    """
    案例分析器
    
    分析硬科技领域的合伙人决策案例:
    - 股权分配纠纷
    - 创始人冲突
    - 技术合伙人退出
    - 成功案例模式
    
    分析方法:
    - 因子提取
    - 模式匹配
    - 教训提取
    - 风险预警
    """
    
    def __init__(self):
        # 案例因子库
        self.factor_library = {
            "partner_conflict": [
                "股权分配不均", "贡献认知差异", "退出机制缺失",
                "角色边界模糊", "沟通机制失效", "信任破裂"
            ],
            "equity_dispute": [
                "口头协议", "未签协议", "估值分歧",
                "期权池争议", "回购条款不明", "稀释条款不清"
            ],
            "success": [
                "明确角色分工", "书面协议完备", "动态调整机制",
                "定期沟通", "共同愿景", "互补技能"
            ],
            "warning_signs": [
                "一直拖着不签协议", "以后再谈", "相信我",
                "避免讨论退出", "股权比例敏感", "贡献难以量化"
            ]
        }
        
        # 历史案例模式
        self.patterns = {
            "比特大陆模式": {
                "factors": ["股权分配不均", "创始人冲突", "技术路线分歧"],
                "outcome": "分裂为比特大陆和比特微"
            },
            "寒武纪模式": {
                "factors": ["兄弟合伙人", "股权纠纷", "巨额索赔"],
                "outcome": "陈天石vs陈云霁43亿纠纷"
            },
            "理想模式": {
                "factors": ["明确角色", "书面协议", "动态调整"],
                "outcome": "成功IPO，合伙人稳定"
            }
        }
    
    def analyze_case(self, case_description: str, case_id: str = None) -> CaseAnalysis:
        """
        分析案例
        
        步骤:
        1. 提取案例因子
        2. 匹配历史模式
        3. 识别红旗信号
        4. 生成建议
        """
        case_id = case_id or f"CASE-{hash(case_description) % 10000:04d}"
        
        # 1. 提取因子
        factors = self._extract_factors(case_description)
        
        # 2. 确定案例类型
        case_type = self._determine_case_type(factors)
        
        # 3. 匹配模式
        pattern_match = self._match_pattern(factors)
        
        # 4. 提取教训
        lessons = self._extract_lessons(factors, case_type)
        
        # 5. 识别红旗
        red_flags = self._identify_red_flags(case_description)
        
        # 6. 生成建议
        recommendations = self._generate_recommendations(factors, case_type)
        
        return CaseAnalysis(
            case_id=case_id,
            case_type=case_type,
            factors=factors,
            key_lessons=lessons,
            red_flags=red_flags,
            recommendations=recommendations,
            pattern_match=pattern_match
        )
    
    def _extract_factors(self, description: str) -> List[CaseFactor]:
        """提取案例因子"""
        factors = []
        
        # 检查冲突因子
        for factor in self.factor_library["partner_conflict"]:
            present = factor in description or re.search(factor, description)
            if present:
                factors.append(CaseFactor(
                    factor_name=factor,
                    present=True,
                    impact="negative",
                    severity=4 if "破裂" in factor else 3
                ))
        
        # 检查股权因子
        for factor in self.factor_library["equity_dispute"]:
            present = factor in description or re.search(factor, description)
            if present:
                factors.append(CaseFactor(
                    factor_name=factor,
                    present=True,
                    impact="negative",
                    severity=5 if "未签" in factor else 3
                ))
        
        # 检查成功因子
        for factor in self.factor_library["success"]:
            present = factor in description or re.search(factor, description)
            if present:
                factors.append(CaseFactor(
                    factor_name=factor,
                    present=True,
                    impact="positive",
                    severity=2
                ))
        
        return factors
    
    def _determine_case_type(self, factors: List[CaseFactor]) -> CaseType:
        """确定案例类型"""
        conflict_count = sum(1 for f in factors if "冲突" in f.factor_name or "股权" in f.factor_name)
        success_count = sum(1 for f in factors if f.impact == "positive")
        
        if conflict_count >= 3:
            return CaseType.PARTNER_CONFLICT
        elif any("股权" in f.factor_name for f in factors):
            return CaseType.EQUITY_DISPUTE
        elif success_count >= 3:
            return CaseType.SUCCESS
        else:
            return CaseType.FAILURE
    
    def _match_pattern(self, factors: List[CaseFactor]) -> str:
        """匹配历史模式"""
        factor_names = {f.factor_name for f in factors}
        
        best_match = None
        best_score = 0
        
        for pattern_name, pattern_data in self.patterns.items():
            pattern_factors = set(pattern_data["factors"])
            overlap = factor_names & pattern_factors
            score = len(overlap) / len(pattern_factors) if pattern_factors else 0
            
            if score > best_score:
                best_score = score
                best_match = f"{pattern_name} (匹配度: {score*100:.0f}%)"
        
        return best_match or "未匹配到已知模式"
    
    def _extract_lessons(self, factors: List[CaseFactor], case_type: CaseType) -> List[str]:
        """提取教训"""
        lessons = []
        
        # 根据因子生成教训
        negative_factors = [f for f in factors if f.impact == "negative"]
        for factor in negative_factors:
            if "协议" in factor.factor_name:
                lessons.append("所有约定必须书面化，口头承诺无法律效力")
            elif "股权" in factor.factor_name:
                lessons.append("股权分配需要动态调整机制，而非一次性决定")
            elif "沟通" in factor.factor_name:
                lessons.append("建立定期合伙人沟通机制，避免问题积累")
            elif "信任" in factor.factor_name:
                lessons.append("信任是合伙人关系的基石，一旦破裂难以修复")
        
        return lessons[:5]  # 限制数量
    
    def _identify_red_flags(self, description: str) -> List[str]:
        """识别红旗信号"""
        red_flags = []
        
        for signal in self.factor_library["warning_signs"]:
            if signal in description or re.search(signal.replace('"', ''), description):
                red_flags.append(f"⚠️ 发现红旗信号: {signal}")
        
        return red_flags
    
    def _generate_recommendations(
        self,
        factors: List[CaseFactor],
        case_type: CaseType
    ) -> List[str]:
        """生成建议"""
        recommendations = []
        
        if case_type == CaseType.PARTNER_CONFLICT:
            recommendations.append("建议引入第三方调解")
            recommendations.append("评估股权回购或分拆的可能性")
        
        if case_type == CaseType.EQUITY_DISPUTE:
            recommendations.append("立即寻求法律建议")
            recommendations.append("收集所有书面/电子沟通记录")
        
        # 预防性建议
        if not any("书面协议" in f.factor_name for f in factors):
            recommendations.append("建立/完善合伙人协议")
        
        if not any("退出机制" in f.factor_name for f in factors):
            recommendations.append("明确合伙人退出机制")
        
        return recommendations
    
    def generate_case_summary(self, analysis: CaseAnalysis) -> str:
        """生成案例摘要"""
        return f"""
案例分析报告: {analysis.case_id}
========================================
案例类型: {analysis.case_type.value}
模式匹配: {analysis.pattern_match}

关键因子 ({len(analysis.factors)}个):
{chr(10).join(f"- {f.factor_name} (影响: {f.impact}, 严重度: {f.severity})" for f in analysis.factors)}

红旗信号 ({len(analysis.red_flags)}个):
{chr(10).join(analysis.red_flags) if analysis.red_flags else "无"}

核心教训:
{chr(10).join(f"{i+1}. {lesson}" for i, lesson in enumerate(analysis.key_lessons))}

建议行动:
{chr(10).join(f"- {rec}" for rec in analysis.recommendations)}
""".strip()


# 便捷函数接口
def analyze_partner_case(case_description: str, case_id: str = None) -> CaseAnalysis:
    """便捷案例分析函数"""
    analyzer = CaseAnalyzer()
    return analyzer.analyze_case(case_description, case_id)


if __name__ == "__main__":
    # 单元测试
    print("=" * 60)
    print("案例分析器 - 单元测试")
    print("=" * 60)
    
    analyzer = CaseAnalyzer()
    
    # 测试1: 冲突案例
    print("\n[测试1] 合伙人冲突案例分析...")
    conflict_case = """
    两位创始人股权分配不均，导致贡献认知差异。
    没有签署正式协议，只有口头约定。
    沟通机制失效，最终信任破裂。
    一方说"一直拖着不签协议"，另一方认为"相信我"。
    """
    result = analyzer.analyze_case(conflict_case, "TEST-001")
    print(f"  案例ID: {result.case_id}")
    print(f"  案例类型: {result.case_type.value}")
    print(f"  因子数: {len(result.factors)}")
    print(f"  模式匹配: {result.pattern_match}")
    print(f"  红旗数: {len(result.red_flags)}")
    
    # 测试2: 生成摘要
    print("\n[测试2] 生成案例摘要...")
    summary = analyzer.generate_case_summary(result)
    print(summary[:500] + "...")
    
    # 测试3: 成功案例
    print("\n[测试3] 成功案例分析...")
    success_case = """
    明确角色分工，书面协议完备。
    有动态调整机制，定期沟通。
    共同愿景清晰，技能互补。
    """
    result = analyzer.analyze_case(success_case, "TEST-002")
    print(f"  案例类型: {result.case_type.value}")
    print(f"  积极因子: {sum(1 for f in result.factors if f.impact == 'positive')}")
    
    print("\n" + "=" * 60)
    print("单元测试完成")
    print("=" * 60)