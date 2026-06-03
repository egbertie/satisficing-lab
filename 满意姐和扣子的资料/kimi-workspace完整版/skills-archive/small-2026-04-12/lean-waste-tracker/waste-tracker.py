#!/usr/bin/env python3
"""
7浪费追踪自动化脚本
功能: 自动分析对话/输出，分类统计7种浪费
触发: 每轮对话后 + 每日汇总
"""

import json
import re
import os
from datetime import datetime

WASTE_TYPES = {
    "Overproduction": {
        "name": "过度生产",
        "description": "生成用户未要求的细节",
        "indicators": ["顺便", "额外", "还有", "补充说明"],
        "threshold": 0.15
    },
    "Waiting": {
        "name": "等待浪费",
        "description": "思考不相关内容",
        "indicators": ["从基础开始", "让我们先理解", "首先介绍"],
        "threshold": 0.30
    },
    "Transportation": {
        "name": "运输浪费",
        "description": "格式来回转换",
        "indicators": ["```", "---", "===", "|"],
        "threshold": 0.10
    },
    "OverProcessing": {
        "name": "过度处理",
        "description": "简单问题复杂推理",
        "indicators": ["复杂分析", "详细推导", "多维度评估"],
        "threshold": 0.20
    },
    "Inventory": {
        "name": "库存浪费",
        "description": "上下文堆积",
        "indicators": ["正如之前", "回顾", "参考第"],
        "threshold": 0.10
    },
    "Motion": {
        "name": "动作浪费",
        "description": "礼貌用语、装饰性格式",
        "indicators": ["好的", "没问题", "很高兴", "请允许我"],
        "threshold": 0.05
    },
    "Defects": {
        "name": "缺陷浪费",
        "description": "幻觉导致返工",
        "indicators": ["根据文件", "数据显示", "统计表明"],
        "threshold": 0.01
    }
}

def analyze_waste(text, context=""):
    """分析文本中的浪费类型"""
    
    total_chars = len(text)
    if total_chars == 0:
        return {}
    
    waste_analysis = {}
    
    for waste_key, waste_config in WASTE_TYPES.items():
        matches = 0
        for indicator in waste_config["indicators"]:
            matches += len(re.findall(indicator, text, re.IGNORECASE))
        
        # 计算浪费比例
        waste_ratio = min(matches * len(waste_config["indicators"][0]) / total_chars * 10, 1.0)
        
        waste_analysis[waste_key] = {
            "name": waste_config["name"],
            "matches": matches,
            "ratio": waste_ratio,
            "threshold": waste_config["threshold"],
            "exceeded": waste_ratio > waste_config["threshold"],
            "description": waste_config["description"]
        }
    
    return waste_analysis

def generate_daily_report():
    """生成每日浪费追踪报告"""
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    # 读取当日日志（如果存在）
    log_file = f"/root/.openclaw/workspace/memory/{date_str}.md"
    text_content = ""
    if os.path.exists(log_file):
        with open(log_file, "r", encoding="utf-8") as f:
            text_content = f.read()
    
    # 分析浪费
    analysis = analyze_waste(text_content)
    
    # 计算总体效率
    total_waste = sum(a["ratio"] for a in analysis.values()) / len(analysis) if analysis else 0
    efficiency = max(0, 1 - total_waste)
    
    report = {
        "date": date_str,
        "timestamp": datetime.now().isoformat(),
        "efficiency": round(efficiency * 100, 2),
        "total_waste_percent": round(total_waste * 100, 2),
        "waste_breakdown": analysis,
        "recommendations": []
    }
    
    # 生成建议
    for waste_key, data in analysis.items():
        if data["exceeded"]:
            report["recommendations"].append({
                "waste_type": waste_key,
                "current_ratio": data["ratio"],
                "target": data["threshold"],
                "action": f"降低{data['name']}"
            })
    
    # 保存报告
    report_file = f"/root/.openclaw/workspace/memory/waste-reports/{date_str}.json"
    os.makedirs(os.path.dirname(report_file), exist_ok=True)
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    # 输出摘要
    print(f"[WASTE-TRACKER] {date_str} 效率: {report['efficiency']}%")
    for waste_key, data in analysis.items():
        status = "🔴" if data["exceeded"] else "🟢"
        print(f"  {status} {data['name']}: {data['ratio']:.1%} (目标: {data['threshold']:.1%})")
    
    return report

if __name__ == "__main__":
    generate_daily_report()
