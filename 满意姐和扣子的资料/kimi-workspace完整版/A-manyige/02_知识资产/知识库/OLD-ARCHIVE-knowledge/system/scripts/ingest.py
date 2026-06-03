#!/usr/bin/env python3
"""
知识摄入管道 - 自动解析文档、提取实体、建立关系
输入: 文件路径
输出: 结构化数据存入data/目录
"""

import os
import sys
import re
import yaml
from datetime import datetime
from pathlib import Path

# 配置
KNOWLEDGE_DIR = Path("/root/.openclaw/workspace/knowledge")
RAW_DIR = KNOWLEDGE_DIR / "raw"
DATA_DIR = KNOWLEDGE_DIR / "data"
PROCESSED_DIR = KNOWLEDGE_DIR / "processed"

def load_ontology():
    """加载本体定义"""
    core_file = KNOWLEDGE_DIR / "ontology" / "core.yaml"
    with open(core_file, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def extract_entities(text, ontology):
    """从文本中提取实体"""
    entities = []
    
    # 专家识别模式
    expert_patterns = [
        r'(黎红雷|罗汉|谢宝剑|李泽湘|方翊沣|陈国祥)',
        r'(教授|博士|研究员)',
    ]
    
    # 方法论识别模式
    method_patterns = [
        r'(五路图腾|合伙人伦理|价值纯度|理性框架|压力管理|极限测试)',
    ]
    
    for pattern in expert_patterns:
        matches = re.finditer(pattern, text)
        for m in matches:
            entities.append({
                'type': '专家',
                'name': m.group(1),
                'position': m.start()
            })
    
    for pattern in method_patterns:
        matches = re.finditer(pattern, text)
        for m in matches:
            entities.append({
                'type': '方法论',
                'name': m.group(1),
                'position': m.start()
            })
    
    return entities

def create_summary(file_path, entities):
    """创建文档摘要"""
    filename = Path(file_path).name
    timestamp = datetime.now().isoformat()
    
    summary = {
        'source_file': filename,
        'processed_at': timestamp,
        'entity_count': len(entities),
        'entities': entities,
        'status': 'processed'
    }
    
    return summary

def ingest(file_path):
    """主摄入函数"""
    file_path = Path(file_path)
    
    if not file_path.exists():
        print(f"错误: 文件不存在 {file_path}")
        return False
    
    # 读取文件
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"错误: 无法读取文件 - {e}")
        return False
    
    # 加载本体
    ontology = load_ontology()
    
    # 提取实体
    entities = extract_entities(content, ontology)
    
    # 创建摘要
    summary = create_summary(file_path, entities)
    
    # 保存摘要
    summary_file = PROCESSED_DIR / "summaries" / f"{file_path.stem}.yaml"
    with open(summary_file, 'w', encoding='utf-8') as f:
        yaml.dump(summary, f, allow_unicode=True, sort_keys=False)
    
    # 保存提取内容
    extract_file = PROCESSED_DIR / "extracts" / f"{file_path.stem}.txt"
    with open(extract_file, 'w', encoding='utf-8') as f:
        f.write(f"# 提取内容: {file_path.name}\n\n")
        f.write(f"## 识别的实体 ({len(entities)}个)\n\n")
        for e in entities:
            f.write(f"- [{e['type']}] {e['name']}\n")
    
    print(f"✓ 已处理: {file_path.name}")
    print(f"  - 识别实体: {len(entities)}个")
    print(f"  - 摘要保存: {summary_file}")
    
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python ingest.py <文件路径>")
        sys.exit(1)
    
    success = ingest(sys.argv[1])
    sys.exit(0 if success else 1)
