#!/usr/bin/env python3
"""
Token Budget Enforcer - 主运行脚本
整合所有模块的统一入口
"""

import sys
import json
import os
from pathlib import Path

# 添加scripts目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from allocator import BudgetAllocator
from circuit_breaker import TokenCircuitBreaker
from estimator import TokenEstimator
from monitor import TokenMonitor
from reporter import BudgetReporter

class TokenBudgetEnforcer:
    """Token预算强制执行器主类"""
    
    def __init__(self):
        self.allocator = BudgetAllocator()
        self.circuit_breaker = TokenCircuitBreaker()
        self.estimator = TokenEstimator()
        self.monitor = TokenMonitor()
        self.reporter = BudgetReporter()
    
    def show_budget(self):
        """显示预算看板"""
        status = self.allocator.get_total_status()
        
        print("=" * 60)
        print("[Token预算看板]")
        print("=" * 60)
        print(f"日期: {status['date']}")
        print(f"总预算: {status['total_budget']:,} tokens")
        print(f"已使用: {status['total_used']:,} tokens ({status['usage_percent']:.1f}%)")
        print(f"剩余: {status['total_remaining']:,} tokens")
        print()
        
        print("预算分配:")
        for pool_name, pool in status['pools'].items():
            status_emoji = {
                "normal": "🟢",
                "warning": "🟡",
                "critical": "🔴",
                "exhausted": "⛔"
            }
            emoji = status_emoji.get(pool['status'], "⚪")
            print(f"  {emoji} {pool_name}:")
            print(f"     分配: {pool['allocated']:,} | 已用: {pool['used']:,} | 剩余: {pool['remaining']:,}")
            print(f"     使用率: {pool['usage_percent']:.1f}%")
        
        print()
        
        # 预警状态
        usage = status['usage_percent']
        if usage < 70:
            alert_status = "🟢 正常"
        elif usage < 90:
            alert_status = "🟡 注意"
        elif usage < 100:
            alert_status = "🔴 紧急"
        else:
            alert_status = "⛔ 已耗尽 - 非P0任务暂停"
        
        print(f"预警状态: {alert_status}")
        
        # 效率指标
        print()
        print("效率指标:")
        print(f"  任务数: 待统计")
        print(f"  预估准确率: 参考forecasts.json")
        
        print("=" * 60)
        print()
        print("[硬约束规则]")
        print("1. 每次回复前显示预估消耗")
        print("2. 任务>500 tokens先给极简摘要")
        print("3. 单日预算耗尽→完全暂停")
        print("4. 每个输出必须有明确效用")
        
        return 0
    
    def estimate_task(self, task_desc):
        """预估任务Token消耗"""
        result = self.estimator.estimate(task_desc)
        
        print(f"任务: {task_desc}")
        print(f"预估消耗: {result.tokens} tokens")
        print(f"置信区间: [{result.range_low}, {result.range_high}]")
        print(f"置信度: {result.confidence:.0%} ({result.confidence_level})")
        print(f"建议: {'分阶段执行' if result.tokens > 1000 else '可单次完成'}")
        
        return 0
    
    def generate_report(self, period="daily"):
        """生成报告"""
        if period == "daily":
            report = self.reporter.generate_daily_report()
            print(self.reporter.format_report_text(report))
            
            # 保存报告
            saved_path = self.reporter.save_report(report)
            print(f"\n报告已保存: {saved_path}")
        else:
            print(f"不支持的报告周期: {period}")
            return 1
        
        return 0
    
    def monitor_status(self):
        """显示监控状态"""
        status = self.monitor.get_status()
        print(json.dumps(status, indent=2))
        return 0
    
    def check_task(self, pool_name, amount):
        """检查任务预算"""
        result = self.allocator.check_availability(pool_name, amount)
        print(json.dumps(result, indent=2))
        return 0
    
    def circuit_status(self):
        """显示熔断器状态"""
        status = self.circuit_breaker.get_status()
        print(json.dumps(status, indent=2))
        return 0
    
    def run_adversarial_test(self):
        """运行对抗测试 (S7)"""
        import sys
        skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sys.path.insert(0, skill_dir)
        from tests.adversarial_test import TokenBudgetAdversarialTest
        tester = TokenBudgetAdversarialTest()
        success = tester.run_all_tests()
        return 0 if success else 1


def print_usage():
    """打印使用说明"""
    print("""
Token Budget Enforcer - 预算强制执行器

Usage: enforcer_runner.py [command] [options]

Commands:
  budget                    显示预算看板
  estimate [task]           预估任务消耗
  report [daily|weekly]     生成报告
  monitor status            显示监控状态
  check [pool] [amount]     检查预算池可用性
  circuit status            显示熔断器状态
  test                      运行对抗测试
  
Examples:
  python3 enforcer_runner.py budget
  python3 enforcer_runner.py estimate "撰写技术报告"
  python3 enforcer_runner.py report daily
  python3 enforcer_runner.py check operational_budget 1000
    """)


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print_usage()
        return 1
    
    enforcer = TokenBudgetEnforcer()
    command = sys.argv[1]
    
    try:
        if command == "budget":
            return enforcer.show_budget()
        
        elif command == "estimate":
            task = sys.argv[2] if len(sys.argv) > 2 else "通用任务"
            return enforcer.estimate_task(task)
        
        elif command == "report":
            period = sys.argv[2] if len(sys.argv) > 2 else "daily"
            return enforcer.generate_report(period)
        
        elif command == "monitor":
            subcmd = sys.argv[2] if len(sys.argv) > 2 else "status"
            if subcmd == "status":
                return enforcer.monitor_status()
            else:
                print(f"Unknown monitor command: {subcmd}")
                return 1
        
        elif command == "check":
            if len(sys.argv) < 4:
                print("Usage: check [pool_name] [amount]")
                return 1
            pool = sys.argv[2]
            amount = int(sys.argv[3])
            return enforcer.check_task(pool, amount)
        
        elif command == "circuit":
            subcmd = sys.argv[2] if len(sys.argv) > 2 else "status"
            if subcmd == "status":
                return enforcer.circuit_status()
            else:
                print(f"Unknown circuit command: {subcmd}")
                return 1
        
        elif command == "test":
            return enforcer.run_adversarial_test()
        
        else:
            print(f"Unknown command: {command}")
            print_usage()
            return 1
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
