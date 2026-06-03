#!/usr/bin/env python3
"""
KIA Batch Processor for A-satisficing-v27
Processes MD files with KIA headers for knowledge ingestion
"""
import os
import json
from pathlib import Path
from datetime import datetime

WORKSPACE = "/root/.openclaw/workspace"
TARGET_DIR = f"{WORKSPACE}/A-satisficing-v27"
OUTPUT_DIR = f"{WORKSPACE}/A-manyige/对话/2026-04-16"
BATCH_SIZE = 25

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
    
    # Determine tier based on content length and importance
    content_length = len(content)
    if content_length > 5000 or 'V1.6' in content or '总纲' in content or '底稿' in content:
        tier = 'T0'
    elif content_length > 2000 or '专家' in content or '方法论' in content:
        tier = 'T1'
    else:
        tier = 'T2'
    
    # Extract title from first heading
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
tags: [auto-kia, v27, batch-2026-04-16]
---

"""
    return header

def process_file(file_path):
    """Process a single file - add KIA header if missing"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Skip if already has KIA header
        if has_kia_header(content):
            return {'file': file_path, 'status': 'skipped', 'reason': 'already_has_kia'}
        
        # Generate and add KIA header
        header = generate_kia_header(file_path, content)
        new_content = header + content
        
        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return {'file': file_path, 'status': 'processed', 'tier': 'T0' if 'V1.6' in content or '总纲' in content else 'T1'}
    except Exception as e:
        return {'file': file_path, 'status': 'error', 'error': str(e)}

def main():
    md_files = get_md_files()
    print(f"Found {len(md_files)} MD files in A-satisficing-v27")
    
    results = {
        'total': len(md_files),
        'processed': 0,
        'skipped': 0,
        'errors': 0,
        'files': []
    }
    
    for i, file_path in enumerate(md_files, 1):
        result = process_file(file_path)
        results['files'].append(result)
        
        if result['status'] == 'processed':
            results['processed'] += 1
        elif result['status'] == 'skipped':
            results['skipped'] += 1
        else:
            results['errors'] += 1
        
        if i % 10 == 0:
            print(f"Processed {i}/{len(md_files)} files...")
    
    # Save report
    report_path = f"{OUTPUT_DIR}/KIA-Batch1-v27-执行报告-{datetime.now().strftime('%Y%m%d-%H%M')}.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\nBatch 1 Complete!")
    print(f"Total: {results['total']}")
    print(f"Processed: {results['processed']}")
    print(f"Skipped (already has KIA): {results['skipped']}")
    print(f"Errors: {results['errors']}")
    print(f"Report saved to: {report_path}")

if __name__ == '__main__':
    main()
