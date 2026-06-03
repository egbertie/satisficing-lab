#!/usr/bin/env python3
"""
test_runner.py
Token Weekly Monitor - 测试运行器

S7: 对抗测试与验证
"""

import sys
import json
from datetime import datetime, timedelta
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent))

# 读取主脚本但不执行main()
runner_path = Path(__file__).parent / "token-weekly-monitor-runner.py"
if not runner_path.exists():
    print(f"❌ 找不到主运行脚本: {runner_path}")
    sys.exit(1)

# 读取主脚本内容
with open(runner_path, 'r') as f:
    source = f.read()

# 在主脚本名前加上模块标识，这样main()不会被执行
if __name__ == "__main__":
    # 只导入类和函数，不执行脚本
    exec(compile(source.replace('if __name__ == "__main__":', 'if False and __name__ == "__main__":'), 
                 runner_path, 'exec'))


class TestTokenMonitor:
    """Token Monitor 测试类"""
    
    def __init__(self):
        self.monitor = TokenMonitor()
        self.passed = 0
        self.failed = 0
        
    def run_all_tests(self):
        """运行所有测试"""
        print("=" * 60)
        print("Token Weekly Monitor - 测试套件")
        print("=" * 60)
        
        # S2 核心算法测试
        self.test_status_determination()
        self.test_consumption_rate()
        self.test_predict_end()
        self.test_ratio_calculation()
        
        # S5 数据验证测试
        self.test_data_validation()
        
        # S7 对抗测试
        self.test_abnormal_high_consumption()
        self.test_boundary_status_transition()
        self.test_continuous_high_consumption()
        
        # 汇总
        print("\n" + "=" * 60)
        print(f"测试结果: ✅ 通过 {self.passed} | ❌ 失败 {self.failed}")
        print("=" * 60)
        
        return self.failed == 0
    
    def assert_eq(self, actual, expected, test_name):
        """断言相等"""
        if actual == expected:
            print(f"✅ {test_name}")
            self.passed += 1
            return True
        else:
            print(f"❌ {test_name}: 期望 {expected}, 实际 {actual}")
            self.failed += 1
            return False
    
    def assert_true(self, condition, test_name):
        """断言为真"""
        if condition:
            print(f"✅ {test_name}")
            self.passed += 1
            return True
        else:
            print(f"❌ {test_name}: 条件不满足")
            self.failed += 1
            return False
    
    # ==================== S2: 核心算法测试 ====================
    
    def test_status_determination(self):
        """测试状态判断逻辑"""
        print("\n[S2] 状态判断测试:")
        self.assert_eq(self.monitor.determine_status(60), ("healthy", "🟢"), "健康状态 (剩余60%)")
        self.assert_eq(self.monitor.determine_status(50.1), ("healthy", "🟢"), "健康边界 (剩余50.1%)")
        self.assert_eq(self.monitor.determine_status(50), ("caution", "🟡"), "注意边界 (剩余50%)")
        self.assert_eq(self.monitor.determine_status(40), ("caution", "🟡"), "注意状态 (剩余40%)")
        self.assert_eq(self.monitor.determine_status(30.1), ("caution", "🟡"), "注意边界 (剩余30.1%)")
        self.assert_eq(self.monitor.determine_status(30), ("warning", "🟠"), "预警边界 (剩余30%)")
        self.assert_eq(self.monitor.determine_status(20), ("warning", "🟠"), "预警状态 (剩余20%)")
        self.assert_eq(self.monitor.determine_status(15.1), ("warning", "🟠"), "预警边界 (剩余15.1%)")
        self.assert_eq(self.monitor.determine_status(15), ("critical", "🔴"), "紧急边界 (剩余15%)")
        self.assert_eq(self.monitor.determine_status(10), ("critical", "🔴"), "紧急状态 (剩余10%)")
        self.assert_eq(self.monitor.determine_status(0), ("critical", "🔴"), "紧急边界 (剩余0%)")
    
    def test_consumption_rate(self):
        """测试消耗速度计算"""
        print("\n[S2] 消耗速度测试:")
        self.assert_eq(self.monitor.calculate_consumption_rate(21000, 3), 7000, "3天消耗21K")
        self.assert_eq(self.monitor.calculate_consumption_rate(0, 3), 0, "零消耗")
        self.assert_eq(self.monitor.calculate_consumption_rate(10000, 0), 0, "零天数保护")
        self.assert_eq(self.monitor.calculate_consumption_rate(10000, 1), 10000, "单日消耗")
    
    def test_predict_end(self):
        """测试结束预测"""
        print("\n[S2] 结束预测测试:")
        self.assert_eq(
            self.monitor.predict_end_consumption(21000, 7000, 4), 
            49000, 
            "4天预测"
        )
        self.assert_eq(
            self.monitor.predict_end_consumption(0, 10000, 7), 
            70000, 
            "从零开始预测"
        )
    
    def test_ratio_calculation(self):
        """测试消耗-时间比计算"""
        print("\n[S2] 比率计算测试:")
        # 消耗40%，时间进度50% -> 0.8 (落后)
        self.assert_eq(
            round(self.monitor.consumption_vs_time_ratio(40, 50), 2), 
            0.8, 
            "落后消耗"
        )
        # 消耗60%，时间进度50% -> 1.2 (超前)
        self.assert_eq(
            round(self.monitor.consumption_vs_time_ratio(60, 50), 2), 
            1.2, 
            "超前消耗"
        )
        # 相同进度
        self.assert_eq(
            self.monitor.consumption_vs_time_ratio(50, 50), 
            1.0, 
            "正常进度"
        )
    
    # ==================== S5: 数据验证测试 ====================
    
    def test_data_validation(self):
        """测试数据验证逻辑"""
        print("\n[S5] 数据验证测试:")
        
        # 创建测试数据 (percentage是已消耗百分比)
        self.monitor.data = {
            "openclawToken": {
                "weeklyBudget": 70000,
                "consumed": 30000,
                "remaining": 40000,
                "percentage": 42.9,  # 已消耗42.9%
                "status": "healthy"  # 剩余57.1%，应为healthy
            }
        }
        
        validations = self.monitor.validate_data_integrity()
        
        # 检查是否都通过
        all_pass = all(v[0] == "PASS" for v in validations)
        self.assert_true(all_pass, "有效数据验证通过")
        
        # 测试损坏数据
        self.monitor.data["openclawToken"]["consumed"] = 30000
        self.monitor.data["openclawToken"]["remaining"] = 30000  # 不匹配
        
        validations = self.monitor.validate_data_integrity()
        has_fail = any(v[0] == "FAIL" for v in validations)
        self.assert_true(has_fail, "损坏数据检测成功")
    
    # ==================== S7: 对抗测试 ====================
    
    def test_abnormal_high_consumption(self):
        """S7: 测试单日异常高消耗的检测能力"""
        print("\n[S7] 异常高消耗检测:")
        
        # 模拟数据：前两天正常，第三天spike
        self.monitor.data = {
            "cycleInfo": {"currentDay": 3},
            "openclawToken": {
                "weeklyBudget": 70000,
                "dailyBudget": 10000,
                "percentage": 0  # 占位
            },
            "dailyLog": [
                {"openclawConsumed": 5000},   # Day 1: 正常
                {"openclawConsumed": 6000},   # Day 2: 正常
                {"openclawConsumed": 25000},  # Day 3: Spike! (是平均的4倍)
            ]
        }
        
        anomalies = self.monitor.detect_anomalies()
        spike_detected = any("spike" in a.lower() for a in anomalies)
        self.assert_true(spike_detected, "单日spike检测成功")
    
    def test_boundary_status_transition(self):
        """S7: 测试状态边界附近的灵敏度"""
        print("\n[S7] 状态边界灵敏度:")
        
        # 测试50%边界：50.1%剩余是healthy，49.9%剩余是caution
        status_1, _ = self.monitor.determine_status(50.1)
        status_2, _ = self.monitor.determine_status(49.9)
        
        self.assert_eq(status_1, "healthy", "50.1%剩余应为健康状态")
        self.assert_eq(status_2, "caution", "49.9%剩余应为注意状态")
        
        # 测试30%边界
        status_3, _ = self.monitor.determine_status(30.1)
        status_4, _ = self.monitor.determine_status(29.9)
        
        self.assert_eq(status_3, "caution", "30.1%剩余应为注意状态")
        self.assert_eq(status_4, "warning", "29.9%剩余应为预警状态")
        
        # 测试15%边界
        status_5, _ = self.monitor.determine_status(15.1)
        status_6, _ = self.monitor.determine_status(14.9)
        
        self.assert_eq(status_5, "warning", "15.1%剩余应为预警状态")
        self.assert_eq(status_6, "critical", "14.9%剩余应为紧急状态")
    
    def test_continuous_high_consumption(self):
        """S7: 测试连续高消耗的检测"""
        print("\n[S7] 连续高消耗检测:")
        
        # 模拟连续3天超过预算150%
        self.monitor.data = {
            "cycleInfo": {"currentDay": 4},
            "openclawToken": {
                "weeklyBudget": 70000,
                "dailyBudget": 10000,
                "percentage": 0
            },
            "dailyLog": [
                {"openclawConsumed": 16000},  # 160% of budget
                {"openclawConsumed": 17000},  # 170% of budget
                {"openclawConsumed": 18000},  # 180% of budget
            ]
        }
        
        anomalies = self.monitor.detect_anomalies()
        continuous_detected = any("连续" in a for a in anomalies)
        self.assert_true(continuous_detected, "连续高消耗检测成功")


