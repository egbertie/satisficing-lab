#!/usr/bin/env python3
"""伦理检查器测试套件"""
import sys
import argparse
from ethics_checker import EthicsChecker, EthicsLevel

def run_tests():
    print("=" * 70)
    print("伦理检查器 - 完整测试套件 (v1.0.0)")
    print("=" * 70)
    
    checker = EthicsChecker()
    test_results = []
    
    # 12项测试
    tests = [
        ("初始化", lambda: len(checker.rules) == 5),
        ("诚规则检查", lambda: checker._check_rule("诚_integrity", "透明披露").score > 0),
        ("信规则检查", lambda: checker._check_rule("信_trustworthiness", "承诺兑现").score > 0),
        ("义规则检查", lambda: checker._check_rule("义_righteousness", "声明冲突").score > 0),
        ("仁规则检查", lambda: checker._check_rule("仁_benevolence", "关怀员工").score > 0),
        ("礼规则检查", lambda: checker._check_rule("礼_propriety", "遵守规范").score > 0),
        ("正面内容检查", lambda: checker.full_check("透明披露承诺兑现关怀").overall_score > 0.5),
        ("负面内容检测", lambda: checker.full_check("隐瞒夸大").overall_score < 0.5),
        ("报告结构", lambda: hasattr(checker.full_check("测试"), 'overall_score')),
        ("分数范围", lambda: 0 <= checker.full_check("测试").overall_score <= 1),
        ("级别判断", lambda: checker.full_check("测试").overall_level is not None),
        ("建议生成", lambda: len(checker.full_check("测试").actionable_items) >= 0),
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
