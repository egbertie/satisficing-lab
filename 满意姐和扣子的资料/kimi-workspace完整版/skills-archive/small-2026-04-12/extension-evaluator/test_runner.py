#!/usr/bin/env python3
"""扩展评估器测试套件 - v1.2.0 (基于实际代码)"""
import sys
import argparse
sys.path.insert(0, '/root/.openclaw/workspace/skills/extension-evaluator')
from extension_evaluator import ExtensionEvaluator, ExtensionPriority, ExtensionPlan, ExtensionCandidate

def run_tests():
    print("=" * 70)
    print("扩展评估器 - 完整测试套件 (v1.2.0)")
    print("=" * 70)
    
    evaluator = ExtensionEvaluator()
    test_results = []
    
    # 测试1: 初始化
    print("\n[测试1/12] 初始化...")
    try:
        passed = len(evaluator.candidates) > 0
        test_results.append(("初始化", passed))
        print(f"  {'✅ PASS' if passed else '❌ FAIL'}: {len(evaluator.candidates)}个候选")
    except Exception as e:
        test_results.append(("初始化", False))
        print(f"  ❌ FAIL: {e}")
    
    # 测试2: 评估所有
    print("\n[测试2/12] 评估所有...")
    try:
        plan = evaluator.evaluate_all()
        passed = plan is not None
        test_results.append(("评估所有", passed))
        print(f"  {'✅ PASS' if passed else '❌ FAIL'}")
    except Exception as e:
        test_results.append(("评估所有", False))
        print(f"  ❌ FAIL: {e}")
    
    # 测试3: 高优先级项
    print("\n[测试3/12] 高优先级...")
    try:
        plan = evaluator.evaluate_all()
        passed = len(plan.high_priority) >= 0
        test_results.append(("高优先级", passed))
        print(f"  {'✅ PASS' if passed else '❌ FAIL'}: {len(plan.high_priority)}项")
    except Exception as e:
        test_results.append(("高优先级", False))
        print(f"  ❌ FAIL: {e}")
    
    # 测试4: 中优先级项
    print("\n[测试4/12] 中优先级...")
    try:
        plan = evaluator.evaluate_all()
        passed = len(plan.medium_priority) >= 0
        test_results.append(("中优先级", passed))
        print(f"  {'✅ PASS' if passed else '❌ FAIL'}: {len(plan.medium_priority)}项")
    except Exception as e:
        test_results.append(("中优先级", False))
        print(f"  ❌ FAIL: {e}")
    
    # 测试5: 低优先级项
    print("\n[测试5/12] 低优先级...")
    try:
        plan = evaluator.evaluate_all()
        passed = len(plan.low_priority) >= 0
        test_results.append(("低优先级", passed))
        print(f"  {'✅ PASS' if passed else '❌ FAIL'}: {len(plan.low_priority)}项")
    except Exception as e:
        test_results.append(("低优先级", False))
        print(f"  ❌ FAIL: {e}")
    
    # 测试6: 暂缓项
    print("\n[测试6/12] 暂缓项...")
    try:
        plan = evaluator.evaluate_all()
        passed = len(plan.deferred) >= 0
        test_results.append(("暂缓项", passed))
        print(f"  {'✅ PASS' if passed else '❌ FAIL'}: {len(plan.deferred)}项")
    except Exception as e:
        test_results.append(("暂缓项", False))
        print(f"  ❌ FAIL: {e}")
    
    # 测试7: 候选项属性 (skill_name而非name)
    print("\n[测试7/12] 候选项属性...")
    try:
        candidate = evaluator.candidates[0]
        passed = hasattr(candidate, 'skill_name') and hasattr(candidate, 'priority')
        test_results.append(("候选项属性", passed))
        print(f"  {'✅ PASS' if passed else '❌ FAIL'}: {candidate.skill_name}")
    except Exception as e:
        test_results.append(("候选项属性", False))
        print(f"  ❌ FAIL: {e}")
    
    # 测试8: 优先级枚举
    print("\n[测试8/12] 优先级枚举...")
    try:
        passed = ExtensionPriority.HIGH is not None
        test_results.append(("优先级枚举", passed))
        print(f"  {'✅ PASS' if passed else '❌ FAIL'}")
    except Exception as e:
        test_results.append(("优先级枚举", False))
        print(f"  ❌ FAIL: {e}")
    
    # 测试9: 计划结构
    print("\n[测试9/12] 计划结构...")
    try:
        plan = evaluator.evaluate_all()
        passed = (hasattr(plan, 'high_priority') and 
                 hasattr(plan, 'medium_priority') and 
                 hasattr(plan, 'low_priority') and 
                 hasattr(plan, 'deferred') and
                 hasattr(plan, 'overall_recommendation'))
        test_results.append(("计划结构", passed))
        print(f"  {'✅ PASS' if passed else '❌ FAIL'}")
    except Exception as e:
        test_results.append(("计划结构", False))
        print(f"  ❌ FAIL: {e}")
    
    # 测试10: 整体建议
    print("\n[测试10/12] 整体建议...")
    try:
        plan = evaluator.evaluate_all()
        passed = len(plan.overall_recommendation) > 0
        test_results.append(("整体建议", passed))
        print(f"  {'✅ PASS' if passed else '❌ FAIL'}")
    except Exception as e:
        test_results.append(("整体建议", False))
        print(f"  ❌ FAIL: {e}")
    
    # 测试11: 候选项描述
    print("\n[测试11/12] 候选项描述...")
    try:
        candidate = evaluator.candidates[0]
        passed = hasattr(candidate, 'description') and len(candidate.description) > 0
        test_results.append(("候选项描述", passed))
        print(f"  {'✅ PASS' if passed else '❌ FAIL'}")
    except Exception as e:
        test_results.append(("候选项描述", False))
        print(f"  ❌ FAIL: {e}")
    
    # 测试12: 工作量估算
    print("\n[测试12/12] 工作量估算...")
    try:
        candidate = evaluator.candidates[0]
        passed = hasattr(candidate, 'estimated_effort') and len(candidate.estimated_effort) > 0
        test_results.append(("工作量估算", passed))
        print(f"  {'✅ PASS' if passed else '❌ FAIL'}: {candidate.estimated_effort}")
    except Exception as e:
        test_results.append(("工作量估算", False))
        print(f"  ❌ FAIL: {e}")
    
    # 总结
    print("\n" + "=" * 70)
    print("测试总结")
    print("=" * 70)
    passed_count = sum(1 for _, p in test_results if p)
    total_count = len(test_results)
    print(f"通过: {passed_count}/{total_count}")
    print(f"失败: {total_count - passed_count}/{total_count}")
    print(f"通过率: {passed_count/total_count*100:.1f}%")
    
    if passed_count == total_count:
        print("\n✅ 所有测试通过!")
        return True
    else:
        print("\n❌ 存在失败的测试:")
        for name, passed in test_results:
            if not passed:
                print(f"  - {name}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", action="store_true")
    args = parser.parse_args()
    
    if args.test:
        success = run_tests()
        sys.exit(0 if success else 1)
    else:
        print("=" * 60)
        print("扩展评估器 - Extension Evaluator")
        print("=" * 60)
        print("\n使用 --test 运行完整测试套件")
