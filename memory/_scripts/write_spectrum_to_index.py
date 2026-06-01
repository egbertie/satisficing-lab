#!/usr/bin/env python3
"""将双光谱评分写入 entities_index.json"""
import json
from datetime import datetime, timezone, timedelta

tz_shanghai = timezone(timedelta(hours=8))

with open("memory/_data/entities_index.json", "r") as f:
    data = json.load(f)

with open("memory/_data/spectrum_full_results.json", "r") as f:
    spectrum_data = json.load(f)

spec_lookup = {p["id"]: p for p in spectrum_data["products"]}

# 写入每个产品
products = data.get("products", [])
updated = 0
for p in products:
    pid = p.get("id", "")
    if pid in spec_lookup:
        spec = spec_lookup[pid]
        # 构建 spectrum 对象
        p["spectrum"] = {
            "L": spec["L"],
            "R": spec["R"],
            "hemisphere": spec["quadrant"],
            "balance": spec["balance"],
            "five_elements": {
                "土_时间轴": spec["scores"]["土"],
                "金_可行域": spec["scores"]["金"],
                "水_身心流": spec["scores"]["水"],
                "木_信义观": spec["scores"]["木"],
                "火_直觉阈": spec["scores"]["火"]
            },
            "primary_element": spec["primary_element"],
            "secondary_element": spec["secondary_element"],
            "evaluation_method": spec["evaluation_method"],
            "evaluated_at": spec["evaluated_at"],
            "needs_llm_review": spec.get("needs_llm_review", False),
            "confidence": spec.get("confidence", 0.75)
        }
        updated += 1

# 写入 meta
summary = spectrum_data["summary"]
data["meta"]["spectrum_summary"] = {
    "L_mean": summary["L_mean"],
    "R_mean": summary["R_mean"],
    "balance_score": summary["balance_score"],
    "health_status": "yellow" if abs(summary["L_mean"] - summary["R_mean"]) > 15 else "green",
    "five_elements_mean": {
        "土_时间轴": round(sum(p["scores"]["土"] for p in spectrum_data["products"]) / len(spectrum_data["products"]), 1),
        "金_可行域": round(sum(p["scores"]["金"] for p in spectrum_data["products"]) / len(spectrum_data["products"]), 1),
        "水_身心流": round(sum(p["scores"]["水"] for p in spectrum_data["products"]) / len(spectrum_data["products"]), 1),
        "木_信义观": round(sum(p["scores"]["木"] for p in spectrum_data["products"]) / len(spectrum_data["products"]), 1),
        "火_直觉阈": round(sum(p["scores"]["火"] for p in spectrum_data["products"]) / len(spectrum_data["products"]), 1)
    },
    "quadrant_distribution": summary["quadrant_distribution"],
    "last_evaluated": summary["evaluated_at"],
    "products_evaluated": updated,
    "products_pending_llm_review": summary.get("needs_llm_review_count", 0)
}

data["meta"]["updated"] = datetime.now(tz_shanghai).isoformat()

# 写入文件
with open("memory/_data/entities_index.json", "w") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"✅ 已将 {updated} 个产品的 spectrum 写入 entities_index.json")
print(f"   meta.spectrum_summary 已更新")
print(f"   健康状态: {data['meta']['spectrum_summary']['health_status']}")
print(f"   左脑均值: {data['meta']['spectrum_summary']['L_mean']}")
print(f"   右脑均值: {data['meta']['spectrum_summary']['R_mean']}")
