#!/usr/bin/env python3
"""
每日诚实审计脚本
自动检查虚报、记录偏差、生成审计报告

质量+诚实第一
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

# 审计配置
AUDIT_CONFIG = {
    "check_skills": True,      # 检查Skill完成情况
    "check_crons": True,       # 检查Cron运行状态
    "check_docs": True,        # 检查文档完整性
}

# 输出目录
OUTPUT_DIR = Path("~/.openclaw/workspace/diary/honesty-audit").expanduser()
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def audit_skills():
    """审计Skill完成情况"""
    skills_dir = Path("~/.openclaw/workspace/skills").expanduser()
    
    if not skills_dir.exists():
        return {"error": "Skill目录不存在"}
    
    skills = []
    for item in skills_dir.iterdir():
        if item.is_dir():
            skill_name = item.name
            has_doc = (item / "SKILL.md").exists()
            has_code = len(list(item.glob("*.py"))) > 0
            has_test = len(list(item.glob("test_*.py"))) > 0
            
            skills.append({
                "name": skill_name,
                "has_doc": has_doc,
                "has_code": has_code,
                "has_test": has_test,
                "completeness": sum([has_doc, has_code, has_test]) / 3,
            })
    
    return {
        "total": len(skills),
        "with_doc": sum(1 for s in skills if s["has_doc"]),
        "with_code": sum(1 for s in skills if s["has_code"]),
        "with_test": sum(1 for s in skills if s["has_test"]),
        "avg_completeness": sum(s["completeness"] for s in skills) / len(skills) if skills else 0,
        "details": skills,
    }


def generate_audit_report():
    """生成审计报告"""
    today = datetime.now().strftime("%Y-%m-%d")
    
    report = {
        "date": today,
        "timestamp": datetime.now().isoformat(),
        "skills_audit": audit_skills() if AUDIT_CONFIG["check_skills"] else None,
        "findings": [],
        "recommendations": [],
    }
    
    # 发现的问题
    if report["skills_audit"]:
        avg_comp = report["skills_audit"]["avg_completeness"]
        if avg_comp < 0.5:
            report["findings"].append(f"Skill平均完成度仅{avg_comp:.1%}，存在严重虚报风险")
        elif avg_comp < 0.8:
            report["findings"].append(f"Skill平均完成度{avg_comp:.1%}，需要加强")
    
    # 建议
    report["recommendations"].append("继续推进全量建设，确保质量")
    report["recommendations"].append("每小时检查进度，防止虚报")
    
    # 保存报告
    report_file = OUTPUT_DIR / f"audit-{today}.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    # 生成摘要
    summary_file = OUTPUT_DIR / f"audit-{today}-summary.txt"
    with open(summary_file, 'w') as f:
        f.write(f"# 诚实审计报告 - {today}\n\n")
        f.write(f"**审计时间**: {report['timestamp']}\n\n")
        
        if report["skills_audit"]:
            f.write(f"## Skill审计\n\n")
            f.write(f"- 总数: {report['skills_audit']['total']}\n")
            f.write(f"- 有文档: {report['skills_audit']['with_doc']}\n")
            f.write(f"- 有代码: {report['skills_audit']['with_code']}\n")
            f.write(f"- 有测试: {report['skills_audit']['with_test']}\n")
            f.write(f"- 平均完成度: {report['skills_audit']['avg_completeness']:.1%}\n\n")
        
        if report["findings"]:
            f.write(f"## 发现的问题\n\n")
            for finding in report["findings"]:
                f.write(f"- ⚠️ {finding}\n")
            f.write("\n")
        
        f.write(f"## 建议\n\n")
        for rec in report["recommendations"]:
            f.write(f"- 💡 {rec}\n")
    
    return report


if __name__ == "__main__":
    report = generate_audit_report()
    print(f"✅ 诚实审计完成: {report['date']}")
    if report["skills_audit"]:
        print(f"   Skill平均完成度: {report['skills_audit']['avg_completeness']:.1%}")
