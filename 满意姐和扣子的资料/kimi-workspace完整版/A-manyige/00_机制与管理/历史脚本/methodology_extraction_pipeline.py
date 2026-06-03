#!/usr/bin/env python3
"""
方法论提取流水线 - 一次性处理全量
用途: 从3,987个历史文件中一次性提取所有方法论
规则: 这一批次一次处理完，不是每天10个
"""

import os
import re
import json
from pathlib import Path
from collections import defaultdict

# 扫描目录
SCAN_DIRS = [
    "/root/.openclaw/workspace/memory",
    "/root/.openclaw/workspace/diary",
    "/root/.openclaw/workspace/docs",
    "/root/.openclaw/workspace/skills",
    "/root/.openclaw/workspace/reports"
]

# 方法论关键词（扩展版）
METHODOLOGY_PATTERNS = {
    "first_principles": ["第一性原理", "物理本质", "拆解"],
    "satisficing": ["满意解", "最优解陷阱", "分批次", "分批"],
    "antifragile": ["反脆弱", "从失败中获益", "失败→学习→机制"],
    "skeptor7": ["Skeptor-7", "7问", "我遗漏了什么"],
    "time_asymmetry": ["时间不对称", "现在省", "未来付", "净收益"],
    "five_totems": ["五图腾", "LIU", "SIMON", "GUANYIN", "CONFUCIUS", "HUINENG"],
    "five_layers": ["五层深挖", "五层", "L1", "L2", "L3", "L4", "L5"],
    "negentropy": ["负熵", "熵增", "熵减", "混乱", "秩序"],
    "identity": ["身份验证", "负熵构造体", "守护型", "操心老妈子", "热血漫男二"],
    "blue_army": ["蓝军", "审计", "质疑"],
    "immediate_execution": ["立即执行", "立即开始", "不等待"],
    "internalization": ["内化", "固化", "物理化", "标准"],
    "honesty": ["诚实", "实事求是", "绝不弄虚"],
    "token_awareness": ["Token", "感知", "档位"]
}

def extract_methodologies_from_file(file_path):
    """从单个文件提取方法论"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
        found_methodologies = []
        for method_name, keywords in METHODOLOGY_PATTERNS.items():
            for keyword in keywords:
                if keyword in content:
                    # 找到关键词，提取上下文
                    idx = content.find(keyword)
                    start = max(0, idx - 50)
                    end = min(len(content), idx + 100)
                    context = content[start:end].replace('\n', ' ')
                    
                    found_methodologies.append({
                        "method": method_name,
                        "keyword": keyword,
                        "context": context,
                        "position": idx
                    })
                    break  # 找到一个关键词就跳出
        
        return found_methodologies
    except Exception as e:
        return []

def run_pipeline():
    """运行提取流水线"""
    
    print("=== 方法论提取流水线 - 全量一次性处理 ===")
    print(f"时间: {datetime.now().isoformat()}")
    print()
    
    # 统计
    total_files = 0
    files_with_methodology = 0
    total_mentions = 0
    methodology_index = defaultdict(list)
    
    # 扫描所有目录
    for scan_dir in SCAN_DIRS:
        if not os.path.exists(scan_dir):
            continue
            
        for root, dirs, files in os.walk(scan_dir):
            for file in files:
                if file.endswith('.md'):
                    file_path = os.path.join(root, file)
                    total_files += 1
                    
                    # 提取方法论
                    methodologies = extract_methodologies_from_file(file_path)
                    
                    if methodologies:
                        files_with_methodology += 1
                        total_mentions += len(methodologies)
                        
                        # 添加到索引
                        relative_path = file_path.replace("/root/.openclaw/workspace/", "")
                        for m in methodologies:
                            methodology_index[m["method"]].append({
                                "file": relative_path,
                                "keyword": m["keyword"],
                                "context": m["context"][:100]  # 限制长度
                            })
                    
                    # 每100个文件报告一次
                    if total_files % 100 == 0:
                        print(f"已处理 {total_files} 个文件，发现 {files_with_methodology} 个含方法论的文件")
    
    print()
    print("=== 处理完成 ===")
    print(f"总文件数: {total_files}")
    print(f"含方法论文件: {files_with_methodology}")
    print(f"总提及数: {total_mentions}")
    print()
    
    # 按方法论分类统计
    print("=== 方法论分布 ===")
    for method, mentions in sorted(methodology_index.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"{method}: {len(mentions)} 处提及")
    
    # 保存索引
    output_file = "/root/.openclaw/workspace/docs/METHODOLOGY_INDEX.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(dict(methodology_index), f, ensure_ascii=False, indent=2)
    
    print()
    print(f"✅ 方法论索引已保存: {output_file}")
    
    return {
        "total_files": total_files,
        "files_with_methodology": files_with_methodology,
        "total_mentions": total_mentions,
        "methodology_count": len(methodology_index)
    }

if __name__ == "__main__":
    from datetime import datetime
    result = run_pipeline()
    print()
    print(f"提取完成: {result['total_mentions']} 处方法论提及来自 {result['files_with_methodology']} 个文件")
