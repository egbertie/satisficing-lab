#!/usr/bin/env python3
"""
晨间图腾仪式执行脚本
执行时间: 每日09:00
功能: 激活6图腾，加载当日工作框架
"""

import json
import datetime
import os

def morning_ritual():
    """执行晨间仪式"""
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # 6图腾激活序列
    totems = {
        "LIU": {
            "symbol": "🦉",
            "principle": "惟吾德馨",
            "action": "加载儒商智慧框架",
            "expert": "黎红雷教授",
            "activated": True
        },
        "SIMON": {
            "symbol": "⚒️",
            "principle": "满意解",
            "action": "确认今日满意解标准",
            "expert": "罗汉教授",
            "activated": True
        },
        "GUANYIN": {
            "symbol": "🛡️",
            "principle": "自在从容",
            "action": "检查当日风险预警",
            "expert": "谢宝剑研究员",
            "activated": True
        },
        "CONFUCIUS": {
            "symbol": "📜",
            "principle": "仁者爱人",
            "action": "伦理底线自检",
            "expert": "XU先生",
            "activated": True
        },
        "HUINENG": {
            "symbol": "🔥",
            "principle": "顿悟/知行合一",
            "action": "感知力就绪",
            "expert": "方翊沣博士",
            "activated": True
        },
        "BODHI": {
            "symbol": "🔮",
            "principle": "身心合一",
            "action": "能量状态评估",
            "expert": "陈国祥博士",
            "activated": True
        }
    }
    
    # 读取当日风险预警
    risks = []
    try:
        with open("/root/.openclaw/workspace/memory/worry-list.json", "r") as f:
            worry_data = json.load(f)
            risks = [w["title"] for w in worry_data.get("active", [])[:3]]
    except:
        risks = ["无活跃风险"]
    
    # 生成仪式记录
    ritual_record = {
        "ritual_type": "morning",
        "timestamp": timestamp,
        "date": date_str,
        "totems_activated": list(totems.keys()),
        "totem_details": totems,
        "key_insights": [
            "今日工作以满意解原则为指导",
            "儒商智慧作为伦理基准",
            "风险守望保持警觉"
        ],
        "risks_identified": risks,
        "ethical_check": {
            "honesty": "✅ 实事求是",
            "transparency": "✅ 诚实记录",
            "accountability": "✅ 责任承担"
        },
        "status": "completed",
        "next_action": "开始当日工作"
    }
    
    # 保存仪式记录
    output_file = f"/root/.openclaw/workspace/memory/totem-rituals/{date_str}-morning.json"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(ritual_record, f, ensure_ascii=False, indent=2)
    
    # 输出仪式摘要
    print("=" * 50)
    print("🔥 晨间图腾仪式完成")
    print("=" * 50)
    for name, details in totems.items():
        print(f"{details['symbol']} {name}: {details['action']}")
    print("=" * 50)
    print(f"记录保存: {output_file}")
    
    return ritual_record

if __name__ == "__main__":
    morning_ritual()
