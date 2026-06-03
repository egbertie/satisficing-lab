#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
海啸导入引擎 (Tsunami Ingest Engine)
批量扫描文件，提取元数据，生成初始索引

用法:
    python3 tsunami-ingest.py --input /path/to/files --output ./tsunami-output/
"""

import os
import sys
import json
import csv
import argparse
from pathlib import Path
from datetime import datetime

# 文件类型映射
FILE_TYPES = {
    'document': ['.md', '.txt', '.doc', '.docx', '.pdf', '.rtf', '.odt'],
    'spreadsheet': ['.csv', '.xls', '.xlsx', '.ods'],
    'presentation': ['.ppt', '.pptx', '.odp'],
    'code': ['.py', '.js', '.java', '.cpp', '.c', '.h', '.sh', '.bash', '.sql', '.yaml', '.yml', '.json', '.xml'],
    'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp'],
    'audio': ['.mp3', '.wav', '.ogg', '.m4a', '.flac'],
    'video': ['.mp4', '.avi', '.mkv', '.mov', '.wmv'],
    'archive': ['.zip', '.tar', '.gz', '.bz2', '.7z', '.rar']
}

def get_file_type(extension):
    """根据扩展名判断文件类型"""
    ext = extension.lower()
    for ftype, extensions in FILE_TYPES.items():
        if ext in extensions:
            return ftype
    return 'other'

def get_file_size_readable(size_bytes):
    """将字节转换为可读格式"""
    if size_bytes < 1024:
        return f"{size_bytes}B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes/1024:.1f}KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes/(1024*1024):.1f}MB"
    else:
        return f"{size_bytes/(1024*1024*1024):.1f}GB"

def scan_directory(input_path):
    """递归扫描目录，收集文件信息"""
    files = []
    input_path = Path(input_path).resolve()
    
    print(f"🔍 开始扫描: {input_path}")
    
    for root, dirs, filenames in os.walk(input_path):
        # 跳过隐藏目录
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        for filename in filenames:
            if filename.startswith('.'):
                continue
                
            file_path = Path(root) / filename
            
            try:
                stat = file_path.stat()
                extension = file_path.suffix
                
                file_info = {
                    'id': len(files) + 1,
                    'filename': filename,
                    'extension': extension,
                    'file_type': get_file_type(extension),
                    'size_bytes': stat.st_size,
                    'size_readable': get_file_size_readable(stat.st_size),
                    'modified_time': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    'created_time': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    'path': str(file_path.relative_to(input_path)),
                    'depth': len(file_path.relative_to(input_path).parts) - 1,
                    'parent_dir': str(file_path.parent.relative_to(input_path)) if file_path.parent != input_path else '.'
                }
                files.append(file_info)
                
                if len(files) % 100 == 0:
                    print(f"  已扫描: {len(files)} 个文件...")
                    
            except (OSError, PermissionError) as e:
                print(f"  ⚠️ 无法读取: {file_path} - {e}")
                continue
    
    return files

def generate_statistics(files):
    """生成统计信息"""
    stats = {
        'total_files': len(files),
        'total_size_bytes': sum(f['size_bytes'] for f in files),
        'by_type': {},
        'by_extension': {},
        'by_depth': {},
        'date_range': {
            'earliest': min(f['modified_time'] for f in files) if files else None,
            'latest': max(f['modified_time'] for f in files) if files else None
        }
    }
    
    for f in files:
        # 按类型统计
        ftype = f['file_type']
        stats['by_type'][ftype] = stats['by_type'].get(ftype, 0) + 1
        
        # 按扩展名统计
        ext = f['extension'] or '(no extension)'
        stats['by_extension'][ext] = stats['by_extension'].get(ext, 0) + 1
        
        # 按深度统计
        depth = f['depth']
        stats['by_depth'][depth] = stats['by_depth'].get(depth, 0) + 1
    
    stats['total_size_readable'] = get_file_size_readable(stats['total_size_bytes'])
    
    return stats

def save_outputs(files, stats, output_path):
    """保存输出文件"""
    output_path = Path(output_path)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 1. 保存JSON索引
    json_path = output_path / '01_初始索引.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump({
            'scan_time': datetime.now().isoformat(),
            'statistics': stats,
            'files': files
        }, f, ensure_ascii=False, indent=2)
    print(f"✅ 初始索引已保存: {json_path}")
    
    # 2. 保存CSV元数据
    csv_path = output_path / '02_文件元数据.csv'
    if files:
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=files[0].keys())
            writer.writeheader()
            writer.writerows(files)
    print(f"✅ 文件元数据已保存: {csv_path}")
    
    # 3. 生成扫描报告
    report_path = output_path / '00_扫描报告.md'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# 海啸扫描报告\n\n")
        f.write(f"**扫描时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("## 统计概览\n\n")
        f.write(f"- **总文件数**: {stats['total_files']}\n")
        f.write(f"- **总大小**: {stats['total_size_readable']}\n")
        f.write(f"- **时间范围**: {stats['date_range']['earliest'][:10]} ~ {stats['date_range']['latest'][:10]}\n\n")
        
        f.write("## 按类型分布\n\n")
        f.write("| 类型 | 数量 | 占比 |\n")
        f.write("|:-----|:-----|:-----|\n")
        for ftype, count in sorted(stats['by_type'].items(), key=lambda x: x[1], reverse=True):
            pct = count / stats['total_files'] * 100
            f.write(f"| {ftype} | {count} | {pct:.1f}% |\n")
        f.write("\n")
        
        f.write("## 按扩展名分布（Top 20）\n\n")
        f.write("| 扩展名 | 数量 |\n")
        f.write("|:-------|:-----|\n")
        for ext, count in sorted(stats['by_extension'].items(), key=lambda x: x[1], reverse=True)[:20]:
            f.write(f"| {ext} | {count} |\n")
        f.write("\n")
        
        f.write("## 按目录深度分布\n\n")
        f.write("| 深度 | 数量 |\n")
        f.write("|:-----|:-----|\n")
        for depth, count in sorted(stats['by_depth'].items()):
            f.write(f"| {depth} | {count} |\n")
        f.write("\n")
        
        f.write("## 下一步\n\n")
        f.write("运行 `smart-triage.py` 进行智能分类。\n")
    
    print(f"✅ 扫描报告已保存: {report_path}")

def main():
    parser = argparse.ArgumentParser(description='海啸导入引擎 - 批量扫描文件')
    parser.add_argument('--input', '-i', required=True, help='输入文件夹路径')
    parser.add_argument('--output', '-o', required=True, help='输出文件夹路径')
    args = parser.parse_args()
    
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"❌ 错误: 输入路径不存在: {input_path}")
        sys.exit(1)
    
    print("="*60)
    print("🌊 知识海啸处理器 - 导入引擎")
    print("="*60)
    
    # 扫描文件
    files = scan_directory(input_path)
    
    if not files:
        print("⚠️ 警告: 未找到任何文件")
        sys.exit(0)
    
    # 生成统计
    stats = generate_statistics(files)
    
    print(f"\n📊 扫描完成:")
    print(f"  总文件数: {stats['total_files']}")
    print(f"  总大小: {stats['total_size_readable']}")
    print(f"  文件类型: {', '.join(stats['by_type'].keys())}")
    
    # 估算处理时间
    est_time = stats['total_files'] * 0.5  # 每个文件约0.5分钟
    print(f"\n⏱️  预估后续处理时间:")
    print(f"  智能分类: ~{est_time * 0.3:.0f} 分钟")
    print(f"  核心萃取: ~{est_time * 0.4:.0f} 分钟")
    print(f"  质量转化: ~{est_time * 0.3:.0f} 分钟")
    print(f"  总计: ~{est_time:.0f} 分钟 ({est_time/60:.1f} 小时)")
    
    # 保存输出
    save_outputs(files, stats, args.output)
    
    print("\n✅ 导入完成！下一步: 运行 smart-triage.py")
    print("="*60)

if __name__ == '__main__':
    main()
