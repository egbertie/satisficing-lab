#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
核心萃取引擎 (Core Extraction Engine)
从海量文件中提取≤5项核心知识+隐性知识候选

用法:
    python3 core-extractor.py --input ./tsunami-output/ --output ./tsunami-output/
"""

import os
import sys
import json
import re
from pathlib import Path
from datetime import datetime
from collections import Counter

def extract_text_from_file(file_path):
    """尝试从文件中提取文本内容（简化版）"""
    try:
        # 只处理文本类文件
        text_extensions = ['.md', '.txt', '.csv', '.json', '.xml', '.yaml', '.yml', '.py', '.js', '.java', '.sql']
        if file_path.suffix.lower() not in text_extensions:
            return None
        
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            # 限制读取长度
            return content[:50000]  # 最多读50KB
    except Exception as e:
        return None

def extract_keywords(text, top_n=50):
    """提取关键词（简化版：基于词频）"""
    if not text:
        return []
    
    # 清理文本
    text = re.sub(r'[^\u4e00-\u9fff\u3000-\u303fa-zA-Z0-9\s]', ' ', text)
    
    # 分词（简化：按空格和标点分）
    words = text.split()
    
    # 过滤停用词（简化版）
    stopwords = {'的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这', '那', '之', '与', '及', '等', '或', '但', '而', 'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by', 'from', 'as', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'between', 'under', 'and', 'but', 'or', 'yet', 'so', 'if', 'because', 'although', 'though', 'while', 'where', 'when', 'that', 'which', 'who', 'whom', 'whose', 'what', 'this', 'these', 'those', 'it', 'its', 'they', 'them', 'their', 'we', 'us', 'our', 'he', 'him', 'his', 'she', 'her', 'you', 'your'}
    
    # 统计词频
    filtered_words = [w for w in words if len(w) > 1 and w.lower() not in stopwords]
    word_counts = Counter(filtered_words)
    
    return word_counts.most_common(top_n)

def identify_core_concepts(classified_files, input_base_path):
    """识别核心概念"""
    print("\n🔍 分析P0文件内容...")
    
    p0_files = [f for f in classified_files if f['classification']['priority'] == 'P0']
    
    if not p0_files:
        print("  ⚠️ 未找到P0文件，使用P1文件")
        p0_files = [f for f in classified_files if f['classification']['priority'] == 'P1'][:20]
    
    all_text = ""
    file_concepts = []
    
    for f in p0_files[:30]:  # 最多分析30个P0文件
        file_path = Path(input_base_path).parent / '..' / f['path']
        # 尝试找到实际文件路径
        actual_path = None
        if 'input' in str(Path(input_base_path).parent):
            possible_paths = list(Path(input_base_path).parent.glob('**/' + f['filename']))
            if possible_paths:
                actual_path = possible_paths[0]
        
        if actual_path and actual_path.exists():
            text = extract_text_from_file(actual_path)
            if text:
                all_text += text + "\n"
                keywords = extract_keywords(text, top_n=20)
                file_concepts.append({
                    'file_id': f['id'],
                    'filename': f['filename'],
                    'keywords': keywords
                })
    
    # 全局关键词
    global_keywords = extract_keywords(all_text, top_n=30) if all_text else []
    
    return {
        'global_keywords': global_keywords,
        'file_concepts': file_concepts
    }

def identify_implicit_knowledge(classified_files, input_base_path):
    """识别可能包含隐性知识的文件"""
    print("\n🔍 识别隐性知识候选...")
    
    # 隐性知识信号词
    implicit_signals = [
        '感觉', '觉得', '认为', '判断', '直觉', '经验', '体会', '感悟',
        '心得', '诀窍', '门道', '火候', '分寸', '拿捏', '把握',
        'feel', 'sense', 'intuition', 'experience', 'insight', 'tip',
        'trick', 'knack', 'secret', 'art', 'judgment', 'gut'
    ]
    
    implicit_candidates = []
    
    for f in classified_files:
        filename = f['filename'].lower()
        signals_found = []
        
        for signal in implicit_signals:
            if signal.lower() in filename:
                signals_found.append(signal)
        
        # 也检查P1级别的文件（隐性知识通常在P1中）
        if signals_found or f['classification']['category'] in ['case_study', 'personal_note']:
            # 检查实际内容
            actual_path = None
            possible_paths = list(Path(input_base_path).parent.glob('**/' + f['filename']))
            if possible_paths:
                actual_path = possible_paths[0]
            
            content_signals = []
            if actual_path and actual_path.exists():
                text = extract_text_from_file(actual_path)
                if text:
                    for signal in implicit_signals:
                        count = text.lower().count(signal.lower())
                        if count > 0:
                            content_signals.append(f"{signal}({count}次)")
            
            if signals_found or content_signals:
                implicit_candidates.append({
                    'file_id': f['id'],
                    'filename': f['filename'],
                    'priority': f['classification']['priority'],
                    'category': f['classification']['category'],
                    'filename_signals': signals_found,
                    'content_signals': content_signals[:5],  # 最多5个
                    'path': f['path']
                })
    
    # 按优先级排序
    priority_order = {'P0': 0, 'P1': 1, 'P2': 2, 'P3': 3}
    implicit_candidates.sort(key=lambda x: priority_order.get(x['priority'], 99))
    
    return implicit_candidates[:20]  # 最多20个候选

def generate_core_knowledge_list(concepts, implicit_candidates):
    """生成核心知识清单"""
    print("\n📝 生成核心知识清单...")
    
    # 从全局关键词中推断核心知识
    global_keywords = concepts.get('global_keywords', [])
    
    # 提取高频概念（出现>3次的）
    frequent_concepts = [kw for kw in global_keywords if kw[1] > 3][:10]
    
    # 生成核心知识候选
    core_knowledge = []
    
    # 基于关键词生成
    for i, (concept, count) in enumerate(frequent_concepts[:5], 1):
        core_knowledge.append({
            'id': i,
            'name': concept,
            'frequency': count,
            'source': '高频关键词分析',
            'confidence': min(count / 10, 0.9),  # 置信度
            'description': f"在P0文件中出现{count}次的核心概念",
            'needs_human_confirm': True
        })
    
    # 补充隐性知识
    implicit_knowledge = []
    for i, candidate in enumerate(implicit_candidates[:3], 1):
        implicit_knowledge.append({
            'id': i,
            'filename': candidate['filename'],
            'signals': candidate['filename_signals'] + candidate['content_signals'],
            'priority': candidate['priority'],
            'description': f"文件'{candidate['filename']}'可能包含隐性知识",
            'extraction_method': '需人工使用隐性知识表达模板提取',
            'needs_human_confirm': True
        })
    
    return {
        'core_knowledge': core_knowledge,
        'implicit_knowledge': implicit_knowledge,
        'total_candidates': len(core_knowledge) + len(implicit_knowledge)
    }

def main():
    import argparse
    parser = argparse.ArgumentParser(description='核心萃取引擎')
    parser.add_argument('--input', '-i', required=True, help='tsunami-output文件夹路径')
    parser.add_argument('--output', '-o', required=True, help='输出文件夹路径')
    args = parser.parse_args()
    
    input_path = Path(args.input)
    output_path = Path(args.output)
    output_path.mkdir(parents=True, exist_ok=True)
    
    print("="*60)
    print("💎 知识海啸处理器 - 核心萃取引擎")
    print("="*60)
    
    # 读取分类结果
    marks_path = input_path / '04_P0-P1-P2标记.json'
    if not marks_path.exists():
        print(f"❌ 错误: 找不到分类标记文件: {marks_path}")
        print("请先运行 smart-triage.py")
        sys.exit(1)
    
    with open(marks_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    classified_files = data.get('files', [])
    print(f"\n📖 读取分类结果: {len(classified_files)} 个文件")
    
    # 识别核心概念
    concepts = identify_core_concepts(classified_files, input_path)
    
    # 识别隐性知识
    implicit_candidates = identify_implicit_knowledge(classified_files, input_path)
    print(f"  发现隐性知识候选: {len(implicit_candidates)} 个")
    
    # 生成核心知识清单
    core_list = generate_core_knowledge_list(concepts, implicit_candidates)
    
    # 保存核心知识清单
    core_path = output_path / '05_核心知识清单.md'
    with open(core_path, 'w', encoding='utf-8') as f:
        f.write("# 核心知识清单（机器萃取）\n\n")
        f.write("> ⚠️ **注意**: 这是机器自动萃取结果，**必须人工确认**核心知识是否准确。\n")
        f.write("> 机器只能识别'高频出现的概念'，真正的核心知识需要传者确认。\n\n")
        
        f.write("## 核心知识候选（最多5项）\n\n")
        f.write("| 序号 | 名称 | 出现频率 | 置信度 | 来源 | 需人工确认 |\n")
        f.write("|:-----|:-----|:---------|:-------|:-----|:-----------|\n")
        for ck in core_list['core_knowledge']:
            f.write(f"| {ck['id']} | {ck['name']} | {ck['frequency']} | {ck['confidence']:.0%} | {ck['source']} | {'✅' if ck['needs_human_confirm'] else '❌'} |\n")
        f.write("\n")
        
        f.write("### 传者确认区\n\n")
        f.write("请传者确认以下问题：\n\n")
        f.write("1. **这5项是否真的是核心知识？**\n")
        f.write("   - 如果有遗漏，请补充：______\n")
        f.write("   - 如果有不重要的，请删除：______\n\n")
        f.write("2. **如果只能传3项，是哪3项？**\n")
        f.write("   - 第1项：______（为什么？）\n")
        f.write("   - 第2项：______（为什么？）\n")
        f.write("   - 第3项：______（为什么？）\n\n")
        f.write("3. **哪些知识是'传了也没用'的？**\n")
        f.write("   - ______\n\n")
        
        f.write("## 高频关键词（Top 30）\n\n")
        f.write("| 排名 | 关键词 | 出现次数 |\n")
        f.write("|:-----|:-------|:---------|\n")
        for i, (kw, count) in enumerate(concepts['global_keywords'], 1):
            f.write(f"| {i} | {kw} | {count} |\n")
        f.write("\n")
        
        f.write("## 隐性知识候选\n\n")
        f.write("| 序号 | 文件名 | 优先级 | 信号词 | 提取方法 |\n")
        f.write("|:-----|:-------|:-------|:-------|:---------|\n")
        for ik in core_list['implicit_knowledge']:
            signals = ', '.join(ik['signals'][:5])
            f.write(f"| {ik['id']} | {ik['filename']} | {ik['priority']} | {signals} | {ik['extraction_method']} |\n")
        f.write("\n")
        
        f.write("### 隐性知识提取模板\n\n")
        f.write("请传者对每个候选文件使用以下模板提取隐性知识：\n\n")
        f.write("```\n场景：当遇到______时\n")
        f.write("我的判断：我会选______\n")
        f.write("判断依据：\n")
        f.write("  - 第一看______（权重40%）\n")
        f.write("  - 第二看______（权重30%）\n")
        f.write("  - 第三看______（权重20%）\n")
        f.write("常见陷阱：新手容易______\n")
        f.write("我的验证方法：______\n")
        f.write("```\n")
    
    print(f"✅ 核心知识清单已保存: {core_path}")
    
    # 保存隐性知识候选
    implicit_path = output_path / '06_隐性知识候选.md'
    with open(implicit_path, 'w', encoding='utf-8') as f:
        f.write("# 隐性知识候选清单\n\n")
        f.write("> ⚠️ **注意**: 这些是机器识别出的'可能包含隐性知识'的文件。\n")
        f.write("> 传者需要逐一检查，使用模板提取真正的隐性知识。\n\n")
        
        f.write("| 序号 | 文件名 | 优先级 | 类别 | 信号词 | 路径 |\n")
        f.write("|:-----|:-------|:-------|:-----|:-------|:-----|\n")
        for i, ic in enumerate(implicit_candidates, 1):
            signals = ', '.join(ic['filename_signals'] + ic['content_signals'][:3])
            f.write(f"| {i} | {ic['filename']} | {ic['priority']} | {ic['category']} | {signals} | {ic['path']} |\n")
        f.write("\n")
        
        f.write("## 处理建议\n\n")
        f.write("1. 对每个候选文件，传者回答：\"这里有没有我说不清但很重要的经验？\"\n")
        f.write("2. 如果有，使用\"隐性知识表达模板\"提取\n")
        f.write("3. 如果没有，标记为\"无隐性知识\"，移出候选\n")
    
    print(f"✅ 隐性知识候选已保存: {implicit_path}")
    
    print(f"\n📊 萃取结果:")
    print(f"  核心知识候选: {len(core_list['core_knowledge'])} 项")
    print(f"  隐性知识候选: {len(implicit_candidates)} 个文件")
    print(f"  总计候选: {core_list['total_candidates']}")
    
    print("\n⚠️  重要: 请传者人工确认核心知识清单")
    print("✅ 萃取完成！下一步: 运行 quality-transform.py")
    print("="*60)

if __name__ == '__main__':
    main()
