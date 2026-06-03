#!/usr/bin/env python3
"""
generate-report.py
门禁报告生成器 - 支持多种格式和趋势分析

Usage:
    python3 generate-report.py --input report.json --format html
    python3 generate-report.py --trend --days 30
    python3 generate-report.py --compare report1.json report2.json
"""

import json
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any
from dataclasses import dataclass

REPORTS_DIR = Path(__file__).parent.parent / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class TrendData:
    """趋势数据"""
    date: str
    total_score: float
    pass_rate: float
    avg_duration: float


class ReportGenerator:
    """报告生成器"""
    
    def __init__(self):
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, str]:
        """加载HTML模板"""
        return {
            "html_header": """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Quality Gate Report</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; background: #f5f5f5; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 20px; }
        .summary { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 20px; }
        .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .score { font-size: 2em; font-weight: bold; }
        .score-pass { color: #22c55e; }
        .score-conditional { color: #f59e0b; }
        .score-fail { color: #ef4444; }
        .dimension { background: white; padding: 20px; border-radius: 8px; margin-bottom: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .check { display: flex; align-items: center; padding: 10px; border-bottom: 1px solid #eee; }
        .check:last-child { border-bottom: none; }
        .status-icon { width: 24px; height: 24px; margin-right: 10px; }
        .status-pass { color: #22c55e; }
        .status-fail { color: #ef4444; }
        .remediation { background: #fef3c7; border-left: 4px solid #f59e0b; padding: 15px; margin: 10px 0; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #f8f9fa; font-weight: 600; }
        .badge { display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 0.85em; font-weight: 500; }
        .badge-success { background: #dcfce7; color: #166534; }
        .badge-warning { background: #fef3c7; color: #92400e; }
        .badge-danger { background: #fee2e2; color: #991b1b; }
    </style>
</head>
<body>
""",
            "html_footer": """
</body>
</html>
"""
        }
    
    def generate_html(self, report_data: Dict) -> str:
        """生成HTML报告"""
        summary = report_data.get("summary", {})
        grade = summary.get("grade", "UNKNOWN")
        
        grade_class = {
            "PASS": "score-pass",
            "CONDITIONAL": "score-conditional",
            "FAIL": "score-fail",
            "BLOCK": "score-fail"
        }.get(grade, "score-fail")
        
        html = self.templates["html_header"]
        
        # Header
        html += f"""
    <div class="header">
        <h1>🔒 Quality Gate Report</h1>
        <p>Gate ID: {report_data.get('gate_id', 'N/A')} | {report_data.get('timestamp', 'N/A')}</p>
    </div>
"""
        
        # Summary Cards
        html += "    <div class='summary'>\n"
        html += f"""
        <div class="card">
            <div>Total Score</div>
            <div class="score {grade_class}">{summary.get('total_score', 0):.1f}</div>
        </div>
        <div class="card">
            <div>Grade</div>
            <div class="score {grade_class}">{grade}</div>
        </div>
        <div class="card">
            <div>Status</div>
            <div class="score">{'🚫 BLOCKED' if summary.get('blocked') else '✅ PASSED'}</div>
        </div>
        <div class="card">
            <div>Level</div>
            <div class="score">{report_data.get('gate_config', {}).get('level', 'N/A').upper()}</div>
        </div>
    </div>
"""
        
        # Dimensions
        html += "    <h2>📊 Dimensions</h2>\n"
        for dim_name, dim in report_data.get("dimensions", {}).items():
            score_class = "score-pass" if dim.get("score", 0) >= 80 else "score-conditional" if dim.get("score", 0) >= 60 else "score-fail"
            html += f"""
    <div class="dimension">
        <h3>{dim_name.replace('_', ' ').title()} <span class="score {score_class}">{dim.get('score', 0):.1f}%</span></h3>
        <table>
            <tr><th>Check</th><th>Status</th><th>Score</th><th>Details</th></tr>
"""
            for check in dim.get("checks", []):
                status = "✅" if check.get("passed") else "❌"
                html += f"            <tr><td>{check.get('name', 'N/A')}</td><td>{status}</td><td>{check.get('score', 0):.0f}</td><td>{check.get('details', 'N/A')}</td></tr>\n"
            
            html += "        </table>\n    </div>\n"
        
        # Remediation
        remediation = report_data.get("remediation", [])
        if remediation:
            html += "    <h2>🔧 Remediation Tasks</h2>\n"
            for task in remediation:
                severity_class = "badge-danger" if task.get("severity") == "critical" else "badge-warning"
                html += f"""
    <div class="remediation">
        <span class="badge {severity_class}">{task.get('severity', 'warning').upper()}</span>
        <strong>[{task.get('dimension', 'N/A')}/{task.get('check', 'N/A')}]</strong>
        <p>{task.get('issue', 'N/A')}</p>
        {"<code>" + task.get('fix_command', '') + "</code>" if task.get("auto_fixable") else ""}
    </div>
"""
        
        html += self.templates["html_footer"]
        return html
    
    def generate_trend_report(self, days: int = 30) -> str:
        """生成趋势分析报告"""
        # 收集历史报告
        trend_data = self._collect_trend_data(days)
        
        if not trend_data:
            return "No historical data available."
        
        html = self.templates["html_header"]
        html += f"""
    <div class="header">
        <h1>📈 Quality Gate Trend Analysis</h1>
        <p>Last {days} days | Generated: {datetime.now().isoformat()}</p>
    </div>
    
    <div class="summary">
        <div class="card">
            <div>Average Score</div>
            <div class="score">{sum(d.total_score for d in trend_data) / len(trend_data):.1f}</div>
        </div>
        <div class="card">
            <div>Pass Rate</div>
            <div class="score">{sum(d.pass_rate for d in trend_data) / len(trend_data) * 100:.1f}%</div>
        </div>
        <div class="card">
            <div>Total Runs</div>
            <div class="score">{len(trend_data)}</div>
        </div>
    </div>
    
    <h2>📅 Daily Summary</h2>
    <table>
        <tr><th>Date</th><th>Avg Score</th><th>Pass Rate</th><th>Avg Duration</th></tr>
"""
        for data in trend_data:
            html += f"        <tr><td>{data.date}</td><td>{data.total_score:.1f}</td><td>{data.pass_rate*100:.1f}%</td><td>{data.avg_duration:.1f}s</td></tr>\n"
        
        html += "    </table>\n"
        html += self.templates["html_footer"]
        
        return html
    
    def _collect_trend_data(self, days: int) -> List[TrendData]:
        """收集趋势数据"""
        # 从报告目录读取历史报告
        trend_data = []
        cutoff = datetime.now() - timedelta(days=days)
        
        for report_file in REPORTS_DIR.glob("QG-*.json"):
            try:
                data = json.loads(report_file.read_text())
                timestamp = data.get("timestamp", "")
                report_date = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                
                if report_date > cutoff:
                    trend_data.append(TrendData(
                        date=report_date.strftime("%Y-%m-%d"),
                        total_score=data.get("summary", {}).get("total_score", 0),
                        pass_rate=0 if data.get("summary", {}).get("blocked") else 1,
                        avg_duration=0  # 简化处理
                    ))
            except:
                continue
        
        return sorted(trend_data, key=lambda x: x.date)
    
    def compare_reports(self, report_files: List[str]) -> str:
        """对比多个报告"""
        reports = []
        for f in report_files:
            try:
                reports.append(json.loads(Path(f).read_text()))
            except:
                pass
        
        if len(reports) < 2:
            return "Need at least 2 reports to compare."
        
        html = self.templates["html_header"]
        html += """
    <div class="header">
        <h1>📊 Report Comparison</h1>
    </div>
    
    <table>
        <tr>
            <th>Gate ID</th>
            <th>Timestamp</th>
            <th>Total Score</th>
            <th>Grade</th>
            <th>Status</th>
        </tr>
"""
        for report in reports:
            summary = report.get("summary", {})
            html += f"""
        <tr>
            <td>{report.get('gate_id', 'N/A')}</td>
            <td>{report.get('timestamp', 'N/A')}</td>
            <td>{summary.get('total_score', 0):.1f}</td>
            <td>{summary.get('grade', 'N/A')}</td>
            <td>{'BLOCKED' if summary.get('blocked') else 'PASSED'}</td>
        </tr>
"""
        html += "    </table>\n"
        html += self.templates["html_footer"]
        
        return html


