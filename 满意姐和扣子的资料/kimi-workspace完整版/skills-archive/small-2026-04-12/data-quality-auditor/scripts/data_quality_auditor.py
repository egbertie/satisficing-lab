#!/usr/bin/env python3
"""
data-quality-auditor - 数据质量审计器
真正实现版本

功能:
- 数据完整性检查
- 数据准确性验证
- 数据一致性检测
- 数据质量评分
- 问题数据标记
- 质量报告生成

作者: 满意妞 (重构)
版本: 2.0.1-real
日期: 2026-04-03
"""

import json
import re
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable
from enum import Enum


class QualityLevel(Enum):
    """质量等级"""
    EXCELLENT = "excellent"  # 90-100%
    GOOD = "good"            # 80-89%
    FAIR = "fair"            # 70-79%
    POOR = "poor"            # 60-69%
    CRITICAL = "critical"    # < 60%


class IssueType(Enum):
    """问题类型"""
    MISSING = "missing"           # 缺失值
    INVALID = "invalid"           # 无效值
    INCONSISTENT = "inconsistent" # 不一致
    DUPLICATE = "duplicate"       # 重复
    OUTLIER = "outlier"           # 异常值
    FORMAT_ERROR = "format_error" # 格式错误


@dataclass
class DataIssue:
    """数据问题"""
    issue_type: str
    field: str
    row_index: Optional[int]
    value: Any
    expected: Any
    message: str
    severity: str  # high, medium, low


@dataclass
class FieldStats:
    """字段统计"""
    field_name: str
    total_count: int
    missing_count: int
    unique_count: int
    valid_count: int
    completeness: float  # 完整度
    validity: float      # 有效度


@dataclass
class QualityReport:
    """质量报告"""
    total_records: int
    total_fields: int
    overall_score: float
    quality_level: str
    issues: List[DataIssue]
    field_stats: List[FieldStats]
    checks_performed: List[str]
    timestamp: str
    recommendations: List[str]


