#!/usr/bin/env python3
"""
蓝军审计助手 - 交互式认知审计脚本
用法: python3 audit-checker.py
"""

print("=" * 50)
print("蓝军审计助手 · 满意解研究所")
print("=" * 50)

checks = [
    ("信源独立性", "信息来源是否独立？有无利益相关？"),
    ("时效性", "信息是否过时？是否有更新版本？"),
    ("因果混淆", "是否混淆了相关与因果？"),
    ("幸存者偏差", "是否考虑了失败案例？"),
    ("基底率忽视", "是否考虑了基础概率？"),
    ("锚定效应", "是否被第一个信息锚定？"),
    ("确认偏误", "是否寻找了反面证据？"),
    ("语言腐败", "用词是否清晰无模糊？"),
    ("数学谬误", "关键计算是否复核？"),
    ("样本偏差", "样本是否有代表性？"),
]

results = []
for name, desc in checks:
    print(f"\n[{name}] {desc}")
    r = input("  结果 (通过p/存疑w/不通过f): ").strip().lower()
    results.append(r)

pass_count = results.count("p")
warn_count = results.count("w")
fail_count = results.count("f")

print("\n" + "=" * 50)
print(f"审计结果: 通过{pass_count} / 存疑{warn_count} / 不通过{fail_count}")

if fail_count >= 1 or warn_count >= 3:
    print("\n🔴 风险等级: 高危")
    print("建议: 修正问题后重新审计")
elif warn_count >= 1:
    print("\n🟡 风险等级: 中危")
    print("建议: 关注存疑项，确认无隐患后放行")
else:
    print("\n🟢 风险等级: 可控")
    print("建议: 可以推进，但持续监控")

print("=" * 50)
