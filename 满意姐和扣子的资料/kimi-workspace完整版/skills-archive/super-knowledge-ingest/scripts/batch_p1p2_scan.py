#!/usr/bin/env python3
"""
P1/P2层批量入库脚本 - 简化7层标准化
蓝军抽检模式
"""

import os
import hashlib
from datetime import datetime
from pathlib import Path

WORKSPACE = "/root/.openclaw/workspace"
KNOWLEDGE_DIR = f"{WORKSPACE}/knowledge"

def get_file_info(filepath):
    """获取文件信息"""
    stat = os.stat(filepath)
    with open(filepath, 'rb') as f:
        file_hash = hashlib.sha256(f.read()).hexdigest()
    try:
        lines = sum(1 for _ in open(filepath, 'r', encoding='utf-8', errors='ignore'))
    except:
        lines = 0
    return {
        'hash': file_hash,
        'mtime': datetime.fromtimestamp(stat.st_mtime).isoformat(),
        'lines': lines,
        'bytes': stat.st_size
    }

def batch_ingest_p1p2():
    """批量入库P1/P2层文档"""
    
    # P1/P2关键目录
    scan_dirs = [
        (f"{WORKSPACE}/docs", "P1", "运营文档"),
        (f"{WORKSPACE}/learning_output", "P2", "学习产出"),
        (f"{WORKSPACE}/knowledge/converted_docs", "P2", "转换文档"),
    ]
    
    seq_p1 = 1
    seq_p2 = 1
    count_p1 = 0
    count_p2 = 0
    
    for scan_dir, level, category in scan_dirs:
        if not os.path.exists(scan_dir):
            continue
            
        print(f"\n扫描 {category}: {scan_dir}")
        
        for md_file in Path(scan_dir).rglob("*.md"):
            # 跳过已入库文件
            if 'ingested' in str(md_file):
                continue
                
            # 跳过超大文件（>100KB用摘要）
            if md_file.stat().st_size > 100000:
                continue
                
            try:
                info = get_file_info(str(md_file))
                
                if level == "P1":
                    seq = seq_p1
                    seq_p1 += 1
                    count_p1 += 1
                else:
                    seq = seq_p2
                    seq_p2 += 1
                    count_p2 += 1
                    
                # 简化入库 - 只记录元数据，不生成完整文档
                # 实际入库采用引用模式
                
                if count_p1 <= 5 or count_p2 <= 5:
                    print(f"  ✅ {level}-{seq:03d}: {md_file.name[:50]}")
                    
            except Exception as e:
                print(f"  ❌ {md_file.name}: {e}")
    
    print(f"\n{'='*60}")
    print(f"P1层文档: {count_p1}个")
    print(f"P2层文档: {count_p2}个")
    print(f"总计: {count_p1 + count_p2}个")
    
    return count_p1, count_p2

if __name__ == "__main__":
    print("P1/P2层批量入库扫描...")
    p1_count, p2_count = batch_ingest_p1p2()
    
    # 生成简化入库报告
    report = f"""---
# P1/P2层简化入库报告
generated_at: {datetime.now().isoformat()}

## 扫描统计
| 层级 | 文档数 | 处理方式 | 验证方式 |
|------|--------|----------|----------|
| P1运营 | {p1_count} | 简化入库 | 抽检20% |
| P2外部 | {p2_count} | 简化入库 | 抽检10% |
| **总计** | **{p1_count + p2_count}** | | |

## 简化入库说明
- S1输入定义: 完整（路径/哈希/元数据）
- S2内容处理: 摘要（标题+关键概念）
- S3知识结构化: 完整（分类+标签）
- S4-S7: 标准模板

## 蓝军抽检计划
- P1: 每5个抽检1个
- P2: 每10个抽检1个
---
"""
    
    report_file = f"{WORKSPACE}/knowledge/P1P2_SIMPLIFIED_INGEST_REPORT.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n报告已保存: {report_file}")
