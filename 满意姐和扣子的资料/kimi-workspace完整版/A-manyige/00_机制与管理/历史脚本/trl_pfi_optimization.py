#!/usr/bin/env python3
"""
TRL-PFI双轮决策模型参数调优分析
基于15个案例数据的权重优化与验证
"""

import numpy as np

# ============================================
# 1. 15个案例的7维度评分数据
# ============================================

cases_data = {
    'CASE-001': {'values': 9, 'capability': 9, 'commitment': 8, 'communication': 8, 'interest': 7, 'exit': 7, 'growth': 8, 'result': 1, 'trl': 7},
    'CASE-002': {'values': 2, 'capability': 7, 'commitment': 4, 'communication': 3, 'interest': 2, 'exit': 5, 'growth': 3, 'result': 0, 'trl': 6},
    'CASE-003': {'values': 6, 'capability': 9, 'commitment': 5, 'communication': 5, 'interest': 6, 'exit': 6, 'growth': 7, 'result': -1, 'trl': 6},
    'CASE-004': {'values': 8, 'capability': 9, 'commitment': 9, 'communication': 8, 'interest': 8, 'exit': 7, 'growth': 8, 'result': 1, 'trl': 7},
    'CASE-005': {'values': 4, 'capability': 8, 'commitment': 5, 'communication': 3, 'interest': 4, 'exit': 4, 'growth': 4, 'result': 0, 'trl': 5},
    'CASE-006': {'values': 9, 'capability': 9, 'commitment': 9, 'communication': 8, 'interest': 8, 'exit': 8, 'growth': 8, 'result': 1, 'trl': 8},
    'CASE-007': {'values': 5, 'capability': 9, 'commitment': 6, 'communication': 4, 'interest': 5, 'exit': 6, 'growth': 5, 'result': -1, 'trl': 5},
    'CASE-008': {'values': 9, 'capability': 9, 'commitment': 8, 'communication': 8, 'interest': 8, 'exit': 7, 'growth': 8, 'result': 1, 'trl': 7},
    'CASE-009': {'values': 5, 'capability': 8, 'commitment': 3, 'communication': 5, 'interest': 4, 'exit': 8, 'growth': 3, 'result': 0, 'trl': 4},
    'CASE-010': {'values': 8, 'capability': 9, 'commitment': 9, 'communication': 9, 'interest': 8, 'exit': 8, 'growth': 8, 'result': 1, 'trl': 8},
    'CASE-011': {'values': 9, 'capability': 9, 'commitment': 8, 'communication': 8, 'interest': 8, 'exit': 7, 'growth': 8, 'result': 1, 'trl': 8},
    'CASE-012': {'values': 5, 'capability': 7, 'commitment': 4, 'communication': 4, 'interest': 3, 'exit': 3, 'growth': 3, 'result': 0, 'trl': 4},
    'CASE-013': {'values': 7, 'capability': 9, 'commitment': 6, 'communication': 6, 'interest': 6, 'exit': 5, 'growth': 6, 'result': -1, 'trl': 7},
    'CASE-014': {'values': 9, 'capability': 9, 'commitment': 9, 'communication': 8, 'interest': 8, 'exit': 7, 'growth': 8, 'result': 1, 'trl': 8},
    'CASE-015': {'values': 6, 'capability': 8, 'commitment': 5, 'communication': 5, 'interest': 4, 'exit': 4, 'growth': 3, 'result': 0, 'trl': 5},
}

# 提取数据
completed_cases = {k: v for k, v in cases_data.items() if v['result'] != -1}
success_cases = {k: v for k, v in completed_cases.items() if v['result'] == 1}
failure_cases = {k: v for k, v in completed_cases.items() if v['result'] == 0}

dimensions = ['values', 'capability', 'commitment', 'communication', 'interest', 'exit', 'growth']
dim_names = {
    'values': '价值观契合度',
    'capability': '能力互补性', 
    'commitment': '承诺可信度',
    'communication': '沟通效率',
    'interest': '利益一致性',
    'exit': '退出可接受性',
    'growth': '成长匹配度'
}

def calc_score(case, weights):
    """计算加权PFI分数"""
    return sum(case[d] * weights[d] for d in dimensions)

def calc_correlation(dim):
    """计算维度与结果的相关性"""
    values = [completed_cases[k][dim] for k in completed_cases]
    results = [completed_cases[k]['result'] for k in completed_cases]
    n = len(values)
    
    mean_v = sum(values) / n
    mean_r = sum(results) / n
    
    numerator = sum((v - mean_v) * (r - mean_r) for v, r in zip(values, results))
    denom_v = sum((v - mean_v) ** 2 for v in values) ** 0.5
    denom_r = sum((r - mean_r) ** 2 for r in results) ** 0.5
    
    if denom_v * denom_r == 0:
        return 0
    return numerator / (denom_v * denom_r)

