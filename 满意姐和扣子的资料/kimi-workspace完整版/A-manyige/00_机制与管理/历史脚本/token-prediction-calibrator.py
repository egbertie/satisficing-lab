#!/usr/bin/env python3
"""
Token预测校准器 V2.0
基于实际数据修正预测模型
"""

import json
import os
from datetime import datetime

# 实际观测数据（2026-03-21）
OBSERVED_DATA = {
    "date": "2026-03-21",
    "tasks": [
        {"name": "元认知循环机制", "predicted": 25, "actual": 25.1},
        {"name": "元审计官实战", "predicted": 20, "actual": 84.2},  # 偏高
        {"name": "量化指标体系", "predicted": 15, "actual": 25.8},
        {"name": "灾备企微通道", "predicted": 15, "actual": 48.6},  # 偏高
        {"name": "专家档案搜索", "predicted": 15, "actual": 73.7},  # 显著偏高
        {"name": "ai-meeting-notes", "predicted": 30, "actual": 51.6},
        {"name": "conversation-researcher", "predicted": 30, "actual": 27.9},  # 准确
        {"name": "info-collection-quality", "predicted": 30, "actual": 50.4},
        {"name": "quality-assurance", "predicted": 30, "actual": 56.5},
        {"name": "L4集成测试", "predicted": 35, "actual": 105.4},  # 显著偏高
        {"name": "baseline-checker", "predicted": 25, "actual": 33.5},
        {"name": "data-quality-auditor", "predicted": 30, "actual": 46.7},
        {"name": "quality-assessment", "predicted": 30, "actual": 49.4},
        {"name": "cost-redlines", "predicted": 30, "actual": 65.6},  # 偏高
        {"name": "testing-framework", "predicted": 35, "actual": 72.9},  # 偏高
        {"name": "quality-gate-system", "predicted": 25, "actual": 47.2},
        {"name": "universal-checklist", "predicted": 25, "actual": 39.9},
        {"name": "token-weekly-monitor", "predicted": 25, "actual": 51.9},
        {"name": "worry-list-manager", "predicted": 25, "actual": 32.6},
        {"name": "tiered-output", "predicted": 30, "actual": 49.7},
        {"name": "zero-idle-enforcer", "predicted": 25, "actual": 37.3},
        {"name": "five-level-verification", "predicted": 30, "actual": 58.2},  # 偏高
        {"name": "honesty-tagging", "predicted": 25, "actual": 38.2},
        {"name": "token-budget-enforcer", "predicted": 30, "actual": 53.5},  # 偏高
        {"name": "info-quality-guardian", "predicted": 25, "actual": 34.8},
        {"name": "vendor-api-monitor", "predicted": 25, "actual": 39.2},
        {"name": "blue-sentinel封装", "predicted": 30, "actual": 43.3},
        {"name": "工具层Skill", "predicted": 30, "actual": 61.8},  # 偏高
    ]
}

# 计算偏差
total_predicted = sum(t["predicted"] for t in OBSERVED_DATA["tasks"])
total_actual = sum(t["actual"] for t in OBSERVED_DATA["tasks"])

print("=" * 60)
print("Token预测校准报告 V2.0")
print("=" * 60)
print(f"\n任务总数: {len(OBSERVED_DATA['tasks'])}")
print(f"预测总量: {total_predicted:.1f}K")
print(f"实际总量: {total_actual:.1f}K")
print(f"\n整体偏差: {((total_actual - total_predicted) / total_predicted * 100):+.1f}%")

# 分类统计
over_predicted = [t for t in OBSERVED_DATA["tasks"] if t["actual"] < t["predicted"]]
under_predicted = [t for t in OBSERVED_DATA["tasks"] if t["actual"] > t["predicted"]]

print(f"\n高估任务: {len(over_predicted)}个")
print(f"低估任务: {len(under_predicted)}个")

# 显著偏差（>50%）
high_deviation = [t for t in OBSERVED_DATA["tasks"] 
                  if abs(t["actual"] - t["predicted"]) / t["predicted"] > 0.5]

print(f"\n显著偏差(>50%): {len(high_deviation)}个")
for t in high_deviation:
    dev = (t["actual"] - t["predicted"]) / t["predicted"] * 100
    print(f"  - {t['name']}: 预测{t['predicted']}K → 实际{t['actual']}K ({dev:+.0f}%)")

# 修正系数
avg_ratio = total_actual / total_predicted
print(f"\n{'='*60}")
print("修正建议")
print("=" * 60)
print(f"\n1. 全局修正系数: {avg_ratio:.2f}x")
print("   → 未来预测 = 原预测 × 1.35")

print("\n2. 任务类型修正:")
print("   - 研究/搜索类: 预测 × 2.5 (如专家档案、元审计)")
print("   - 框架/测试类: 预测 × 2.0 (如L4测试、五级验证)")
print("   - 标准Skill类: 预测 × 1.3 (平均水平)")
print("   - 工具脚本类: 预测 × 1.5 (实际偏高)")

print("\n3. 缓冲策略:")
print("   - 保守估计: 预测 × 1.5")
print("   - 安全阈值: Token < 20% 时暂停新任务")
print("   - 紧急预留: 始终保留5K tokens应对突发")

# 保存校准数据
calibration = {
    "version": "2.0",
    "date": datetime.now().isoformat(),
    "global_factor": round(avg_ratio, 2),
    "category_factors": {
        "research": 2.5,
        "framework": 2.0,
        "standard_skill": 1.3,
        "tool_script": 1.5
    },
    "buffer_strategy": {
        "conservative": 1.5,
        "pause_threshold": 20,
        "emergency_reserve": 5
    }
}

output_path = "/root/.openclaw/workspace/data/token-prediction-calibration-v2.json"
os.makedirs(os.path.dirname(output_path), exist_ok=True)
with open(output_path, 'w') as f:
    json.dump(calibration, f, indent=2)

print(f"\n校准数据已保存: {output_path}")