def main():
    parser = argparse.ArgumentParser(description="Quality Gate Report Generator")
    parser.add_argument("--input", "-i", help="Input JSON report file")
    parser.add_argument("--format", "-f", default="html", choices=["html", "md", "console"])
    parser.add_argument("--output", "-o", help="Output file")
    parser.add_argument("--trend", "-t", action="store_true", help="Generate trend report")
    parser.add_argument("--days", "-d", type=int, default=30, help="Days for trend analysis")
    parser.add_argument("--compare", "-c", nargs="+", help="Compare multiple reports")
    
    args = parser.parse_args()
    
    generator = ReportGenerator()
    
    if args.trend:
        content = generator.generate_trend_report(args.days)
        output_file = args.output or REPORTS_DIR / f"trend-{datetime.now().strftime('%Y%m%d')}.html"
    elif args.compare:
        content = generator.compare_reports(args.compare)
        output_file = args.output or REPORTS_DIR / f"compare-{datetime.now().strftime('%Y%m%d')}.html"
    elif args.input:
        report_data = json.loads(Path(args.input).read_text())
        if args.format == "html":
            content = generator.generate_html(report_data)
        elif args.format == "md":
            # 简化处理，使用quality-gate-check.py中的markdown生成
            content = "# Markdown generation not implemented separately"
        else:
            content = json.dumps(report_data, indent=2)
        output_file = args.output or REPORTS_DIR / f"{Path(args.input).stem}.{args.format}"
    else:
        print("Please specify --input, --trend, or --compare")
        return
    
    Path(output_file).write_text(content)
    print(f"Report generated: {output_file}")


if __name__ == "__main__":
    main()
