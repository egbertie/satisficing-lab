#!/usr/bin/env python3
"""
知识库P0批次准备脚本
筛选核心文件，准备入库
"""

import os
import json
from pathlib import Path
from datetime import datetime

# P0批次筛选规则
P0_EXTENSIONS = {'.md', '.txt', '.docx', '.doc', '.pdf'}
P0_KEYWORDS = ['决策', '合伙人', '方法论', '框架', '图腾', '技能', 'skill', '设计', '方案']
EXCLUDE_DIRS = {'.git', '__pycache__', 'node_modules', 'z_archive_unified'}

def scan_files(base_path):
    """扫描符合条件的文件"""
    p0_files = []
    p1_files = []
    
    for root, dirs, files in os.walk(base_path):
        # 排除目录
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        
        for file in files:
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, base_path)
            _, ext = os.path.splitext(file)
            
            # 检查扩展名
            if ext.lower() not in P0_EXTENSIONS:
                continue
            
            # 检查文件大小（<50MB）
            try:
                size = os.path.getsize(file_path)
                if size > 50 * 1024 * 1024:
                    continue
            except:
                continue
            
            # 检查关键词
            is_p0 = any(kw in rel_path.lower() for kw in P0_KEYWORDS)
            
            file_info = {
                'path': rel_path,
                'size': size,
                'mtime': os.path.getmtime(file_path)
            }
            
            if is_p0:
                p0_files.append(file_info)
            else:
                p1_files.append(file_info)
    
    return p0_files, p1_files

def generate_batch_report(base_path):
    """生成批次报告"""
    p0_files, p1_files = scan_files(base_path)
    
    # 按修改时间排序，优先处理最新的
    p0_files.sort(key=lambda x: x['mtime'], reverse=True)
    p1_files.sort(key=lambda x: x['mtime'], reverse=True)
    
    # 限制P0批次数量
    p0_batch = p0_files[:50]
    
    report = {
        'generated_at': datetime.now().isoformat(),
        'total_scanned': len(p0_files) + len(p1_files),
        'p0_count': len(p0_files),
        'p1_count': len(p1_files),
        'p0_batch': p0_batch,
        'estimated_time': len(p0_batch) * 2  # 每个文件约2分钟
    }
    
    return report

if __name__ == '__main__':
    base_path = '/root/.openclaw/workspace'
    report = generate_batch_report(base_path)
    
    output_path = '/root/.openclaw/workspace/knowledge-ingestion/P0_BATCH_REPORT.json'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"P0批次报告已生成: {output_path}")
    print(f"P0核心文件: {report['p0_count']}个")
    print(f"P1普通文件: {report['p1_count']}个")
    print(f"首批处理: {len(report['p0_batch'])}个")
    print(f"预计时间: {report['estimated_time']}分钟")
