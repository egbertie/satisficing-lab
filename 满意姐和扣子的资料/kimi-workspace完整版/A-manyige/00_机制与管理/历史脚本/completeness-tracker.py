#!/usr/bin/env python3
"""
5标准完成度实时追踪器
版本: V2.0
"""

import os
import json
from pathlib import Path
from datetime import datetime

def check_skill_completeness(skill_path):
    """检查单个Skill的5标准完成度"""
    skill_path = Path(skill_path)
    name = skill_path.name
    
    checks = {
        "has_skill_md": False,
        "has_scripts": False,
        "has_cron": False,
        "script_count": 0
    }
    
    # 检查SKILL.md
    if (skill_path / "SKILL.md").exists():
        checks["has_skill_md"] = True
    
    # 检查脚本
    scripts_dir = skill_path / "scripts"
    if scripts_dir.exists():
        scripts = list(scripts_dir.glob("*.py")) + list(scripts_dir.glob("*.sh"))
        checks["has_scripts"] = len(scripts) > 0
        checks["script_count"] = len(scripts)
    
    # 检查Cron配置
    if (skill_path / "cron.json").exists() or (skill_path / "cron-config.sh").exists():
        checks["has_cron"] = True
    
    # 计算完成度
    if checks["has_skill_md"] and checks["has_scripts"] and checks["has_cron"]:
        completeness = 100
    elif checks["has_skill_md"] and checks["has_scripts"]:
        completeness = 80  # 有文档+脚本
    elif checks["has_skill_md"]:
        completeness = 40  # 只有文档
    else:
        completeness = 0
    
    return {
        "name": name,
        "completeness": completeness,
        **checks
    }

def scan_all_skills():
    """扫描所有Skill"""
    skills_dir = Path("/root/.openclaw/workspace/skills")
    results = []
    
    for skill_dir in skills_dir.iterdir():
        if skill_dir.is_dir() and not skill_dir.name.startswith("."):
            result = check_skill_completeness(skill_dir)
            results.append(result)
    
    return results

def generate_report(results):
    """生成报告"""
    total = len(results)
    complete = len([r for r in results if r["completeness"] == 100])
    partial = len([r for r in results if 0 < r["completeness"] < 100])
    none_complete = len([r for r in results if r["completeness"] == 0])
    
    avg_completeness = sum(r["completeness"] for r in results) / total if total > 0 else 0
    
    report = f"""
=== 5标准完成度实时追踪 ===
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

总体统计:
- Skill总数: {total}
- 100%完成: {complete} ({complete/total*100:.1f}%)
- 部分完成: {partial} ({partial/total*100:.1f}%)
- 未开始: {none_complete} ({none_complete/total*100:.1f}%)
- 平均完成度: {avg_completeness:.1f}%

完成度分布:
"""
    
    for r in sorted(results, key=lambda x: x["completeness"], reverse=True):
        status = "✅" if r["completeness"] == 100 else "🟡" if r["completeness"] > 0 else "❌"
        report += f"{status} {r['name']}: {r['completeness']}% (脚本:{r['script_count']})\n"
    
    return report

def main():
    results = scan_all_skills()
    report = generate_report(results)
    print(report)
    
    # 保存报告
    report_path = Path("/root/.openclaw/workspace/docs/COMPLETENESS_TRACKER_LATEST.md")
    report_path.write_text(report, encoding='utf-8')
    print(f"\n报告已保存: {report_path}")
    
    return 0

if __name__ == "__main__":
    exit(main())