class DataQualityAuditor:
    """数据质量审计器"""
    
    def __init__(self, config: Optional[Dict] = None):
        """初始化审计器"""
        self.config = config or {}
        self.issues: List[DataIssue] = []
        self.checks_performed: List[str] = []
    
    def audit(self, data: List[Dict[str, Any]], rules: Optional[Dict] = None) -> QualityReport:
        """审计数据质量"""
        self.issues = []
        self.checks_performed = []
        
        if not data:
            return self._create_empty_report()
        
        rules = rules or {}
        
        # 执行各项检查
        self._check_completeness(data)
        self._check_validity(data, rules)
        self._check_consistency(data)
        self._check_duplicates(data)
        self._check_format(data, rules)
        
        # 计算统计信息
        field_stats = self._calculate_field_stats(data)
        
        # 计算总体评分
        overall_score = self._calculate_overall_score(data, field_stats)
        quality_level = self._get_quality_level(overall_score)
        
        # 生成建议
        recommendations = self._generate_recommendations(overall_score, field_stats)
        
        return QualityReport(
            total_records=len(data),
            total_fields=len(data[0]) if data else 0,
            overall_score=overall_score,
            quality_level=quality_level,
            issues=self.issues,
            field_stats=field_stats,
            checks_performed=self.checks_performed,
            timestamp=datetime.now().isoformat(),
            recommendations=recommendations
        )
    
    def _check_completeness(self, data: List[Dict[str, Any]]):
        """检查数据完整性"""
        self.checks_performed.append("完整性检查")
        
        if not data:
            return
        
        fields = list(data[0].keys())
        
        for row_idx, record in enumerate(data):
            for field in fields:
                value = record.get(field)
                if value is None or value == "" or (isinstance(value, str) and value.strip() == ""):
                    self.issues.append(DataIssue(
                        issue_type=IssueType.MISSING.value,
                        field=field,
                        row_index=row_idx,
                        value=value,
                        expected="非空值",
                        message=f"字段 '{field}' 在第 {row_idx + 1} 行缺失",
                        severity="high"
                    ))
    
    def _check_validity(self, data: List[Dict[str, Any]], rules: Dict):
        """检查数据有效性"""
        self.checks_performed.append("有效性检查")
        
        if not data:
            return
        
        # 获取字段类型规则
        field_types = rules.get('field_types', {})
        
        for row_idx, record in enumerate(data):
            for field, value in record.items():
                if value is None or value == "":
                    continue  # 缺失值已在完整性检查中处理
                
                field_type = field_types.get(field)
                if not field_type:
                    continue
                
                # 类型检查
                if field_type == 'integer' and not self._is_integer(value):
                    self.issues.append(DataIssue(
                        issue_type=IssueType.INVALID.value,
                        field=field,
                        row_index=row_idx,
                        value=value,
                        expected="整数",
                        message=f"字段 '{field}' 应为整数，实际值: {value}",
                        severity="medium"
                    ))
                elif field_type == 'number' and not self._is_number(value):
                    self.issues.append(DataIssue(
                        issue_type=IssueType.INVALID.value,
                        field=field,
                        row_index=row_idx,
                        value=value,
                        expected="数字",
                        message=f"字段 '{field}' 应为数字，实际值: {value}",
                        severity="medium"
                    ))
                elif field_type == 'email' and not self._is_email(value):
                    self.issues.append(DataIssue(
                        issue_type=IssueType.FORMAT_ERROR.value,
                        field=field,
                        row_index=row_idx,
                        value=value,
                        expected="有效邮箱格式",
                        message=f"字段 '{field}' 邮箱格式无效: {value}",
                        severity="medium"
                    ))
                elif field_type == 'date' and not self._is_date(value):
                    self.issues.append(DataIssue(
                        issue_type=IssueType.FORMAT_ERROR.value,
                        field=field,
                        row_index=row_idx,
                        value=value,
                        expected="日期格式 (YYYY-MM-DD)",
                        message=f"字段 '{field}' 日期格式无效: {value}",
                        severity="medium"
                    ))
    
    def _check_consistency(self, data: List[Dict[str, Any]]):
        """检查数据一致性"""
        self.checks_performed.append("一致性检查")
        
        # 检查数值范围一致性
        numeric_fields = self._get_numeric_fields(data)
        
        for field in numeric_fields:
            values = [r[field] for r in data if r.get(field) is not None]
            if values:
                mean = sum(values) / len(values)
                std = (sum((v - mean) ** 2 for v in values) / len(values)) ** 0.5
                
                # 标记异常值 (>3σ)
                for row_idx, record in enumerate(data):
                    value = record.get(field)
                    if value is not None and std > 0:
                        if abs(value - mean) > 3 * std:
                            self.issues.append(DataIssue(
                                issue_type=IssueType.OUTLIER.value,
                                field=field,
                                row_index=row_idx,
                                value=value,
                                expected=f"正常范围 ({mean - 3*std:.2f} ~ {mean + 3*std:.2f})",
                                message=f"字段 '{field}' 存在异常值: {value}",
                                severity="low"
                            ))
    
    def _check_duplicates(self, data: List[Dict[str, Any]]):
        """检查重复数据"""
        self.checks_performed.append("重复性检查")
        
        seen = {}
        for row_idx, record in enumerate(data):
            # 基于关键字段生成唯一键
            key_fields = self.config.get('key_fields', list(record.keys()))
            key = tuple(str(record.get(f, '')) for f in key_fields)
            
            if key in seen:
                self.issues.append(DataIssue(
                    issue_type=IssueType.DUPLICATE.value,
                    field=",".join(key_fields),
                    row_index=row_idx,
                    value=key,
                    expected="唯一记录",
                    message=f"第 {row_idx + 1} 行与第 {seen[key] + 1} 行重复",
                    severity="medium"
                ))
            else:
                seen[key] = row_idx
    
    def _check_format(self, data: List[Dict[str, Any]], rules: Dict):
        """检查格式规范"""
        self.checks_performed.append("格式检查")
        
        format_rules = rules.get('format_rules', {})
        
        for row_idx, record in enumerate(data):
            for field, pattern in format_rules.items():
                value = record.get(field)
                if value and not re.match(pattern, str(value)):
                    self.issues.append(DataIssue(
                        issue_type=IssueType.FORMAT_ERROR.value,
                        field=field,
                        row_index=row_idx,
                        value=value,
                        expected=f"匹配模式: {pattern}",
                        message=f"字段 '{field}' 格式不符合规范: {value}",
                        severity="low"
                    ))
    
    def _calculate_field_stats(self, data: List[Dict[str, Any]]) -> List[FieldStats]:
        """计算字段统计信息"""
        if not data:
            return []
        
        fields = list(data[0].keys())
        stats = []
        
        for field in fields:
            values = [r.get(field) for r in data]
            total = len(values)
            missing = sum(1 for v in values if v is None or v == "")
            unique = len(set(str(v) for v in values if v is not None and v != ""))
            valid = total - missing
            
            stats.append(FieldStats(
                field_name=field,
                total_count=total,
                missing_count=missing,
                unique_count=unique,
                valid_count=valid,
                completeness=(total - missing) / total if total > 0 else 0,
                validity=valid / total if total > 0 else 0
            ))
        
        return stats
    
    def _calculate_overall_score(self, data: List[Dict[str, Any]], field_stats: List[FieldStats]) -> float:
        """计算总体质量评分"""
        if not data or not field_stats:
            return 0.0
        
        # 基于字段统计计算
        total_completeness = sum(s.completeness for s in field_stats)
        avg_completeness = total_completeness / len(field_stats)
        
        # 基于问题数量扣分
        issue_penalty = len(self.issues) * 2  # 每个问题扣2分
        
        score = avg_completeness * 100 - issue_penalty
        return max(score, 0)
    
    def _get_quality_level(self, score: float) -> str:
        """获取质量等级"""
        if score >= 90:
            return QualityLevel.EXCELLENT.value
        elif score >= 80:
            return QualityLevel.GOOD.value
        elif score >= 70:
            return QualityLevel.FAIR.value
        elif score >= 60:
            return QualityLevel.POOR.value
        else:
            return QualityLevel.CRITICAL.value
    
    def _generate_recommendations(self, score: float, field_stats: List[FieldStats]) -> List[str]:
        """生成优化建议"""
        recommendations = []
        
        if score < 60:
            recommendations.append("🔴 数据质量严重不达标，建议暂停使用并全面清洗")
        elif score < 80:
            recommendations.append("🟠 数据质量有待提升，建议针对性修复")
        
        # 检查缺失率高的字段
        for stat in field_stats:
            if stat.completeness < 0.8:
                recommendations.append(
                    f"📝 字段 '{stat.field_name}' 缺失率 {(1-stat.completeness)*100:.1f}%，建议补充数据"
                )
        
        # 检查高严重性问题
        high_severity = [i for i in self.issues if i.severity == "high"]
        if high_severity:
            recommendations.append(
                f"⚠️ 发现 {len(high_severity)} 个高严重性问题，需要优先处理"
            )
        
        return recommendations
    
    def _create_empty_report(self) -> QualityReport:
        """创建空报告"""
        return QualityReport(
            total_records=0,
            total_fields=0,
            overall_score=0.0,
            quality_level=QualityLevel.CRITICAL.value,
            issues=[],
            field_stats=[],
            checks_performed=[],
            timestamp=datetime.now().isoformat(),
            recommendations=["无数据可审计"]
        )
    
    # 辅助方法
    @staticmethod
    def _is_integer(value) -> bool:
        """检查是否为整数"""
        try:
            int(value)
            return True
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def _is_number(value) -> bool:
        """检查是否为数字"""
        try:
            float(value)
            return True
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def _is_email(value) -> bool:
        """检查是否为邮箱"""
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return bool(re.match(pattern, str(value)))
    
    @staticmethod
    def _is_date(value) -> bool:
        """检查是否为日期"""
        date_patterns = [
            r'^\d{4}-\d{2}-\d{2}$',
            r'^\d{4}/\d{2}/\d{2}$',
            r'^\d{2}-\d{2}-\d{4}$',
        ]
        return any(re.match(p, str(value)) for p in date_patterns)
    
    @staticmethod
    def _get_numeric_fields(data: List[Dict[str, Any]]) -> List[str]:
        """获取数值型字段"""
        if not data:
            return []
        
        numeric_fields = []
        for field in data[0].keys():
            values = [r[field] for r in data if r.get(field) is not None]
            if values and all(isinstance(v, (int, float)) or DataQualityAuditor._is_number(v) for v in values[:10]):
                numeric_fields.append(field)
        
        return numeric_fields
    
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
            "# 数据质量审计报告",
            "",
            f"**审计时间**: {report.timestamp}",
            f"**总记录数**: {report.total_records}",
            f"**总字段数**: {report.total_fields}",
            "",
            "---",
            "",
            "## 📊 质量概览",
            "",
            f"- **总体评分**: {report.overall_score:.1f}/100",
            f"- **质量等级**: {report.quality_level.upper()}",
            f"- **执行检查**: {', '.join(report.checks_performed)}",
            "",
            "---",
            "",
        ]
        
        if report.field_stats:
            lines.extend(["## 📁 字段统计", ""])
            lines.append("| 字段 | 总数 | 缺失 | 唯一值 | 完整度 | 有效度 |")
            lines.append("|------|------|------|--------|--------|--------|")
            
            for stat in report.field_stats:
                lines.append(
                    f"| {stat.field_name} | {stat.total_count} | "
                    f"{stat.missing_count} | {stat.unique_count} | "
                    f"{stat.completeness:.1%} | {stat.validity:.1%} |"
                )
            lines.append("")
        
        if report.issues:
            lines.extend([
                "---",
                "",
                f"## 🚨 发现的问题 ({len(report.issues)}个)",
                "",
            ])
            
            # 按严重度分组
            severity_order = ["high", "medium", "low"]
            severity_labels = {"high": "🔴 高", "medium": "🟠 中", "low": "🟡 低"}
            
            for severity in severity_order:
                issues = [i for i in report.issues if i.severity == severity]
                if issues:
                    lines.append(f"### {severity_labels[severity]}严重度 ({len(issues)}个)")
                    lines.append("")
                    for issue in issues[:10]:  # 每种严重度最多显示10个
                        lines.append(f"- **{issue.field}** (第{issue.row_index + 1}行): {issue.message}")
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
    
    parser = argparse.ArgumentParser(description='Data Quality Auditor - 数据质量审计')
    parser.add_argument('--data', '-d', required=True, help='数据文件 (JSON)')
    parser.add_argument('--rules', '-r', help='规则配置文件 (JSON)')
    parser.add_argument('--format', choices=['json', 'markdown'], default='markdown',
                       help='报告格式')
    parser.add_argument('--output', '-o', help='输出文件路径')
    
    args = parser.parse_args()
    
    try:
        # 加载数据
        with open(args.data, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 加载规则
        rules = {}
        if args.rules:
            with open(args.rules, 'r', encoding='utf-8') as f:
                rules = json.load(f)
        
        # 执行审计
        auditor = DataQualityAuditor()
        report = auditor.audit(data, rules)
        
        # 输出报告
        output = auditor.export_report(report, args.format)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"✅ 报告已保存: {args.output}")
        else:
            print(output)
        
        # 返回质量等级作为退出码
        level_codes = {
            'excellent': 0,
            'good': 0,
            'fair': 1,
            'poor': 2,
            'critical': 3
        }
        return level_codes.get(report.quality_level, 1)
        
    except Exception as e:
        print(f"❌ 错误: {e}", file=__import__('sys').stderr)
        return 1


if __name__ == '__main__':
    import sys
    sys.exit(main())
