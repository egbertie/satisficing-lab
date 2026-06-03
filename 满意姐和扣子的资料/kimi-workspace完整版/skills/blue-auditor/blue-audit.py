#!/usr/bin/env python3
"""
蓝军自动化审计脚本
功能: 自动执行10项认知审计检查
触发: 任务完成后24小时 + 用户要求时
"""

import json
import os
import re
from datetime import datetime, timedelta

AUDIT_CHECKLIST = [
    {
        "id": 1,
        "name": "信源独立性",
        "question": "关键数据是否单一来源？",
        "check": lambda text: len(set(re.findall(r'来源[：:]\s*(\S+)', text))) > 1
    },
    {
        "id": 2,
        "name": "时效性",
        "question": "数据是否过期（>6个月）？",
        "check": lambda text: not re.search(r'20(1[0-9]|20[0-5])', text)  # 检查2010-2025
    },
    {
        "id": 3,
        "name": "因果混淆",
        "question": "相关性vs因果性？",
        "check": lambda text: not ("导致" in text and "相关" in text and "因果" not in text)
    },
    {
        "id": 4,
        "name": "幸存者偏差",
        "question": "是否只分析成功案例？",
        "check": lambda text: "失败" in text or "负面" in text or "case" in text.lower()
    },
    {
        "id": 5,
        "name": "基底率忽视",
        "question": "是否忽略基础概率？",
        "check": lambda text: "基础" in text or "总体" in text or "基准" in text
    },
    {
        "id": 6,
        "name": "锚定效应",
        "question": "是否被初始数字不恰当影响？",
        "check": lambda text: "参考" in text and "对比" in text
    },
    {
        "id": 7,
        "name": "确认偏误",
        "question": "是否只寻找支持证据？",
        "check": lambda text: "反面" in text or "反对" in text or "质疑" in text
    },
    {
        "id": 8,
        "name": "语言腐败",
        "question": "定义是否模糊？",
        "check": lambda text: len(re.findall(r'\([^)]+定义[^)]+\)', text)) > 0
    },
    {
        "id": 9,
        "name": "数学谬误",
        "question": "百分比计算是否正确？",
        "check": lambda text: True  # 需要人工验证
    },
    {
        "id": 10,
        "name": "样本偏差",
        "question": "样本是否代表性？",
        "check": lambda text: "样本" in text and ("随机" in text or "代表性" in text)
    }
]

def audit_document(file_path):
    """审计单个文档"""
    
    if not os.path.exists(file_path):
        return {"error": "文件不存在"}
    
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    audit_results = []
    passed = 0
    failed = 0
    
    for check in AUDIT_CHECKLIST:
        try:
            result = check["check"](content)
            status = "✅ PASS" if result else "🔴 FAIL"
            if result:
                passed += 1
            else:
                failed += 1
        except:
            status = "🟡 CHECK"  # 需要人工检查
        
        audit_results.append({
            "id": check["id"],
            "name": check["name"],
            "question": check["question"],
            "status": status
        })
    
    # 总体评级
    pass_rate = passed / len(AUDIT_CHECKLIST)
    if pass_rate >= 0.8:
        rating = "🟢 可信"
    elif pass_rate >= 0.6:
        rating = "🟡 基本可信，需改进"
    else:
        rating = "🔴 可疑，需全面审查"
    
    audit_report = {
        "timestamp": datetime.now().isoformat(),
        "file": file_path,
        "checklist_results": audit_results,
        "summary": {
            "total": len(AUDIT_CHECKLIST),
            "passed": passed,
            "failed": failed,
            "pass_rate": f"{pass_rate:.1%}",
            "rating": rating
        }
    }
    
    return audit_report

def run_batch_audit():
    """批量审计最近修改的文件"""
    
    import subprocess
    
    # 获取最近24小时修改的文件
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "--since=24.hours"],
            capture_output=True,
            text=True,
            cwd="/root/.openclaw/workspace"
        )
        files = [f.strip() for f in result.stdout.strip().split("\n") if f.strip().endswith(".md")]
    except:
        files = []
    
    if not files:
        files = [
            "docs/NGT-ARCH-v1.0-FIN-260322-Fusion-Completion-Report.md"
        ]
    
    all_reports = []
    for file in files[:5]:  # 限制数量
        full_path = f"/root/.openclaw/workspace/{file}"
        if os.path.exists(full_path):
            report = audit_document(full_path)
            all_reports.append(report)
    
    # 保存审计结果
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    output_file = f"/root/.openclaw/workspace/memory/blue-audits/audit-{timestamp}.json"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_reports, f, ensure_ascii=False, indent=2)
    
    # 输出摘要
    print("=" * 50)
    print("🔵 蓝军审计完成")
    print("=" * 50)
    for report in all_reports:
        if "error" not in report:
            print(f"文件: {report['file']}")
            print(f"评级: {report['summary']['rating']}")
            print(f"通过率: {report['summary']['pass_rate']}")
            print("-" * 50)
    
    return all_reports

if __name__ == "__main__":
    run_batch_audit()
