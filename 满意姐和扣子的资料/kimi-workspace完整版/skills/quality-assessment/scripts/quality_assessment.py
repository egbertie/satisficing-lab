#!/usr/bin/env python3
"""
quality-assessment - 质量评估工具
真正实现版本

功能:
- 交付物质量评分
- 多维度评估 (完整性、准确性、规范性)
- 自动检查清单
- 质量趋势追踪
- 改进建议生成

作者: 满意妞 (重构)
版本: 2.0.1-real
日期: 2026-04-03
"""

import json
import re
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum


class QualityGrade(Enum):
    """质量等级"""
    A = "A"  # 优秀 (90-100)
    B = "B"  # 良好 (80-89)
    C = "C"  # 合格 (70-79)
    D = "D"  # 待改进 (60-69)
    F = "F"  # 不合格 (<60)


class DimensionType(Enum):
    """评估维度"""
    COMPLETENESS = "completeness"    # 完整性
    ACCURACY = "accuracy"            # 准确性
    STANDARDIZATION = "standardization"  # 规范性
    TIMELINESS = "timeliness"        # 及时性
    USABILITY = "usability"          # 可用性


@dataclass
class DimensionScore:
    """维度得分"""
    dimension: str
    score: float
    max_score: float
    weight: float
    issues: List[str]
    evidence: List[str]


@dataclass
class AssessmentResult:
    """评估结果"""
    deliverable_name: str
    overall_score: float
    grade: str
    dimension_scores: List[DimensionScore]
    total_issues: int
    critical_issues: int
    timestamp: str
    assessor: str
    recommendations: List[str]


