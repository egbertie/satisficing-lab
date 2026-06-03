#!/usr/bin/env python3
"""
全量知识入库脚本 V1.0
扫描所有知识文件，建立统一索引
"""

import os
import json
from pathlib import Path
from datetime import datetime

WORKSPACE = Path("/root/.openclaw/workspace")
KNOWLEDGE_DIR = WORKSPACE / "knowledge"
OUTPUT_FILE = KNOWLEDGE_DIR / "system" / "full_index.json"

def scan_all_files():
    """扫描所有知识文件"""
    files = []
    
    # 扫描目录和文件类型
    scan_dirs = [
        ("docs", [".md"]),
        ("skills", [".md", ".yaml", ".yml", ".json"]),
        ("memory", [".md"]),
        ("A满意哥专属文件夹", [".md", ".yaml", ".json"]),
        ("diary", [".md"]),
        ("deliverables", [".md"]),
    ]
    
    for dir_name, extensions in scan_dirs:
        dir_path = WORKSPACE / dir_name
        if not dir_path.exists():
            continue
            
        for ext in extensions:
            for file_path in dir_path.rglob(f"*{ext}"):
                if ".git" in str(file_path) or "node_modules" in str(file_path):
                    continue
                
                try:
                    stat = file_path.stat()
                    files.append({
                        "path": str(file_path.relative_to(WORKSPACE)),
                        "type": ext.replace(".", ""),
                        "size": stat.st_size,
                        "mtime": stat.st_mtime,
                        "category": dir_name
                    })
                except Exception as e:
                    print(f"Error scanning {file_path}: {e}")
    
    return files

def categorize_files(files):
    """分类文件"""
    categories = {
        "战略文档": [],
        "技能文档": [],
        "记忆日志": [],
        "专家档案": [],
        "案例库": [],
        "工具脚本": [],
        "其他": []
    }
    
    for f in files:
        path = f["path"].lower()
        
        if "soul.md" in path or "user.md" in path or "memory.md" in path:
            categories["战略文档"].append(f)
        elif "skill" in path and f["type"] == "md":
            categories["技能文档"].append(f)
        elif "expert" in path:
            categories["专家档案"].append(f)
        elif "case" in path:
            categories["案例库"].append(f)
        elif "memory/" in path and f["type"] == "md":
            categories["记忆日志"].append(f)
        elif f["type"] in ["py", "sh", "yaml"]:
            categories["工具脚本"].append(f)
        else:
            categories["其他"].append(f)
    
    return categories

def generate_index():
    """生成完整索引"""
    print("开始全量知识扫描...")
    files = scan_all_files()
    print(f"扫描完成: 共 {len(files)} 个文件")
    
    categories = categorize_files(files)
    
    # 统计
    stats = {
        "total_files": len(files),
        "total_size_mb": sum(f["size"] for f in files) / (1024 * 1024),
        "by_category": {k: len(v) for k, v in categories.items()},
        "by_type": {}
    }
    
    # 按类型统计
    for f in files:
        t = f["type"]
        stats["by_type"][t] = stats["by_type"].get(t, 0) + 1
    
    # 生成索引
    index = {
        "generated_at": datetime.now().isoformat(),
        "stats": stats,
        "categories": categories,
        "all_files": files[:100]  # 只保留前100个作为示例
    }
    
    # 保存
    OUTPUT_FILE.write_text(json.dumps(index, indent=2, ensure_ascii=False))
    print(f"索引已保存: {OUTPUT_FILE}")
    
    # 输出统计
    print("\n=== 知识库统计 ===")
    print(f"总文件数: {stats['total_files']}")
    print(f"总大小: {stats['total_size_mb']:.2f} MB")
    print("\n按分类:")
    for cat, count in stats["by_category"].items():
        print(f"  {cat}: {count}")
    print("\n按类型:")
    for typ, count in stats["by_type"].items():
        print(f"  {typ}: {count}")
    
    return index

if __name__ == "__main__":
    generate_index()