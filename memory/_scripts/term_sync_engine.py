#!/usr/bin/env python3
"""
满意红 · 术语一致性引擎 V1.0
扫描全站文件，检测术语不一致，自动替换，生成报告
"""

import os, re, json
from datetime import datetime
from pathlib import Path

WORKSPACE = "/Users/egbertielau/.openclaw/workspace"
SITE_DIR = f"{WORKSPACE}/site"

# 术语映射表（核心词汇产权表 V1.1）
TERM_MAP = {
    '观自在': '水月观音',
    '四骑士': '关系危机信号',
    '决策教练': '决策外脑',
    '满意红/扣子': '研究积累',
    '满意红和扣子': '研究积累',
    '五路图腾': '五维决策',  # 对外表达
}

# 排除目录
EXCLUDE_DIRS = {'.git', '.bak', 'node_modules', '__pycache__', '.openclaw', '扣子资料_'}

def scan_terms():
    """扫描所有文件中过时的术语"""
    results = []
    
    for root, dirs, files in os.walk(WORKSPACE):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS and not d.startswith('.')]
        
        for f in files:
            if not f.endswith(('.html', '.md', '.json', '.txt')):
                continue
            
            fp = os.path.join(root, f)
            rel = os.path.relpath(fp, WORKSPACE)
            
            try:
                with open(fp, 'r', encoding='utf-8', errors='ignore') as fh:
                    content = fh.read()
            except:
                continue
            
            for old_term, new_term in TERM_MAP.items():
                if old_term in content:
                    # Count occurrences
                    count = content.count(old_term)
                    results.append({
                        'file': rel,
                        'old_term': old_term,
                        'new_term': new_term,
                        'count': count
                    })
    
    return results

def auto_replace(scan_results, dry_run=True):
    """自动替换过时术语"""
    replaced = []
    files_modified = set()
    
    # Group by file
    by_file = {}
    for r in scan_results:
        fp = r['file']
        if fp not in by_file:
            by_file[fp] = []
        by_file[fp].append(r)
    
    for fp, terms in by_file.items():
        full_path = os.path.join(WORKSPACE, fp)
        try:
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as fh:
                content = fh.read()
        except:
            continue
        
        modified = content
        for t in terms:
            modified = modified.replace(t['old_term'], t['new_term'])
        
        if modified != content:
            if not dry_run:
                with open(full_path, 'w', encoding='utf-8') as fh:
                    fh.write(modified)
            
            replaced.append({
                'file': fp,
                'terms': [{'from': t['old_term'], 'to': t['new_term'], 'count': t['count']} for t in terms]
            })
            files_modified.add(fp)
    
    return replaced

def main():
    print("📖 满意红 · 术语一致性引擎")
    print(f"   时间: {datetime.now().isoformat()}")
    print()
    
    # Scan
    print("🔍 扫描全站术语...")
    results = scan_terms()
    
    if not results:
        print("   ✅ 所有术语一致，无需修复")
        return
    
    # Report
    by_term = {}
    for r in results:
        t = r['old_term']
        if t not in by_term:
            by_term[t] = []
        by_term[t].append(r['file'])
    
    print(f"   ⚠️ 发现 {len(results)} 处不一致")
    for term, files in by_term.items():
        print(f"   '{term}' → '{TERM_MAP[term]}': {len(files)} 个文件")
        for f in files[:3]:
            print(f"      - {f}")
        if len(files) > 3:
            print(f"      ... 及其他 {len(files)-3} 个文件")
    
    # Save report
    report = {
        'scan_time': datetime.now().isoformat(),
        'total_issues': len(results),
        'by_term': {t: {'new': TERM_MAP[t], 'files': fs, 'file_count': len(fs)} for t, fs in by_term.items()},
        'details': results
    }
    
    report_path = f"{WORKSPACE}/memory/_data/term_scan_{datetime.now().strftime('%Y%m%d')}.json"
    with open(report_path, 'w') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 报告: {report_path}")
    print("   运行 --fix 参数自动替换（谨慎使用）")

if __name__ == '__main__':
    import sys
    dry_run = '--fix' not in sys.argv
    main()