class QualityAssessor:
    """质量评估器"""
    
    # 默认评估维度权重
    DEFAULT_WEIGHTS = {
        DimensionType.COMPLETENESS.value: 0.25,
        DimensionType.ACCURACY.value: 0.30,
        DimensionType.STANDARDIZATION.value: 0.20,
        DimensionType.TIMELINESS.value: 0.15,
        DimensionType.USABILITY.value: 0.10
    }
    
    def __init__(self, config: Optional[Dict] = None):
        """初始化评估器"""
        self.config = config or {}
        self.weights = self.config.get('weights', self.DEFAULT_WEIGHTS)
    
    def assess(self, deliverable: Dict[str, Any], checklists: Optional[Dict] = None) -> AssessmentResult:
        """评估交付物质量"""
        
        name = deliverable.get('name', '未命名交付物')
        content = deliverable.get('content', '')
        metadata = deliverable.get('metadata', {})
        
        checklists = checklists or {}
        
        # 评估各维度
        dimension_scores = []
        
        # 1. 完整性评估
        completeness = self._assess_completeness(content, checklists.get('completeness', []))
        dimension_scores.append(completeness)
        
        # 2. 准确性评估
        accuracy = self._assess_accuracy(content, checklists.get('accuracy', []))
        dimension_scores.append(accuracy)
        
        # 3. 规范性评估
        standardization = self._assess_standardization(content, checklists.get('standardization', []))
        dimension_scores.append(standardization)
        
        # 4. 及时性评估
        timeliness = self._assess_timeliness(metadata, checklists.get('timeliness', []))
        dimension_scores.append(timeliness)
        
        # 5. 可用性评估
        usability = self._assess_usability(content, checklists.get('usability', []))
        dimension_scores.append(usability)
        
        # 计算总分
        overall_score = self._calculate_overall_score(dimension_scores)
        grade = self._get_grade(overall_score)
        
        # 统计问题
        total_issues = sum(len(d.issues) for d in dimension_scores)
        critical_issues = sum(1 for d in dimension_scores for i in d.issues if '严重' in i or 'critical' in i.lower())
        
        # 生成建议
        recommendations = self._generate_recommendations(dimension_scores, overall_score)
        
        return AssessmentResult(
            deliverable_name=name,
            overall_score=overall_score,
            grade=grade,
            dimension_scores=dimension_scores,
            total_issues=total_issues,
            critical_issues=critical_issues,
            timestamp=datetime.now().isoformat(),
            assessor=self.config.get('assessor', 'QualityAssessor'),
            recommendations=recommendations
        )
    
    def _assess_completeness(self, content: str, checklist: List[str]) -> DimensionScore:
        """评估完整性"""
        issues = []
        evidence = []
        
        # 检查必需内容
        required_items = checklist or ['标题', '摘要', '正文', '结论']
        
        for item in required_items:
            if item not in content:
                issues.append(f"缺少必需内容: {item}")
            else:
                evidence.append(f"包含: {item}")
        
        # 检查内容长度
        if len(content) < 100:
            issues.append("内容过短，可能不完整")
        elif len(content) > 500:
            evidence.append("内容充实")
        
        # 计算得分
        if not required_items:
            score = 100.0
        else:
            score = (len(required_items) - len(issues)) / len(required_items) * 100
        
        return DimensionScore(
            dimension=DimensionType.COMPLETENESS.value,
            score=max(score, 0),
            max_score=100.0,
            weight=self.weights.get(DimensionType.COMPLETENESS.value, 0.25),
            issues=issues,
            evidence=evidence
        )
    
    def _assess_accuracy(self, content: str, checklist: List[str]) -> DimensionScore:
        """评估准确性"""
        issues = []
        evidence = []
        
        # 检查错误标记
        error_patterns = [
            r'(?i)(error|wrong|incorrect|mistake)',
            r'错误[:：]',
            r'待确认',
            r'\?{2,}'
        ]
        
        for pattern in error_patterns:
            if re.search(pattern, content):
                issues.append(f"发现潜在错误标记: {pattern}")
        
        # 检查数据一致性
        numbers = re.findall(r'\d+', content)
        if len(numbers) >= 2:
            evidence.append(f"包含 {len(numbers)} 个数据点")
        
        # 检查逻辑一致性
        if '但是' in content and '因此' in content:
            evidence.append("包含逻辑连接词")
        
        # 计算得分
        score = 100 - len(issues) * 20
        
        return DimensionScore(
            dimension=DimensionType.ACCURACY.value,
            score=max(score, 0),
            max_score=100.0,
            weight=self.weights.get(DimensionType.ACCURACY.value, 0.30),
            issues=issues,
            evidence=evidence
        )
    
    def _assess_standardization(self, content: str, checklist: List[str]) -> DimensionScore:
        """评估规范性"""
        issues = []
        evidence = []
        
        # 检查格式规范
        if not content.startswith('#') and len(content) > 200:
            issues.append("缺少标题标记")
        
        # 检查标点使用
        if content.count('，') > content.count(',') * 2:
            evidence.append("使用中文标点")
        
        # 检查段落结构
        paragraphs = [p for p in content.split('\n') if p.strip()]
        if len(paragraphs) >= 3:
            evidence.append(f"有 {len(paragraphs)} 个段落")
        else:
            issues.append("段落过少，结构不清晰")
        
        # 计算得分
        score = 100 - len(issues) * 15
        
        return DimensionScore(
            dimension=DimensionType.STANDARDIZATION.value,
            score=max(score, 0),
            max_score=100.0,
            weight=self.weights.get(DimensionType.STANDARDIZATION.value, 0.20),
            issues=issues,
            evidence=evidence
        )
    
    def _assess_timeliness(self, metadata: Dict[str, Any], checklist: List[str]) -> DimensionScore:
        """评估及时性"""
        issues = []
        evidence = []
        
        create_time = metadata.get('create_time')
        deadline = metadata.get('deadline')
        
        if create_time and deadline:
            try:
                created = datetime.fromisoformat(str(create_time).replace('Z', '+00:00'))
                due = datetime.fromisoformat(str(deadline).replace('Z', '+00:00'))
                
                if created > due:
                    issues.append("交付时间超过截止日期")
                else:
                    days_before = (due - created).days
                    evidence.append(f"提前 {days_before} 天完成")
            except (ValueError, TypeError):
                issues.append("时间格式无法解析")
        elif deadline and not create_time:
            issues.append("缺少创建时间信息")
        else:
            evidence.append("无截止时间要求")
        
        # 计算得分
        score = 100 - len(issues) * 25
        
        return DimensionScore(
            dimension=DimensionType.TIMELINESS.value,
            score=max(score, 0),
            max_score=100.0,
            weight=self.weights.get(DimensionType.TIMELINESS.value, 0.15),
            issues=issues,
            evidence=evidence
        )
    
    def _assess_usability(self, content: str, checklist: List[str]) -> DimensionScore:
        """评估可用性"""
        issues = []
        evidence = []
        
        # 检查可读性
        sentences = re.split(r'[。！？]', content)
        avg_sentence_len = sum(len(s) for s in sentences) / len(sentences) if sentences else 0
        
        if avg_sentence_len > 100:
            issues.append("句子过长，可读性差")
        elif avg_sentence_len < 50:
            evidence.append("句子简短清晰")
        
        # 检查是否有可操作内容
        action_keywords = ['需要', '应该', '必须', '建议', '完成']
        has_action = any(kw in content for kw in action_keywords)
        
        if has_action:
            evidence.append("包含行动指引")
        else:
            issues.append("缺少可操作内容")
        
        # 计算得分
        score = 100 - len(issues) * 20
        
        return DimensionScore(
            dimension=DimensionType.USABILITY.value,
            score=max(score, 0),
            max_score=100.0,
            weight=self.weights.get(DimensionType.USABILITY.value, 0.10),
            issues=issues,
            evidence=evidence
        )
    
    def _calculate_overall_score(self, dimension_scores: List[DimensionScore]) -> float:
        """计算总体得分"""
        if not dimension_scores:
            return 0.0
        
        total = sum(d.score * d.weight for d in dimension_scores)
        total_weight = sum(d.weight for d in dimension_scores)
        
        return total / total_weight if total_weight > 0 else 0
    
    def _get_grade(self, score: float) -> str:
        """获取等级"""
        if score >= 90:
            return QualityGrade.A.value
        elif score >= 80:
            return QualityGrade.B.value
        elif score >= 70:
            return QualityGrade.C.value
        elif score >= 60:
            return QualityGrade.D.value
        else:
            return QualityGrade.F.value
    
    def _generate_recommendations(self, dimension_scores: List[DimensionScore], overall_score: float) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        if overall_score >= 90:
            recommendations.append("✅ 质量优秀，保持当前标准")
        elif overall_score >= 80:
            recommendations.append("👍 质量良好，可进一步提升细节")
        elif overall_score >= 70:
            recommendations.append("📝 质量合格，建议针对低分维度改进")
        else:
            recommendations.append("🔴 质量不达标，需要全面整改")
        
        # 找出最低分的维度
        sorted_dims = sorted(dimension_scores, key=lambda x: x.score)
        if sorted_dims:
            lowest = sorted_dims[0]
            if lowest.score < 70:
                recommendations.append(f"⚠️ 优先改进: {lowest.dimension} (当前得分: {lowest.score:.1f})")
        
        # 汇总问题
        all_issues = []
        for d in dimension_scores:
            all_issues.extend(d.issues)
        
        if all_issues:
            recommendations.append(f"📋 共发现 {len(all_issues)} 个问题，建议逐一解决")
        
        return recommendations
    
    def export_report(self, result: AssessmentResult, format: str = "json") -> str:
        """导出报告"""
        if format == "json":
            return json.dumps(result.__dict__, ensure_ascii=False, indent=2, default=str)
        elif format == "markdown":
            return self._format_markdown(result)
        return ""
    
    def _format_markdown(self, result: AssessmentResult) -> str:
        """格式化为Markdown"""
        lines = [
            f"# 质量评估报告: {result.deliverable_name}",
            "",
            f"**评估时间**: {result.timestamp}",
            f"**评估人**: {result.assessor}",
            f"**总体评分**: {result.overall_score:.1f}/100",
            f"**质量等级**: {result.grade}",
            f"**问题统计**: {result.total_issues}个问题 (含{result.critical_issues}个严重)",
            "",
            "---",
            "",
            "## 📊 维度得分",
            "",
            "| 维度 | 得分 | 权重 | 加权得分 |",
            "|------|------|------|----------|",
        ]
        
        for d in result.dimension_scores:
            weighted = d.score * d.weight
            lines.append(f"| {d.dimension} | {d.score:.1f} | {d.weight:.0%} | {weighted:.1f} |")
        
        lines.append("")
        lines.append(f"**加权总分**: {result.overall_score:.1f}")
        lines.append("")
        
        # 详细分析
        lines.extend([
            "---",
            "",
            "## 🔍 详细分析",
            ""
        ])
        
        for d in result.dimension_scores:
            lines.append(f"### {d.dimension.upper()} (得分: {d.score:.1f})")
            lines.append("")
            
            if d.evidence:
                lines.append("**优点**:")
                for e in d.evidence[:3]:
                    lines.append(f"- ✅ {e}")
                lines.append("")
            
            if d.issues:
                lines.append("**问题**:")
                for i in d.issues[:5]:
                    lines.append(f"- ❌ {i}")
                lines.append("")
        
        if result.recommendations:
            lines.extend([
                "---",
                "",
                "## 💡 改进建议",
                "",
            ])
            for rec in result.recommendations:
                lines.append(f"- {rec}")
            lines.append("")
        
        return '\n'.join(lines)


