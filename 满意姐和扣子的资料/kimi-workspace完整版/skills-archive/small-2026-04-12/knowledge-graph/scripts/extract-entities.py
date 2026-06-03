#!/usr/bin/env python3
"""
知识图谱数据提取脚本
功能: 从现有文档提取实体关系，填充知识图谱
触发: 每日一次 + 新文件创建时
"""

import json
import os
import re
from datetime import datetime

def extract_entities_from_file(file_path):
    """从单个文件提取实体"""
    
    if not os.path.exists(file_path):
        return [], []
    
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    entities = []
    relations = []
    doc_title = None  # 初始化doc_title
    
    # 提取标题作为实体
    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if title_match:
        doc_title = title_match.group(1)
        entities.append({
            "id": f"doc_{os.path.basename(file_path)}",
            "type": "Document",
            "name": doc_title,
            "source": file_path
        })
    
    # 提取人名（假设大写或特定格式）
    person_patterns = [
        r'([\u4e00-\u9fa5]{2,4})(?:博士|教授|研究员|先生)',
        r'([A-Z][a-z]+\s+[A-Z][a-z]+)',  # 英文名
    ]
    for pattern in person_patterns:
        matches = re.findall(pattern, content)
        for match in matches:
            if isinstance(match, tuple):
                match = match[0]
            entities.append({
                "id": f"person_{match}",
                "type": "Person",
                "name": match,
                "source": file_path
            })
    
    # 提取Skill名称
    skill_pattern = r'`?(\w+-\w+|\w+-(?:system|manager|engine|planner|sentinel|tracker))`?'
    skill_matches = re.findall(skill_pattern, content, re.IGNORECASE)
    for match in set(skill_matches):
        entities.append({
            "id": f"skill_{match}",
            "type": "Skill",
            "name": match,
            "source": file_path
        })
        # 建立文档包含Skill的关系
        if doc_title:
            relations.append({
                "subject": doc_title,
                "predicate": "contains",
                "object": match,
                "source": file_path
            })
    
    # 提取项目代码
    project_pattern = r'\b(NGT|WLU|PHX|SKL|DR|MGT)-\w+'
    project_matches = re.findall(project_pattern, content)
    for match in set(project_matches):
        entities.append({
            "id": f"project_{match}",
            "type": "Project",
            "name": match,
            "source": file_path
        })
    
    return entities, relations

def build_knowledge_graph():
    """构建知识图谱"""
    
    all_entities = []
    all_relations = []
    
    # 扫描目录
    scan_dirs = [
        "/root/.openclaw/workspace/docs",
        "/root/.openclaw/workspace/skills",
        "/root/.openclaw/workspace/memory"
    ]
    
    for scan_dir in scan_dirs:
        if os.path.exists(scan_dir):
            for root, dirs, files in os.walk(scan_dir):
                for file in files:
                    if file.endswith(".md"):
                        file_path = os.path.join(root, file)
                        entities, relations = extract_entities_from_file(file_path)
                        all_entities.extend(entities)
                        all_relations.extend(relations)
    
    # 去重实体
    unique_entities = {}
    for entity in all_entities:
        key = entity["id"]
        if key not in unique_entities:
            unique_entities[key] = entity
    
    # 去重关系
    unique_relations = []
    seen_relations = set()
    for rel in all_relations:
        key = f"{rel['subject']}-{rel['predicate']}-{rel['object']}"
        if key not in seen_relations:
            seen_relations.add(key)
            unique_relations.append(rel)
    
    # 构建图谱
    knowledge_graph = {
        "timestamp": datetime.now().isoformat(),
        "entities": list(unique_entities.values()),
        "relations": unique_relations,
        "statistics": {
            "entity_count": len(unique_entities),
            "relation_count": len(unique_relations),
            "entity_types": {}
        }
    }
    
    # 统计实体类型
    for entity in unique_entities.values():
        entity_type = entity["type"]
        if entity_type not in knowledge_graph["statistics"]["entity_types"]:
            knowledge_graph["statistics"]["entity_types"][entity_type] = 0
        knowledge_graph["statistics"]["entity_types"][entity_type] += 1
    
    # 保存图谱
    output_file = "/root/.openclaw/workspace/knowledge/graph/knowledge-graph.json"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(knowledge_graph, f, ensure_ascii=False, indent=2)
    
    # 输出摘要
    print("=" * 50)
    print("🧠 知识图谱构建完成")
    print("=" * 50)
    print(f"实体总数: {knowledge_graph['statistics']['entity_count']}")
    print(f"关系总数: {knowledge_graph['statistics']['relation_count']}")
    print("实体类型分布:")
    for entity_type, count in knowledge_graph["statistics"]["entity_types"].items():
        print(f"  - {entity_type}: {count}")
    print(f"图谱文件: {output_file}")
    
    return knowledge_graph

if __name__ == "__main__":
    build_knowledge_graph()