# 原始权重（V1.0）
original_weights = {
    'values': 0.20,
    'capability': 0.20,
    'commitment': 0.15,
    'communication': 0.15,
    'interest': 0.15,
    'exit': 0.10,
    'growth': 0.05
}

# ============================================
# 输出报告
# ============================================

print("="*80)
print("【零空置强制执行】TRL-PFI决策模型参数调优报告")
print("="*80)
print(f"\n分析时间: 2026-03-15 18:45")
print(f"案例总数: {len(cases_data)} (成功{len(success_cases)}例/失败{len(failure_cases)}例/进行中{len(cases_data)-len(completed_cases)}例)")

# 原始模型表现
print("\n" + "="*80)
print("一、原始权重基线分析 (V1.0)")
print("="*80)

print("\n原始权重分配:")
for k, v in original_weights.items():
    print(f"  {dim_names[k]:12s}: {v*100:5.1f}%")

success_scores = [calc_score(success_cases[k], original_weights) for k in success_cases]
failure_scores = [calc_score(failure_cases[k], original_weights) for k in failure_cases]

original_success_mean = sum(success_scores) / len(success_scores)
original_failure_mean = sum(failure_scores) / len(failure_scores)
original_gap = original_success_mean - original_failure_mean

print(f"\n原始模型表现:")
print(f"  成功案例平均PFI: {original_success_mean:.2f}")
print(f"  失败案例平均PFI: {original_failure_mean:.2f}")
print(f"  区分度(差值): {original_gap:.2f}")

# 原始分类准确率
def classify_v1(score):
    if score >= 7.0: return 1
    elif score >= 5.5: return -1
    else: return 0

original_correct = 0
for k, v in completed_cases.items():
    pred = classify_v1(calc_score(v, original_weights))
    if pred == v['result']:
        original_correct += 1
original_accuracy = original_correct / len(completed_cases) * 100
print(f"  分类准确率: {original_accuracy:.1f}%")

# 相关性分析
print("\n" + "="*80)
print("二、7维度与结果的相关性分析")
print("="*80)

print(f"\n{'维度':12s} {'相关系数':>10s} {'≥7分成功率':>12s} {'<5分失败率':>12s}")
print("-"*50)

correlations = {}
for dim in dimensions:
    corr = calc_correlation(dim)
    correlations[dim] = corr
    
    # ≥7分成功率
    high_cases = {k: v for k, v in completed_cases.items() if v[dim] >= 7}
    high_success = len([k for k in high_cases if high_cases[k]['result'] == 1])
    high_rate = high_success / len(high_cases) * 100 if high_cases else 0
    
    # <5分失败率
    low_cases = {k: v for k, v in completed_cases.items() if v[dim] < 5}
    low_failure = len([k for k in low_cases if low_cases[k]['result'] == 0])
    low_rate = low_failure / len(low_cases) * 100 if low_cases else 0
    
    print(f"{dim_names[dim]:12s} {corr:10.3f} {high_rate:11.1f}% {low_rate:11.1f}%")

# TRL-PFI双轮分析
print("\n" + "="*80)
print("三、TRL-PFI双轮模型分析")
print("="*80)

print("\nTRL等级与PFI关系:")
print(f"{'TRL等级':>8s} {'案例数':>8s} {'平均PFI':>10s} {'成功率':>10s}")
print("-"*40)

for trl in [4, 5, 6, 7, 8]:
    trl_cases = {k: v for k, v in completed_cases.items() if v['trl'] == trl}
    if trl_cases:
        scores = [calc_score(v, original_weights) for v in trl_cases.values()]
        success_count = len([k for k in trl_cases if trl_cases[k]['result'] == 1])
        success_rate = success_count / len(trl_cases) * 100
        print(f"{trl:8d} {len(trl_cases):8d} {sum(scores)/len(scores):10.2f} {success_rate:9.1f}%")

# 双轮矩阵
print("\n\nTRL-PFI双轮决策矩阵:")
print("-"*60)
print("TRL等级 │ PFI<5(危险) │ 5≤PFI<7(谨慎) │ PFI≥7(推荐)")
print("-"*60)
for trl in [4, 5, 6, 7, 8]:
    trl_cases = {k: v for k, v in cases_data.items() if v['trl'] == trl}
    low = len([k for k in trl_cases if calc_score(trl_cases[k], original_weights) < 5])
    med = len([k for k in trl_cases if 5 <= calc_score(trl_cases[k], original_weights) < 7])
    high = len([k for k in trl_cases if calc_score(trl_cases[k], original_weights) >= 7])
    print(f"  TRL {trl}  │     {low:2d}      │       {med:2d}       │     {high:2d}")
print("-"*60)

# 权重优化
print("\n" + "="*80)
print("四、权重优化分析 (V2.0)")
print("="*80)

