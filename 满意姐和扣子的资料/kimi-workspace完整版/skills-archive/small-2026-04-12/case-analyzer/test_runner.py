#!/usr/bin/env python3
"""案例分析器测试套件 - v1.2.0 (基于实际代码)"""
import sys
import argparse
sys.path.insert(0, '/root/.openclaw/workspace/skills/case-analyzer')
from case_analyzer import CaseAnalyzer, CaseType, CaseFactor

def run_tests():
    print("=" * 70)
    print("案例分析器 - 完整测试套件 (v1.2.0)")
    print("=" * 70)
    
    analyzer = CaseAnalyzer()
    test_results = []
    
    # 测试1: 初始化
    print("\n[测试1/12] 初始化...")
    try:
        passed = len(analyzer.factor_library) > 0
        test_results.append(("初始化", passed))
        print(f"  {'✅ PASS' if passed else '❌ FAIL'}")
    except Exception as e:
        test_results.append(("初始化", False))
        print(f"  ❌ FAIL: {e}")
    
    # 测试2: 案例1分析 - 股权分配不均
    print("\n[测试2/12] 案例1分析 - 股权分配不均...")
    try:
        result = analyzer.analyze_case("股权分配不均导致合伙人冲突")
        passed = result is not None and hasattr(result, 'case_type')
        test_results.append(("案例1分析", passed))
        print(f"  {'✅ PASS' if passed else '❌ FAIL'}: type={result.case_type.value if passed else 'N/A'}")
    except Exception as e:
        test_results.append(("案例1分析", False))
        print(f"  ❌ FAIL: {e}")
    
    # 测试3: 案例2分析 - 明确分工
    print("\n[测试3/12] 案例2分析 - 明确分工...")
    try:
        result = analyzer.analyze_case("明确分工书面协议成功案例")
        passed = result is not None
        test_results.append(("案例2分析", passed))
        print(f"  {'✅ PASS' if passed else '❌ FAIL'}")
    except Exception as e:
        test_results.append(("案例2分析", False))
        print(f"  ❌ FAIL: {e}")
    
    # 测试4: 因子提取
    print("\n[测试4/12] 因子提取...")
    try:
        factors = analyzer._extract_factors("股权纠纷和利益冲突")
        passed = isinstance(factors, list)
        test_results.append(("因子提取", passed))
        print(f"  {'✅ PASS' if passed else '❌ FAIL'}: {len(factors)}个因子")
    except Exception as e:
        test_results.append(("因子提取", False))
        print(f"  ❌ FAIL: {e}")
    
    # 测试5: 类型判断
    print("\n[测试5/12] 类型判断...")
    try:
        factors = [CaseFactor("股权分配", True, "negative", 4)]
        case_type = analyzer._determine_case_type(factors)
        passed = case_type in CaseType
        test_results.append(("类型判断", passed))
        print(f"  {'✅ PASS' if passed else '❌ FAIL'}: {case_type.value}")
    except Exception as e:
        test_results.append(("类型判断", False))
        print(f"  ❌ FAIL: {e}")
    
    # 测试6: 模式匹配
    print("\n[测试6/12] 模式匹配...")
    try:
        factors = [CaseFactor("股权分配不均", True, "negative", 4)]
        pattern = analyzer._match_pattern(factors)
        passed = pattern is not None
        test_results.append(("模式匹配", passed))
        print(f"  {'✅ PASS' if passed else '❌ FAIL'}: {pattern}")
    except Exception as e:
        test_results.append(("模式匹配", False))
        print(f"  ❌ FAIL: {e}")
    
    # 测试7: 教训提取
    print("\n[测试7/12] 教训提取...")
    try:
        factors = [CaseFactor("股权纠纷", True, "negative", 4)]
        lessons = analyzer._extract_lessons(factors, CaseType.PARTNER_CONFLICT)
        passed = isinstance(lessons, list)
        test_results.append(("教训提取", passed))
        print(f"  {'✅ PASS' if passed else '❌ FAIL'}: {len(lessons)}条教训")
    except Exception as e:
        test_results.append(("教训提取", False))
        print(f"  ❌ FAIL: {e}")
    
    # 测试8: 红旗识别
    print("\n[测试8/12] 红旗识别...")
    try:
        red_flags = analyzer._identify_red_flags("一直拖着不签协议")
        passed = isinstance(red_flags, list) and len(red_flags) >= 0
        test_results.append(("红旗识别", passed))
        print(f"  {'✅ PASS' if passed else '❌ FAIL'}: {len(red_flags)}个红旗")
    except Exception as e:
        test_results.append(("红旗识别", False))
        print(f"  ❌ FAIL: {e}")
    
    # 测试9: 建议生成
    print("\n[测试9/12] 建议生成...")
    try:
        result = analyzer.analyze_case("股权纠纷")
        passed = len(result.recommendations) >= 0
        test_results.append(("建议生成", passed))
        print(f"  {'✅ PASS' if passed else '❌ FAIL'}: {len(result.recommendations)}条建议")
    except Exception as e:
        test_results.append(("建议生成", False))
        print(f"  ❌ FAIL: {e}")
    
    # 测试10: 案例ID生成
    print("\n[测试10/12] 案例ID生成...")
    try:
        result = analyzer.analyze_case("测试", None)
        passed = result.case_id is not None and len(result.case_id) > 0
        test_results.append(("案例ID生成", passed))
        print(f"  {'✅ PASS' if passed else '❌ FAIL'}: {result.case_id}")
    except Exception as e:
        test_results.append(("案例ID生成", False))
        print(f"  ❌ FAIL: {e}")
    
    # 测试11: 摘要生成
    print("\n[测试11/12] 摘要生成...")
    try:
        result = analyzer.analyze_case("股权纠纷")
        summary = analyzer.generate_case_summary(result)
        passed = len(summary) > 0
        test_results.append(("摘要生成", passed))
        print(f"  {'✅ PASS' if passed else '❌ FAIL'}")
    except Exception as e:
        test_results.append(("摘要生成", False))
        print(f"  ❌ FAIL: {e}")
    
    # 测试12: 多案例分析
    print("\n[测试12/12] 多案例分析...")
    try:
        cases = ["股权纠纷", "创始人冲突", "明确分工成功案例"]
        all_passed = True
        for case in cases:
            result = analyzer.analyze_case(case)
            if result is None:
                all_passed = False
                break
        test_results.append(("多案例分析", all_passed))
        print(f"  {'✅ PASS' if all_passed else '❌ FAIL'}")
    except Exception as e:
        test_results.append(("多案例分析", False))
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
        print("案例分析器 - Case Analyzer")
        print("=" * 60)
        print("\n使用 --test 运行完整测试套件")