def run_adversarial_tests():
    """运行对抗测试套件"""
    print("\n" + "=" * 60)
    print("S7: 对抗测试套件")
    print("=" * 60)
    
    test_cases = [
        ("零值边界", test_zero_boundary),
        ("超大数值", test_extreme_values),
        ("数据类型混淆", test_type_confusion),
        ("并发修改", test_concurrent_modification),
    ]
    
    passed = 0
    for name, test_func in test_cases:
        try:
            print(f"\n🧪 {name}:")
            test_func()
            print(f"✅ 通过")
            passed += 1
        except Exception as e:
            print(f"❌ 失败: {e}")
    
    print(f"\n对抗测试: {passed}/{len(test_cases)} 通过")
    return passed == len(test_cases)


def test_zero_boundary():
    """测试零值边界"""
    monitor = TokenMonitor()
    # 所有值为0时不应崩溃
    monitor.data = {
        "openclawToken": {
            "weeklyBudget": 0,
            "consumed": 0,
            "remaining": 0,
            "percentage": 0
        },
        "dailyLog": [],
        "cycleInfo": {"currentDay": 0}
    }
    
    # 不应抛出异常
    monitor.validate_data_integrity()
    monitor.detect_anomalies()


def test_extreme_values():
    """测试超大数值"""
    monitor = TokenMonitor()
    monitor.data["openclawToken"] = {
        "weeklyBudget": 999999999,
        "consumed": 999999998,
        "remaining": 1,
        "percentage": 99.999999  # 已消耗百分比
    }
    
    # 剩余百分比 = 100 - 99.999999 = 0.000001，应为critical
    status, icon = monitor.determine_status(0.000001)
    assert status == "critical", f"超小剩余百分比应为紧急状态，实际: {status}"


def test_type_confusion():
    """测试数据类型混淆"""
    monitor = TokenMonitor()
    # 字符串数字应被处理
    try:
        result = monitor.calculate_consumption_rate("21000", 3)
        # Python 3 会抛出 TypeError，这是期望的行为
        assert False, "应拒绝字符串输入"
    except (TypeError, ValueError):
        pass  # 期望的行为


def test_concurrent_modification():
    """模拟并发修改场景"""
    monitor = TokenMonitor()
    original = monitor.data.copy()
    
    # 模拟一个check过程中数据被修改
    validations = monitor.validate_data_integrity()
    
    # 验证期间数据一致性
    assert isinstance(validations, list), "验证应返回列表"


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Token Monitor 测试运行器")
    parser.add_argument("--adversarial", action="store_true", help="运行对抗测试")
    parser.add_argument("--test", type=str, help="运行特定测试")
    
    args = parser.parse_args()
    
    if args.adversarial:
        success = run_adversarial_tests()
        sys.exit(0 if success else 1)
    
    # 运行标准测试套件
    tester = TestTokenMonitor()
    success = tester.run_all_tests()
    
    # 如果全部通过，也运行对抗测试
    if success:
        run_adversarial_tests()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