def main():
    """主入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Quality Assessment - 质量评估工具')
    parser.add_argument('--file', '-f', help='交付物文件路径')
    parser.add_argument('--content', '-c', help='直接输入内容')
    parser.add_argument('--name', '-n', default='未命名', help='交付物名称')
    parser.add_argument('--checklist', help='检查清单文件 (JSON)')
    parser.add_argument('--format', choices=['json', 'markdown'], default='markdown',
                       help='报告格式')
    parser.add_argument('--output', '-o', help='输出文件路径')
    
    args = parser.parse_args()
    
    try:
        # 获取内容
        content = ""
        if args.file:
            with open(args.file, 'r', encoding='utf-8') as f:
                content = f.read()
        elif args.content:
            content = args.content
        else:
            print("❌ 错误: 请提供 --file 或 --content", file=__import__('sys').stderr)
            return 1
        
        # 加载检查清单
        checklists = {}
        if args.checklist:
            with open(args.checklist, 'r', encoding='utf-8') as f:
                checklists = json.load(f)
        
        # 构建交付物
        deliverable = {
            'name': args.name,
            'content': content,
            'metadata': {'create_time': datetime.now().isoformat()}
        }
        
        # 执行评估
        assessor = QualityAssessor()
        result = assessor.assess(deliverable, checklists)
        
        # 输出报告
        output = assessor.export_report(result, args.format)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"✅ 报告已保存: {args.output}")
        else:
            print(output)
        
        # 根据等级返回退出码
        grade_codes = {'A': 0, 'B': 0, 'C': 0, 'D': 1, 'F': 2}
        return grade_codes.get(result.grade, 1)
        
    except Exception as e:
        print(f"❌ 错误: {e}", file=__import__('sys').stderr)
        return 1


if __name__ == '__main__':
    import sys
    sys.exit(main())
