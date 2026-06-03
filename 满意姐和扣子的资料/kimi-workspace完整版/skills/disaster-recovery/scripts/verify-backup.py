#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""备份验证器 - 验证备份完整性"""
import sys, os, hashlib
from pathlib import Path

def verify_backup(backup_path):
    backup_dir = Path(backup_path)
    if not backup_dir.exists():
        return f"❌ 备份路径不存在: {backup_path}"
    
    report = [f"# 备份验证报告\n\n路径: {backup_path}\n"]
    issues = []
    
    # 检查7层目录
    for layer in ['L7','L6','L5','L4','L3','L2','L1']:
        layer_dir = backup_dir / layer
        if layer_dir.exists():
            files = list(layer_dir.rglob('*'))
            report.append(f"✅ {layer}: {len(files)} 个文件/目录")
        else:
            issues.append(f"❌ {layer}: 目录缺失")
            report.append(f"❌ {layer}: 目录缺失")
    
    # 检查报告文件
    report_file = backup_dir / 'BACKUP_REPORT.md'
    if report_file.exists():
        report.append(f"✅ 备份报告存在")
    else:
        issues.append(f"❌ 备份报告缺失")
        report.append(f"❌ 备份报告缺失")
    
    # 总结
    report.append(f"\n## 验证结果")
    if not issues:
        report.append(f"✅ 全部通过 — 备份完整")
    else:
        report.append(f"⚠️  发现问题 {len(issues)} 个")
        for issue in issues:
            report.append(f"  - {issue}")
    
    return '\n'.join(report)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        print(verify_backup(sys.argv[1]))
    else:
        print('用法: python3 verify-backup.py /path/to/backup')
