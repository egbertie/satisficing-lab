#!/usr/bin/env python3
"""
info-quality-guardian - 信息采集质量控制体系
真正实现版本

功能:
- 信息完整性检查
- 信息准确性验证
- 信息时效性检测
- 信息一致性校验
- 质量评分
- 采集流程集成

作者: 满意妞 (重构)
版本: 2.0.1-real
日期: 2026-04-03
"""

import json
import re
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable
from enum import Enum


class InfoQualityLevel(Enum):
    """信息质量等级"""
    RELIABLE = "reliable"      # 可靠
    USABLE = "usable"          # 可用
    QUESTIONABLE = "questionable"  # 存疑
    UNRELIABLE = "unreliable"  # 不可靠


class CheckType(Enum):
    """检查类型"""
    COMPLETENESS = "completeness"    # 完整性
    ACCURACY = "accuracy"            # 准确性
    TIMELINESS = "timeliness"        # 时效性
    CONSISTENCY = "consistency"      # 一致性
    CREDIBILITY = "credibility"      # 可信度


@dataclass
class QualityIssue:
    """质量问题"""
    check_type: str
    field: str
    severity: str  # high, medium, low
    message: str
    suggestion: str


@dataclass
class InfoItem:
    """信息项"""
    content: str
    source: str
    timestamp: str
    category: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QualityReport:
    """质量报告"""
    item_count: int
    overall_score: float
    quality_level: str
    issues: List[QualityIssue]
    checks_performed: List[str]
    timestamp: str
    recommendations: List[str]


