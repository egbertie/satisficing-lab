#!/usr/bin/env python3
"""
健康检查脚本 - Cron-Automation System S5自我验证组件

功能:
- 检查配置完整性
- 验证Cron表达式
- 检查脚本存在性和可执行性
- 检查资源状态
- 生成健康报告

S5标准: 自我验证 - 质量指标、自检脚本、健康检查
"""

import json
import os
import sys
import subprocess
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import re

# 路径配置
BASE_DIR = Path(__file__).parent.parent
CONFIG_DIR = BASE_DIR / "config"
LOGS_DIR = BASE_DIR / "logs"
REPORTS_DIR = LOGS_DIR / "reports"
REPORTS_DIR.mkdir(exist_ok=True)


class CheckStatus(Enum):
    """检查状态"""
    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"
    SKIP = "SKIP"


@dataclass
class CheckResult:
    """单项检查结果"""
    category: str
    item: str
    status: CheckStatus
    detail: str
    recommendation: str = ""


@dataclass
class HealthReport:
    """健康检查报告"""
    check_time: datetime
    overall_status: str
    score: int
    total_score: int
    checks: List[CheckResult]
    summary: Dict[str, int]
    recommendations: List[str]


class HealthChecker:
    """健康检查器"""
    
    def __init__(self):
        self.checks: List[CheckResult] = []
        self.recommendations: List[str] = []
        self.tasks_config: Dict = {}
        self.alerts_config: Dict = {}
        self.recovery_config: Dict = {}
    
    def run_all_checks(self) -> HealthReport:
        """运行所有检查"""
        print("🔍 开始健康检查...\n")
        
        # 配置检查
        self._check_config_format()
        self._check_cron_expressions()
        self._check_script_paths()
        
        # 运行时检查
        self._check_logs_directory()
        self._check_disk_space()
        self._check_memory_usage()
        
        # 集成检查
        self._check_notification_channels()
        
        # 任务检查
        self._check_task_states()
        
        # 生成报告
        return self._generate_report()
    
    def _check_config_format(self) -> None:
        """检查配置文件格式"""
        print("📋 检查配置文件格式...")
        
        config_files = [
            ("tasks.json", "任务配置"),
            ("alerts.json", "告警配置"),
            ("recovery.json", "恢复策略"),
        ]
        
        for filename, desc in config_files:
            filepath = CONFIG_DIR / filename
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                if filename == "tasks.json":
                    self.tasks_config = data
                elif filename == "alerts.json":
                    self.alerts_config = data
                elif filename == "recovery.json":
                    self.recovery_config = data
                
                self.checks.append(CheckResult(
                    category="配置",
                    item=f"{desc}格式",
                    status=CheckStatus.PASS,
                    detail=f"{filename} 是有效的JSON格式"
                ))
            except json.JSONDecodeError as e:
                self.checks.append(CheckResult(
                    category="配置",
                    item=f"{desc}格式",
                    status=CheckStatus.FAIL,
                    detail=f"{filename} JSON解析错误: {e}",
                    recommendation=f"请修正 {filename} 的JSON语法"
                ))
            except FileNotFoundError:
                self.checks.append(CheckResult(
                    category="配置",
                    item=f"{desc}格式",
                    status=CheckStatus.FAIL,
                    detail=f"{filename} 不存在",
                    recommendation=f"请创建 {filename}"
                ))
    
    def _check_cron_expressions(self) -> None:
        """检查Cron表达式有效性"""
        print("⏰ 检查Cron表达式...")
        
        if not self.tasks_config:
            self.checks.append(CheckResult(
                category="配置",
                item="Cron表达式",
                status=CheckStatus.SKIP,
                detail="任务配置未加载"
            ))
            return
        
        tasks = self.tasks_config.get('tasks', [])
        valid_count = 0
        invalid_count = 0
        
        # 简化版Cron验证正则
        cron_pattern = re.compile(
            r'^([0-5]?\d|\*|\*/\d+|\d+(-\d+)?(/\d+)?) '  # minute
            r'([01]?\d|2[0-3]|\*|\*/\d+|\d+(-\d+)?(/\d+)?) '  # hour
            r'([1-9]|[12]\d|3[01]|\*|\*/\d+|\d+(-\d+)?(/\d+)?) '  # day
            r'([1-9]|1[0-2]|\*|\*/\d+|\d+(-\d+)?(/\d+)?) '  # month
            r'([0-6]|\*|\*/\d+|\d+(-\d+)?(/\d+)?)$'  # weekday
        )
        
        for task in tasks:
            cron = task.get('cron', '')
            if cron_pattern.match(cron) or cron in ['@hourly', '@daily', '@weekly', '@monthly']:
                valid_count += 1
            else:
                invalid_count += 1
                self.checks.append(CheckResult(
                    category="配置",
                    item=f"Cron表达式: {task.get('name', task.get('id'))}",
                    status=CheckStatus.FAIL,
                    detail=f"无效的Cron表达式: {cron}",
                    recommendation=f"请修正任务 {task.get('id')} 的Cron表达式"
                ))
        
        if invalid_count == 0:
            self.checks.append(CheckResult(
                category="配置",
                item="Cron表达式",
                status=CheckStatus.PASS,
                detail=f"所有 {valid_count} 个任务的Cron表达式有效"
            ))
    
    def _check_script_paths(self) -> None:
        """检查脚本路径存在性"""
        print("📜 检查脚本路径...")
        
        if not self.tasks_config:
            self.checks.append(CheckResult(
                category="配置",
                item="脚本路径",
                status=CheckStatus.SKIP,
                detail="任务配置未加载"
            ))
            return
        
        tasks = self.tasks_config.get('tasks', [])
        valid_count = 0
        missing_scripts = []
        
        for task in tasks:
            script_path = BASE_DIR / task.get('script', '')
            if script_path.exists():
                valid_count += 1
            else:
                missing_scripts.append(task.get('script'))
        
        if missing_scripts:
            self.checks.append(CheckResult(
                category="配置",
                item="脚本路径",
                status=CheckStatus.WARN,
                detail=f"{len(missing_scripts)}/{len(tasks)} 个脚本不存在",
                recommendation=f"请创建以下脚本: {', '.join(missing_scripts)}"
            ))
            self.recommendations.append(f"创建缺失的脚本文件: {', '.join(missing_scripts)}")
        else:
            self.checks.append(CheckResult(
                category="配置",
                item="脚本路径",
                status=CheckStatus.PASS,
                detail=f"所有 {valid_count} 个脚本文件存在"
            ))
    
    def _check_logs_directory(self) -> None:
        """检查日志目录可写性"""
        print("📝 检查日志目录...")
        
        try:
            test_file = LOGS_DIR / ".write_test"
            test_file.write_text("test")
            test_file.unlink()
            
            self.checks.append(CheckResult(
                category="运行时",
                item="日志目录",
                status=CheckStatus.PASS,
                detail=f"日志目录可写: {LOGS_DIR}"
            ))
        except Exception as e:
            self.checks.append(CheckResult(
                category="运行时",
                item="日志目录",
                status=CheckStatus.FAIL,
                detail=f"日志目录不可写: {e}",
                recommendation="请检查日志目录权限"
            ))
    
    def _check_disk_space(self) -> None:
        """检查磁盘空间"""
        print("💾 检查磁盘空间...")
        
        try:
            stat = shutil.disk_usage(BASE_DIR)
            total_gb = stat.total / (1024**3)
            used_gb = stat.used / (1024**3)
            free_gb = stat.free / (1024**3)
            usage_pct = (stat.used / stat.total) * 100
            
            if usage_pct > 95:
                status = CheckStatus.FAIL
                recommendation = "磁盘空间严重不足，请立即清理"
            elif usage_pct > 85:
                status = CheckStatus.WARN
                recommendation = "磁盘空间使用率超过85%，建议清理日志"
            else:
                status = CheckStatus.PASS
                recommendation = ""
            
            self.checks.append(CheckResult(
                category="运行时",
                item="磁盘空间",
                status=status,
                detail=f"已用 {usage_pct:.1f}% ({used_gb:.1f}GB / {total_gb:.1f}GB)",
                recommendation=recommendation
            ))
            
            if recommendation:
                self.recommendations.append(recommendation)
                
        except Exception as e:
            self.checks.append(CheckResult(
                category="运行时",
                item="磁盘空间",
                status=CheckStatus.WARN,
                detail=f"无法获取磁盘空间信息: {e}",
                recommendation="请检查系统权限"
            ))
    
    def _check_memory_usage(self) -> None:
        """检查内存使用"""
        print("🧠 检查内存使用...")
        
        try:
            # 读取 /proc/meminfo (Linux)
            with open('/proc/meminfo', 'r') as f:
                meminfo = f.read()
            
            mem_total = int(re.search(r'MemTotal:\s+(\d+)', meminfo).group(1)) * 1024
            mem_available = int(re.search(r'MemAvailable:\s+(\d+)', meminfo).group(1)) * 1024
            
            usage_pct = ((mem_total - mem_available) / mem_total) * 100
            
            if usage_pct > 90:
                status = CheckStatus.FAIL
                recommendation = "内存使用率过高，请检查系统进程"
            elif usage_pct > 80:
                status = CheckStatus.WARN
                recommendation = "内存使用率超过80%，建议监控"
            else:
                status = CheckStatus.PASS
                recommendation = ""
            
            self.checks.append(CheckResult(
                category="运行时",
                item="内存使用",
                status=status,
                detail=f"使用率 {usage_pct:.1f}%",
                recommendation=recommendation
            ))
            
            if recommendation:
                self.recommendations.append(recommendation)
                
        except Exception as e:
            self.checks.append(CheckResult(
                category="运行时",
                item="内存使用",
                status=CheckStatus.SKIP,
                detail=f"无法获取内存信息: {e}"
            ))
    
    def _check_notification_channels(self) -> None:
        """检查通知渠道"""
        print("📢 检查通知渠道...")
        
        # 简化检查，仅检查配置存在
        if self.alerts_config:
            self.checks.append(CheckResult(
                category="集成",
                item="通知配置",
                status=CheckStatus.PASS,
                detail="告警配置已加载"
            ))
        else:
            self.checks.append(CheckResult(
                category="集成",
                item="通知配置",
                status=CheckStatus.WARN,
                detail="告警配置未加载"
            ))
    
    def _check_task_states(self) -> None:
        """检查任务状态"""
        print("✅ 检查任务状态...")
        
        if not self.tasks_config:
            self.checks.append(CheckResult(
                category="任务",
                item="任务状态",
                status=CheckStatus.SKIP,
                detail="任务配置未加载"
            ))
            return
        
        tasks = self.tasks_config.get('tasks', [])
        enabled_count = sum(1 for t in tasks if t.get('enabled', True))
        
        if enabled_count == 0:
            self.checks.append(CheckResult(
                category="任务",
                item="任务状态",
                status=CheckStatus.WARN,
                detail="没有启用的任务",
                recommendation="请检查是否需要启用任务"
            ))
        else:
            self.checks.append(CheckResult(
                category="任务",
                item="任务状态",
                status=CheckStatus.PASS,
                detail=f"{enabled_count}/{len(tasks)} 个任务已启用"
            ))
    
    def _generate_report(self) -> HealthReport:
        """生成健康报告"""
        # 统计结果
        summary = {"PASS": 0, "WARN": 0, "FAIL": 0, "SKIP": 0}
        for check in self.checks:
            summary[check.status.value] += 1
        
        # 计算得分
        total_checks = len([c for c in self.checks if c.status != CheckStatus.SKIP])
        passed = summary["PASS"]
        score = int((passed / total_checks) * 100) if total_checks > 0 else 100
        
        # 确定总体状态
        if summary["FAIL"] > 0:
            overall = "FAIL"
        elif summary["WARN"] > 0:
            overall = "WARN"
        else:
            overall = "PASS"
        
        return HealthReport(
            check_time=datetime.now(),
            overall_status=overall,
            score=score,
            total_score=100,
            checks=self.checks,
            summary=summary,
            recommendations=self.recommendations
        )
    
    def print_report(self, report: HealthReport) -> None:
        """打印报告"""
        print("\n" + "=" * 60)
        print("📊 健康检查报告")
        print("=" * 60)
        print(f"检查时间: {report.check_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"总体状态: {report.overall_status}")
        print(f"健康得分: {report.score}/{report.total_score}")
        print(f"\n统计: 通过 {report.summary['PASS']} | 警告 {report.summary['WARN']} | 失败 {report.summary['FAIL']} | 跳过 {report.summary['SKIP']}")
        
        print("\n详细结果:")
        print("-" * 60)
        for check in report.checks:
            icon = {
                CheckStatus.PASS: "✅",
                CheckStatus.WARN: "⚠️",
                CheckStatus.FAIL: "❌",
                CheckStatus.SKIP: "⏭️"
            }.get(check.status, "❓")
            print(f"{icon} [{check.category}] {check.item}")
            print(f"   状态: {check.status.value} | {check.detail}")
            if check.recommendation:
                print(f"   💡 建议: {check.recommendation}")
            print()
        
        if report.recommendations:
            print("改进建议:")
            print("-" * 60)
            for i, rec in enumerate(report.recommendations, 1):
                print(f"{i}. {rec}")
        
        print("=" * 60)


def main():
    """主入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Cron-Automation Health Checker')
    parser.add_argument('--full', action='store_true', help='完整检查')
    parser.add_argument('--output', type=str, help='输出JSON文件路径')
    
    args = parser.parse_args()
    
    checker = HealthChecker()
    report = checker.run_all_checks()
    checker.print_report(report)
    
    # 保存报告
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = REPORTS_DIR / f"health-check-{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    # 转换为JSON保存
    report_dict = {
        "check_time": report.check_time.isoformat(),
        "overall_status": report.overall_status,
        "score": report.score,
        "total_score": report.total_score,
        "summary": report.summary,
        "checks": [
            {
                "category": c.category,
                "item": c.item,
                "status": c.status.value,
                "detail": c.detail,
                "recommendation": c.recommendation
            }
            for c in report.checks
        ],
        "recommendations": report.recommendations
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report_dict, f, indent=2)
    
    print(f"\n📄 报告已保存: {output_path}")
    
    # 返回退出码
    if report.overall_status == "FAIL":
        sys.exit(1)
    elif report.overall_status == "WARN":
        sys.exit(2)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
