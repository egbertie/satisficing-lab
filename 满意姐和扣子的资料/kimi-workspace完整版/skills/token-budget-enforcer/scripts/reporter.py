#!/usr/bin/env python3
"""
Token预算报告生成器 (Reporter)
S3标准: 输出预算报告+预警通知+调整建议
S5标准: 预算核算准确性验证
"""

import json
import yaml
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List
from dataclasses import dataclass, asdict

@dataclass
class BudgetReport:
    """预算报告"""
    report_type: str  # daily, weekly, monthly
    generated_at: str
    period_start: str
    period_end: str
    summary: dict
    pools: dict
    metrics: dict
    alerts: List[dict]
    recommendations: List[str]

class BudgetReporter:
    """Token预算报告生成器"""
    
    def __init__(self, data_dir: str = None, config_dir: str = None):
        if data_dir is None:
            data_dir = Path(__file__).parent.parent / "data"
        if config_dir is None:
            config_dir = Path(__file__).parent.parent / "config"
        
        self.data_dir = Path(data_dir)
        self.config_dir = Path(config_dir)
        
        self.consumption_file = self.data_dir / "consumption.json"
        self.forecasts_file = self.data_dir / "forecasts.json"
        
        # 加载配置
        self.budget_config = self._load_yaml("budgets.yaml")
    
    def _load_yaml(self, filename: str) -> dict:
        """加载YAML配置"""
        filepath = self.config_dir / filename
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        return {}
    
    def _load_consumption_data(self) -> dict:
        """加载消耗数据"""
        if self.consumption_file.exists():
            with open(self.consumption_file, 'r') as f:
                return json.load(f)
        return {"daily_records": {}}
    
    def _load_forecasts(self) -> dict:
        """加载预测数据"""
        if self.forecasts_file.exists():
            with open(self.forecasts_file, 'r') as f:
                return json.load(f)
        return {"forecasts": {}}
    
    def generate_daily_report(self, date: str = None) -> BudgetReport:
        """生成日报"""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        data = self._load_consumption_data()
        forecasts = self._load_forecasts()
        
        record = data.get("daily_records", {}).get(date, {})
        if not record:
            record = self._create_empty_record(date)
        
        # 计算指标
        metrics = self._calculate_metrics(record, forecasts, date)
        
        # 生成告警
        alerts = self._generate_alerts(record, metrics)
        
        # 生成建议
        recommendations = self._generate_recommendations(record, metrics, alerts)
        
        # S5: 预算核算准确性验证
        accuracy_validation = self._validate_budget_accuracy(record, forecasts, date)
        
        return BudgetReport(
            report_type="daily",
            generated_at=datetime.now().isoformat(),
            period_start=date,
            period_end=date,
            summary={
                "total_budget": record.get("total_budget", 50000),
                "total_used": record.get("total_used", 0),
                "total_remaining": record.get("total_budget", 50000) - record.get("total_used", 0),
                "usage_percent": metrics.get("usage_percent", 0),
                "task_count": record.get("task_count", 0),
                "efficiency_score": record.get("efficiency_score", 0)
            },
            pools=record.get("pools", {}),
            metrics={
                "usage": metrics,
                "accuracy_validation": accuracy_validation,
                "efficiency": {
                    "score": record.get("efficiency_score", 0),
                    "tokens_per_task": record.get("total_used", 0) / max(record.get("task_count", 1), 1)
                }
            },
            alerts=alerts,
            recommendations=recommendations
        )
    
    def _create_empty_record(self, date: str) -> dict:
        """创建空记录"""
        return {
            "date": date,
            "total_budget": 50000,
            "total_used": 0,
            "pools": {},
            "task_count": 0,
            "efficiency_score": 0
        }
    
    def _calculate_metrics(self, record: dict, forecasts: dict, date: str) -> dict:
        """计算指标"""
        total_budget = record.get("total_budget", 50000)
        total_used = record.get("total_used", 0)
        usage_percent = (total_used / total_budget * 100) if total_budget > 0 else 0
        
        # 获取预测
        forecast = forecasts.get("forecasts", {}).get(date, {})
        predicted = forecast.get("predicted_usage", 0)
        
        # 预测偏差
        if predicted > 0:
            forecast_deviation = abs(total_used - predicted) / predicted
        else:
            forecast_deviation = 0
        
        return {
            "usage_percent": round(usage_percent, 1),
            "remaining_percent": round(100 - usage_percent, 1),
            "predicted_usage": predicted,
            "forecast_deviation": round(forecast_deviation, 2),
            "forecast_deviation_percent": f"{forecast_deviation*100:.1f}%"
        }
    
    def _generate_alerts(self, record: dict, metrics: dict) -> List[dict]:
        """生成告警"""
        alerts = []
        usage_percent = metrics.get("usage_percent", 0)
        
        if usage_percent >= 100:
            alerts.append({
                "level": "emergency",
                "type": "budget_exhausted",
                "message": "日预算已耗尽！",
                "value": f"{usage_percent:.1f}%"
            })
        elif usage_percent >= 90:
            alerts.append({
                "level": "critical",
                "type": "budget_critical",
                "message": "预算使用超过90%",
                "value": f"{usage_percent:.1f}%"
            })
        elif usage_percent >= 70:
            alerts.append({
                "level": "warning",
                "type": "budget_warning",
                "message": "预算使用超过70%",
                "value": f"{usage_percent:.1f}%"
            })
        
        # 预测偏差告警
        deviation = metrics.get("forecast_deviation", 0)
        if deviation > 0.5:
            alerts.append({
                "level": "warning",
                "type": "forecast_inaccurate",
                "message": f"预测偏差过大 ({metrics.get('forecast_deviation_percent')})",
                "value": metrics.get('forecast_deviation_percent')
            })
        
        return alerts
    
    def _generate_recommendations(self, record: dict, metrics: dict, alerts: List[dict]) -> List[str]:
        """生成调整建议"""
        recommendations = []
        usage_percent = metrics.get("usage_percent", 0)
        
        if usage_percent >= 90:
            recommendations.append("🔴 预算紧急：立即启用极简模式，非P0任务暂停")
        elif usage_percent >= 70:
            recommendations.append("🟡 预算注意：考虑减少非必要任务，优先高价值产出")
        
        efficiency = record.get("efficiency_score", 0)
        if efficiency < 0.7:
            recommendations.append("📉 效率偏低：建议审查任务类型，优化高频Skill")
        
        deviation = metrics.get("forecast_deviation", 0)
        if deviation > 0.3:
            recommendations.append("📊 预估偏差大：建议重新校准预估模型")
        
        if not recommendations:
            recommendations.append("✅ 预算使用正常，继续保持")
        
        return recommendations
    
    def _validate_budget_accuracy(self, record: dict, forecasts: dict, date: str) -> dict:
        """
        S5: 预算核算准确性验证
        验证预算记录、消耗统计、预测准确性的完整性
        """
        validation = {
            "status": "valid",
            "checks": [],
            "errors": []
        }
        
        # 检查1: 预算池总和是否等于总预算
        pools = record.get("pools", {})
        pools_total = sum(p.get("allocated", 0) for p in pools.values())
        total_budget = record.get("total_budget", 0)
        
        if abs(pools_total - total_budget) > 1:  # 允许1token误差
            validation["checks"].append({
                "check": "pool_allocation_sum",
                "status": "error",
                "message": f"预算池总和({pools_total})不等于总预算({total_budget})"
            })
            validation["errors"].append("预算分配不平衡")
        else:
            validation["checks"].append({
                "check": "pool_allocation_sum",
                "status": "pass",
                "message": "预算池分配正确"
            })
        
        # 检查2: 消耗统计一致性
        pools_used = sum(p.get("used", 0) for p in pools.values())
        total_used = record.get("total_used", 0)
        
        if abs(pools_used - total_used) > 1:
            validation["checks"].append({
                "check": "consumption_consistency",
                "status": "error",
                "message": f"各池消耗总和({pools_used})不等于总消耗({total_used})"
            })
            validation["errors"].append("消耗统计不一致")
        else:
            validation["checks"].append({
                "check": "consumption_consistency",
                "status": "pass",
                "message": "消耗统计一致"
            })
        
        # 检查3: 预测准确性
        forecast = forecasts.get("forecasts", {}).get(date, {})
        if forecast:
            predicted = forecast.get("predicted_usage", 0)
            actual = record.get("total_used", 0)
            if predicted > 0:
                accuracy = 1 - abs(actual - predicted) / predicted
                validation["checks"].append({
                    "check": "forecast_accuracy",
                    "status": "pass" if accuracy >= 0.8 else "warning",
                    "message": f"预测准确率: {accuracy*100:.1f}%"
                })
        
        # 检查4: 数据完整性
        required_fields = ["date", "total_budget", "total_used", "pools"]
        missing = [f for f in required_fields if f not in record]
        if missing:
            validation["checks"].append({
                "check": "data_completeness",
                "status": "error",
                "message": f"缺少字段: {missing}"
            })
            validation["errors"].append("数据不完整")
        else:
            validation["checks"].append({
                "check": "data_completeness",
                "status": "pass",
                "message": "数据完整"
            })
        
        if validation["errors"]:
            validation["status"] = "invalid"
        
        return validation
    
    def format_report_text(self, report: BudgetReport) -> str:
        """格式化报告为文本"""
        lines = []
        lines.append("=" * 60)
        lines.append(f"[Token效率日报 - {report.period_start}]")
        lines.append("=" * 60)
        lines.append("")
        
        # 概览
        summary = report.summary
        lines.append("📊 概览:")
        lines.append(f"  总预算: {summary['total_budget']:,} tokens")
        lines.append(f"  已使用: {summary['total_used']:,} tokens ({summary['usage_percent']:.1f}%)")
        lines.append(f"  剩余: {summary['total_remaining']:,} tokens")
        lines.append(f"  任务数: {summary['task_count']}")
        lines.append(f"  效率评分: {summary['efficiency_score']*100:.0f}%")
        lines.append("")
        
        # 预算池
        lines.append("💰 预算池状态:")
        for pool_name, pool_data in report.pools.items():
            status_emoji = {
                "normal": "🟢",
                "warning": "🟡",
                "critical": "🔴",
                "exhausted": "⛔"
            }
            emoji = status_emoji.get(pool_data.get("status", "normal"), "⚪")
            lines.append(f"  {emoji} {pool_name}:")
            lines.append(f"     已用: {pool_data.get('used', 0):,} / {pool_data.get('allocated', 0):,}")
            lines.append(f"     使用率: {pool_data.get('usage_percent', 0):.1f}%")
        lines.append("")
        
        # 告警
        if report.alerts:
            lines.append("⚠️ 告警:")
            for alert in report.alerts:
                emoji = {"emergency": "🚨", "critical": "🔴", "warning": "🟡"}
                lines.append(f"  {emoji.get(alert['level'], '⚠️')} {alert['message']}")
            lines.append("")
        
        # 建议
        lines.append("💡 建议:")
        for rec in report.recommendations:
            lines.append(f"  {rec}")
        lines.append("")
        
        # S5: 准确性验证
        validation = report.metrics.get("accuracy_validation", {})
        lines.append("✅ 准确性验证:")
        for check in validation.get("checks", []):
            emoji = {"pass": "✓", "warning": "⚠", "error": "✗"}
            lines.append(f"  {emoji.get(check['status'], '?')} {check['check']}: {check['message']}")
        
        lines.append("")
        lines.append(f"报告生成时间: {report.generated_at}")
        lines.append("=" * 60)
        
        return "\n".join(lines)
    
    def save_report(self, report: BudgetReport):
        """保存报告到文件"""
        reports_dir = self.data_dir / "reports"
        reports_dir.mkdir(exist_ok=True)
        
        filename = f"report_{report.period_start}_{report.report_type}.json"
        filepath = reports_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(asdict(report), f, indent=2)
        
        # 同时保存文本版
        text_filepath = reports_dir / filename.replace(".json", ".txt")
        with open(text_filepath, 'w') as f:
            f.write(self.format_report_text(report))
        
        return filepath


def main():
    """命令行接口"""
    import sys
    
    reporter = BudgetReporter()
    
    if len(sys.argv) < 2:
        # 生成今日报告
        report = reporter.generate_daily_report()
        print(reporter.format_report_text(report))
        return 0
    
    command = sys.argv[1]
    
    if command == "daily":
        date = sys.argv[2] if len(sys.argv) > 2 else None
        report = reporter.generate_daily_report(date)
        print(reporter.format_report_text(report))
        
        # 保存报告
        saved_path = reporter.save_report(report)
        print(f"\n报告已保存: {saved_path}")
    
    elif command == "json":
        date = sys.argv[2] if len(sys.argv) > 2 else None
        report = reporter.generate_daily_report(date)
        print(json.dumps(asdict(report), indent=2))
    
    else:
        print(f"Unknown command: {command}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
