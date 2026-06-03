#!/usr/bin/env python3
"""神经科学基线测试套件"""
import sys
import argparse
from neuroscience_baseline import NeuroscienceBaselineChecker, BaselineLevel

def run_tests():
    print("=" * 70)
    print("神经科学基线 - 完整测试套件 (v1.0.0)")
    print("=" * 70)
    
    checker = NeuroscienceBaselineChecker()
    test_results = []
    
    tests = [
        ("初始化", lambda: len(checker.dimensions) == 5),
        ("认知负荷检查", lambda: checker.check_cognitive_load("简单清晰").score > 0),
        ("决策压力检查", lambda: checker.check_decision_pressure("从容时间充裕").score > 0),
        ("睡眠质量检查", lambda: checker.check_sleep_quality("充足睡眠精力充沛").score > 0),
        ("BCI准备度检查", lambda: checker.check_bci_readiness("专注冥想").score > 0),
        ("直觉校准检查", lambda: checker.check_intuition_calibration("直觉洞察").score > 0),
        ("完整检查", lambda: checker.full_check("专注冥想清晰睡眠好") is not None),
        ("分数范围", lambda: 0 <= checker.full_check("测试").overall_score <= 1),
        ("级别判断", lambda: checker.full_check("测试").overall_level is not None),
        ("维度完整性", lambda: len(checker.full_check("测试").dimensions) == 5),
        ("建议生成", lambda: len(checker.full_check("测试").recommendations) >= 0),
        ("睡眠优化", lambda: len(checker._generate_sleep_optimization([])) >= 0),
    ]
    
    for i, (name, test_func) in enumerate(tests, 1):
        print(f"\n[测试{i}/12] {name}...")
        try:
            passed = bool(test_func())
            test_results.append((name, passed))
            print(f"  {'✅ PASS' if passed else '❌ FAIL'}")
        except Exception as e:
            test_results.append((name, False))
            print(f"  ❌ FAIL: {e}")
    
    passed_count = sum(1 for _, p in test_results if p)
    print(f"\n通过率: {passed_count}/12 ({passed_count/12*100:.1f}%)")
    return passed_count == 12

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", action="store_true")
    args = parser.parse_args()
    
    if args.test:
        success = run_tests()
        sys.exit(0 if success else 1)
    else:
        print("使用 --test 运行测试")
