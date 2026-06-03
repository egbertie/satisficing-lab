#!/usr/bin/env python3
"""
FIN状态诚实审计脚本
每日检查声称FIN的系统是否真实有代码
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime

WORKSPACE = Path("/root/.openclaw/workspace")
SKILLS_DIR = WORKSPACE / "skills"
REPORT_DIR = WORKSPACE / "diary" / "honesty-audit"

def audit_fin_honesty():
    """审计FIN状态诚实性"""
    issues = []
    total_checked = 0
    
    for skill_dir in SKILLS_DIR.iterdir():
        if not skill_dir.is_dir():
            continue
        
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue
        
        content = skill_md.read_text()
        
        # 检查是否声称FIN
        claims_fin = "FIN" in content and ("状态.*FIN" in content or "status.*FIN" in content.lower() or "FIN (已完成)" in content)
        
        if claims_fin:
            total_checked += 1
            py_files = list(skill_dir.glob("*.py"))
            py_files = [f for f in py_files if "test" not in f.name.lower() or f.name == f"{skill_dir.name.replace('-', '_')}.py"]
            
            if not py_files:
                issues.append({
                    "skill": skill_dir.name,
                    "issue": "声称FIN但无Python实现代码",
                    "severity": "high"
                })
            else:
                # 检查是否有--test支持（主文件或test_runner.py）
                main_file = skill_dir / f"{skill_dir.name.replace('-', '_')}.py"
                test_runner = skill_dir / "test_runner.py"
                
                has_test = False
                if main_file.exists():
                    content_py = main_file.read_text()
                    has_test = "--test" in content_py
                if test_runner.exists():
                    has_test = True  # test_runner.py存在即认为有测试支持
                
                if not has_test:
                    issues.append({
                        "skill": skill_dir.name,
                        "issue": "有代码但无--test参数",
                        "severity": "medium"
                    })
    
    return {
        "total_checked": total_checked,
        "issues": issues,
        "pass_rate": (total_checked - len(issues)) / total_checked * 100 if total_checked > 0 else 0
    }

def generate_report(audit_result):
    """生成审计报告"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    report = f"""# FIN状态诚实审计报告

**审计时间**: {now}
**审计范围**: 所有声称FIN的系统

## 统计摘要

| 指标 | 数值 |
|------|------|
| 检查系统数 | {audit_result['total_checked']} |
| 发现问题数 | {len(audit_result['issues'])} |
| 通过率 | {audit_result['pass_rate']:.1f}% |

## 问题清单

"""
    
    if audit_result["issues"]:
        report += "| 系统名称 | 问题 | 严重程度 |\\n"
        report += "|----------|------|----------|\\n"
        for issue in audit_result["issues"]:
            severity_emoji = "🔴" if issue["severity"] == "high" else "⚠️"
            report += f"| {issue['skill']} | {issue['issue']} | {severity_emoji} {issue['severity']} |\\n"
    else:
        report += "✅ **所有FIN系统均通过诚实性验证**\\n"
    
    report += f"""
## 纠正要求

对于标记为 🔴 high 的问题：
1. 立即撤销FIN标记，改为WIP
2. 在24小时内补充实现代码
3. 通过蓝军验证后恢复FIN标记

## 历史趋势

查看历史审计报告：
- `diary/honesty-audit/` 目录

---
*本报告由FIN状态诚实审计脚本自动生成*
*执行命令: python3 scripts/fin_honesty_audit.py*
"""
    
    return report

def main():
    print("="*60)
    print("🔍 FIN状态诚实审计")
    print("="*60)
    
    result = audit_fin_honesty()
    
    print(f"\n📊 检查系统数: {result['total_checked']}")
    print(f"📊 通过率: {result['pass_rate']:.1f}%")
    
    if result["issues"]:
        print(f"\n🔴 发现 {len(result['issues'])} 个问题:")
        for issue in result["issues"]:
            print(f"   - {issue['skill']}: {issue['issue']}")
    else:
        print("\n✅ 所有FIN系统均通过诚实性验证")
    
    # 生成报告
    report = generate_report(result)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report_file = REPORT_DIR / f"{datetime.now().strftime('%Y-%m-%d')}.md"
    report_file.write_text(report)
    
    print(f"\n📄 报告已保存: {report_file}")
    print("="*60)
    
    # 如果有问题，返回非0状态码
    return 1 if result["issues"] else 0

if __name__ == "__main__":
    sys.exit(main())
