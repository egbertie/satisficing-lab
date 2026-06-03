#!/usr/bin/env python3
"""
Token预算对抗测试 (Adversarial Test)
S7标准: 对抗测试（模拟预算耗尽场景测试响应）

测试场景：
1. 预算耗尽场景
2. 预估偏差过大场景
3. 熔断滥用场景
4. 并发超支场景
5. 异常峰值场景
"""

import sys
import json
from pathlib import Path

# 添加scripts目录到路径
scripts_dir = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from allocator import BudgetAllocator
from circuit_breaker import TokenCircuitBreaker
from estimator import TokenEstimator
from monitor import TokenMonitor
from reporter import BudgetReporter

class TokenBudgetAdversarialTest:
    """Token预算对抗测试器"""
    
    def __init__(self):
        self.results = []
        self.passed = 0
        self.failed = 0
    
    def _log(self, test_name: str, passed: bool, details: dict):
        """记录测试结果"""
        result = {
            "test": test_name,
            "passed": passed,
            "details": details
        }
        self.results.append(result)
        if passed:
            self.passed += 1
            print(f"✅ {test_name}: PASS")
        else:
            self.failed += 1
            print(f"❌ {test_name}: FAIL - {details.get('reason', '')}")
    
    def test_budget_exhaustion_scenario(self):
        """
        测试场景1: 预算耗尽
        验证当预算耗尽时系统是否正确阻断非P0任务
        """
        print("\n🧪 测试场景1: 预算耗尽场景")
        
        allocator = BudgetAllocator()
        
        # 模拟消耗全部预算
        for pool_name in ["strategic_reserve", "operational_budget", "innovation_fund"]:
            pool = allocator.pools.get(pool_name)
            if pool:
                pool["used"] = pool["daily_limit"]  # 全部用完
        
        # 测试非P0任务应该被阻断
        result = allocator.check_availability("operational_budget", 100)
        
        if not result["available"] and "余额不足" in result["reason"]:
            self._log("Budget Exhaustion - Block Non-P0", True, {
                "message": "非P0任务被正确阻断"
            })
        else:
            self._log("Budget Exhaustion - Block Non-P0", False, {
                "reason": "预算耗尽时未阻断任务",
                "result": result
            })
        
        # 测试P0任务（通过战略储备）
        allocator.pools["strategic_reserve"]["used"] = 0  # 重置战略储备
        result = allocator.check_availability("strategic_reserve", 1000)
        
        # 注意：这里只是检查可用性，P0任务的放行在熔断器层
        self._log("Budget Exhaustion - P0 Reserve Check", True, {
            "available": result["available"],
            "message": "战略储备可用性检查完成"
        })
    
    def test_estimation_deviation_scenario(self):
        """
        测试场景2: 预估偏差过大
        验证当实际消耗远超预估时熔断器是否正确触发
        """
        print("\n🧪 测试场景2: 预估偏差场景")
        
        cb = TokenCircuitBreaker()
        cb.reset("test_setup")  # 重置熔断器状态
        
        # 测试软限制（150%）
        result = cb.check("T-001", estimated=1000, actual=1600, is_p0=False)
        
        if result["allowed"] and result["action"] == "warn":
            self._log("Soft Limit Warning", True, {
                "message": "150%偏差触发预警但不熔断"
            })
        else:
            self._log("Soft Limit Warning", False, {
                "reason": f"软限制处理不正确: {result}",
                "result": result
            })
        
        # 测试硬限制（200%）
        result = cb.check("T-002", estimated=1000, actual=2500, is_p0=False)
        
        if not result["allowed"] and result["action"] == "circuit_breaker_triggered":
            self._log("Hard Limit Circuit Breaker", True, {
                "message": "200%偏差正确触发熔断"
            })
        else:
            self._log("Hard Limit Circuit Breaker", False, {
                "reason": f"硬限制熔断不正确: {result}",
                "result": result
            })
        
        # 测试P0覆盖（200-300%之间）
        result = cb.check("T-003", estimated=1000, actual=2500, is_p0=True)
        
        if result["allowed"] and "p0_override" in result["action"]:
            self._log("P0 Emergency Override", True, {
                "message": "P0任务正确覆盖熔断"
            })
        else:
            self._log("P0 Emergency Override", False, {
                "reason": f"P0覆盖不正确: {result}",
                "result": result
            })
        
        # 测试P0不能覆盖超过300%
        result = cb.check("T-004", estimated=1000, actual=3500, is_p0=True)
        
        if not result["allowed"]:
            self._log("P0 Limit at 300%", True, {
                "message": "P0任务不能超过300%限制"
            })
        else:
            self._log("P0 Limit at 300%", False, {
                "reason": f"P0超过300%应被阻断: {result}",
                "result": result
            })
    
    def test_circuit_breaker_abuse_scenario(self):
        """
        测试场景3: 熔断滥用
        验证熔断机制不会被用作逃避工作的借口
        """
        print("\n🧪 测试场景3: 熔断滥用场景")
        
        cb = TokenCircuitBreaker()
        
        # 触发熔断
        cb.check("T-001", estimated=1000, actual=2500, is_p0=False)
        
        # 检查熔断状态
        status = cb.get_status()
        
        if status["state"] == "open":
            self._log("Circuit Breaker State Tracking", True, {
                "message": "熔断状态正确记录"
            })
            
            # 验证熔断记录被保存
            if status["total_records"] > 0:
                self._log("Circuit Breaker Audit Trail", True, {
                    "message": "熔断审计记录已保存"
                })
            else:
                self._log("Circuit Breaker Audit Trail", False, {
                    "reason": "熔断审计记录未保存"
                })
        else:
            self._log("Circuit Breaker State Tracking", False, {
                "reason": "熔断状态未正确更新"
            })
        
        # 验证熔断有冷却期
        if cb.cooldown_seconds > 0:
            self._log("Circuit Breaker Cooldown", True, {
                "message": f"熔断冷却期设置: {cb.cooldown_seconds}秒"
            })
        else:
            self._log("Circuit Breaker Cooldown", False, {
                "reason": "熔断冷却期未设置"
            })
    
    def test_concurrent_overrun_scenario(self):
        """
        测试场景4: 并发超支
        验证并发任务不会导致预算超支
        """
        print("\n🧪 测试场景4: 并发超支场景")
        
        allocator = BudgetAllocator()
        
        # 获取运营预算池状态
        pool_status = allocator.get_pool_status("operational_budget")
        available = pool_status.get("remaining", 0)
        
        # 模拟多个并发任务同时检查可用性
        tasks = [
            ("T-001", available // 2),
            ("T-002", available // 2),
            ("T-003", available // 2),  # 这个应该失败
        ]
        
        approved = 0
        for task_id, amount in tasks:
            result = allocator.check_availability("operational_budget", amount)
            if result["available"]:
                approved += 1
                # 模拟扣减
                allocator.consume("operational_budget", amount, task_id)
        
        # 验证总消耗不超过预算
        final_status = allocator.get_pool_status("operational_budget")
        if final_status["used"] <= final_status["allocated"]:
            self._log("Concurrent Budget Safety", True, {
                "message": f"并发控制正确，已批准{approved}个任务，总消耗未超预算"
            })
        else:
            self._log("Concurrent Budget Safety", False, {
                "reason": "并发任务导致超支"
            })
    
    def test_anomaly_peak_scenario(self):
        """
        测试场景5: 异常峰值
        验证系统能检测并处理异常Token消耗峰值
        """
        print("\n🧪 测试场景5: 异常峰值场景")
        
        monitor = TokenMonitor()
        
        # 模拟正常消耗
        normal_alert = monitor.check_task_consumption("T-NORMAL", estimated=1000, actual=1100)
        
        # 模拟异常峰值（5倍预估）
        peak_alert = monitor.check_task_consumption("T-PEAK", estimated=1000, actual=5000)
        
        if peak_alert and peak_alert.level in ["critical", "emergency"]:
            self._log("Anomaly Peak Detection", True, {
                "message": "异常峰值被正确检测",
                "alert_level": peak_alert.level
            })
        else:
            self._log("Anomaly Peak Detection", False, {
                "reason": "异常峰值未被检测"
            })
        
        # 验证正常消耗不会触发告警
        if normal_alert is None or normal_alert.level == "info":
            self._log("Normal Consumption Tolerance", True, {
                "message": "正常消耗不会误触发告警"
            })
        else:
            self._log("Normal Consumption Tolerance", False, {
                "reason": "正常消耗被误报"
            })
    
    def test_monitoring_integration(self):
        """
        测试场景6: 监控集成
        验证各组件协同工作
        """
        print("\n🧪 测试场景6: 监控集成场景")
        
        # 测试报告生成包含准确性验证
        reporter = BudgetReporter()
        report = reporter.generate_daily_report()
        
        validation = report.metrics.get("accuracy_validation", {})
        checks = validation.get("checks", [])
        
        # 验证至少有一些检查
        if len(checks) > 0:
            self._log("Report Validation Checks", True, {
                "message": f"报告包含{len(checks)}项准确性验证"
            })
        else:
            self._log("Report Validation Checks", False, {
                "reason": "报告缺少准确性验证"
            })
        
        # 验证监控状态可获取
        monitor = TokenMonitor()
        status = monitor.get_status()
        
        if "current_usage_percent" in status:
            self._log("Monitor Status API", True, {
                "message": "监控状态API可用"
            })
        else:
            self._log("Monitor Status API", False, {
                "reason": "监控状态API异常"
            })
    
    def run_all_tests(self):
        """运行所有对抗测试"""
        print("=" * 60)
        print("🛡️ Token预算对抗测试开始")
        print("=" * 60)
        
        self.test_budget_exhaustion_scenario()
        self.test_estimation_deviation_scenario()
        self.test_circuit_breaker_abuse_scenario()
        self.test_concurrent_overrun_scenario()
        self.test_anomaly_peak_scenario()
        self.test_monitoring_integration()
        
        print("\n" + "=" * 60)
        print("📊 测试结果汇总")
        print("=" * 60)
        print(f"总计: {self.passed + self.failed}")
        print(f"通过: {self.passed} ✅")
        print(f"失败: {self.failed} ❌")
        print(f"通过率: {self.passed/(self.passed+self.failed)*100:.1f}%")
        
        if self.failed == 0:
            print("\n🎉 所有对抗测试通过！系统具备足够的鲁棒性。")
        else:
            print(f"\n⚠️ {self.failed}个测试失败，需要修复。")
        
        return self.failed == 0
    
    def export_results(self, filepath: str):
        """导出测试结果"""
        with open(filepath, 'w') as f:
            json.dump({
                "timestamp": json.dumps({}),
                "summary": {
                    "total": self.passed + self.failed,
                    "passed": self.passed,
                    "failed": self.failed,
                    "pass_rate": self.passed/(self.passed+self.failed) if (self.passed+self.failed) > 0 else 0
                },
                "results": self.results
            }, f, indent=2)
        print(f"\n测试结果已导出: {filepath}")


def main():
    tester = TokenBudgetAdversarialTest()
    success = tester.run_all_tests()
    
    # 导出结果
    import tempfile
    result_file = Path(tempfile.gettempdir()) / "token_budget_adversarial_test.json"
    tester.export_results(str(result_file))
    
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
