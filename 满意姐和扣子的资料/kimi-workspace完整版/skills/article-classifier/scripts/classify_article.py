#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文章分类脚本
根据文章内容自动判断分类并生成存储路径
"""

import json
import os
from datetime import datetime
from pathlib import Path

def load_categories(config_path):
    """加载分类配置"""
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def classify_article(content, title, categories_config):
    """
    根据文章内容判断分类
    
    Args:
        content: 文章内容
        title: 文章标题
        categories_config: 分类配置
    
    Returns:
        dict: {level1: str, level2: str, level3: str, category_name: str}
    """
    text = (title + " " + content).lower()
    
    best_match = None
    best_score = 0
    
    # 匹配一级分类
    for category in categories_config['categories']:
        score = 0
        for keyword in category['keywords']:
            if keyword.lower() in text:
                score += 1
        
        if score > best_score:
            best_score = score
            best_match = category
    
    if not best_match:
        # 默认归类到新闻资讯
        best_match = categories_config['categories'][9]
    
    # 提取二级分类关键词（从标题或前 200 字中提取主题词）
    level2 = extract_subcategory(title, content[:200])
    
    return {
        'level1_id': best_match['id'],
        'level1_name': best_match['name'],
        'level2': level2,
        'level3': '',
        'confidence': best_score
    }

def extract_subcategory(title, preview):
    """从标题和摘要中提取二级分类名称"""
    # 简单实现：取标题中的核心词
    # 可以扩展为使用 NLP 提取关键词
    words = title.replace('-', ' ').replace('_', ' ').split()
    if len(words) >= 2:
        return ' '.join(words[:3])
    return '综合'

def generate_filename(title, date):
    """生成存储文件名"""
    # 清理标题中的非法字符
    safe_title = title.replace('/', '-').replace('\\', '-').replace(':', '-')
    safe_title = safe_title.replace('*', '-').replace('?', '-').replace('"', '-').replace('<', '-').replace('>', '-').replace('|', '-')
    safe_title = safe_title[:50]  # 限制长度
    return f"{date}_{safe_title}.md"

def save_article(storage_path, category_name, subcategory, filename, content, metadata):
    """保存文章到指定分类目录"""
    # 创建目录结构
    level1_path = Path(storage_path) / category_name
    level2_path = level1_path / subcategory
    
    level2_path.mkdir(parents=True, exist_ok=True)
    
    # 生成完整文件内容
    file_content = f"""---
title: {metadata.get('title', 'Untitled')}
source: {metadata.get('source', 'Unknown')}
url: {metadata.get('url', '')}
category: {category_name}/{subcategory}
date: {metadata.get('date', datetime.now().strftime('%Y-%m-%d'))}
tags: {', '.join(metadata.get('tags', []))}
---

{content}
"""
    
    file_path = level2_path / filename
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(file_content)
    
    return str(file_path)

def update_index(index_path, article_info):
    """更新索引文件"""
    with open(index_path, 'r', encoding='utf-8') as f:
        index = json.load(f)
    
    index['articles'].append(article_info)
    index['last_updated'] = datetime.now().isoformat()
    
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

def main():
    """主函数 - 用于测试"""
    print("文章分类脚本已就绪")
    print("此脚本由 article-classifier 技能调用")

if __name__ == '__main__':
    main()