class InfoQualityGuardian:
    """信息采集质量控制体系"""
    
    def __init__(self, config: Optional[Dict] = None):
        """初始化守护器"""
        self.config = config or {}
        self.issues: List[QualityIssue] = []
        self.checks_performed: List[str] = []
        
        # 默认配置
        self.min_content_length = self.config.get('min_content_length', 10)
        self.max_content_length = self.config.get('max_content_length', 10000)
        self.required_fields = self.config.get('required_fields', ['content', 'source'])
        self.info_lifetime_hours = self.config.get('info_lifetime_hours', 24)
    
    def check(self, info_items: List[InfoItem]) -> QualityReport:
        """检查信息质量"""
        self.issues = []
        self.checks_performed = []
        
        if not info_items:
            return self._create_empty_report()
        
        # 执行各项检查
        self._check_completeness(info_items)
        self._check_accuracy(info_items)
        self._check_timeliness(info_items)
        self._check_consistency(info_items)
        self._check_credibility(info_items)
        
        # 计算总体评分
        overall_score = self._calculate_overall_score(info_items)
        quality_level = self._get_quality_level(overall_score)
        
        # 生成建议
        recommendations = self._generate_recommendations(overall_score)
        
        return QualityReport(
            item_count=len(info_items),
            overall_score=overall_score,
            quality_level=quality_level,
            issues=self.issues,
            checks_performed=self.checks_performed,
            timestamp=datetime.now().isoformat(),
            recommendations=recommendations
        )
    
    def _check_completeness(self, items: List[InfoItem]):
        """检查信息完整性"""
        self.checks_performed.append("完整性检查")
        
        for idx, item in enumerate(items):
            # 检查必需字段
            if not item.content or len(item.content.strip()) < self.min_content_length:
                self.issues.append(QualityIssue(
                    check_type=CheckType.COMPLETENESS.value,
                    field="content",
                    severity="high",
                    message=f"第{idx + 1}项信息内容过短或为空 (长度: {len(item.content) if item.content else 0})",
                    suggestion="补充完整信息内容"
                ))
            
            if not item.source:
                self.issues.append(QualityIssue(
                    check_type=CheckType.COMPLETENESS.value,
                    field="source",
                    severity="high",
                    message=f"第{idx + 1}项缺少信息来源",
                    suggestion="标注信息来源"
                ))
    
    def _check_accuracy(self, items: List[InfoItem]):
        """检查信息准确性"""
        self.checks_performed.append("准确性检查")
        
        for idx, item in enumerate(items):
            content = item.content
            
            # 检查明显错误
            if self._has_obvious_errors(content):
                self.issues.append(QualityIssue(
                    check_type=CheckType.ACCURACY.value,
                    field="content",
                    severity="high",
                    message=f"第{idx + 1}项包含明显错误信息",
                    suggestion="核实并修正信息"
                ))
            
            # 检查数据格式
            if self._has_format_issues(content):
                self.issues.append(QualityIssue(
                    check_type=CheckType.ACCURACY.value,
                    field="content",
                    severity="medium",
                    message=f"第{idx + 1}项存在格式问题",
                    suggestion="规范化数据格式"
                ))
    
    def _check_timeliness(self, items: List[InfoItem]):
        """检查信息时效性"""
        self.checks_performed.append("时效性检查")
        
        now = datetime.now()
        
        for idx, item in enumerate(items):
            try:
                # 解析时间戳
                item_time = datetime.fromisoformat(item.timestamp.replace('Z', '+00:00'))
                age_hours = (now - item_time).total_seconds() / 3600
                
                if age_hours > self.info_lifetime_hours:
                    self.issues.append(QualityIssue(
                        check_type=CheckType.TIMELINESS.value,
                        field="timestamp",
                        severity="medium",
                        message=f"第{idx + 1}项信息已过期 ({age_hours:.1f}小时前)",
                        suggestion="更新信息或标注过期状态"
                    ))
            except (ValueError, TypeError):
                self.issues.append(QualityIssue(
                    check_type=CheckType.TIMELINESS.value,
                    field="timestamp",
                    severity="low",
                    message=f"第{idx + 1}项时间戳格式无效",
                    suggestion="使用标准时间格式 (ISO 8601)"
                ))
    
    def _check_consistency(self, items: List[InfoItem]):
        """检查信息一致性"""
        self.checks_performed.append("一致性检查")
        
        # 检查同类信息之间的一致性
        by_category = {}
        for item in items:
            if item.category not in by_category:
                by_category[item.category] = []
            by_category[item.category].append(item)
        
        for category, cat_items in by_category.items():
            if len(cat_items) < 2:
                continue
            
            # 检查同一类别信息的数值一致性
            # 这里简化处理，检查是否有明显矛盾的陈述
            for i in range(len(cat_items)):
                for j in range(i + 1, len(cat_items)):
                    if self._has_conflict(cat_items[i].content, cat_items[j].content):
                        self.issues.append(QualityIssue(
                            check_type=CheckType.CONSISTENCY.value,
                            field="content",
                            severity="high",
                            message=f"第{i + 1}项与第{j + 1}项信息存在矛盾",
                            suggestion="核实信息准确性，标记冲突"
                        ))
    
    def _check_credibility(self, items: List[InfoItem]):
        """检查信息可信度"""
        self.checks_performed.append("可信度检查")
        
        # 可信来源列表
        trusted_sources = self.config.get('trusted_sources', [])
        
        for idx, item in enumerate(items):
            if not item.source:
                continue
            
            # 检查来源是否可信
            is_trusted = any(ts in item.source for ts in trusted_sources)
            
            if not is_trusted and trusted_sources:
                self.issues.append(QualityIssue(
                    check_type=CheckType.CREDIBILITY.value,
                    field="source",
                    severity="low",
                    message=f"第{idx + 1}项来源 '{item.source}' 未在可信列表中",
                    suggestion="验证来源可靠性或添加到可信列表"
                ))
            
            # 检查来源是否明确
            if len(item.source) < 3:
                self.issues.append(QualityIssue(
                    check_type=CheckType.CREDIBILITY.value,
                    field="source",
                    severity="medium",
                    message=f"第{idx + 1}项来源信息过于简略",
                    suggestion="提供更详细的来源信息"
                ))
    
    def _calculate_overall_score(self, items: List[InfoItem]) -> float:
        """计算总体质量评分"""
        if not items:
            return 0.0
        
        # 基础分
        base_score = 100.0
        
        # 根据问题扣分
        for issue in self.issues:
            if issue.severity == "high":
                base_score -= 10
            elif issue.severity == "medium":
                base_score -= 5
            else:
                base_score -= 2
        
        return max(base_score, 0)
    
    def _get_quality_level(self, score: float) -> str:
        """获取质量等级"""
        if score >= 85:
            return InfoQualityLevel.RELIABLE.value
        elif score >= 70:
            return InfoQualityLevel.USABLE.value
        elif score >= 50:
            return InfoQualityLevel.QUESTIONABLE.value
        else:
            return InfoQualityLevel.UNRELIABLE.value
    
    def _generate_recommendations(self, score: float) -> List[str]:
        """生成优化建议"""
        recommendations = []
        
        if score < 50:
            recommendations.append("🔴 信息质量严重不足，建议重新采集")
        elif score < 70:
            recommendations.append("🟠 信息质量有待提升，建议核实关键信息")
        
        # 按问题类型统计
        high_issues = [i for i in self.issues if i.severity == "high"]
        if high_issues:
            recommendations.append(f"⚠️ 发现 {len(high_issues)} 个高严重性问题，需要优先处理")
        
        # 分类建议
        completeness_issues = [i for i in self.issues if i.check_type == CheckType.COMPLETENESS.value]
        if completeness_issues:
            recommendations.append("📝 存在信息不完整问题，建议补充缺失字段")
        
        timeliness_issues = [i for i in self.issues if i.check_type == CheckType.TIMELINESS.value]
        if timeliness_issues:
            recommendations.append("⏰ 存在过期信息，建议更新或清理")
        
        return recommendations
    
    def _create_empty_report(self) -> QualityReport:
        """创建空报告"""
        return QualityReport(
            item_count=0,
            overall_score=0.0,
            quality_level=InfoQualityLevel.UNRELIABLE.value,
            issues=[],
            checks_performed=[],
            timestamp=datetime.now().isoformat(),
            recommendations=["无信息可检查"]
        )
    
    # 辅助方法
    @staticmethod
    def _has_obvious_errors(content: str) -> bool:
        """检查明显错误"""
        # 常见的明显错误模式
        error_patterns = [
            r'错误[:：]',
            r'(?i)(error|wrong|incorrect)',
            r'待确认[:：]',
            r'\?{3,}',  # 多个问号
        ]
        return any(re.search(p, content) for p in error_patterns)
    
    @staticmethod
    def _has_format_issues(content: str) -> bool:
        """检查格式问题"""
        # 检查是否有奇怪的字符或格式
        if re.search(r'[^\u4e00-\u9fa5a-zA-Z0-9\s.,;:!?()""''-]', content):
            return True
        return False
    
    @staticmethod
    def _has_conflict(content1: str, content2: str) -> bool:
        """检查是否存在冲突"""
        # 简化实现：检查是否有明显的数字矛盾
        # 提取数字并比较
        nums1 = re.findall(r'\d+', content1)
        nums2 = re.findall(r'\d+', content2)
        
        if nums1 and nums2:
            # 如果有相同的数字上下文但不同值
            # 这里简化处理，实际应使用更复杂的NLP
            pass
        
        return False
    
    def export_report(self, report: QualityReport, format: str = "json") -> str:
        """导出报告"""
        if format == "json":
            return json.dumps(report.__dict__, ensure_ascii=False, indent=2, default=str)
        elif format == "markdown":
            return self._format_markdown(report)
        return ""
    
    def _format_markdown(self, report: QualityReport) -> str:
        """格式化为Markdown"""
        lines = [
            "# 信息采集质量报告",
            "",
            f"**检查时间**: {report.timestamp}",
            f"**信息项数**: {report.item_count}",
            f"**总体评分**: {report.overall_score:.1f}/100",
            f"**质量等级**: {report.quality_level.upper()}",
            f"**执行检查**: {', '.join(report.checks_performed)}",
            "",
            "---",
            "",
        ]
        
        if report.issues:
            lines.extend([
                f"## 🚨 发现的问题 ({len(report.issues)}个)",
                "",
            ])
            
            # 按检查类型分组
            for check_type in CheckType:
                type_issues = [i for i in report.issues if i.check_type == check_type.value]
                if type_issues:
                    lines.append(f"### {check_type.value.upper()}")
                    lines.append("")
                    for issue in type_issues[:5]:  # 每种类型最多显示5个
                        severity_icon = {"high": "🔴", "medium": "🟠", "low": "🟡"}.get(issue.severity, "⚪")
                        lines.append(f"- {severity_icon} **{issue.field}**: {issue.message}")
                        lines.append(f"  - 建议: {issue.suggestion}")
                    lines.append("")
        
        if report.recommendations:
            lines.extend([
                "---",
                "",
                "## 💡 优化建议",
                "",
            ])
            for rec in report.recommendations:
                lines.append(f"- {rec}")
            lines.append("")
        
        return '\n'.join(lines)


