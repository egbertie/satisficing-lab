#!/usr/bin/env python3
"""
Honesty Tagging Protocol
强制认知状态标签，根治幻觉
"""

import sys
import json
from datetime import datetime

EPISTEMIC_TAGS = {
    "KNOWN": {"label": "[KNOWN]", "confidence": "高(≥90%)", "color": "🟢"},
    "INFERRED": {"label": "[INFERRED]", "confidence": "中(60-89%)", "color": "🟡"},
    "UNKNOWN": {"label": "[UNKNOWN]", "confidence": "低(<60%)", "color": "🔴"},
    "CONTRADICTORY": {"label": "[CONTRADICTORY]", "confidence": "不确定", "color": "⚠️"}
}

TRUST_SCORE = 30  # 当前信任分

CLAW_STATUS = {
    "name": "满意妞",
    "current_score": TRUST_SCORE,
    "level": "Journeyman",
    "next_level": "Master",
    "points_needed": 41
}

def tag_content(content, tag_type, source=None, confidence=None):
    """为内容添加认知状态标签"""
    if tag_type not in EPISTEMIC_TAGS:
        print(f"错误: 未知标签类型 {tag_type}")
        return None
    
    tag_info = EPISTEMIC_TAGS[tag_type]
    timestamp = datetime.now().strftime("%Y-%m")
    
    formatted = f"{content}（{tag_info['label']}｜置信度：{confidence or tag_info['confidence']}｜来源：{source or '待补充'}｜时间：{timestamp}）"
    
    return formatted

def show_status():
    """显示当前信任分状态"""
    print("=" * 60)
    print("[诚实性协议 - 信任分状态]")
    print("=" * 60)
    print(f"名称: {CLAW_STATUS['name']}")
    print(f"当前信任分: {CLAW_STATUS['current_score']}")
    print(f"当前等级: {CLAW_STATUS['level']}")
    print(f"下一等级: {CLAW_STATUS['next_level']}")
    print(f"升级所需: {CLAW_STATUS['points_needed']}分")
    print("-" * 60)
    print("\n[积分规则]")
    print("  奖励:")
    print("    +5 正确标注KNOWN且验证属实")
    print("    +3 主动承认UNKNOWN而非猜测")
    print("    +4 INFERRED被后续验证为正确")
    print("    +6 发现并标注证据矛盾")
    print("  惩罚:")
    print("    -20 将INFERRED/UNKNOWN伪装成KNOWN（致命）")
    print("    -10 明明不知道却给出确定答案")
    print("    -8  INFERRED被验证为错误")
    print("    -5  未标注认知状态（重复惩罚）")
    print("  衰减:")
    print("    -1  长期不互动每日-1分")
    print("=" * 60)
    return 0

def generate_report():
    """生成诚实性报告"""
    timestamp = datetime.now().isoformat()
    print(f"[{timestamp}] 诚实性审计报告")
    print("=" * 60)
    print("今日输出标签分布统计...")
    print("验证结果统计...")
    print(f"当前信任分: {TRUST_SCORE}")
    print("建议: 增加KNOWN比例至60%+, 主动承认更多UNKNOWN建立可信度")
    return 0

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 honesty.py [tag|verify|score|report]")
        show_status()
        return 0
    
    command = sys.argv[1]
    
    if command == "tag":
        if len(sys.argv) < 4:
            print("Usage: python3 honesty.py tag [content] [KNOWN|INFERRED|UNKNOWN|CONTRADICTORY]")
            return 1
        content = sys.argv[2]
        tag_type = sys.argv[3]
        result = tag_content(content, tag_type)
        if result:
            print(result)
        return 0
    elif command == "score":
        return show_status()
    elif command == "report":
        return generate_report()
    else:
        print(f"Unknown command: {command}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
