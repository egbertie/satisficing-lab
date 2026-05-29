#!/usr/bin/env python3
"""
为 entities_index.json 的所有 products 添加 quality_confidence 字段
A/B/C/D 四级可信度标记

规则:
- vi_compliance≥85 AND content_accuracy≥80 AND ux_rating≥80 → A级
- vi_compliance≥70 AND content_accuracy≥70 → B级
- 任一维度<70 → C级
- Q值基于模板推断(非实测) → D级
- D级产品在quality_score旁标注 "(校准中)"
"""
import json
import re
from pathlib import Path

INDEX_PATH = Path("/Users/egbertielau/.openclaw/workspace/memory/_data/entities_index.json")

with open(INDEX_PATH, 'r', encoding='utf-8') as f:
    data = json.load(f)

# 统计
stats = {"A": 0, "B": 0, "C": 0, "D": 0, "total": 0}
products = data.get("products", [])

# 检测模板推断的特征
def is_template_inferred(product):
    """检测Q值是否基于模板推断（非实测）"""
    # 特征1: quality_score 是精确的100/98/95等 (模板默认值)
    qs = product.get("quality_score", 0)
    if qs in (100, 98, 95, 93, 94, 92, 91, 90, 88, 85):
        # 这些是常见模板值，但还需要其他证据
        # 特征2: 三个维度分数完全一致 (高度可疑的模板)
        vi = product.get("vi_compliance", 0)
        ca = product.get("content_accuracy", 0)
        ux = product.get("ux_rating", 0)
        
        # 三值全等 → 几乎确定是模板
        if vi == ca == ux:
            return True
        
        # content_accuracy < 60 且 quality_score ≥ 90 → 矛盾，模板推断
        if ca < 60 and qs >= 90:
            return True
        
        # 三值都≥80且quality_score≥90但content_accuracy<70 → 矛盾
        if qs >= 90 and ca < 50:
            return True
    
    # 特征3: quality_score高但quality_issues为空+无实际数据支撑
    issues = product.get("quality_issues", [])
    if qs >= 98 and (not issues or len(issues) == 0):
        # 完美分数的产品如果有任何维度偏低→模板推断
        vi = product.get("vi_compliance", 0)
        ca = product.get("content_accuracy", 0)
        ux = product.get("ux_rating", 0)
        if vi < 80 or ca < 50 or ux < 65:
            return True
    
    return False


for product in products:
    stats["total"] += 1
    vi = product.get("vi_compliance", 0)
    ca = product.get("content_accuracy", 0)
    ux = product.get("ux_rating", 0)
    
    # D级优先判断: 模板推断
    if is_template_inferred(product):
        grade = "D"
        product["quality_confidence"] = {
            "grade": "D",
            "reason": "Q值基于模板推断(非实测数据)",
            "calibration_status": "校准中",
            "requires": "需要人工实测vi_compliance/content_accuracy/ux_rating三个维度"
        }
        # D级在quality_score旁标注
        product["quality_score_note"] = "(校准中)"
        stats["D"] += 1
        continue
    
    # A级: 三维度≥各自阈值
    if vi >= 85 and ca >= 80 and ux >= 80:
        grade = "A"
        product["quality_confidence"] = {
            "grade": "A",
            "reason": "三维度全部达标: vi_compliance≥85, content_accuracy≥80, ux_rating≥80",
            "calibration_status": "已校准",
            "audited_by": f"蓝军·Skeptor-7 (review_date: {product.get('review_date', 'N/A')})"
        }
        stats["A"] += 1
    
    # B级: vi和ca≥70
    elif vi >= 70 and ca >= 70:
        grade = "B"
        # 检查是否需要标注
        note = ""
        if ux < 70:
            note = f" (ux_rating={ux}<70可提升)"
        product["quality_confidence"] = {
            "grade": "B",
            "reason": f"vi_compliance≥70, content_accuracy≥70{note}",
            "calibration_status": "部分校准",
            "improvement_areas": []
        }
        if ux < 70:
            product["quality_confidence"]["improvement_areas"].append("ux_rating")
        if ca < 80:
            product["quality_confidence"]["improvement_areas"].append("content_accuracy")
        stats["B"] += 1
    
    # C级: 任一维度<70
    else:
        grade = "C"
        weak_dims = []
        if vi < 70: weak_dims.append(f"vi_compliance={vi}")
        if ca < 70: weak_dims.append(f"content_accuracy={ca}")
        if ux < 70: weak_dims.append(f"ux_rating={ux}")
        
        product["quality_confidence"] = {
            "grade": "C",
            "reason": f"存在未达标维度: {', '.join(weak_dims)}",
            "calibration_status": "需要校准",
            "improvement_areas": []
        }
        if vi < 70: product["quality_confidence"]["improvement_areas"].append("vi_compliance")
        if ca < 70: product["quality_confidence"]["improvement_areas"].append("content_accuracy")
        if ux < 70: product["quality_confidence"]["improvement_areas"].append("ux_rating")
        stats["C"] += 1

# 更新meta
data["meta"]["quality_confidence"] = {
    "added": "2026-05-30T05:25:00",
    "version": "1.0",
    "grades": {
        "A": "三维度≥阈值: vi≥85, ca≥80, ux≥80",
        "B": "vi≥70, ca≥70 (ux可低于70)",
        "C": "任一维度<70",
        "D": "Q值基于模板推断(非实测)"
    },
    "distribution": stats,
    "total_graded": stats["total"]
}

# 更新quality_framework
data["meta"]["quality_framework"]["confidence_grades"] = {
    "description": "Q值可信度四级标记",
    "rules": [
        "A: vi≥85 AND ca≥80 AND ux≥80 → 高可信",
        "B: vi≥70 AND ca≥70 → 中可信",
        "C: 任一维<70 → 低可信",
        "D: 模板推断(非实测) → 不可信(校准中)"
    ],
    "d_note": "D级产品 quality_score 旁标注 '(校准中)'"
}

# Write back
with open(INDEX_PATH, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"✅ quality_confidence 已添加")
print(f"   总计: {stats['total']} 产品")
print(f"   A级: {stats['A']} ({stats['A']/max(stats['total'],1)*100:.1f}%)")
print(f"   B级: {stats['B']} ({stats['B']/max(stats['total'],1)*100:.1f}%)")
print(f"   C级: {stats['C']} ({stats['C']/max(stats['total'],1)*100:.1f}%)")
print(f"   D级: {stats['D']} ({stats['D']/max(stats['total'],1)*100:.1f}%)")
print(f"\n📁 已写入: {INDEX_PATH}")
