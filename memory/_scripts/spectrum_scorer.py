#!/usr/bin/env python3
"""产品双光谱批量评分脚本
Phase 2b: 基于规则的自动化初评 + 优先级标记
使用方法: python3 memory/_scripts/spectrum_scorer.py
"""

import json
import sys
from datetime import datetime, timezone, timedelta

tz_shanghai = timezone(timedelta(hours=8))

# ==================== 评分规则映射表 ====================

# product_type → 五维初始评分
PRODUCT_TYPE_SCORES = {
    "diagnostic_tool":     {"土":45, "金":78, "水":25, "木":30, "火":25},
    "quantitative_tool":   {"土":40, "金":82, "水":12, "木":25, "火":15},
    "simulation_game":     {"土":45, "金":30, "水":68, "木":42, "火":72},
    "simple_tool":         {"土":35, "金":55, "水":30, "木":35, "火":40},
    "infrastructure":      {"土":50, "金":65, "水":15, "木":20, "火":20},
    "knowledge_page":      {"土":62, "金":28, "水":22, "木":48, "火":30},
    "":                    {"土":40, "金":40, "水":40, "木":40, "火":40},
}

# jtbd_category → 五维调整（与 product_type 叠加取均值）
JTBD_ADJUST = {
    "diagnose":  {"土":0, "金":+5, "水":+5, "木":0, "火":0},
    "decide":    {"土":+10, "金":+10, "水":0, "木":+15, "火":+5},
    "grow":      {"土":+15, "金":-5, "水":+5, "木":+5, "火":+15},
    "knowledge": {"土":+20, "金":-10, "水":-5, "木":+10, "火":0},
    "":           {"土":0, "金":0, "水":0, "木":0, "火":0},
}

# tags → 五维微调
TAG_ADJUST = {
    "测评":    {"金":+5},
    "诊断":    {"金":+5},
    "分析":    {"金":+5},
    "数据":    {"金":+5},
    "KPI":     {"金":+5},
    "量化":    {"金":+5},
    "模型":    {"金":+5},
    "统计":    {"金":+5},
    "指标":    {"金":+5},
    "报告":    {"金":+3, "土":+3},
    "雷达图":  {"金":+5},
    "可视化":  {"金":+3, "火":+3},
    "清单":    {"金":+5},
    "自检":    {"金":+5},
    "质量":    {"金":+5},
    "系统":    {"金":+3, "土":+3},
    "架构":    {"金":+3, "土":+3},
    "自动化":  {"金":+3},
    "引擎":    {"金":+3},
    "流程":    {"金":+3, "土":+3},
    "导航":    {"金":+3},
    "目录":    {"金":+3},
    "搜索":    {"金":+3},
    "筛选":    {"金":+3},

    "创意":    {"火":+8},
    "设计":    {"火":+8},
    "灵感":    {"火":+8},
    "故事":    {"火":+8, "水":+5},
    "叙事":    {"火":+8, "水":+5},
    "体验":    {"火":+5, "水":+5},
    "角色扮演":{"火":+10, "水":+8},
    "场景模拟":{"火":+10, "水":+8},
    "模拟":    {"火":+8, "水":+5},
    "游戏":    {"火":+10, "水":+5},
    "卡牌":    {"火":+8},
    "对局":    {"火":+5, "水":+5},
    "危机":    {"水":+10, "火":+5},
    "压力":    {"水":+10},
    "品牌":    {"火":+5},
    "首页":    {"火":+3},
    "入口":    {"火":+3},
    "突破":    {"火":+8},
    "顿悟":    {"火":+10},

    "身体":    {"水":+10},
    "觉察":    {"水":+10},
    "直觉":    {"火":+8, "水":+8},
    "感受":    {"水":+10},
    "情绪":    {"水":+10},
    "身心":    {"水":+10},
    "PRE-0":   {"水":+10},
    "健康":    {"水":+8},
    "关系":    {"水":+8, "木":+5},
    "温度计":  {"水":+5},
    "合伙人":  {"木":+10, "水":+5},
    "合作":    {"木":+5, "水":+5},

    "长期":    {"土":+10},
    "历史":    {"土":+10},
    "复盘":    {"土":+10},
    "沉淀":    {"土":+10},
    "传承":    {"土":+10},
    "时间":    {"土":+8},
    "里程碑":  {"土":+8},
    "日历":    {"土":+5},
    "案例":    {"土":+5},
    "教训":    {"土":+5},

    "承诺":    {"木":+10},
    "原则":    {"木":+10},
    "道德":    {"木":+10},
    "合规":    {"木":+8},
    "契约":    {"木":+10},
    "责任":    {"木":+8},
    "治理":    {"木":+8},
    "章程":    {"木":+10},
    "协议":    {"木":+8},
    "规则":    {"木":+5},
    "诚信":    {"木":+10},
    "信义":    {"木":+10},

    "决策":    {"金":+5, "木":+5},
    "选择":    {"金":+5},
    "选项":    {"金":+5},
    "权衡":    {"金":+5},
    "方案":    {"金":+5},
    "满意解":  {"金":+8},
    "五维":    {"金":+3},
}

