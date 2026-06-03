#!/usr/bin/env python3
"""
监控报告生成脚本 - 生成 API 监控报告
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class ReportGenerator:
    """报告生成器"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.reports_dir = Path("reports")
        self.reports_dir.mkdir(exist_ok=True)
        
    def load_metrics(self, hours: int = 24) -> list:
        """加载指定时间范围内的指标数据"""
        metrics = []
        cutoff = datetime.now() - timedelta(hours=hours)
        
        data_file = self.data_dir / "metrics.jsonl"
        if not data_file.exists():
            return metrics
            
        with open(data_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    record = json.loads(line.strip())
                    record_time = datetime.fromisoformat(record.get('timestamp', ''))
                    if record_time >= cutoff:
                        metrics.append(record)
                except (json.JSONDecodeError, ValueError):
                    continue
                    
        return metrics
    
    def analyze_metrics(self, metrics: list) -> dict:
        """分析指标数据"""
        vendors = {}
        
        for m in metrics:
            vendor = m.get('vendor', 'unknown')
            if vendor not in vendors:
                vendors[vendor] = {
                    'checks': [],
                    'success_count': 0,
                    'error_types': {},
                    'latencies': []
                }
            
            vendors[vendor]['checks'].append(m)
            if m.get('success'):
                vendors[vendor]['success_count'] += 1
            else:
                error = m.get('error', 'unknown')
                vendors[vendor]['error_types'][error] = \
                    vendors[vendor]['error_types'].get(error, 0) + 1
            
            vendors[vendor]['latencies'].append(m.get('response_time_ms', 0))
        
        # 计算统计数据
        summary = {}
        for vendor, data in vendors.items():
            total = len(data['checks'])
            if total == 0:
                continue
                
            latencies = sorted(data['latencies'])
            summary[vendor] = {
                'total_checks': total,
                'success_count': data['success_count'],
                'availability': round((data['success_count'] / total) * 100, 2),
                'error_rate': round(((total - data['success_count']) / total) * 100, 2),
                'p50_latency': latencies[len(latencies)//2] if latencies else 0,
                'p95_latency': latencies[int(len(latencies)*0.95)] if latencies else 0,
                'p99_latency': latencies[int(len(latencies)*0.99)] if latencies else 0,
                'avg_latency': round(sum(latencies) / len(latencies), 2) if latencies else 0,
                'error_types': data['error_types'],
                'status': 'healthy' if data['success_count'] == total else 'degraded'
            }
            
        return summary
    
    def generate_recommendations(self, summary: dict) -> list:
        """生成优化建议"""
        recommendations = []
        
        for vendor, stats in summary.items():
            # 可用性建议
            if stats['availability'] < 99.9:
                recommendations.append({
                    'vendor': vendor,
                    'type': 'availability',
                    'priority': 'critical',
                    'message': f"{vendor} 可用性 {stats['availability']}% 低于 SLA 目标 99.9%",
                    'action': '检查网络连接和认证配置'
                })
            
            # 延迟建议
            if stats['p95_latency'] > 2000:
                recommendations.append({
                    'vendor': vendor,
                    'type': 'performance',
                    'priority': 'medium',
                    'message': f"{vendor} P95 延迟 {stats['p95_latency']}ms 超过阈值 2000ms",
                    'action': '启用连接池复用，考虑使用 CDN'
                })
            
            # 错误率建议
            if stats['error_rate'] > 1.0:
                recommendations.append({
                    'vendor': vendor,
                    'type': 'reliability',
                    'priority': 'high',
                    'message': f"{vendor} 错误率 {stats['error_rate']}% 超过阈值 1%",
                    'action': '实现指数退避重试策略'
                })
        
        return recommendations
    
    def generate_json_report(self, hours: int = 24) -> dict:
        """生成 JSON 格式报告"""
        metrics = self.load_metrics(hours)
        summary = self.analyze_metrics(metrics)
        recommendations = self.generate_recommendations(summary)
        
        total_checks = sum(s['total_checks'] for s in summary.values())
        total_success = sum(s['success_count'] for s in summary.values())
        
        report = {
            'report_type': 'api_monitor',
            'generated_at': datetime.now().isoformat(),
            'period_hours': hours,
            'summary': {
                'total_checks': total_checks,
                'success_count': total_success,
                'overall_availability': round((total_success / total_checks) * 100, 2) if total_checks else 0,
            },
            'vendors': summary,
            'recommendations': recommendations
        }
        
        return report
    
    def generate_markdown_report(self, hours: int = 24) -> str:
        """生成 Markdown 格式报告"""
        report = self.generate_json_report(hours)
        
        md = f"""# API 监控报告

生成时间: {report['generated_at']}
监控周期: 过去 {report['period_hours']} 小时

## 总体概览

| 指标 | 数值 |
|------|------|
| 总检查次数 | {report['summary']['total_checks']} |
| 成功次数 | {report['summary']['success_count']} |
| 整体可用性 | {report['summary']['overall_availability']}% |

## 各厂商详情

"""
        
        for vendor, stats in report['vendors'].items():
            status_emoji = "✅" if stats['status'] == 'healthy' else "⚠️"
            md += f"""### {status_emoji} {vendor}

| 指标 | 数值 |
|------|------|
| 状态 | {stats['status']} |
| 检查次数 | {stats['total_checks']} |
| 可用性 | {stats['availability']}% |
| 错误率 | {stats['error_rate']}% |
| P50 延迟 | {stats['p50_latency']}ms |
| P95 延迟 | {stats['p95_latency']}ms |
| P99 延迟 | {stats['p99_latency']}ms |
| 平均延迟 | {stats['avg_latency']}ms |

"""
            if stats['error_types']:
                md += "**错误分布:**\n"
                for error, count in stats['error_types'].items():
                    md += f"- {error}: {count}\n"
                md += "\n"
        
        if report['recommendations']:
            md += """## 优化建议

"""
            for rec in report['recommendations']:
                priority_emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(rec['priority'], "⚪")
                md += f"""### {priority_emoji} [{rec['priority'].upper()}] {rec['vendor']}

- **问题**: {rec['message']}
- **建议**: {rec['action']}

"""
        else:
            md += """## 优化建议

✅ 当前无优化建议，所有指标正常。
"""
        
        return md
    
    def save_report(self, report: dict, fmt: str = 'json'):
        """保存报告到文件"""
        date_str = datetime.now().strftime('%Y-%m-%d')
        time_str = datetime.now().strftime('%H%M%S')
        
        report_dir = self.reports_dir / date_str
        report_dir.mkdir(parents=True, exist_ok=True)
        
        if fmt == 'json':
            filename = report_dir / f"report_{time_str}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
        else:
            filename = report_dir / f"report_{time_str}.md"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.generate_markdown_report())
        
        return filename


def main():
    parser = argparse.ArgumentParser(description='生成 API 监控报告')
    parser.add_argument('--hours', type=int, default=24, help='监控时间范围(小时)')
    parser.add_argument('--format', '-f', choices=['json', 'markdown', 'md'], default='markdown',
                       help='报告格式')
    parser.add_argument('--save', '-s', action='store_true', help='保存到文件')
    parser.add_argument('--data-dir', '-d', default='data', help='数据目录')
    
    args = parser.parse_args()
    
    generator = ReportGenerator(args.data_dir)
    
    if args.format == 'json':
        report = generator.generate_json_report(args.hours)
        output = json.dumps(report, indent=2, ensure_ascii=False)
        if args.save:
            filename = generator.save_report(report, 'json')
            print(f"报告已保存: {filename}")
    else:
        output = generator.generate_markdown_report(args.hours)
        if args.save:
            report = generator.generate_json_report(args.hours)
            filename = generator.save_report(report, 'markdown')
            print(f"报告已保存: {filename}")
    
    print(output)


if __name__ == '__main__':
    main()
