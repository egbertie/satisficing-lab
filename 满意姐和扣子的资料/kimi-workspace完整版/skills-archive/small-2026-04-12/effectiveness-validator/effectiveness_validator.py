"""
效果验证器 - Effectiveness Validator
核心模块: 整改效果验证与迭代追踪
版本: 1.0.0
日期: 2026-04-02
"""

import json
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional
from datetime import datetime


@dataclass
class ValidationMetric:
    """验证指标"""
    metric_name: str
    target_value: float
    actual_value: float
    status: str  # pass/fail/partial
    notes: str


@dataclass
class ValidationReport:
    """验证报告"""
    validation_date: str
    overall_status: str
    metrics: List[ValidationMetric]
    issues: List[str]
    iteration_plan: List[str]


class EffectivenessValidator:
    """
    效果验证器
    
    验证整改措施的实际效果:
    - 严格写入纪律: 写入失败率
    - Token预算守卫: 预算超限次数
    - 质量闸口: 拦截率
    - 记忆索引: 索引大小
    
    迭代追踪:
    - 发现问题 → 生成迭代计划
    - 持续改进
    """
    
    def __init__(self, log_dir: str = "~/.openclaw/validation_logs"):
        self.log_dir = Path(log_dir).expanduser()
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # 验证指标定义
        self.metrics_def = {
            "write_failure_rate": {
                "name": "写入失败率",
                "target": 0.0,  # 目标0%
                "threshold": 0.05  # 容忍5%
            },
            "token_meltdown_count": {
                "name": "Token熔断次数",
                "target": 0,
                "threshold": 1
            },
            "quality_gate_miss": {
                "name": "质量闸口漏检率",
                "target": 0.0,
                "threshold": 0.10
            },
            "memory_index_size": {
                "name": "MEMORY.md大小",
                "target": 5120,  # 5KB
                "threshold": 6144  # 6KB容忍
            },
            "compression_ratio": {
                "name": "记忆压缩比",
                "target": 5.0,
                "threshold": 3.0
            }
        }
    
    def validate_all(self, measurement_data: Dict) -> ValidationReport:
        """
        验证所有指标
        
        Args:
            measurement_data: 实际测量数据
        """
        metrics = []
        issues = []
        
        for metric_key, metric_def in self.metrics_def.items():
            actual = measurement_data.get(metric_key, 0)
            target = metric_def["target"]
            threshold = metric_def["threshold"]
            
            # 判断状态
            if actual <= target:
                status = "pass"
                notes = "达标"
            elif actual <= threshold:
                status = "partial"
                notes = "部分达标，需关注"
                issues.append(f"{metric_def['name']}: {actual} (目标: {target})")
            else:
                status = "fail"
                notes = "未达标，需整改"
                issues.append(f"{metric_def['name']}: {actual} (目标: {target}) - 需立即整改")
            
            metrics.append(ValidationMetric(
                metric_name=metric_def["name"],
                target_value=target,
                actual_value=actual,
                status=status,
                notes=notes
            ))
        
        # 确定整体状态
        fail_count = sum(1 for m in metrics if m.status == "fail")
        partial_count = sum(1 for m in metrics if m.status == "partial")
        
        if fail_count > 0:
            overall = "needs_immediate_fix"
        elif partial_count > 0:
            overall = "needs_iteration"
        else:
            overall = "all_passed"
        
        # 生成迭代计划
        iteration_plan = self._generate_iteration_plan(metrics)
        
        report = ValidationReport(
            validation_date=datetime.now().isoformat(),
            overall_status=overall,
            metrics=metrics,
            issues=issues,
            iteration_plan=iteration_plan
        )
        
        # 保存日志
        self._save_validation_log(report)
        
        return report
    
    def _generate_iteration_plan(self, metrics: List[ValidationMetric]) -> List[str]:
        """生成迭代计划"""
        plan = []
        
        for metric in metrics:
            if metric.status == "fail":
                plan.append(f"[紧急] 修复{metric.metric_name}: 当前{metric.actual_value} → 目标{metric.target_value}")
            elif metric.status == "partial":
                plan.append(f"[优化] 改进{metric.metric_name}: 当前{metric.actual_value} → 目标{metric.target_value}")
        
        if not plan:
            plan.append("所有指标达标，保持当前状态")
        
        return plan
    
    def _save_validation_log(self, report: ValidationReport):
        """保存验证日志"""
        log_file = self.log_dir / f"validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        data = {
            "date": report.validation_date,
            "overall_status": report.overall_status,
            "metrics": [asdict(m) for m in report.metrics],
            "issues": report.issues,
            "iteration_plan": report.iteration_plan
        }
        
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def get_validation_history(self, limit: int = 10) -> List[Dict]:
        """获取验证历史"""
        logs = sorted(self.log_dir.glob("validation_*.json"), reverse=True)
        
        history = []
        for log in logs[:limit]:
            with open(log, 'r', encoding='utf-8') as f:
                history.append(json.load(f))
        
        return history
    
    def generate_summary(self, report: ValidationReport) -> str:
        """生成验证摘要"""
        lines = [
            "=" * 50,
            "效果验证报告",
            "=" * 50,
            f"验证时间: {report.validation_date}",
            f"整体状态: {report.overall_status}",
            "",
            "指标详情:"
        ]
        
        for m in report.metrics:
            icon = "✅" if m.status == "pass" else "⚠️" if m.status == "partial" else "❌"
            lines.append(f"  {icon} {m.metric_name}: {m.actual_value} (目标: {m.target_value}) - {m.notes}")
        
        if report.issues:
            lines.extend(["", "待解决问题:"])
            for issue in report.issues:
                lines.append(f"  - {issue}")
        
        if report.iteration_plan:
            lines.extend(["", "迭代计划:"])
            for plan in report.iteration_plan:
                lines.append(f"  - {plan}")
        
        lines.append("=" * 50)
        
        return '\n'.join(lines)


# 便捷函数接口
def validate_effectiveness(measurement_data: Dict) -> ValidationReport:
    """便捷验证函数"""
    validator = EffectivenessValidator()
    return validator.validate_all(measurement_data)


if __name__ == "__main__":
    # 单元测试
    print("=" * 50)
    print("效果验证器 - 单元测试")
    print("=" * 50)
    
    validator = EffectivenessValidator()
    
    # 测试1: 全部通过
    print("\n[测试1] 全部指标通过...")
    good_data = {
        "write_failure_rate": 0.0,
        "token_meltdown_count": 0,
        "quality_gate_miss": 0.0,
        "memory_index_size": 4000,
        "compression_ratio": 6.0
    }
    report = validator.validate_all(good_data)
    print(f"  整体状态: {report.overall_status}")
    print(f"  通过数: {sum(1 for m in report.metrics if m.status == 'pass')}")
    
    # 测试2: 部分未达标
    print("\n[测试2] 部分指标未达标...")
    bad_data = {
        "write_failure_rate": 0.02,
        "token_meltdown_count": 1,
        "quality_gate_miss": 0.15,
        "memory_index_size": 7000,
        "compression_ratio": 2.5
    }
    report = validator.validate_all(bad_data)
    print(f"  整体状态: {report.overall_status}")
    print(f"  问题数: {len(report.issues)}")
    print(f"  迭代计划数: {len(report.iteration_plan)}")
    
    # 测试3: 生成摘要
    print("\n[测试3] 生成验证摘要...")
    summary = validator.generate_summary(report)
    print(summary[:300] + "...")
    
    print("\n" + "=" * 50)
    print("单元测试完成")
    print("=" * 50)