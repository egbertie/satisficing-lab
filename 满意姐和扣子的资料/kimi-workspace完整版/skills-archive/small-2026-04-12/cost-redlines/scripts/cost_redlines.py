#!/usr/bin/env python3
"""
cost-redlines - Token/成本红线监控系统
真正实现版本

功能:
- 4级成本模型 (L1-L4)
- 实时成本监控
- 超支预警系统
- 成本趋势分析
- 预算限制执行

作者: 满意妞 (重构)
版本: 2.0.1-real
日期: 2026-04-03
"""

import json
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Tuple
from enum import Enum
import yaml


class CostLevel(Enum):
    """成本级别"""
    L1_BASE = "L1_BASE"              # 基础成本
    L2_EXTENDED = "L2_EXTENDED"      # 扩展成本
    L3_VALUE_ADDED = "L3_VALUE_ADDED" # 增值成本
    L4_RISK = "L4_RISK"              # 风险成本


class AlertLevel(Enum):
    """预警级别"""
    NORMAL = "normal"      # 正常
    WARNING = "warning"    # 警告 (80%)
    CRITICAL = "critical"  # 临界 (95%)
    EXCEEDED = "exceeded"  # 超支 (100%+)


@dataclass
class CostEntry:
    """成本条目"""
    timestamp: str
    amount: float
    category: str
    level: str
    description: str
    source: str


@dataclass
class Alert:
    """预警信息"""
    level: str
    timestamp: str
    message: str
    current_cost: float
    budget_limit: float
    percentage: float


@dataclass
class CostReport:
    """成本报告"""
    period: str
    total_cost: float
    budget_limit: float
    usage_percentage: float
    alert_level: str
    cost_by_category: Dict[str, float]
    cost_by_level: Dict[str, float]
    alerts: List[Alert]
    recommendations: List[str]


