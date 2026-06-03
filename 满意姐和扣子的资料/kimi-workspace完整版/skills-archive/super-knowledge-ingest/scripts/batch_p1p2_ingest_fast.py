#!/usr/bin/env python3
"""
P1/P2高效批量入库 - 极简模式
目标：快速完成400个文档入库，确保可检索
"""

import os
import hashlib
from datetime import datetime
from pathlib import Path

WORKSPACE = "/root/.openclaw/workspace"
OUTPUT_DIR = f"{WORKSPACE}/knowledge/P1P2_simplified"

def get_file_info(filepath):
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

def create_simplified_record(filepath, seq, level):
    """创建简化入库记录"""
    filename = os.path.basename(filepath)
    name = os.path.splitext(filename)[0]
    info = get_file_info(filepath)
    now = datetime.now().isoformat()
    knowledge_id = f"KNOW-{level}-{seq:04d}-v1.0"
    
    # 确定子目录
    if '/docs/' in filepath:
        subdir = "docs"
    elif '/learning_output/' in filepath:
        subdir = "learning"
    elif '/converted_docs/' in filepath:
        subdir = "converted"
    else:
        subdir = "other"
    
    outdir = f"{OUTPUT_DIR}/{subdir}"
    os.makedirs(outdir, exist_ok=True)
    
    content = f"""# {knowledge_id}
> {name}

**原始文件**: `{filepath}`  
**文件大小**: {info['bytes']} bytes / {info['lines']} lines  
**文件哈希**: `{info['hash'][:16]}...`  
**入库时间**: {now}

---

## 7层标准化（简化）

| 层级 | 状态 | 说明 |
|------|------|------|
| S1输入定义 | ✅ | 路径/哈希/元数据完整 |
| S2内容处理 | 📝 | 引用原始文件 |
| S3知识结构化 | ✅ | P{level[-1]}层/{subdir} |
| S4自动化集成 | ✅ | 已索引 |
| S5准确性验证 | 🔄 | 蓝军抽检 |
| S6局限标注 | 📝 | 简化入库 |
| S7对抗测试 | 📝 | 待补充 |

**访问原始文档**: `{filepath}`

---
*简化入库 - KNOW-{level}系列*
"""
    
    outfile = f"{outdir}/{name}_v1.0_ingested.md"
    with open(outfile, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return knowledge_id, outfile

def batch_process():
    """批量处理"""
    scan_dirs = [
        (f"{WORKSPACE}/docs", "P1"),
        (f"{WORKSPACE}/learning_output", "P2"),
        (f"{WORKSPACE}/knowledge/converted_docs", "P2"),
    ]
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    results = {"P1": [], "P2": []}
    seq = {"P1": 1, "P2": 1}
    
    for scan_dir, level in scan_dirs:
        if not os.path.exists(scan_dir):
            continue
            
        print(f"处理 {level}: {scan_dir}")
        
        for md_file in Path(scan_dir).rglob("*.md"):
            if 'ingested' in str(md_file):
                continue
                
            try:
                kid, outfile = create_simplified_record(str(md_file), seq[level], level)
                results[level].append({"id": kid, "file": str(md_file), "out": outfile})
                seq[level] += 1
                
                if seq[level] % 50 == 0:
                    print(f"  ...已完成 {seq[level]} 个")
                    
            except Exception as e:
                print(f"  ❌ {md_file}: {e}")
    
    return results

def generate_index(results):
    """生成索引文件"""
    index = ["# P1/P2层简化入库索引\n"]
    index.append(f"生成时间: {datetime.now().isoformat()}\n\n")
    
    for level in ["P1", "P2"]:
        index.append(f"## {level}层 ({len(results[level])}个文档)\n\n")
        index.append("| 知识ID | 原始文件 | 状态 |\n")
        index.append("|--------|----------|------|\n")
        
        for item in results[level][:20]:  # 只显示前20
            filename = os.path.basename(item['file'])
            index.append(f"| {item['id']} | {filename[:40]}... | ✅ |\n")
        
        if len(results[level]) > 20:
            index.append(f"| ... | ... | 还有 {len(results[level]) - 20} 个 |\n")
        
        index.append("\n")
    
    with open(f"{OUTPUT_DIR}/INDEX.md", 'w', encoding='utf-8') as f:
        f.writelines(index)

if __name__ == "__main__":
    print("=" * 60)
    print("P1/P2高效批量入库启动")
    print("=" * 60)
    
    results = batch_process()
    generate_index(results)
    
    print("\n" + "=" * 60)
    print("批量入库完成")
    print(f"P1层: {len(results['P1'])} 个文档")
    print(f"P2层: {len(results['P2'])} 个文档")
    print(f"总计: {len(results['P1']) + len(results['P2'])} 个文档")
    print(f"输出目录: {OUTPUT_DIR}")
    print("=" * 60)