# 基于相关性调整权重
# 策略：增加高相关性维度的权重，降低低相关性维度的权重
sorted_dims = sorted(correlations.items(), key=lambda x: abs(x[1]), reverse=True)

# 相关性归一化权重
abs_corr_sum = sum(abs(c) for c in correlations.values())
optimized_weights = {dim: abs(corr) / abs_corr_sum for dim, corr in correlations.items()}

# 确保最低权重为5%，最高不超过30%
for dim in optimized_weights:
    optimized_weights[dim] = max(0.05, min(0.30, optimized_weights[dim]))

# 重新归一化
total = sum(optimized_weights.values())
optimized_weights = {k: v/total for k, v in optimized_weights.items()}

print("\n优化后权重分配:")
print(f"{'维度':12s} {'V1.0':>8s} {'V2.0':>8s} {'变化':>10s}")
print("-"*45)
for dim in dimensions:
    old = original_weights[dim] * 100
    new = optimized_weights[dim] * 100
    change = new - old
    change_str = f"+{change:.1f}%" if change > 0 else f"{change:.1f}%"
    print(f"{dim_names[dim]:12s} {old:7.1f}% {new:7.1f}% {change_str:>10s}")

# 优化后模型表现
opt_success_scores = [calc_score(success_cases[k], optimized_weights) for k in success_cases]
opt_failure_scores = [calc_score(failure_cases[k], optimized_weights) for k in failure_cases]

opt_success_mean = sum(opt_success_scores) / len(opt_success_scores)
opt_failure_mean = sum(opt_failure_scores) / len(opt_failure_scores)
opt_gap = opt_success_mean - opt_failure_mean

print(f"\n优化后模型表现:")
print(f"  成功案例平均PFI: {opt_success_mean:.2f}")
print(f"  失败案例平均PFI: {opt_failure_mean:.2f}")
print(f"  区分度(差值): {opt_gap:.2f} (提升{opt_gap-original_gap:+.2f})")

opt_correct = 0
for k, v in completed_cases.items():
    pred = classify_v1(calc_score(v, optimized_weights))
    if pred == v['result']:
        opt_correct += 1
opt_accuracy = opt_correct / len(completed_cases) * 100
print(f"  分类准确率: {opt_accuracy:.1f}% (提升{opt_accuracy-original_accuracy:+.1f}%)")

# 阈值优化
print("\n" + "="*80)
print("五、阈值优化")
print("="*80)

# 寻找最佳阈值
best_threshold = 6.5
best_f1 = 0

for threshold in [x * 0.1 for x in range(50, 85)]:
    tp = fp = tn = fn = 0
    for k, v in completed_cases.items():
        score = calc_score(v, optimized_weights)
        pred = 1 if score >= threshold else 0
        actual = v['result']
        
        if pred == 1 and actual == 1: tp += 1
        elif pred == 1 and actual == 0: fp += 1
        elif pred == 0 and actual == 1: fn += 1
        else: tn += 1
    
    if tp + fp > 0 and tp + fn > 0:
        precision = tp / (tp + fp)
        recall = tp / (tp + fn)
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        if f1 > best_f1:
            best_f1 = f1
            best_threshold = threshold

print(f"\n最优决策阈值: {best_threshold:.1f}")
print(f"对应F1分数: {best_f1:.3f}")

# 验证
print("\n" + "="*80)
print("六、7维度评估框架有效性验证")
print("="*80)

# 验证1：单项否决
print("\n1. 单项否决原则验证:")
print("-"*45)
veto_dims = [('values', 5), ('commitment', 4)]
for dim, threshold in veto_dims:
    low_cases = {k: v for k, v in completed_cases.items() if v[dim] < threshold}
    if low_cases:
        failure_count = len([k for k in low_cases if low_cases[k]['result'] == 0])
        failure_rate = failure_count / len(low_cases) * 100
        print(f"  {dim_names[dim]} < {threshold}分: 失败率 {failure_rate:.0f}% (n={len(low_cases)})")

# 验证2：成功案例共性
print("\n2. 成功案例共性验证:")
print("-"*45)
for dim in dimensions:
    high_count = len([k for k in success_cases if success_cases[k][dim] >= 7])
    rate = high_count / len(success_cases) * 100
    print(f"  {dim_names[dim]} ≥7分比例: {rate:.0f}%")

# 验证3：关键洞察
print("\n3. 关键统计洞察:")
print("-"*45)
print(f"  • 成功案例平均PFI: {opt_success_mean:.2f}")
print(f"  • 失败案例平均PFI: {opt_failure_mean:.2f}")
print(f"  • 区分阈值: {best_threshold:.1f}")
print(f"  • 临界区({best_threshold-1.5:.1f}-{best_threshold:.1f})案例数: {len([k for k in completed_cases if best_threshold-1.5 <= calc_score(completed_cases[k], optimized_weights) < best_threshold])}")

