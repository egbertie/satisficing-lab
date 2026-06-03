#!/usr/bin/env python3
"""
每日Skill使用审计 - 自动化监控
满意妞直接执行 - 2026-03-31
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = Path("/root/.openclaw/workspace")
LOG_DIR = WORKSPACE / "logs/skill_enforcement"
AUDIT_REPORT = WORKSPACE / "reports/skill_usage_audit"

def analyze_daily_usage():
    """分析每日Skill使用情况"""
    
    # 读取执行日志
    execution_log = LOG_DIR / "execution.log"
    violation_log = LOG_DIR / "violations.log"
    blocked_log = LOG_DIR / "blocked.log"
    
    stats = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "total_checked": 0,
        "skill_invocations": 0,
        "violations": 0,
        "blocked": 0,
        "compliance_rate": 0.0,
        "top_violations": []
    }
    
    # 统计执行次数
    if execution_log.exists():
        with open(execution_log) as f:
            lines = f.readlines()
            stats["total_checked"] = len([l for l in lines if "检查任务" in l])
            stats["skill_invocations"] = len([l for l in lines if "通过Skill框架调用" in l])
    
    # 统计违规
    if violation_log.exists():
        with open(violation_log) as f:
            violations = [json.loads(line) for line in f if line.strip()]
            stats["violations"] = len(violations)
            
            # 统计最常见的违规类型
            violation_types = {}
            for v in violations:
                vtype = v.get("type", "UNKNOWN")
                violation_types[vtype] = violation_types.get(vtype, 0) + 1
            
            stats["top_violations"] = sorted(
                violation_types.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
    
    # 统计阻断次数
    if blocked_log.exists():
        with open(blocked_log) as f:
            stats["blocked"] = len([l for l in f if "BLOCKED" in l])
    
    # 计算合规率
    if stats["total_checked"] > 0:
        stats["compliance_rate"] = (
            (stats["total_checked"] - stats["violations"]) / stats["total_checked"] * 100
        )
    
    return stats

def generate_report(stats):
    """生成审计报告"""
    
    AUDIT_REPORT.mkdir(parents=True, exist_ok=True)
    
    report_file = AUDIT_REPORT / f"skill_usage_audit_{stats['date']}.md"
    
    report = f"""# Skill使用审计报告 - {stats['date']}

## 执行摘要

| 指标 | 数值 |
|------|------|
| 总检查次数 | {stats['total_checked']} |
| Skill调用次数 | {stats['skill_invocations']} |
| 违规次数 | {stats['violations']} |
| 阻断次数 | {stats['blocked']} |
| **合规率** | **{stats['compliance_rate']:.1f}%** |

## 合规率趋势

```
合规率: {'█' * int(stats['compliance_rate'] / 5)}{'░' * (20 - int(stats['compliance_rate'] / 5))} {stats['compliance_rate']:.1f}%
```

## 最常见的违规类型

"""
    
    if stats['top_violations']:
        report += "| 排名 | 违规类型 | 次数 |\n"
        report += "|------|----------|------|\n"
        for i, (vtype, count) in enumerate(stats['top_violations'], 1):
            report += f"| {i} | {vtype} | {count} |\n"
    else:
        report += "✅ 今日无违规记录\n"
    
    report += f"""

## 建议行动

"""
    
    if stats['compliance_rate'] < 80:
        report += "🔴 **合规率低于80%，需要立即整改**\n"
        report += "- 检查违规原因\n"
        report += "- 加强强制执行\n"
        report += "- 进行额外培训\n"
    elif stats['compliance_rate'] < 95:
        report += "🟡 **合规率良好，但仍有改进空间**\n"
        report += "- 继续监控\n"
        report += "- 优化执行流程\n"
    else:
        report += "🟢 **合规率优秀，保持现状**\n"
    
    report += f"""

---
*自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
    
    with open(report_file, "w") as f:
        f.write(report)
    
    return report_file

def main():
    """主函数"""
    print("=" * 60)
    print("Skill使用审计 - 每日报告")
    print("=" * 60)
    
    stats = analyze_daily_usage()
    report_file = generate_report(stats)
    
    print(f"\n审计日期: {stats['date']}")
    print(f"总检查: {stats['total_checked']}")
    print(f"Skill调用: {stats['skill_invocations']}")
    print(f"违规: {stats['violations']}")
    print(f"阻断: {stats['blocked']}")
    print(f"合规率: {stats['compliance_rate']:.1f}%")
    
    print(f"\n报告已生成: {report_file}")
    
    # 如果合规率低，发出警告
    if stats['compliance_rate'] < 80:
        print("\n🚨 警告: 合规率低于80%，需要立即整改！")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
