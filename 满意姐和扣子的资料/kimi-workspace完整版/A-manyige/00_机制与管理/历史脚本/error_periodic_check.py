#!/usr/bin/env python3
"""
错误记录周期检查脚本
每日执行，防止错误复发
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta

WORKSPACE = Path("/root/.openclaw/workspace")
ERRORS_DIR = WORKSPACE / "diary" / "errors"
REPORT_FILE = WORKSPACE / "diary" / "errors" / "weekly-review.md"

def load_error_files():
    """加载所有错误记录文件"""
    errors = []
    if not ERRORS_DIR.exists():
        return errors
    
    for file in ERRORS_DIR.glob("ERR-*.md"):
        content = file.read_text()
        errors.append({
            "file": file.name,
            "content": content[:500],  # 前500字符
            "mtime": file.stat().st_mtime
        })
    
    return errors

def analyze_errors(errors):
    """分析错误趋势"""
    now = datetime.now()
    recent_errors = []
    recurring_patterns = []
    
    for e in errors:
        mtime = datetime.fromtimestamp(e["mtime"])
        days_ago = (now - mtime).days
        
        if days_ago <= 7:  # 最近7天
            recent_errors.append(e)
        
        # 检查复发模式
        if "ERR-20260320-001" in e["file"] or "报喜不报忧" in e["content"]:
            recurring_patterns.append("报喜不报忧模式")
        if "FIN" in e["content"] and "无代码" in e["content"]:
            recurring_patterns.append("虚报FIN模式")
    
    return {
        "total": len(errors),
        "recent": len(recent_errors),
        "patterns": list(set(recurring_patterns))
    }

def generate_report():
    """生成周期报告"""
    errors = load_error_files()
    analysis = analyze_errors(errors)
    
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    report = f"""# 错误记录周期检查报告

**生成时间**: {now}
**检查周期**: 每日

## 统计摘要

| 指标 | 数值 |
|------|------|
| 历史错误总数 | {analysis['total']} |
| 近7天新增 | {analysis['recent']} |
| 复发模式 | {len(analysis['patterns'])} 个 |

## 复发模式预警

"""
    
    if analysis["patterns"]:
        for pattern in analysis["patterns"]:
            report += f"- 🔴 **{pattern}**: 需要重点防范\\n"
    else:
        report += "- ✅ 暂无复发模式\\n"
    
    report += f"""
## 纠正措施检查

请检查以下错误是否已完成纠正：

"""
    
    for e in errors:
        if "ERR-20260328" in e["file"]:
            report += f"- [ ] {e['file']}: 需要确认纠正完成\\n"
    
    report += """
## 预防措施有效性

| 措施 | 状态 | 备注 |
|------|------|------|
| FIN状态诚实审计 | 每日执行 | 防止虚报 |
| 蓝军实时拦截 | 持续运行 | 防止错误扩散 |
| 强制完整汇报 | 每次汇报 | 防止报喜不报忧 |

## 下一步行动

1. 检查未完成纠正的错误
2. 确认预防措施有效性
3. 更新错误趋势分析

---
*本报告由错误记录周期检查脚本自动生成*
*执行命令: python3 scripts/error_periodic_check.py*
"""
    
    return report

def main():
    print("="*60)
    print("🔍 错误记录周期检查")
    print("="*60)
    
    errors = load_error_files()
    print(f"\n📁 发现 {len(errors)} 个错误记录文件")
    
    analysis = analyze_errors(errors)
    print(f"📊 近7天新增: {analysis['recent']} 个")
    
    if analysis["patterns"]:
        print(f"\n🔴 发现复发模式:")
        for p in analysis["patterns"]:
            print(f"   - {p}")
    else:
        print("\n✅ 暂无复发模式")
    
    # 生成报告
    report = generate_report()
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    REPORT_FILE.write_text(report)
    
    print(f"\n📄 报告已保存: {REPORT_FILE}")
    print("="*60)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
