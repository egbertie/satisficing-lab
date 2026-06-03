#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能分类引擎 (Smart Triage Engine)
基于内容的自动分类，P0/P1/P2/P3自动标记

用法:
    python3 smart-triage.py --input ./tsunami-output/01_初始索引.json --output ./tsunami-output/
"""

import os
import sys
import json
import re
from pathlib import Path
from datetime import datetime

# 分类关键词库
CLASSIFICATION_RULES = {
    'core_knowledge': {
        'keywords': ['核心', '关键', '重要', '原则', '标准', '规范', '方法论', '框架', '体系', '模型', '理论', '总结', '精华', '概要', 'overview', 'framework', 'methodology', 'principle', 'standard', 'core', 'key', 'important'],
        'patterns': [r'^(\d+_)?(核心|关键|重要)', r'^(\d+_)?(原则|标准|规范)', r'^(\d+_)?(总结|概要|overview)', r'^(\d+_)?(方法论|框架|体系)'],
        'default_priority': 'P0'
    },
    'case_study': {
        'keywords': ['案例', '实例', '故事', '经历', '项目', '案件', '客户', '实战', '经验', '教训', 'case', 'example', 'project', 'client', 'story', 'experience'],
        'patterns': [r'案例', r'项目', r'案件', r'client', r'project'],
        'default_priority': 'P1'
    },
    'template_tool': {
        'keywords': ['模板', '工具', '清单', '表格', '脚本', '工具包', '模板库', 'template', 'tool', 'checklist', 'script', 'form', 'worksheet'],
        'patterns': [r'模板', r'工具', r'清单', r'template', r'tool'],
        'default_priority': 'P1'
    },
    'process_procedure': {
        'keywords': ['流程', '步骤', '操作', '指南', '手册', '指引', 'SOP', 'procedure', 'process', 'guide', 'manual', 'step', 'howto', 'tutorial'],
        'patterns': [r'流程', r'步骤', r'指南', r'手册', r'procedure', r'process'],
        'default_priority': 'P1'
    },
    'reference_material': {
        'keywords': ['参考', '资料', '文献', '文章', '论文', '报告', '调研', '数据', 'reference', 'material', 'article', 'paper', 'report', 'research', 'data'],
        'patterns': [r'参考', r'资料', r'文献', r'论文', r'reference', r'report'],
        'default_priority': 'P2'
    },
    'communication_record': {
        'keywords': ['邮件', '会议', '讨论', '沟通', '记录', '纪要', '聊天', 'email', 'meeting', 'discussion', 'communication', 'memo', 'chat'],
        'patterns': [r'邮件', r'会议', r'纪要', r'email', r'meeting'],
        'default_priority': 'P2'
    },
    'draft_temporary': {
        'keywords': ['草稿', '临时', '备份', '旧版', '历史', '废弃', 'draft', 'temp', 'backup', 'old', 'archive', 'deprecated'],
        'patterns': [r'草稿', r'临时', r'备份', r'旧', r'draft', r'temp', r'backup'],
        'default_priority': 'P3'
    },
    'personal_note': {
        'keywords': ['笔记', '备忘', '日记', '随想', '感想', 'note', 'memo', 'diary', 'journal', 'thought'],
        'patterns': [r'笔记', r'备忘', r'日记', r'note', r'memo'],
        'default_priority': 'P2'
    }
}

# P0 强制标记规则（高优先级覆盖）
P0_FORCE_RULES = [
    {'pattern': r'^(\d+_)?(00_|01_)', 'reason': '编号靠前的通常是核心'},
    {'pattern': r'(README|INDEX|总纲|导览|overview|summary)', 'reason': '索引/总纲类'},
    {'pattern': r'(核心知识|核心经验|key knowledge|core competency)', 'reason': '明确标记为核心'},
    {'pattern': r'(方法论|框架|体系|model|framework)', 'reason': '方法论类'},
]

# P3 强制降级规则（低优先级覆盖）
P3_FORCE_RULES = [
    {'pattern': r'(草稿|draft|temp|tmp|备份|backup|旧版|old)', 'reason': '临时/备份文件'},
    {'pattern': r'(copy|副本|复件|修改版|修订)', 'reason': '副本/修改版'},
    {'pattern': r'~\$', 'reason': '临时文件'},
]

def classify_file(file_info):
    """对单个文件进行分类和优先级标记"""
    filename = file_info['filename'].lower()
    parent_dir = file_info.get('parent_dir', '').lower()
    file_type = file_info.get('file_type', 'other')
    
    # 初始化
    category = 'uncategorized'
    priority = 'P2'  # 默认P2
    reasons = []
    score = 0
    
    # Step 1: 检查P0强制规则
    for rule in P0_FORCE_RULES:
        if re.search(rule['pattern'], filename, re.IGNORECASE):
            priority = 'P0'
            reasons.append(f"P0强制: {rule['reason']}")
            score += 100
            break
    
    # Step 2: 检查P3强制规则
    if priority != 'P0':
        for rule in P3_FORCE_RULES:
            if re.search(rule['pattern'], filename, re.IGNORECASE):
                priority = 'P3'
                reasons.append(f"P3强制: {rule['reason']}")
                score -= 100
                break
    
    # Step 3: 关键词匹配分类
    if category == 'uncategorized':
        max_matches = 0
        best_category = 'uncategorized'
        
        for cat_name, rules in CLASSIFICATION_RULES.items():
            matches = 0
            # 文件名匹配
            for kw in rules['keywords']:
                if kw.lower() in filename:
                    matches += 1
            # 目录匹配
            for kw in rules['keywords']:
                if kw.lower() in parent_dir:
                    matches += 1
            # 正则匹配
            for pat in rules['patterns']:
                if re.search(pat, filename, re.IGNORECASE):
                    matches += 3  # 正则匹配权重更高
            
            if matches > max_matches:
                max_matches = matches
                best_category = cat_name
                if priority not in ['P0', 'P3']:
                    priority = rules['default_priority']
        
        category = best_category
        if max_matches > 0:
            reasons.append(f"关键词匹配: {max_matches}个")
            score += max_matches * 10
    
    # Step 4: 基于文件类型的调整
    if file_type in ['code', 'script']:
        if 'tool' in filename or 'script' in filename:
            category = 'template_tool'
            if priority not in ['P0', 'P3']:
                priority = 'P1'
    
    # Step 5: 基于路径深度的调整
    depth = file_info.get('depth', 0)
    if depth == 0 and priority not in ['P0', 'P3']:
        # 根目录文件通常是核心
        score += 5
        reasons.append("根目录文件")
    
    # Step 6: 基于文件大小的调整
    size = file_info.get('size_bytes', 0)
    if size > 10 * 1024 * 1024:  # >10MB
        if priority not in ['P0', 'P3']:
            reasons.append("大文件(>10MB)")
    
    return {
        'category': category,
        'priority': priority,
        'reasons': reasons,
        'score': score
    }

def detect_duplicates(files):
    """检测重复文件（基于文件名和大小）"""
    duplicates = []
    seen = {}
    
    for f in files:
        key = (f['filename'], f['size_bytes'])
        if key in seen:
            duplicates.append({
                'original': seen[key],
                'duplicate': f['id'],
                'filename': f['filename']
            })
        else:
            seen[key] = f['id']
    
    return duplicates

def generate_reading_order(files_with_classification):
    """生成推荐阅读顺序"""
    # 按优先级排序：P0 -> P1 -> P2 -> P3
    priority_order = {'P0': 0, 'P1': 1, 'P2': 2, 'P3': 3}
    
    sorted_files = sorted(
        files_with_classification,
        key=lambda x: (
            priority_order.get(x['classification']['priority'], 99),
            -x['classification']['score'],  # 分数高的优先
            x['depth'],
            x['path']
        )
    )
    
    return sorted_files

def main():
    import argparse
    parser = argparse.ArgumentParser(description='智能分类引擎')
    parser.add_argument('--input', '-i', required=True, help='初始索引JSON文件路径')
    parser.add_argument('--output', '-o', required=True, help='输出文件夹路径')
    args = parser.parse_args()
    
    input_path = Path(args.input)
    output_path = Path(args.output)
    output_path.mkdir(parents=True, exist_ok=True)
    
    print("="*60)
    print("🧠 知识海啸处理器 - 智能分类引擎")
    print("="*60)
    
    # 读取初始索引
    print(f"\n📖 读取索引: {input_path}")
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    files = data.get('files', [])
    print(f"  待分类文件: {len(files)}")
    
    # 分类每个文件
    print("\n🔍 开始分类...")
    classified_files = []
    for file_info in files:
        classification = classify_file(file_info)
        file_info['classification'] = classification
        classified_files.append(file_info)
        
        if len(classified_files) % 100 == 0:
            print(f"  已分类: {len(classified_files)}...")
    
    # 检测重复
    print("\n🔍 检测重复文件...")
    duplicates = detect_duplicates(files)
    print(f"  发现重复: {len(duplicates)} 组")
    
    # 统计分类结果
    category_stats = {}
    priority_stats = {'P0': 0, 'P1': 0, 'P2': 0, 'P3': 0}
    
    for f in classified_files:
        cat = f['classification']['category']
        pri = f['classification']['priority']
        category_stats[cat] = category_stats.get(cat, 0) + 1
        priority_stats[pri] = priority_stats.get(pri, 0) + 1
    
    print(f"\n📊 分类统计:")
    print(f"  P0 (必须传): {priority_stats['P0']} 个")
    print(f"  P1 (应该传): {priority_stats['P1']} 个")
    print(f"  P2 (可以传): {priority_stats['P2']} 个")
    print(f"  P3 (不用传): {priority_stats['P3']} 个")
    
    # 生成阅读顺序
    print("\n📋 生成阅读顺序...")
    reading_order = generate_reading_order(classified_files)
    
    # 保存分类索引
    index_path = output_path / '03_分类索引.md'
    with open(index_path, 'w', encoding='utf-8') as out_f:
        out_f.write("# 智能分类索引\n\n")
        out_f.write("> ⚠️ **注意**: 这是机器自动分类结果，**必须人工确认**P0/P1/P2标记是否准确。\n\n")
        out_f.write("## 优先级统计\n\n")
        out_f.write("| 优先级 | 数量 | 说明 |\n")
        out_f.write("|:-------|:-----|:-----|\n")
        out_f.write(f"| 🔴 P0 | {priority_stats['P0']} | 必须传（没有它系统崩溃） |\n")
        out_f.write(f"| 🟡 P1 | {priority_stats['P1']} | 应该传（没有它效率降低） |\n")
        out_f.write(f"| 🟢 P2 | {priority_stats['P2']} | 可以传（有了更好） |\n")
        out_f.write(f"| ⚪ P3 | {priority_stats['P3']} | 不用传（存了也不会用） |\n\n")
        
        out_f.write("## 按类别统计\n\n")
        out_f.write("| 类别 | 数量 | 默认优先级 |\n")
        out_f.write("|:-----|:-----|:-----------|\n")
        for cat, count in sorted(category_stats.items(), key=lambda x: x[1], reverse=True):
            default_p = CLASSIFICATION_RULES.get(cat, {}).get('default_priority', 'P2')
            out_f.write(f"| {cat} | {count} | {default_p} |\n")
        out_f.write("\n")
        
        out_f.write("## 推荐阅读顺序\n\n")
        out_f.write("### P0 - 必须传（先读这些）\n\n")
        out_f.write("| 序号 | 文件名 | 类别 | 路径 | 标记理由 |\n")
        out_f.write("|:-----|:-------|:-----|:-----|:---------|\n")
        idx = 1
        for file_item in reading_order:
            if file_item['classification']['priority'] == 'P0':
                reasons = '；'.join(file_item['classification']['reasons'])
                out_f.write(f"| {idx} | {file_item['filename']} | {file_item['classification']['category']} | {file_item['path']} | {reasons} |\n")
                idx += 1
        
        out_f.write("\n### P1 - 应该传（P0完成后读）\n\n")
        out_f.write("| 序号 | 文件名 | 类别 | 路径 | 标记理由 |\n")
        out_f.write("|:-----|:-------|:-----|:-----|:---------|\n")
        idx = 1
        for file_item in reading_order:
            if file_item['classification']['priority'] == 'P1':
                reasons = '；'.join(file_item['classification']['reasons'])
                out_f.write(f"| {idx} | {file_item['filename']} | {file_item['classification']['category']} | {file_item['path']} | {reasons} |\n")
                idx += 1
        
        out_f.write("\n### P2 - 可以传（有时间再读）\n\n")
        out_f.write("| 序号 | 文件名 | 类别 | 路径 | 标记理由 |\n")
        out_f.write("|:-----|:-------|:-----|:-----|:---------|\n")
        idx = 1
        for file_item in reading_order:
            if file_item['classification']['priority'] == 'P2':
                reasons = '；'.join(file_item['classification']['reasons'])
                out_f.write(f"| {idx} | {file_item['filename']} | {file_item['classification']['category']} | {file_item['path']} | {reasons} |\n")
                idx += 1
        
        if priority_stats['P3'] > 0:
            out_f.write("\n### P3 - 不用传（可忽略）\n\n")
            out_f.write("| 序号 | 文件名 | 类别 | 路径 | 标记理由 |\n")
            out_f.write("|:-----|:-------|:-----|:-----|:---------|\n")
            idx = 1
            for file_item in reading_order:
                if file_item['classification']['priority'] == 'P3':
                    reasons = '；'.join(file_item['classification']['reasons'])
                    out_f.write(f"| {idx} | {file_item['filename']} | {file_item['classification']['category']} | {file_item['path']} | {reasons} |\n")
                    idx += 1
        
        if duplicates:
            out_f.write("\n## 重复文件\n\n")
            out_f.write("| 文件名 | 重复次数 | 建议 |\n")
            out_f.write("|:-------|:---------|:-----|\n")
            for dup in duplicates[:20]:  # 只显示前20
                out_f.write(f"| {dup['filename']} | 2 | 保留最新版本，删除重复 |\n")
    
    print(f"✅ 分类索引已保存: {index_path}")
    
    # 保存JSON格式的标记
    marks_path = output_path / '04_P0-P1-P2标记.json'
    with open(marks_path, 'w', encoding='utf-8') as f:
        json.dump({
            'classification_time': datetime.now().isoformat(),
            'statistics': {
                'by_priority': priority_stats,
                'by_category': category_stats,
                'duplicates': len(duplicates)
            },
            'files': [{k: v for k, v in f.items() if k != 'classification'} | {'classification': f['classification']} for f in classified_files]
        }, f, ensure_ascii=False, indent=2)
    
    print(f"✅ P0-P1-P2标记已保存: {marks_path}")
    print("\n⚠️  重要: 请人工确认P0/P1/P2标记，机器准确率约70-80%")
    print("✅ 分类完成！下一步: 运行 core-extractor.py")
    print("="*60)

if __name__ == '__main__':
    main()