def clamp(v, lo=0, hi=100):
    return max(lo, min(hi, round(v)))

def score_product(p):
    """为单个产品计算五维+左右脑评分"""
    pt = p.get("product_type", "")
    jtbd = p.get("jtbd_category", "")
    tags = p.get("tags", [])
    
    # 1. 基于 product_type 的基础分
    base = PRODUCT_TYPE_SCORES.get(pt, PRODUCT_TYPE_SCORES[""])
    scores = dict(base)
    
    # 2. JTBD 调整
    j_adj = JTBD_ADJUST.get(jtbd, JTBD_ADJUST[""])
    for dim in scores:
        scores[dim] += j_adj.get(dim, 0)
    
    # 3. Tags 微调
    for tag in tags:
        t_adj = TAG_ADJUST.get(tag, {})
        for dim, adj in t_adj.items():
            scores[dim] = scores.get(dim, 40) + adj
    
    # clamp to 0-100
    for dim in scores:
        scores[dim] = clamp(scores[dim])
    
    # 4. 计算 L/R
    L = round((scores["土"] + scores["金"]) / 2, 1)
    R = round((scores["水"] + scores["火"]) / 2, 1)
    balance = round(1 - abs(L - R) / 100, 2)
    
    # 5. 象限判断
    if L >= 50 and R >= 50:
        quadrant = "Ⅰ·全脑型"
    elif L < 50 and R >= 50:
        quadrant = "Ⅱ·体验型"
    elif L < 50 and R < 50:
        quadrant = "Ⅲ·真空型"
    else:
        quadrant = "Ⅳ·分析型"
    
    # 6. 主次元素
    dims_sorted = sorted(scores.items(), key=lambda x: -x[1])
    primary_elem = dims_sorted[0][0]
    secondary_elem = dims_sorted[1][0]
    
    return {
        "scores": scores,
        "L": L,
        "R": R,
        "balance": balance,
        "quadrant": quadrant,
        "primary_element": primary_elem,
        "secondary_element": secondary_elem,
        "evaluation_method": "rule_based_v1",
        "evaluated_at": datetime.now(tz_shanghai).isoformat(),
        "needs_llm_review": False,
        "confidence": 0.75
    }

def main():
    with open("memory/_data/entities_index.json", "r") as f:
        data = json.load(f)

    products = data.get("products", [])
    results = []
    needs_review = []
    
    for p in products:
        spec = score_product(p)
        spec["id"] = p.get("id", "")
        spec["name"] = p.get("name", "")
        
        # 标记需要LLM精评的场景
        if not p.get("product_type"):
            spec["needs_llm_review"] = True
            needs_review.append(spec["id"])
        elif spec["quadrant"] == "Ⅲ·真空型":
            spec["needs_llm_review"] = True
            needs_review.append(spec["id"])
        
        results.append(spec)
    
    # 统计
    quads = {}
    for r in results:
        q = r["quadrant"]
        quads[q] = quads.get(q, 0) + 1
    
    Ls = [r["L"] for r in results]
    Rs = [r["R"] for r in results]
    
    summary = {
        "total_products": len(results),
        "L_mean": round(sum(Ls)/len(Ls), 1),
        "R_mean": round(sum(Rs)/len(Rs), 1),
        "balance_score": round(1 - abs(sum(Ls)/len(Ls) - sum(Rs)/len(Rs))/100, 2),
        "quadrant_distribution": quads,
        "needs_llm_review_count": len(needs_review),
        "needs_llm_review_ids": needs_review,
        "evaluated_at": datetime.now(tz_shanghai).isoformat(),
        "evaluation_method": "rule_based_v1"
    }
    
    # 保存完整结果
    output = {
        "summary": summary,
        "products": results
    }
    
    with open("memory/_data/spectrum_full_results.json", "w") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 已完成 {len(results)} 个产品的评分")
    print(f"   左脑均值: {summary['L_mean']} | 右脑均值: {summary['R_mean']} | 平衡度: {summary['balance_score']}")
    print(f"   象限分布: {quads}")
    print(f"   需要LLM精评: {len(needs_review)} 个产品")
    print(f"   结果已保存: memory/_data/spectrum_full_results.json")

if __name__ == "__main__":
    main()
