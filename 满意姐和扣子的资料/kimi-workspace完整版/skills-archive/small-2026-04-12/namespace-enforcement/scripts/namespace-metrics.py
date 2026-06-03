#!/usr/bin/env python3
"""
Namespace Metrics - 指标收集与可视化
S3: 可观测输出 - 合规率、违规清单、迁移进度
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# 导入检查器
sys.path.insert(0, str(Path(__file__).parent))

import importlib.util
spec = importlib.util.spec_from_file_location("namespace_checker", str(Path(__file__).parent / "namespace-checker.py"))
namespace_checker_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(namespace_checker_module)
NamespaceChecker = namespace_checker_module.NamespaceChecker


class NamespaceMetrics:
    """命名空间指标收集器"""
    
    def __init__(self, checker: NamespaceChecker = None):
        self.checker = checker or NamespaceChecker()
        self.history_file = Path(__file__).parent.parent / "reports" / "metrics-history.json"
    
    def collect_metrics(self, directory: str) -> Dict[str, Any]:
        """收集当前指标"""
        result = self.checker.scan_directory(directory)
        
        # 按类型统计违规
        violations_by_type = {}
        for v in result.violations:
            key = v.violation_type.value
            violations_by_type[key] = violations_by_type.get(key, 0) + 1
        
        # 按严重级别统计
        violations_by_severity = {}
        for v in result.violations:
            violations_by_severity[v.severity] = violations_by_severity.get(v.severity, 0) + 1
        
        # 目录分析
        dir_analysis = self._analyze_directory_structure(directory)
        
        metrics = {
            "timestamp": result.timestamp,
            "directory": directory,
            "summary": {
                "total_files": result.total_files,
                "compliant_files": result.compliant_files,
                "compliance_rate": result.compliance_rate,
                "legacy_files": result.legacy_files,
                "migration_progress": result.migration_progress,
                "total_violations": len(result.violations)
            },
            "violations_by_type": violations_by_type,
            "violations_by_severity": violations_by_severity,
            "directory_analysis": dir_analysis,
            "s6_cognitive_humility": {
                "note": "存量文件不强制迁移，渐进式规范化",
                "legacy_file_count": result.legacy_files,
                "migration_recommendation": "建议每周处理5-10个存量文件"
            }
        }
        
        return metrics
    
    def _analyze_directory_structure(self, directory: str) -> Dict[str, Any]:
        """分析目录结构规范度"""
        directory = Path(directory)
        
        # 分析各子目录的合规率
        subdirs = [d for d in directory.iterdir() if d.is_dir() and not d.name.startswith('.')]
        
        subdir_stats = []
        for subdir in subdirs:
            try:
                result = self.checker.scan_directory(str(subdir))
                subdir_stats.append({
                    "name": subdir.name,
                    "file_count": result.total_files,
                    "compliance_rate": result.compliance_rate,
                    "violations": len(result.violations)
                })
            except:
                pass
        
        # 排序：按合规率升序（问题最多的在前）
        subdir_stats.sort(key=lambda x: x['compliance_rate'])
        
        return {
            "subdirectory_compliance": subdir_stats[:10],  # 只显示前10
            "most_problematic": subdir_stats[0] if subdir_stats else None
        }
    
    def save_history(self, metrics: Dict[str, Any]):
        """保存历史记录"""
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        
        history = []
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            except:
                history = []
        
        # 添加新记录
        history.append(metrics)
        
        # 只保留最近30条
        history = history[-30:]
        
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
    
    def generate_trend_report(self) -> Dict[str, Any]:
        """生成趋势报告"""
        if not self.history_file.exists():
            return {"error": "没有历史数据"}
        
        with open(self.history_file, 'r', encoding='utf-8') as f:
            history = json.load(f)
        
        if len(history) < 2:
            return {"error": "需要至少2条历史记录才能生成趋势"}
        
        # 计算趋势
        first = history[0]['summary']
        last = history[-1]['summary']
        
        trend = {
            "record_count": len(history),
            "time_span_days": self._calculate_days(history[0]['timestamp'], history[-1]['timestamp']),
            "compliance_rate_change": round(last['compliance_rate'] - first['compliance_rate'], 2),
            "migration_progress_change": round(last['migration_progress'] - first['migration_progress'], 2),
            "violation_count_change": last['total_violations'] - first['total_violations'],
            "current_status": last,
            "trend_direction": "improving" if last['compliance_rate'] > first['compliance_rate'] else "declining"
        }
        
        return trend
    
    def _calculate_days(self, start: str, end: str) -> int:
        """计算时间跨度"""
        try:
            t1 = datetime.fromisoformat(start)
            t2 = datetime.fromisoformat(end)
            return (t2 - t1).days
        except:
            return 0
    
    def print_metrics(self, metrics: Dict[str, Any]):
        """打印指标"""
        summary = metrics['summary']
        
        print("\n" + "=" * 60)
        print("命名空间合规指标")
        print("=" * 60)
        print(f"扫描时间: {metrics['timestamp']}")
        print(f"扫描目录: {metrics['directory']}")
        print("\n📊 合规概览:")
        print(f"  总文件数: {summary['total_files']}")
        print(f"  合规文件: {summary['compliant_files']}")
        print(f"  合规率: {summary['compliance_rate']}%")
        print(f"  违规数: {summary['total_violations']}")
        print("\n📝 S6 迁移状态 (认知谦逊):")
        print(f"  存量文件: {summary['legacy_files']} (不强制迁移)")
        print(f"  迁移进度: {summary['migration_progress']}%")
        print(f"  建议: {metrics['s6_cognitive_humility']['migration_recommendation']}")
        
        if metrics['violations_by_type']:
            print("\n⚠️ 违规类型分布:")
            for vtype, count in sorted(metrics['violations_by_type'].items(), key=lambda x: -x[1]):
                print(f"  {vtype}: {count}")
        
        if metrics['violations_by_severity']:
            print("\n🔴 严重级别分布:")
            for sev, count in sorted(metrics['violations_by_severity'].items(), key=lambda x: -x[1]):
                print(f"  {sev}: {count}")
        
        # 目录分析
        dir_analysis = metrics.get('directory_analysis', {})
        if dir_analysis.get('most_problematic'):
            worst = dir_analysis['most_problematic']
            print(f"\n⚡ 最需要关注的目录: {worst['name']} (合规率: {worst['compliance_rate']}%)")
        
        print("=" * 60)
    
    def generate_markdown_report(self, metrics: Dict[str, Any], output_path: str):
        """生成Markdown格式报告"""
        summary = metrics['summary']
        
        md = f"""# Namespace Compliance Report

