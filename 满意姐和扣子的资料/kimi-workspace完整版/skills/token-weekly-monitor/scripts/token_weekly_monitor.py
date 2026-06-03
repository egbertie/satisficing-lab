#!/usr/bin/env python3
"""
token-weekly-monitor - Token周度监控器
真正实现版本

功能:
- Token使用周度统计
- 趋势分析
- 预算跟踪
- 异常检测
- 预警通知

作者: 满意妞 (重构)
版本: 2.0.1-real
日期: 2026-04-03
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum


class AlertLevel(Enum):
    """预警级别"""
    NORMAL = "normal"
    CAUTION = "caution"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class DailyUsage:
    """每日使用"""
    date: str
    tokens_used: int
    budget: int
    operations: int
    peak_hour: int
    peak_usage: int


@dataclass
class WeeklyReport:
    """周报"""
    week_start: str
    week_end: str
    total_tokens: int
    total_budget: int
    usage_percentage: float
    daily_breakdown: List[DailyUsage]
    trend_direction: str  # up, down, stable
    avg_daily_usage: float
    peak_day: str
    peak_usage: int
    alert_level: str
    recommendations: List[str]
    anomalies: List[str]


class TokenWeeklyMonitor:
    """Token周度监控器"""
    
    def __init__(self, data_dir: Optional[str] = None):
        """初始化"""
        self.data_dir = Path(data_dir) if data_dir else Path(__file__).parent / "data"
        self.data_dir.mkdir(exist_ok=True)
        
        self.usage_file = self.data_dir / "weekly_usage.json"
        self.config_file = self.data_dir / "config.json"
        
        self.config = self._load_config()
        self.usage_history: List[DailyUsage] = self._load_usage()
    
    def _load_config(self) -> Dict:
        """加载配置"""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # 默认配置
        return {
            'weekly_budget': 100000,  # 每周预算10万Token
            'caution_threshold': 0.7,
            'warning_threshold': 0.9,
            'critical_threshold': 1.0,
            'track_operations': True
        }
    
    def _load_usage(self) -> List[DailyUsage]:
        """加载使用历史"""
        if self.usage_file.exists():
            with open(self.usage_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [DailyUsage(**item) for item in data]
        return []
    
    def _save_usage(self):
        """保存使用历史"""
        with open(self.usage_file, 'w', encoding='utf-8') as f:
            data = [self._usage_to_dict(u) for u in self.usage_history]
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _usage_to_dict(self, usage: DailyUsage) -> Dict:
        """转换为字典"""
        return {
            'date': usage.date,
            'tokens_used': usage.tokens_used,
            'budget': usage.budget,
            'operations': usage.operations,
            'peak_hour': usage.peak_hour,
            'peak_usage': usage.peak_usage
        }
    
    def record_daily_usage(self, date: str, tokens_used: int,
                          operations: int = 0, peak_hour: int = 0,
                          peak_usage: int = 0) -> DailyUsage:
        """记录每日使用"""
        usage = DailyUsage(
            date=date,
            tokens_used=tokens_used,
            budget=self.config.get('weekly_budget', 100000) // 7,
            operations=operations,
            peak_hour=peak_hour,
            peak_usage=peak_usage
        )
        
        # 检查是否已存在该日期的记录
        existing = next((i for i, u in enumerate(self.usage_history) if u.date == date), None)
        if existing is not None:
            self.usage_history[existing] = usage
        else:
            self.usage_history.append(usage)
        
        self._save_usage()
        return usage
    
    def generate_weekly_report(self, week_start: Optional[str] = None) -> WeeklyReport:
        """生成周报"""
        if week_start is None:
            # 默认上周
            today = datetime.now()
            week_start_date = today - timedelta(days=today.weekday() + 7)
            week_start = week_start_date.strftime('%Y-%m-%d')
        
        week_start_dt = datetime.strptime(week_start, '%Y-%m-%d')
        week_end_dt = week_start_dt + timedelta(days=6)
        week_end = week_end_dt.strftime('%Y-%m-%d')
        
        # 筛选本周数据
        week_dates = [
            (week_start_dt + timedelta(days=i)).strftime('%Y-%m-%d')
            for i in range(7)
        ]
        
        daily_data = []
        for date in week_dates:
            usage = next((u for u in self.usage_history if u.date == date), None)
            if usage:
                daily_data.append(usage)
            else:
                # 创建空记录
                daily_data.append(DailyUsage(
                    date=date,
                    tokens_used=0,
                    budget=self.config.get('weekly_budget', 100000) // 7,
                    operations=0,
                    peak_hour=0,
                    peak_usage=0
                ))
        
        # 计算统计
        total_tokens = sum(d.tokens_used for d in daily_data)
        total_budget = sum(d.budget for d in daily_data)
        usage_percentage = total_tokens / total_budget if total_budget > 0 else 0
        avg_daily = total_tokens / 7
        
        # 找到峰值日
        peak_day_usage = max(daily_data, key=lambda x: x.tokens_used)
        
        # 趋势分析
        trend = self._analyze_trend(daily_data)
        
        # 异常检测
        anomalies = self._detect_anomalies(daily_data)
        
        # 预警级别
        alert_level = self._determine_alert_level(usage_percentage, anomalies)
        
        # 生成建议
        recommendations = self._generate_recommendations(
            usage_percentage, total_tokens, total_budget, anomalies
        )
        
        return WeeklyReport(
            week_start=week_start,
            week_end=week_end,
            total_tokens=total_tokens,
            total_budget=total_budget,
            usage_percentage=usage_percentage,
            daily_breakdown=daily_data,
            trend_direction=trend,
            avg_daily_usage=avg_daily,
            peak_day=peak_day_usage.date,
            peak_usage=peak_day_usage.tokens_used,
            alert_level=alert_level,
            recommendations=recommendations,
            anomalies=anomalies
        )
    
    def _analyze_trend(self, daily_data: List[DailyUsage]) -> str:
        """分析趋势"""
        if len(daily_data) < 3:
            return "stable"
        
        # 比较前半周和后半周
        mid = len(daily_data) // 2
        first_half = sum(d.tokens_used for d in daily_data[:mid])
        second_half = sum(d.tokens_used for d in daily_data[mid:])
        
        if second_half > first_half * 1.2:
            return "up"
        elif second_half < first_half * 0.8:
            return "down"
        return "stable"
    
    def _detect_anomalies(self, daily_data: List[DailyUsage]) -> List[str]:
        """检测异常"""
        anomalies = []
        
        usages = [d.tokens_used for d in daily_data if d.tokens_used > 0]
        if not usages:
            return anomalies
        
        avg = sum(usages) / len(usages)
        std = (sum((u - avg) ** 2 for u in usages) / len(usages)) ** 0.5
        
        for d in daily_data:
            if d.tokens_used > avg + 2 * std:
                anomalies.append(f"{d.date}: 使用量异常高 ({d.tokens_used})")
            elif d.tokens_used > d.budget * 1.5:
                anomalies.append(f"{d.date}: 超出日预算 {d.tokens_used/d.budget:.1%}")
        
        return anomalies
    
    def _determine_alert_level(self, usage_percentage: float,
                              anomalies: List[str]) -> str:
        """确定预警级别"""
        if usage_percentage >= self.config.get('critical_threshold', 1.0):
            return AlertLevel.CRITICAL.value
        elif usage_percentage >= self.config.get('warning_threshold', 0.9):
            return AlertLevel.WARNING.value
        elif usage_percentage >= self.config.get('caution_threshold', 0.7):
            return AlertLevel.CAUTION.value
        elif anomalies:
            return AlertLevel.CAUTION.value
        return AlertLevel.NORMAL.value
    
    def _generate_recommendations(self, usage_percentage: float,
                                 total_tokens: int, budget: int,
                                 anomalies: List[str]) -> List[str]:
        """生成建议"""
        recommendations = []
        
        if usage_percentage >= 1.0:
            recommendations.append(f"🔴 周Token使用已超预算 ({usage_percentage:.1%})，建议立即优化")
        elif usage_percentage >= 0.9:
            recommendations.append(f"🟠 Token使用接近预算上限 ({usage_percentage:.1%})，建议监控")
        elif usage_percentage >= 0.7:
            recommendations.append(f"🟡 Token使用率较高 ({usage_percentage:.1%})，注意趋势")
        else:
            recommendations.append(f"✅ Token使用正常 ({usage_percentage:.1%})")
        
        if anomalies:
            recommendations.append(f"⚠️ 检测到 {len(anomalies)} 个异常使用日，建议检查")
        
        remaining = budget - total_tokens
        if remaining > 0:
            days_left = 7 - datetime.now().weekday()
            if days_left > 0:
                daily_budget = remaining / days_left
                recommendations.append(f"💡 剩余日均预算: {daily_budget:.0f} Token")
        
        return recommendations
    
    def get_current_week_status(self) -> Dict:
        """获取本周状态"""
        today = datetime.now()
        week_start = (today - timedelta(days=today.weekday())).strftime('%Y-%m-%d')
        
        # 计算本周已用
        week_dates = [
            (today - timedelta(days=today.weekday() - i)).strftime('%Y-%m-%d')
            for i in range(today.weekday() + 1)
        ]
        
        used = sum(u.tokens_used for u in self.usage_history if u.date in week_dates)
        budget = self.config.get('weekly_budget', 100000)
        remaining = budget - used
        
        return {
            'week_start': week_start,
            'today': today.strftime('%Y-%m-%d'),
            'days_elapsed': today.weekday() + 1,
            'days_remaining': 7 - today.weekday(),
            'used': used,
            'budget': budget,
            'remaining': remaining,
            'usage_percentage': used / budget if budget > 0 else 0,
            'projected_weekly': used / (today.weekday() + 1) * 7 if today.weekday() >= 0 else 0
        }
    
    def export_report(self, report: WeeklyReport, format: str = "json") -> str:
        """导出报告"""
        if format == "json":
            return json.dumps(report.__dict__, ensure_ascii=False, indent=2, default=str)
        elif format == "markdown":
            return self._format_markdown(report)
        return ""
    
    def _format_markdown(self, report: WeeklyReport) -> str:
        """格式化为Markdown"""
        level_icons = {
            AlertLevel.NORMAL.value: "🟢",
            AlertLevel.CAUTION.value: "🟡",
            AlertLevel.WARNING.value: "🟠",
            AlertLevel.CRITICAL.value: "🔴"
        }
        
        icon = level_icons.get(report.alert_level, '⚪')
        
        lines = [
            f"# Token周度监控报告",
            "",
            f"**统计周期**: {report.week_start} ~ {report.week_end}",
            f"**预警级别**: {icon} {report.alert_level.upper()}",
            f"**趋势**: {report.trend_direction}",
            "",
            "---",
            "",
            "## 📊 使用概览",
            "",
            f"- **总使用量**: {report.total_tokens:,} Token",
            f"- **周预算**: {report.total_budget:,} Token",
            f"- **使用率**: {report.usage_percentage:.1%}",
            f"- **日均使用**: {report.avg_daily_usage:.0f} Token",
            f"- **峰值日**: {report.peak_day} ({report.peak_usage:,} Token)",
            "",
            "---",
            "",
            "## 📅 每日明细",
            "",
            "| 日期 | 使用 | 预算 | 操作数 | 峰值时段 |",
            "|------|------|------|--------|----------|"
        ]
        
        for day in report.daily_breakdown:
            lines.append(
                f"| {day.date} | {day.tokens_used:,} | {day.budget:,} | "
                f"{day.operations} | {day.peak_hour}:00 |"
            )
        
        if report.anomalies:
            lines.extend([
                "",
                "---",
                "",
                "## ⚠️ 异常检测",
                ""
            ])
            for anomaly in report.anomalies:
                lines.append(f"- {anomaly}")
        
        if report.recommendations:
            lines.extend([
                "",
                "---",
                "",
                "## 💡 建议",
                ""
            ])
            for rec in report.recommendations:
                lines.append(f"- {rec}")
            lines.append("")
        
        return '\n'.join(lines)


def main():
    """主入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Token Weekly Monitor - Token周度监控器')
    parser.add_argument('--record', nargs=3, metavar=('DATE', 'TOKENS', 'OPS'),
                       help='记录每日使用 (YYYY-MM-DD TOKENS OPERATIONS)')
    parser.add_argument('--report', action='store_true',
                       help='生成本周报告')
    parser.add_argument('--week', help='指定周开始日期 (YYYY-MM-DD)')
    parser.add_argument('--status', action='store_true',
                       help='查看本周状态')
    parser.add_argument('--format', choices=['json', 'markdown'], default='markdown',
                       help='输出格式')
    parser.add_argument('--output', '-o', help='输出文件路径')
    parser.add_argument('--data-dir', help='数据目录')
    
    args = parser.parse_args()
    
    try:
        monitor = TokenWeeklyMonitor(args.data_dir)
        
        if args.record:
            date, tokens, ops = args.record
            usage = monitor.record_daily_usage(date, int(tokens), int(ops))
            print(f"✅ 已记录: {usage.date} - {usage.tokens_used} Token ({usage.operations} 操作)")
        
        elif args.report:
            report = monitor.generate_weekly_report(args.week)
            output = monitor.export_report(report, args.format)
            
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(output)
                print(f"✅ 报告已保存: {args.output}")
            else:
                print(output)
        
        elif args.status:
            status = monitor.get_current_week_status()
            print("=" * 50)
            print("Token周度监控 - 本周状态")
            print("=" * 50)
            print(f"周期: {status['week_start']} ~ {status['today']}")
            print(f"进度: {status['days_elapsed']}/7 天")
            print(f"已用: {status['used']:,} / {status['budget']:,} Token ({status['usage_percentage']:.1%})")
            print(f"剩余: {status['remaining']:,} Token")
            print(f"预计周用量: {status['projected_weekly']:,.0f} Token")
            print("=" * 50)
        
        else:
            # 默认显示状态
            status = monitor.get_current_week_status()
            print(f"本周Token使用: {status['usage_percentage']:.1%} ({status['used']:,}/{status['budget']:,})")
            print(f"剩余: {status['remaining']:,} Token")
        
        return 0
        
    except Exception as e:
        print(f"❌ 错误: {e}", file=__import__('sys').stderr)
        return 1


if __name__ == '__main__':
    import sys
    sys.exit(main())
