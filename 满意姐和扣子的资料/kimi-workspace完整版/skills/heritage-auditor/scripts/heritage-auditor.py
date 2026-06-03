#!/usr/bin/env python3
"""传承审计师 - 传承质量独立审计"""
import sys, json
from pathlib import Path
from datetime import datetime

def audit_package(package_path):
    package = Path(package_path)
    results = {
        'audit_time': datetime.now().isoformat(),
        'package': str(package),
        'checks': {}
    }
    
    # 检查1: 完整性
    required_files = ['00_索引.md', '01_P0核心层', '05_质量报告.md']
    missing = []
    for req in required_files:
        if not (package / req).exists():
            missing.append(req)
    results['checks']['completeness'] = {
        'status': 'PASS' if not missing else 'FAIL',
        'missing': missing
    }
    
    # 检查2: P0数量
    p0_dir = package / '01_P0核心层'
    p0_count = len(list(p0_dir.glob('*'))) if p0_dir.exists() else 0
    results['checks']['p0_count'] = {
        'status': 'PASS' if 0 < p0_count <= 5 else 'WARN',
        'count': p0_count
    }
    
    # 检查3: 质量报告
    report_file = package / '05_质量报告.md'
    results['checks']['quality_report'] = {
        'status': 'PASS' if report_file.exists() else 'FAIL'
    }
    
    # 总体 verdict
    all_pass = all(c['status'] == 'PASS' for c in results['checks'].values())
    any_fail = any(c['status'] == 'FAIL' for c in results['checks'].values())
    results['verdict'] = 'PASS' if all_pass else 'FAIL' if any_fail else 'WARN'
    
    print(json.dumps(results, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python3 heritage-auditor.py <传承包路径>")
        return
    audit_package(sys.argv[1])