class CostMonitor:
    """成本监控器"""
    
    # 预警阈值
    WARNING_THRESHOLD = 0.80  # 80%
    CRITICAL_THRESHOLD = 0.95  # 95%
    
    def __init__(self, config_path: Optional[str] = None):
        """初始化监控器"""
        self.config = self._load_config(config_path)
        self.cost_history: List[CostEntry] = []
        self.alerts: List[Alert] = []
        
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """加载配置"""
        if config_path and Path(config_path).exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                if config_path.endswith('.yaml') or config_path.endswith('.yml'):
                    return yaml.safe_load(f)
                else:
                    return json.load(f)
        
        # 默认配置
        return {
            'budget_limit': 1000.0,  # 默认预算1000
            'categories': ['人力', '设备', '服务', '软件', '运营'],
            'levels': ['L1_BASE', 'L2_EXTENDED', 'L3_VALUE_ADDED', 'L4_RISK'],
            'alert_thresholds': {
                'warning': 0.80,
                'critical': 0.95
            }
        }
    
    def record_cost(self, amount: float, category: str, level: str,
                   description: str = "", source: str = "") -> CostEntry:
        """记录成本"""
        entry = CostEntry(
            timestamp=datetime.now().isoformat(),
            amount=amount,
            category=category,
            level=level,
            description=description,
            source=source
        )
        self.cost_history.append(entry)
        
        # 检查是否需要触发预警
        self._check_alert()
        
        return entry
    
    def _check_alert(self):
        """检查预警状态"""
        total = self.get_total_cost()
        budget = self.config.get('budget_limit', 1000.0)
        percentage = total / budget if budget > 0 else 0
        
        if percentage >= 1.0:
            alert_level = AlertLevel.EXCEEDED
        elif percentage >= self.CRITICAL_THRESHOLD:
            alert_level = AlertLevel.CRITICAL
        elif percentage >= self.WARNING_THRESHOLD:
            alert_level = AlertLevel.WARNING
        else:
            return  # 正常，无需预警
        
        alert = Alert(
            level=alert_level.value,
            timestamp=datetime.now().isoformat(),
            message=self._generate_alert_message(alert_level, percentage),
            current_cost=total,
            budget_limit=budget,
            percentage=percentage
        )
        self.alerts.append(alert)
    
    def _generate_alert_message(self, level: AlertLevel, percentage: float) -> str:
        """生成预警消息"""
        messages = {
            AlertLevel.WARNING: f"成本使用率达到 {percentage:.1%}，接近预算上限",
            AlertLevel.CRITICAL: f"成本使用率达到 {percentage:.1%}，即将超支！",
            AlertLevel.EXCEEDED: f"成本已超支 {percentage:.1%}，请立即采取措施！"
        }
        return messages.get(level, "成本预警")
    
    def get_total_cost(self) -> float:
        """获取总成本"""
        return sum(entry.amount for entry in self.cost_history)
    
    def get_cost_by_category(self) -> Dict[str, float]:
        """按类别统计成本"""
        result = {}
        for entry in self.cost_history:
            result[entry.category] = result.get(entry.category, 0) + entry.amount
        return result
    
    def get_cost_by_level(self) -> Dict[str, float]:
        """按级别统计成本"""
        result = {}
        for entry in self.cost_history:
            result[entry.level] = result.get(entry.level, 0) + entry.amount
        return result
    
    def get_alert_level(self) -> AlertLevel:
        """获取当前预警级别"""
        total = self.get_total_cost()
        budget = self.config.get('budget_limit', 1000.0)
        percentage = total / budget if budget > 0 else 0
        
        if percentage >= 1.0:
            return AlertLevel.EXCEEDED
        elif percentage >= self.CRITICAL_THRESHOLD:
            return AlertLevel.CRITICAL
        elif percentage >= self.WARNING_THRESHOLD:
            return AlertLevel.WARNING
        return AlertLevel.NORMAL
    
    def generate_report(self, period: str = "daily") -> CostReport:
        """生成成本报告"""
        total = self.get_total_cost()
        budget = self.config.get('budget_limit', 1000.0)
        percentage = total / budget if budget > 0 else 0
        
        return CostReport(
            period=period,
            total_cost=total,
            budget_limit=budget,
            usage_percentage=percentage,
            alert_level=self.get_alert_level().value,
            cost_by_category=self.get_cost_by_category(),
            cost_by_level=self.get_cost_by_level(),
            alerts=self.alerts[-10:],  # 最近10条预警
            recommendations=self._generate_recommendations(percentage)
        )
    
    def _generate_recommendations(self, percentage: float) -> List[str]:
        """生成优化建议"""
        recommendations = []
        
        if percentage >= 1.0:
            recommendations.append("🔴 已超支，立即停止非必要支出")
            recommendations.append("🔴 启动成本审查流程")
        elif percentage >= 0.95:
            recommendations.append("🟠 即将超支，暂停新增支出")
            recommendations.append("🟠 评估剩余预算使用计划")
        elif percentage >= 0.80:
            recommendations.append("🟡 成本使用率较高，监控趋势")
        
        # 按类别分析
        by_category = self.get_cost_by_category()
        if by_category:
            max_category = max(by_category.items(), key=lambda x: x[1])
            total = sum(by_category.values())
            if total > 0 and max_category[1] / total > 0.5:
                recommendations.append(
                    f"💡 '{max_category[0]}' 占比超过50%，建议优化该类别成本"
                )
        
        return recommendations
    
    def check_budget_available(self, estimated_cost: float) -> Tuple[bool, str]:
        """检查预算是否可用"""
        total = self.get_total_cost()
        budget = self.config.get('budget_limit', 1000.0)
        remaining = budget - total
        
        if estimated_cost > remaining:
            return False, f"预算不足: 需要 {estimated_cost:.2f}, 剩余 {remaining:.2f}"
        
        # 检查是否会触发预警
        new_percentage = (total + estimated_cost) / budget
        if new_percentage >= 1.0:
            return False, f"此项支出将导致超支 (预计 {new_percentage:.1%})"
        elif new_percentage >= self.CRITICAL_THRESHOLD:
            return True, f"⚠️ 此项支出后将接近预算上限 ({new_percentage:.1%})"
        
        return True, f"预算充足 ({new_percentage:.1%})"
    
    def export_report(self, report: CostReport, format: str = "json") -> str:
        """导出报告"""
        if format == "json":
            return json.dumps(asdict(report), ensure_ascii=False, indent=2)
        elif format == "markdown":
            return self._format_markdown(report)
        return ""
    
    def _format_markdown(self, report: CostReport) -> str:
        """格式化为Markdown"""
        lines = [
            "# 成本监控报告",
            "",
            f"**统计周期**: {report.period}",
            f"**生成时间**: {datetime.now().isoformat()}",
            "",
            "---",
            "",
            "## 📊 成本概览",
            "",
            f"- **总成本**: {report.total_cost:.2f}",
            f"- **预算上限**: {report.budget_limit:.2f}",
            f"- **使用率**: {report.usage_percentage:.1%}",
            f"- **预警级别**: {report.alert_level}",
            "",
            "---",
            "",
            "## 📁 成本分布",
            "",
            "### 按类别",
        ]
        
        for category, amount in report.cost_by_category.items():
            lines.append(f"- {category}: {amount:.2f}")
        
        lines.extend(["", "### 按级别", ""])
        
        level_names = {
            'L1_BASE': 'L1 基础成本',
            'L2_EXTENDED': 'L2 扩展成本',
            'L3_VALUE_ADDED': 'L3 增值成本',
            'L4_RISK': 'L4 风险成本'
        }
        
        for level, amount in report.cost_by_level.items():
            name = level_names.get(level, level)
            lines.append(f"- {name}: {amount:.2f}")
        
        if report.alerts:
            lines.extend([
                "",
                "---",
                "",
                "## 🚨 预警记录",
                "",
            ])
            for alert in report.alerts[-5:]:  # 最近5条
                lines.append(f"- [{alert['level'].upper()}] {alert['message']}")
        
        if report.recommendations:
            lines.extend([
                "",
                "---",
                "",
                "## 💡 优化建议",
                "",
            ])
            for rec in report.recommendations:
                lines.append(f"- {rec}")
        
        return '\n'.join(lines)