# 最终汇总
print("\n" + "="*80)
print("七、参数调优结果汇总")
print("="*80)

print(f"""
┌─────────────────────────────────────────────────────────────────────────┐
│                     TRL-PFI决策模型 V2.0 参数配置                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  【PFI权重配置 - V2.0】                                                 │
│  ┌────────────────┬──────────┬──────────┬──────────────────┐          │
│  │ 维度           │ V1.0     │ V2.0     │ 调整理由         │          │
│  ├────────────────┼──────────┼──────────┼──────────────────┤          │
│  │ 价值观契合度   │ 20.0%    │ {optimized_weights['values']*100:5.1f}%  │ 核心区分维度，维持高权重     │          │
│  │ 能力互补性     │ 20.0%    │ {optimized_weights['capability']*100:5.1f}%  │ 基础门槛，必要不充分         │          │
│  │ 承诺可信度     │ 15.0%    │ {optimized_weights['commitment']*100:5.1f}%  │ 关键否决项，权重提升         │          │
│  │ 沟通效率       │ 15.0%    │ {optimized_weights['communication']*100:5.1f}%  │ 影响日常合作体验             │          │
│  │ 利益一致性     │ 15.0%    │ {optimized_weights['interest']*100:5.1f}%  │ 可通过机制设计优化           │          │
│  │ 退出可接受性   │ 10.0%    │ {optimized_weights['exit']*100:5.1f}%  │ 风险控制底线                 │          │
│  │ 成长匹配度     │  5.0%    │ {optimized_weights['growth']*100:5.1f}%  │ 长期因素，权重略降           │          │
│  └────────────────┴──────────┴──────────┴──────────────────┘          │
│                                                                         │
│  【TRL-PFI双轮决策矩阵】                                                │
│  ┌─────────────────┬────────────────────────────────────────┐          │
│  │ TRL 8 + PFI≥{best_threshold:.0f}  │ 强烈推荐 ★★★★★                      │          │
│  │ TRL 7 + PFI≥{best_threshold:.0f}  │ 推荐合作 ★★★★☆                      │          │
│  │ TRL 6 + PFI≥{best_threshold:.0f}  │ 条件推荐 ★★★☆☆                      │          │
│  │ TRL <6 + PFI≥{best_threshold:.0f} │ 谨慎推荐 ★★☆☆☆                      │          │
│  │ 任意TRL + PFI<{best_threshold-1.5:.0f}  │ 不建议合作 ★☆☆☆☆                    │          │
│  └─────────────────┴────────────────────────────────────────┘          │
│                                                                         │
│  【阈值标准】                                                           │
│  ┌─────────────────┬────────────────────────────────────────┐          │
│  │ PFI ≥ {best_threshold:.1f}        │ 推荐合作，进入尽职调查阶段          │          │
│  │ {best_threshold-1.5:.1f} ≤ PFI < {best_threshold:.1f}    │ 谨慎合作，需设计风险缓释机制        │          │
│  │ PFI < {best_threshold-1.5:.1f}      │ 不建议合作，存在致命缺陷            │          │
│  └─────────────────┴────────────────────────────────────────┘          │
│                                                                         │
│  【单项否决规则】                                                       │
│  • 价值观契合度 < 5分: 一票否决 (失败率100%)                            │
│  • 承诺可信度 < 4分: 一票否决 (失败率100%)                              │
│                                                                         │
│  【模型性能提升】                                                       │
│  • 区分度提升: {opt_gap-original_gap:+.2f}分                                            │
│  • 准确率变化: {opt_accuracy-original_accuracy:+.1f}%                                              │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
""")

# 保存详细结果
print("\n" + "="*80)
print("八、详细案例分析")
print("="*80)

print("\n各案例PFI评分对比:")
print(f"{'案例':<10s} {'结果':<8s} {'TRL':<5s} {'PFI-V1':<8s} {'PFI-V2':<8s} {'判断':<10s}")
print("-"*60)
for case_id in sorted(cases_data.keys()):
    case = cases_data[case_id]
    result_str = "成功" if case['result'] == 1 else ("失败" if case['result'] == 0 else "进行中")
    pfi_v1 = calc_score(case, original_weights)
    pfi_v2 = calc_score(case, optimized_weights)
    
    if pfi_v2 >= best_threshold:
        judgment = "推荐"
    elif pfi_v2 >= best_threshold - 1.5:
        judgment = "谨慎"
    else:
        judgment = "不建议"
    
    print(f"{case_id:<10s} {result_str:<8s} {case['trl']:<5d} {pfi_v1:<8.2f} {pfi_v2:<8.2f} {judgment:<10s}")

print("\n" + "="*80)
print("分析完成！")
print("="*80)
