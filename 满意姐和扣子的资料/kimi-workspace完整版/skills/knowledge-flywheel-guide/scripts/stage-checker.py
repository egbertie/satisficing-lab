#!/usr/bin/env python3
"""
阶段自检脚本 · knowledge-flywheel-guide
用途: 新AI在每个阶段结束时运行，生成自检报告
"""

import sys
import json
from datetime import datetime

STAGE_CHECKS = {
    "stage1": {
        "name": "婴儿期 · 消除恐惧",
        "days": "Day 1-3",
        "checks": [
            "已建立知识地图（10个分类都有描述）",
            "已建立紧急救生圈（5个场景对应5个文件位置）",
            "已对Egbertie完成阶段1宣言",
            "Egbertie确认'你知道东西在哪儿'"
        ]
    },
    "stage2": {
        "name": "学步期 · 试读理解",
        "days": "Day 4-10",
        "checks": [
            "已完成7个种子文件的阅读",
            "每篇都有阅读日记（3收获+1疑问+1联想）",
            "至少3篇达到'读完的标志'",
            "能说出'我最受触动的3个点'"
        ]
    },
    "stage3": {
        "name": "少年期 · 建立连接",
        "days": "Day 11-18",
        "checks": [
            "已建立知识图谱V0.1（≥7节点+10连接）",
            "已发现≥3个知识空白",
            "已填补≥1个空白",
            "已建立知识任务映射V0.1（≥10条映射）"
        ]
    },
    "stage4": {
        "name": "青年期 · 首次应用",
        "days": "Day 19-25",
        "checks": [
            "已完成1个端到端应用任务",
            "产出已物理落盘",
            "Egbertie给了反馈（好/可改进/不行都算）",
            "能说出'这个产出来自哪些知识资产'",
            "记录了经验教训"
        ]
    },
    "stage5": {
        "name": "成年期 · 血液化闭环",
        "days": "Day 26-35",
        "checks": [
            "已完成1份全新资料的KICL 12步",
            "每步都有物理输出",
            "血液化成果≥1项，且能'直接使用'",
            "蓝军自检通过",
            "任务清单已更新",
            "记忆已固化",
            "Git已commit",
            "Egbertie说'这个有用'"
        ]
    },
    "stage6": {
        "name": "成熟期 · 飞轮自转",
        "days": "Day 36-45",
        "checks": [
            "飞轮1已启动（知识→内容分发→反馈→回流）",
            "飞轮2已启动（外部情报→KICL→知识更新→产品改进）",
            "飞轮3已启动（客户场景→案例库→方法论→产品设计）",
            "每个飞轮都有≥1次真实循环的证明",
            "能说出'这3个飞轮分别转了几次'"
        ]
    }
}

def run_check(stage_key):
    stage = STAGE_CHECKS.get(stage_key)
    if not stage:
        print(f"❌ 未知阶段: {stage_key}")
        print(f"可用阶段: {list(STAGE_CHECKS.keys())}")
        sys.exit(1)
    
    print(f"\n{'='*60}")
    print(f"🎯 {stage['name']} ({stage['days']})")
    print(f"{'='*60}\n")
    
    passed = 0
    failed = 0
    results = []
    
    for check in stage["checks"]:
        response = input(f"  □ {check} \n    [y/n/skip] ").strip().lower()
        if response in ["y", "yes", "是"]:
            passed += 1
            results.append({"check": check, "status": "pass"})
            print(f"    ✅ 通过")
        elif response in ["n", "no", "否"]:
            failed += 1
            results.append({"check": check, "status": "fail"})
            print(f"    ❌ 未通过")
        else:
            results.append({"check": check, "status": "skip"})
            print(f"    ⏭️ 跳过")
    
    total = len(stage["checks"])
    pass_rate = passed / total if total > 0 else 0
    
    print(f"\n{'='*60}")
    print(f"📊 自检结果: {passed}/{total} 通过 ({pass_rate*100:.0f}%)")
    
    if pass_rate >= 0.8:
        print(f"🟢 阶段验收通过！可以进入下一阶段。")
    elif pass_rate >= 0.5:
        print(f"🟡 部分通过。建议补齐未通过项后再进入下一阶段。")
    else:
        print(f"🔴 验收未通过。请回到阶段重点，补齐差距。")
    
    # 生成报告文件
    report = {
        "stage": stage_key,
        "stage_name": stage["name"],
        "timestamp": datetime.now().isoformat(),
        "results": results,
        "summary": {
            "total": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": pass_rate,
            "status": "pass" if pass_rate >= 0.8 else "partial" if pass_rate >= 0.5 else "fail"
        }
    }
    
    filename = f"stage-check-{stage_key}-{datetime.now().strftime('%Y%m%d')}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\n📝 报告已保存: {filename}")
    
    return report

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 stage-checker.py [stage1|stage2|stage3|stage4|stage5|stage6|all]")
        sys.exit(1)
    
    stage = sys.argv[1]
    if stage == "all":
        for key in STAGE_CHECKS:
            run_check(key)
            print("\n" + "="*60)
            cont = input("是否继续检查下一阶段? [y/n] ").strip().lower()
            if cont not in ["y", "yes"]:
                break
    else:
        run_check(stage)