**生成时间**: {metrics['timestamp']}

**扫描目录**: `{metrics['directory']}`

## 📊 合规概览

| 指标 | 数值 |
|------|------|
| 总文件数 | {summary['total_files']} |
| 合规文件 | {summary['compliant_files']} |
| 合规率 | {summary['compliance_rate']}% |
| 违规总数 | {summary['total_violations']} |

## 📝 S6 迁移状态 (认知谦逊原则)

| 指标 | 数值 |
|------|------|
| 存量文件数 | {summary['legacy_files']} |
| 迁移进度 | {summary['migration_progress']}% |

> **S6 认知谦逊**: 存量文件不强制迁移，采用渐进式规范化策略。
> 建议每周处理5-10个存量文件，避免一次性大量变更影响现有工作流。

## ⚠️ 违规类型分布

"""
        
        if metrics['violations_by_type']:
            md += "| 违规类型 | 数量 |\n|----------|------|\n"
            for vtype, count in sorted(metrics['violations_by_type'].items(), key=lambda x: -x[1]):
                md += f"| {vtype} | {count} |\n"
        else:
            md += "✅ 未发现违规\n"
        
        md += f"""

## 🔴 严重级别分布

"""
        
        if metrics['violations_by_severity']:
            md += "| 级别 | 数量 |\n|------|------|\n"
            for sev, count in sorted(metrics['violations_by_severity'].items(), key=lambda x: -x[1]):
                md += f"| {sev} | {count} |\n"
        
        md += f"""

## 📈 改进建议

1. **优先级 P0**: 修复 error 级别的违规
2. **优先级 P1**: 处理新创建文件（非存量）的违规
3. **优先级 P2**: 逐步迁移存量文件（参考 S6 渐进策略）

---
*Generated by Namespace Enforcement Extension*
"""
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md)
        
        print(f"Markdown报告已保存: {output_path}")


def main():
    """主入口"""
    parser = argparse.ArgumentParser(description="Namespace Metrics")
    parser.add_argument("--scan", "-s", required=True, help="扫描目录")
    parser.add_argument("--save", help="保存历史记录", action="store_true")
    parser.add_argument("--trend", help="生成趋势报告", action="store_true")
    parser.add_argument("--markdown", "-m", help="生成Markdown报告")
    parser.add_argument("--json", "-j", help="生成JSON报告")
    
    args = parser.parse_args()
    
    metrics_collector = NamespaceMetrics()
    
    # 收集指标
    print("正在收集指标...")
    metrics = metrics_collector.collect_metrics(args.scan)
    
    # 打印
    metrics_collector.print_metrics(metrics)
    
    # 保存历史
    if args.save:
        metrics_collector.save_history(metrics)
        print("\n指标已保存到历史记录")
    
    # 趋势报告
    if args.trend:
        print("\n" + "=" * 60)
        print("趋势分析")
        print("=" * 60)
        trend = metrics_collector.generate_trend_report()
        if "error" in trend:
            print(trend["error"])
        else:
            print(f"时间跨度: {trend['time_span_days']} 天")
            print(f"合规率变化: {trend['compliance_rate_change']:+.2f}%")
            print(f"迁移进度变化: {trend['migration_progress_change']:+.2f}%")
            print(f"趋势: {trend['trend_direction']}")
    
    # 输出报告
    if args.markdown:
        metrics_collector.generate_markdown_report(metrics, args.markdown)
    
    if args.json:
        Path(args.json).parent.mkdir(parents=True, exist_ok=True)
        with open(args.json, 'w', encoding='utf-8') as f:
            json.dump(metrics, f, indent=2, ensure_ascii=False)
        print(f"JSON报告已保存: {args.json}")


if __name__ == "__main__":
    main()
