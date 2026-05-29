#!/usr/bin/env python3
"""
Fix outdated terms ONLY in site/*.html (excluding site/.bak/).
Mappings: 观自在→水月观音, 四骑士→关系危机信号, 决策教练→决策外脑
"""
import os, json
from datetime import datetime
from collections import defaultdict

WORKSPACE = "/Users/egbertielau/.openclaw/workspace"
SITE_DIR = os.path.join(WORKSPACE, "site")

TERM_MAP = {
    '观自在': '水月观音',
    '四骑士': '关系危机信号',
    '决策教练': '决策外脑',
}

def find_site_html_files():
    """Find all .html files directly under site/ (not .bak/)"""
    files = []
    for entry in os.listdir(SITE_DIR):
        fp = os.path.join(SITE_DIR, entry)
        if os.path.isfile(fp) and entry.endswith('.html'):
            files.append((entry, fp))
    return files

def scan():
    """Scan site/*.html for old terms"""
    results = []  # list of {file, old_term, new_term, count}
    files = find_site_html_files()
    
    for fname, fp in files:
        with open(fp, 'r', encoding='utf-8', errors='ignore') as fh:
            content = fh.read()
        
        for old_term, new_term in TERM_MAP.items():
            count = content.count(old_term)
            if count > 0:
                results.append({
                    'file': fname,
                    'path': fp,
                    'old_term': old_term,
                    'new_term': new_term,
                    'count': count
                })
    
    return results

def fix(scan_results):
    """Apply replacements to site/*.html files"""
    replaced = []
    files_modified = set()
    
    # Group by file
    by_file = defaultdict(list)
    for r in scan_results:
        by_file[r['path']].append(r)
    
    for fp, terms in by_file.items():
        fname = os.path.basename(fp)
        with open(fp, 'r', encoding='utf-8', errors='ignore') as fh:
            content = fh.read()
        
        modified = content
        for t in terms:
            modified = modified.replace(t['old_term'], t['new_term'])
        
        if modified != content:
            with open(fp, 'w', encoding='utf-8') as fh:
                fh.write(modified)
            
            replaced.append({
                'file': fname,
                'terms': [{'from': t['old_term'], 'to': t['new_term'], 'count': t['count']} for t in terms]
            })
            files_modified.add(fname)
    
    return replaced, files_modified

def verify():
    """Verify no old terms remain in site/*.html (excluding .bak/)"""
    remaining = []
    for fname, fp in find_site_html_files():
        with open(fp, 'r', encoding='utf-8', errors='ignore') as fh:
            content = fh.read()
        for old_term in TERM_MAP:
            if old_term in content:
                remaining.append((fname, old_term))
    return remaining

def count_total_replacements(replaced):
    """Count total individual term occurrences replaced"""
    total = 0
    for r in replaced:
        for t in r['terms']:
            total += t['count']
    return total

# ── Main ──
print("📖 满意红 · 术语一致性修复 (仅 site/*.html)")
print(f"   时间: {datetime.now().isoformat()}")
print(f"   映射: 观自在→水月观音 | 四骑士→关系危机信号 | 决策教练→决策外脑")
print()

# 1. Scan
print("🔍 扫描 site/*.html ...")
scan_results = scan()
print(f"   发现 {len(scan_results)} 处术语待替换")
for r in scan_results:
    print(f"   {r['file']}: '{r['old_term']}' → '{r['new_term']}' ({r['count']}处)")
print()

# 2. Fix
print("🔧 执行替换...")
replaced, files_modified = fix(scan_results)

if not replaced:
    print("   ✅ 没有需要替换的内容")
else:
    total = count_total_replacements(replaced)
    print(f"   ✅ 已修改 {len(files_modified)} 个文件，共 {total} 处术语替换")
    for r in replaced:
        detail = ', '.join(f"'{t['from']}'({t['count']})" for t in r['terms'])
        print(f"      {r['file']}: {detail}")

print()

# 3. Verify
print("🔍 验证修复结果...")
remaining = verify()
if remaining:
    print(f"   ❌ 仍有 {len(remaining)} 处旧术语残留:")
    for fname, term in remaining:
        print(f"      {fname}: {term}")
else:
    print(f"   ✅ site/ 下所有 .html 不再包含旧术语")

print()

# 4. Save report
report = {
    'scan_time': datetime.now().isoformat(),
    'target_dir': 'site/*.html (excluding .bak/)',
    'mappings': TERM_MAP,
    'files_scanned': len(find_site_html_files()),
    'files_modified': len(files_modified),
    'total_replacements': count_total_replacements(replaced),
    'details': [
        {
            'file': r['file'],
            'terms': r['terms']
        }
        for r in replaced
    ],
    'verification': {
        'passed': len(remaining) == 0,
        'remaining_count': len(remaining),
        'remaining_details': remaining
    }
}

report_path = f"{WORKSPACE}/memory/_data/term_scan_20260530.json"
with open(report_path, 'w', encoding='utf-8') as f:
    json.dump(report, f, ensure_ascii=False, indent=2)
print(f"📄 报告已保存: {report_path}")

# Summary
print()
print("=" * 50)
print(f"  修改文件数: {len(files_modified)}")
print(f"  术语替换处: {count_total_replacements(replaced)}")
print(f"  验证通过: {'✅' if len(remaining) == 0 else '❌'}")
print("=" * 50)
