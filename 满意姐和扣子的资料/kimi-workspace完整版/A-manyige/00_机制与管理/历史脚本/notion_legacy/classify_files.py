#!/usr/bin/env python3
"""
Markdown文件分类器 - 按优先级将文件分成5批（优化版）
"""
import json
import os
from pathlib import Path

def get_all_md_files(workspace):
    """获取所有markdown文件"""
    files = []
    for root, dirs, filenames in os.walk(workspace):
        # 跳过隐藏目录
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '.git']
        for f in filenames:
            if f.endswith('.md'):
                files.append(os.path.join(root, f))
    return sorted(files)

def classify_files(files, workspace):
    """按优先级分类文件"""
    batches = {
        'batch_1': [],  # 核心文档 + docs/ + memory/
        'batch_2': [],  # 本地文档包 + 五路图腾
        'batch_3': [],  # 专家档案 + 角色定义
        'batch_4': [],  # 组织架构 + 研究文档
        'batch_5': []   # 剩余所有 + skills/
    }
    
    assigned = set()
    workspace_path = Path(workspace)
    
    for f in files:
        rel_path = os.path.relpath(f, workspace)
        
        # Batch 1: 核心文档 + docs/ + memory/
        if (rel_path.startswith('docs/') or 
            rel_path.startswith('memory/') or
            os.path.basename(f) in ['MEMORY.md', 'SOUL.md', 'USER.md', 'AGENTS.md', 
                                    'BOOTSTRAP.md', 'IDENTITY.md', 'ORGANIZATION.md', 
                                    'TOOLS.md', 'README-合伙人决策教练.md']):
            batches['batch_1'].append(rel_path)
            assigned.add(f)
            continue
        
        # Batch 2: 本地文档包 + 五路图腾相关
        if (rel_path.startswith('本地文档包/') or 
            '五路图腾' in f or 
            '图腾' in f):
            batches['batch_2'].append(rel_path)
            assigned.add(f)
            continue
        
        # Batch 3: 专家档案 + 角色定义 + 官宣相关
        if (rel_path.startswith('飞书角色档案/') or 
            '专家' in f or 
            'ROLE-' in f or
            '官宣' in f or
            'ANNOUNCE' in f):
            batches['batch_3'].append(rel_path)
            assigned.add(f)
            continue
        
        # Batch 4: 组织架构 + 研究文档 + 知识库
        if (rel_path.startswith('knowledge_base/') or 
            rel_path.startswith('满意解研究所资料库/') or 
            rel_path.startswith('personas/') or
            '组织架构' in f or
            '合伙人' in f or
            '研究' in f or
            '完整员工' in f or
            'reports' in f):
            batches['batch_4'].append(rel_path)
            assigned.add(f)
            continue
    
    # Batch 5: 剩余所有 + skills/
    for f in files:
        if f not in assigned:
            rel_path = os.path.relpath(f, workspace)
            batches['batch_5'].append(rel_path)
    
    return batches

def main():
    workspace = '/root/.openclaw/workspace'
    all_files = get_all_md_files(workspace)
    
    print(f"找到 {len(all_files)} 个Markdown文件")
    
    batches = classify_files(all_files, workspace)
    
    # 打印分类结果
    for batch_name, files in batches.items():
        print(f"\n{batch_name}: {len(files)} 个文件")
    
    # 保存分类结果
    output = {
        'total_files': len(all_files),
        'batches': batches,
        'workspace': workspace
    }
    
    with open('/root/.openclaw/workspace/.notion_sync_batches.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n分类结果已保存到 .notion_sync_batches.json")
    
    # 保存详细清单
    for batch_name, files in batches.items():
        with open(f'/root/.openclaw/workspace/.notion_sync_{batch_name}.txt', 'w', encoding='utf-8') as f:
            for file_path in files:
                f.write(file_path + '\n')
        print(f"{batch_name} 文件列表已保存到 .notion_sync_{batch_name}.txt")

if __name__ == '__main__':
    main()