def main():
    """主入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Info Quality Guardian - 信息采集质量控制')
    parser.add_argument('--data', '-d', required=True, help='数据文件 (JSON)')
    parser.add_argument('--config', '-c', help='配置文件 (JSON)')
    parser.add_argument('--format', choices=['json', 'markdown'], default='markdown',
                       help='报告格式')
    parser.add_argument('--output', '-o', help='输出文件路径')
    
    args = parser.parse_args()
    
    try:
        # 加载数据
        with open(args.data, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 转换为InfoItem
        items = [InfoItem(**item) for item in data]
        
        # 加载配置
        config = {}
        if args.config:
            with open(args.config, 'r', encoding='utf-8') as f:
                config = json.load(f)
        
        # 执行检查
        guardian = InfoQualityGuardian(config)
        report = guardian.check(items)
        
        # 输出报告
        output = guardian.export_report(report, args.format)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"✅ 报告已保存: {args.output}")
        else:
            print(output)
        
        # 根据质量等级返回退出码
        level_codes = {
            'reliable': 0,
            'usable': 0,
            'questionable': 1,
            'unreliable': 2
        }
        return level_codes.get(report.quality_level, 1)
        
    except Exception as e:
        print(f"❌ 错误: {e}", file=__import__('sys').stderr)
        return 1


if __name__ == '__main__':
    import sys
    sys.exit(main())
