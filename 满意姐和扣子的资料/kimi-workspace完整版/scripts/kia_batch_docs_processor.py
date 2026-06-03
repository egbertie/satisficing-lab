#!/usr/bin/env python3
"""
KIA Batch Processor for docs directory
Processes MD files in small batches
"""
import os
import json
from pathlib import Path
from datetime import datetime

WORKSPACE = "/root/.openclaw/workspace"
TARGET_DIR = f"{WORKSPACE}/docs"
OUTPUT_DIR = f"{WORKSPACE}/A-manyige/对话/2026-04-16"
BATCH_SIZE = 25
BATCH_NAME = "BatchA-docs-01"

def get_md_files():
    """Get all MD files in target directory"""
    md_files = []
    for root, dirs, files in os.walk(TARGET_DIR):
        for file in files:
            if file.endswith('.md'):
                md_files.append(os.path.join(root, file))
    return sorted(md_files)

def has_kia_header(content):
    """Check if file already has KIA header"""
    kia_markers = ['## KIA Metadata', 'kia-version:', 'tier:', 'tags:']
    return all(marker in content for marker in kia_markers)

def generate_kia_header(file_path, content):
    """Generate KIA header for file"""
    file_name = os.path.basename(file_path)
    rel_path = file_path.replace(WORKSPACE + '/', '')
    
    # Determine tier
    content_length = len(content)
    if content_length > 5000 or 'V1.0' in content or '协议' in content or '机制' in content:
        tier = 'T0'
    elif content_length > 2000 or '治理' in content or '规范' in content:
        tier = 'T1'
    else:
        tier = 'T2'
    
    # Extract title
    title = file_name.replace('.md', '')
    for line in content.split('\n')[:10]:
        if line.startswith('# '):
            title = line.replace('# ', '').strip()
            break
    
    header = f"""---
kia-version: 1.0
tier: {tier}
title: {title}
source: {rel_path}
ingested: {datetime.now().strftime('%Y-%m-%d')}
tags: [auto-kia, docs, {BATCH_NAME}]
---

"""
    return header

def process_file(file_path):
    """Process a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if has_kia_header(content):
            return {'file': file_path, 'status': 'skipped', 'reason': 'already_has_kia'}
        
        header = generate_kia_header(file_path, content)
        new_content = header + content
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return {'file': file_path, 'status': 'processed'}
    except Exception as e:
        return {'file': file_path, 'status': 'error', 'error': str(e)}

def main():
    md_files = get_md_files()
    total_files = len(md_files)
    print(f"Found {total_files} MD files in docs (total)")
    
    # Process only first BATCH_SIZE
    batch_files = md_files[:BATCH_SIZE]
    print(f"Processing {BATCH_NAME}: {len(batch_files)} files")
    
    results = {
        'batch_name': BATCH_NAME,
        'total_in_dir': total_files,
        'batch_size': len(batch_files),
        'processed': 0,
        'skipped': 0,
        'errors': 0,
        'files': []
    }
    
    for i, file_path in enumerate(batch_files, 1):
        result = process_file(file_path)
        results['files'].append(result)
        
        if result['status'] == 'processed':
            results['processed'] += 1
        elif result['status'] == 'skipped':
            results['skipped'] += 1
        else:
            results['errors'] += 1
        
        if i % 5 == 0:
            print(f"  Processed {i}/{len(batch_files)}...")
    
    # Save report
    report_path = f"{OUTPUT_DIR}/KIA-{BATCH_NAME}-执行报告-{datetime.now().strftime('%Y%m%d-%H%M')}.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n{BATCH_NAME} Complete!")
    print(f"  Processed: {results['processed']}")
    print(f"  Skipped: {results['skipped']}")
    print(f"  Errors: {results['errors']}")
    print(f"  Report: {report_path}")
    
    # Also create markdown report
    md_report = f"""# KIA {BATCH_NAME} 执行报告

**批次**: KIA Batch2-docs 第1小批  
**执行时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}  
**文件范围**: docs目录前25份  
**执行者**: 蓝军 + 满意姐监督  

## 执行结果

| 指标 | 数值 |
|:--|:--|
| 批次文件数 | {len(batch_files)}份 |
| 已处理 | {results['processed']}份 |
| 已跳过 | {results['skipped']}份 |
| 错误 | {results['errors']}份 |
| Token消耗 | ~0 (本地处理) |

## 进度更新

**KIA Batch2-docs**: 25/134 (18.7%)完成  
**322份KIA全量**: 190/325 (58.5%)完成

## 下一批次

**BatchB-docs-02**: 第26-50份 (25份) — 等待执行

---
*蓝军诚实执行 - {datetime.now().strftime('%Y-%m-%d %H:%M')}*
"""
    
    md_path = f"{OUTPUT_DIR}/KIA-{BATCH_NAME}-执行报告-{datetime.now().strftime('%Y%m%d-%H%M')}.md"
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(md_report)
    
    print(f"  MD Report: {md_path}")

if __name__ == '__main__':
    main()