def main():
    """主入口"""
    parser = argparse.ArgumentParser(description='Cost Redlines - 成本红线监控')
    parser.add_argument('--config', '-c', default='config.yaml',
                       help='配置文件路径')
    parser.add_argument('--record', nargs=4,
                       metavar=('AMOUNT', 'CATEGORY', 'LEVEL', 'DESC'),
                       help='记录成本: 金额 类别 级别 描述')
    parser.add_argument('--report', action='store_true',
                       help='生成成本报告')
    parser.add_argument('--check', type=float,
                       metavar='AMOUNT',
                       help='检查预算是否可用')
    parser.add_argument('--format', choices=['json', 'markdown'], default='markdown',
                       help='报告格式')
    
    args = parser.parse_args()
    
    # 初始化监控器
    monitor = CostMonitor(args.config)
    
    try:
        if args.record:
            amount = float(args.record[0])
            category = args.record[1]
            level = args.record[2]
            description = args.record[3]
            
            entry = monitor.record_cost(amount, category, level, description)
            print(f"✅ 成本已记录: {amount:.2f} ({category})")
            
            # 显示当前状态
            total = monitor.get_total_cost()
            budget = monitor.config.get('budget_limit', 1000.0)
            print(f"   当前总计: {total:.2f} / {budget:.2f} ({total/budget:.1%})")
            
        elif args.report:
            report = monitor.generate_report()
            output = monitor.export_report(report, args.format)
            print(output)
            
        elif args.check is not None:
            available, message = monitor.check_budget_available(args.check)
            status = "✅" if available else "❌"
            print(f"{status} {message}")
            
        else:
            # 显示当前状态
            total = monitor.get_total_cost()
            budget = monitor.config.get('budget_limit', 1000.0)
            alert = monitor.get_alert_level()
            
            print("=" * 50)
            print("Cost Redlines - 成本红线监控")
            print("=" * 50)
            print(f"当前成本: {total:.2f}")
            print(f"预算上限: {budget:.2f}")
            print(f"使用率: {total/budget:.1%}")
            print(f"预警级别: {alert.value}")
            print("=" * 50)
            
    except Exception as e:
        print(f"❌ 错误: {e}", file=__import__('sys').stderr)
        return 1
    
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
