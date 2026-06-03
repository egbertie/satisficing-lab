#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Metrics Collector V1.0
量化指标自动化收集脚本

功能：
1. 每日自动统计核心指标数据
2. 生成 metrics-report.json 报告
3. 阈值告警检查
4. 数据持久化存储

使用：
    python3 metrics-collector.py [--date YYYY-MM-DD] [--output path]
"""

import json
import os
import sys
import argparse
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============ 核心指标定义 ============

@dataclass
class CoreMetrics:
    """核心量化指标数据结构"""
    
    # 1. ASR - 任务成功率 (Task Success Rate)
    # 公式: 实际完成任务数 / 承诺完成任务数 × 100%
    asr: float = 0.0  # 百分比
    tasks_promised: int = 0
    tasks_completed: int = 0
    
    # 2. 幻觉率 (Hallucination Rate)
    # 公式: 虚假声明数 / 总声明数 × 100%
    # 需通过抽样审计确定
    hallucination_rate: float = 0.0  # 百分比
    total_statements: int = 0
    false_statements: int = 0
    sample_size: int = 0  # 抽样审计样本数
    
    # 3. Token效率 (Token Efficiency)
    # 公式: 有效产出字数 / 消耗Token数
    token_efficiency: float = 0.0
    output_chars: int = 0  # 有效产出字数
    tokens_consumed: int = 0  # 消耗Token数
    
    # 4. 响应时间 (Response Time)
    # 公式: 请求到首token的平均延迟 (毫秒)
    avg_response_time_ms: float = 0.0
    max_response_time_ms: float = 0.0
    min_response_time_ms: float = 0.0
    request_count: int = 0
    
    # 5. 错误重复率 (Error Recurrence Rate)
    # 公式: 重复错误数 / 总错误数 × 100%
    error_recurrence_rate: float = 0.0  # 百分比
    total_errors: int = 0
    repeated_errors: int = 0
    
    # 6. 蓝军发现率 (Red Team Discovery Rate)
    # 公式: 蓝军发现问题数 / 总问题数 × 100%
    red_team_discovery_rate: float = 0.0  # 百分比
    red_team_issues: int = 0
    total_issues: int = 0
    
    # 7. 用户满意度 (User Satisfaction)
    # 公式: 用户确认满意数 / 总交互数 × 100%
    # 需反馈机制支持
    user_satisfaction: float = 0.0  # 百分比
    satisfied_users: int = 0
    total_interactions: int = 0
    feedback_received: int = 0
    
    # 元数据
    date: str = ""  # 统计日期
    generated_at: str = ""  # 生成时间
    version: str = "1.0"


# ============ 阈值配置 ============

class ThresholdConfig:
    """阈值告警配置"""
    
    # 关键指标阈值 (触发告警的边界值)
    THRESHOLDS = {
        # ASR: 低于80%触发告警
        "asr_min": 80.0,
        
        # 幻觉率: 高于5%触发告警
        "hallucination_max": 5.0,
        
        # Token效率: 低于30%触发告警 (每Token产出字符数)
        "token_efficiency_min": 0.30,
        
        # 响应时间: 超过3000ms触发告警
        "response_time_max_ms": 3000,
        
        # 错误重复率: 高于20%触发告警
        "error_recurrence_max": 20.0,
        
        # 蓝军发现率: 低于50%触发告警 (蓝军发现问题占比过低说明测试不充分)
        "red_team_discovery_min": 50.0,
        
        # 用户满意度: 低于70%触发告警
        "user_satisfaction_min": 70.0,
    }
    
    # 目标值 (期望达到的目标)
    TARGETS = {
        "asr_target": 95.0,
        "hallucination_target": 1.0,
        "token_efficiency_target": 0.50,
        "response_time_target_ms": 1000,
        "error_recurrence_target": 5.0,
        "red_team_discovery_target": 70.0,
        "user_satisfaction_target": 85.0,
    }


# ============ 告警系统 ============

class AlertSystem:
    """阈值告警系统"""
    
    ALERT_LEVELS = {
        "CRITICAL": "🔴 严重",
        "WARNING": "🟡 警告", 
        "INFO": "🟢 正常"
    }
    
    def __init__(self):
        self.alerts: List[Dict[str, Any]] = []
    
    def check_thresholds(self, metrics: CoreMetrics) -> List[Dict[str, Any]]:
        """检查所有指标阈值并生成告警"""
        self.alerts = []
        
        # ASR检查
        if metrics.asr < ThresholdConfig.THRESHOLDS["asr_min"]:
            self._add_alert(
                "ASR", "CRITICAL",
                f"任务成功率 {metrics.asr:.1f}% 低于阈值 {ThresholdConfig.THRESHOLDS['asr_min']}%",
                metrics.asr,
                ThresholdConfig.THRESHOLDS["asr_min"]
            )
        
        # 幻觉率检查
        if metrics.hallucination_rate > ThresholdConfig.THRESHOLDS["hallucination_max"]:
            self._add_alert(
                "幻觉率", "CRITICAL",
                f"幻觉率 {metrics.hallucination_rate:.1f}% 超过阈值 {ThresholdConfig.THRESHOLDS['hallucination_max']}%",
                metrics.hallucination_rate,
                ThresholdConfig.THRESHOLDS["hallucination_max"]
            )
        
        # Token效率检查
        if metrics.token_efficiency < ThresholdConfig.THRESHOLDS["token_efficiency_min"]:
            self._add_alert(
                "Token效率", "WARNING",
                f"Token效率 {metrics.token_efficiency:.2f} 低于阈值 {ThresholdConfig.THRESHOLDS['token_efficiency_min']}",
                metrics.token_efficiency,
                ThresholdConfig.THRESHOLDS["token_efficiency_min"]
            )
        
        # 响应时间检查
        if metrics.avg_response_time_ms > ThresholdConfig.THRESHOLDS["response_time_max_ms"]:
            self._add_alert(
                "响应时间", "WARNING",
                f"平均响应时间 {metrics.avg_response_time_ms:.0f}ms 超过阈值 {ThresholdConfig.THRESHOLDS['response_time_max_ms']}ms",
                metrics.avg_response_time_ms,
                ThresholdConfig.THRESHOLDS["response_time_max_ms"]
            )
        
        # 错误重复率检查
        if metrics.error_recurrence_rate > ThresholdConfig.THRESHOLDS["error_recurrence_max"]:
            self._add_alert(
                "错误重复率", "WARNING",
                f"错误重复率 {metrics.error_recurrence_rate:.1f}% 超过阈值 {ThresholdConfig.THRESHOLDS['error_recurrence_max']}%",
                metrics.error_recurrence_rate,
                ThresholdConfig.THRESHOLDS["error_recurrence_max"]
            )
        
        # 蓝军发现率检查
        if metrics.red_team_discovery_rate < ThresholdConfig.THRESHOLDS["red_team_discovery_min"]:
            self._add_alert(
                "蓝军发现率", "INFO",
                f"蓝军发现率 {metrics.red_team_discovery_rate:.1f}% 低于阈值 {ThresholdConfig.THRESHOLDS['red_team_discovery_min']}%",
                metrics.red_team_discovery_rate,
                ThresholdConfig.THRESHOLDS["red_team_discovery_min"]
            )
        
        # 用户满意度检查
        if metrics.user_satisfaction < ThresholdConfig.THRESHOLDS["user_satisfaction_min"]:
            self._add_alert(
                "用户满意度", "CRITICAL",
                f"用户满意度 {metrics.user_satisfaction:.1f}% 低于阈值 {ThresholdConfig.THRESHOLDS['user_satisfaction_min']}%",
                metrics.user_satisfaction,
                ThresholdConfig.THRESHOLDS["user_satisfaction_min"]
            )
        
        return self.alerts
    
    def _add_alert(self, metric: str, level: str, message: str, 
                   actual: float, threshold: float):
        """添加告警记录"""
        self.alerts.append({
            "metric": metric,
            "level": level,
            "level_display": self.ALERT_LEVELS.get(level, level),
            "message": message,
            "actual_value": actual,
            "threshold": threshold,
            "timestamp": datetime.now().isoformat()
        })
    
    def has_critical(self) -> bool:
        """是否存在严重告警"""
        return any(a["level"] == "CRITICAL" for a in self.alerts)


# ============ 数据收集器 ============

class MetricsCollector:
    """指标数据收集器"""
    
    def __init__(self, data_dir: str = "./data/metrics"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.alert_system = AlertSystem()
    
    def collect_from_logs(self, date: str) -> CoreMetrics:
        """
        从日志文件收集指标数据
        实际实现中需要解析真实的日志文件
        """
        metrics = CoreMetrics(date=date)
        metrics.generated_at = datetime.now().isoformat()
        
        # TODO: 实现从实际日志文件解析数据
        # 以下是模拟数据，实际使用时替换为真实数据收集逻辑
        
        log_path = self.data_dir / f"raw_{date}.log"
        if log_path.exists():
            # 解析日志文件
            metrics = self._parse_log_file(log_path, date)
        else:
            # 使用模拟数据（首次运行）
            logger.warning(f"未找到日志文件 {log_path}，使用基线数据")
            metrics = self._generate_baseline_metrics(date)
        
        return metrics
    
    def _parse_log_file(self, log_path: Path, date: str) -> CoreMetrics:
        """解析日志文件提取指标"""
        metrics = CoreMetrics(date=date)
        metrics.generated_at = datetime.now().isoformat()
        
        # TODO: 实现具体的日志解析逻辑
        # 解析任务完成记录、错误日志、响应时间等
        
        return metrics
    
    def _generate_baseline_metrics(self, date: str) -> CoreMetrics:
        """生成基线指标数据（首次运行使用）"""
        return CoreMetrics(
            date=date,
            generated_at=datetime.now().isoformat(),
            # ASR
            asr=85.0,
            tasks_promised=100,
            tasks_completed=85,
            # 幻觉率
            hallucination_rate=3.5,
            total_statements=1000,
            false_statements=35,
            sample_size=100,
            # Token效率
            token_efficiency=0.35,
            output_chars=35000,
            tokens_consumed=100000,
            # 响应时间
            avg_response_time_ms=1500,
            max_response_time_ms=5000,
            min_response_time_ms=200,
            request_count=500,
            # 错误重复率
            error_recurrence_rate=15.0,
            total_errors=50,
            repeated_errors=7,
            # 蓝军发现率
            red_team_discovery_rate=60.0,
            red_team_issues=30,
            total_issues=50,
            # 用户满意度
            user_satisfaction=75.0,
            satisfied_users=75,
            total_interactions=100,
            feedback_received=80
        )
    
    def generate_report(self, metrics: CoreMetrics) -> Dict[str, Any]:
        """生成完整报告"""
        # 检查阈值告警
        alerts = self.alert_system.check_thresholds(metrics)
        
        report = {
            "report_version": "1.0",
            "generated_at": datetime.now().isoformat(),
            "date": metrics.date,
            "metrics": asdict(metrics),
            "thresholds": ThresholdConfig.THRESHOLDS,
            "targets": ThresholdConfig.TARGETS,
            "alerts": alerts,
            "summary": self._generate_summary(metrics, alerts)
        }
        
        return report
    
    def _generate_summary(self, metrics: CoreMetrics, alerts: List[Dict]) -> Dict[str, Any]:
        """生成报告摘要"""
        critical_count = sum(1 for a in alerts if a["level"] == "CRITICAL")
        warning_count = sum(1 for a in alerts if a["level"] == "WARNING")
        
        return {
            "total_metrics": 7,
            "critical_alerts": critical_count,
            "warning_alerts": warning_count,
            "overall_health": "CRITICAL" if critical_count > 0 else "WARNING" if warning_count > 0 else "HEALTHY",
            "key_findings": [
                f"ASR: {metrics.asr:.1f}% (目标: {ThresholdConfig.TARGETS['asr_target']}%)",
                f"幻觉率: {metrics.hallucination_rate:.1f}% (目标: <{ThresholdConfig.TARGETS['hallucination_target']}%)",
                f"用户满意度: {metrics.user_satisfaction:.1f}% (目标: {ThresholdConfig.TARGETS['user_satisfaction_target']}%)",
            ]
        }
    
    def save_report(self, report: Dict[str, Any], output_path: Optional[str] = None):
        """保存报告到文件"""
        if output_path is None:
            date = report.get("date", datetime.now().strftime("%Y-%m-%d"))
            output_path = self.data_dir / f"metrics-report-{date}.json"
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"报告已保存: {output_path}")
        return output_path
    
    def load_historical_data(self, days: int = 30) -> List[CoreMetrics]:
        """加载历史指标数据用于趋势分析"""
        history = []
        
        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            report_path = self.data_dir / f"metrics-report-{date}.json"
            
            if report_path.exists():
                with open(report_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    metrics = CoreMetrics(**data.get("metrics", {}))
                    history.append(metrics)
        
        return history


# ============ 主入口 ============

def main():
    parser = argparse.ArgumentParser(description='量化指标收集器 V1.0')
    parser.add_argument('--date', type=str, 
                        default=datetime.now().strftime("%Y-%m-%d"),
                        help='统计日期 (YYYY-MM-DD)')
    parser.add_argument('--output', type=str, 
                        default='./data/metrics/metrics-report.json',
                        help='输出文件路径')
    parser.add_argument('--data-dir', type=str,
                        default='./data/metrics',
                        help='数据目录')
    parser.add_argument('--collect-only', action='store_true',
                        help='仅收集数据，不生成报告')
    
    args = parser.parse_args()
    
    # 初始化收集器
    collector = MetricsCollector(data_dir=args.data_dir)
    
    # 收集数据
    logger.info(f"开始收集 {args.date} 的指标数据...")
    metrics = collector.collect_from_logs(args.date)
    
    if args.collect_only:
        logger.info("数据收集完成 (collect-only 模式)")
        print(json.dumps(asdict(metrics), ensure_ascii=False, indent=2))
        return
    
    # 生成报告
    logger.info("生成报告...")
    report = collector.generate_report(metrics)
    
    # 保存报告
    output_path = collector.save_report(report, args.output)
    
    # 输出摘要
    summary = report.get("summary", {})
    print("\n" + "="*60)
    print(f"📊 量化指标报告 - {args.date}")
    print("="*60)
    print(f"整体状态: {summary.get('overall_health', 'UNKNOWN')}")
    print(f"严重告警: {summary.get('critical_alerts', 0)}")
    print(f"警告: {summary.get('warning_alerts', 0)}")
    print("\n关键指标:")
    for finding in summary.get('key_findings', []):
        print(f"  • {finding}")
    print("\n告警详情:")
    for alert in report.get('alerts', []):
        print(f"  {alert['level_display']} [{alert['metric']}] {alert['message']}")
    print("="*60)
    print(f"\n报告已保存: {output_path}")
    
    # 如果有严重告警，返回非零退出码
    if summary.get('critical_alerts', 0) > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
