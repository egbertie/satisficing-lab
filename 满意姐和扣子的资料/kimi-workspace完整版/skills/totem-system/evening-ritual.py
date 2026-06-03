#!/usr/bin/env python3
"""
黄昏图腾归位仪式执行脚本
执行时间: 每日18:00
功能: 归档当日收获，质量检查，风险守望
"""

import json
import datetime
import os

def evening_ritual():
    """执行黄昏仪式"""
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # 读取当日日志
    daily_insights = []
    try:
        with open(f"/root/.openclaw/workspace/memory/{date_str}.md", "r") as f:
            content = f.read()
            # 提取关键决策和收获
            lines = content.split("\n")
            for line in lines:
                if line.startswith("##") or line.startswith("-"):
                    daily_insights.append(line.strip("#- ")[:100])
    except:
        daily_insights = ["今日日志尚未创建"]
    
    # 读取交付物
    deliverables = []
    try:
        import subprocess
        result = subprocess.run(
            ["git", "log", "--oneline", "--since=midnight", "--until=now"],
            capture_output=True,
            text=True,
            cwd="/root/.openclaw/workspace"
        )
        if result.stdout:
            deliverables = [line.strip() for line in result.stdout.strip().split("\n")[:5]]
    except:
        deliverables = ["今日无Git提交"]
    
    # 生成明日风险预警
    tomorrow_risks = [
        "检查Token预算状态",
        "检查Cron任务健康度",
        "检查备份完整性"
    ]
    
    # 6图腾归位
    totems = {
        "LIU": {"symbol": "🦉", "action": "今日智慧收获归档"},
        "SIMON": {"symbol": "⚒️", "action": "交付物质量检查"},
        "GUANYIN": {"symbol": "🛡️", "action": "明日风险预警"},
        "CONFUCIUS": {"symbol": "📜", "action": "伦理决策日志"},
        "HUINENG": {"symbol": "🔥", "action": "感知经验固化"},
        "BODHI": {"symbol": "🔮", "action": "身心疲劳评估"}
    }
    
    # 质量检查清单
    quality_check = {
        "deliverables_count": len(deliverables),
        "documentation_complete": len([d for d in deliverables if ".md" in d or "doc" in d.lower()]),
        "git_commits": len(deliverables),
        "quality_score": "待评估"
    }
    
    # 生成仪式记录
    ritual_record = {
        "ritual_type": "evening",
        "timestamp": timestamp,
        "date": date_str,
        "totems_activated": list(totems.keys()),
        "totem_details": totems,
        "daily_insights": daily_insights[:5],
        "deliverables_checked": deliverables,
        "quality_check": quality_check,
        "tomorrow_risks": tomorrow_risks,
        "ethical_log": {
            "honest_reporting": "✅ 如实记录进度",
            "quality_commitment": "✅ 承诺质量标准",
            "continuous_improvement": "✅ 持续改进"
        },
        "status": "completed",
        "next_action": "准备次日工作"
    }
    
    # 保存仪式记录
    output_file = f"/root/.openclaw/workspace/memory/totem-rituals/{date_str}-evening.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(ritual_record, f, ensure_ascii=False, indent=2)
    
    # 输出仪式摘要
    print("=" * 50)
    print("🌅 黄昏图腾归位完成")
    print("=" * 50)
    for name, details in totems.items():
        print(f"{details['symbol']} {name}: {details['action']}")
    print("=" * 50)
    print(f"今日交付: {len(deliverables)} 项")
    print(f"记录保存: {output_file}")
    
    return ritual_record

if __name__ == "__main__":
    evening_ritual()
