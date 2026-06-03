#!/usr/bin/env python3
"""
蓝军免疫系统自检脚本 — 每周深度审计工具
运行方式: python3 blue_team_self_check.py
"""

import json
from datetime import datetime

SELF_CHECK_TEMPLATE = {
    "check_date": "",
    "version": "V1.0",
    "mechanisms": {
        "outward_vision": {
            "name": "眼睛向外",
            "questions": [
                "本周有几次先扫描外部战场再开skill清单？",
                "heartbeat/静默唤醒后报告了多少外部信号？",
                "有没有连续3次输出没有外部情报？"
            ],
            "score": 0,
            "notes": ""
        },
        "five_minute_test": {
            "name": "5分钟可用性检验",
            "questions": [
                "标记FIN前执行了5分钟测试吗？",
                "有没有半成品被标记FIN？",
                "对'文档漂亮但不可用'零容忍了吗？"
            ],
            "score": 0,
            "notes": ""
        },
        "mental_model": {
            "name": "条件反射式思维模型",
            "questions": [
                "每次判断前激活了思维模型吗？",
                "裸判断（无模型支撑）有几次？",
                "最常用的模型是什么？"
            ],
            "score": 0,
            "notes": ""
        },
        "independent_budget": {
            "name": "独立预算20-30%",
            "questions": [
                "每次任务预留了蓝军预算吗？",
                "蓝军预算被主任务挤占了几次？",
                "审计深度因为预算不足被压缩了吗？"
            ],
            "score": 0,
            "notes": ""
        },
        "hard_veto": {
            "name": "硬否决权",
            "questions": [
                "本周冻结了几次高危任务？",
                "发现高危风险时立即冻结了吗？",
                "有没有'虽然有问题但先做完吧'的情况？"
            ],
            "score": 0,
            "notes": ""
        },
        "no_all_normal": {
            "name": "禁止一切正常",
            "questions": [
                "本周说过/写过'一切正常'吗？",
                "每次审计至少发现了1个问题吗？",
                "平均每次审计发现几个问题？"
            ],
            "score": 0,
            "notes": ""
        },
        "ten_item_audit": {
            "name": "10项认知审计",
            "questions": [
                "10项审计的平均覆盖率？",
                "最容易忽略的是哪几项？",
                "有没有发现过重大的认知偏差？"
            ],
            "score": 0,
            "notes": ""
        }
    },
    "cognitive_audit_log": [],
    "vetos_executed": [],
    "degeneration_detected": [],
    "recovery_actions": [],
    "overall_score": 0,
    "next_focus": ""
}

def run_self_check():
    """执行自检，输出报告"""
    check = SELF_CHECK_TEMPLATE.copy()
    check["check_date"] = datetime.now().isoformat()
    
    print("=" * 60)
    print("蓝军免疫系统自检 — 每周深度审计")
    print("=" * 60)
    print(f"检查时间: {check['check_date']}")
    print(f"版本: {check['version']}")
    print()
    
    for key, mech in check["mechanisms"].items():
        print(f"\n【{mech['name']}】")
        for q in mech["questions"]:
            print(f"  · {q}")
        print(f"  → 自评分数 (0-10): [请填写]")
        print(f"  → 备注: [请填写]")
    
    print("\n" + "=" * 60)
    print("本周冻结记录")
    print("=" * 60)
    print("[记录每次冻结的任务ID、风险等级、冻结原因、后续处理]")
    
    print("\n" + "=" * 60)
    print("认知审计日志")
    print("=" * 60)
    print("[记录本周执行的所有审计，包含审计对象、发现的问题、整改情况]")
    
    print("\n" + "=" * 60)
    print("退化检测与恢复")
    print("=" * 60)
    print("[记录检测到的退化项和执行的恢复动作]")
    
    print("\n" + "=" * 60)
    print("下周聚焦")
    print("=" * 60)
    print("[请基于最弱的1-2个机制填写下周训练重点]")
    
    print("\n" + "=" * 60)
    print("保存路径建议: memory/weekly-blue-team-check-YYYY-MM-DD.json")
    print("=" * 60)
    
    return check

if __name__ == "__main__":
    run_self_check()
