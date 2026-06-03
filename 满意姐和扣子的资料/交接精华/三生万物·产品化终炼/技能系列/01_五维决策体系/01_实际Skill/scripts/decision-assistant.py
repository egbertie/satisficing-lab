#!/usr/bin/env python3
"""
五维决策助手 - 交互式决策脚本
用法: python3 decision-assistant.py
"""

print("=" * 50)
print("五维决策助手 · 满意解研究所")
print("=" * 50)

# 土
trust = int(input("\n[土] 信任基础 (1-10): "))
# 金
standard = int(input("[金] 满意标准清晰度 (1-10): "))
# 水
flexible = int(input("[水] 方向灵活度 (1-10): "))
# 木
ethics = int(input("[木] 伦理合规度 (1-10): "))
# 火
intuition = int(input("[火] 直觉确认度 (1-10): "))

total = trust + standard + flexible + ethics + intuition

print("\n" + "=" * 50)
print(f"五维评分: 土{trust} / 金{standard} / 水{flexible} / 木{ethics} / 火{intuition}")
print(f"总分: {total}/50")

if total >= 35:
    print("\n✅ 建议: 可以推进")
elif any(s < 5 for s in [trust, standard, flexible, ethics, intuition]):
    weak = []
    if trust < 5: weak.append("土")
    if standard < 5: weak.append("金")
    if flexible < 5: weak.append("水")
    if ethics < 5: weak.append("木")
    if intuition < 5: weak.append("火")
    print(f"\n⚠️  建议: 补强维度 {', '.join(weak)} 后再决策")
else:
    print("\n🟡 建议: 接近标准，可推进但需关注")

print("=" * 50)
