#!/usr/bin/env python3
"""
知识图谱构建器 - 承诺洗澡Phase 1
基于Skill知识提取结果，构建知识关联
"""

import json
from pathlib import Path

def build_knowledge_graph():
    """构建知识图谱"""
    # 读取Skill知识索引
    with open("/root/.openclaw/workspace/knowledge/system/skill_knowledge_index.json", 'r') as f:
        skill_data = json.load(f)
    
    # 核心概念节点
    core_concepts = {
        "五路图腾": {"type": "methodology", "related": []},
        "合伙人决策": {"type": "domain", "related": []},
        "知识管理": {"type": "system", "related": []},
        "自动化": {"type": "system", "related": []},
        "内容创作": {"type": "capability", "related": []},
        "数据分析": {"type": "capability", "related": []},
        "决策支持": {"type": "capability", "related": []},
        "文档处理": {"type": "capability", "related": []},
    }
    
    # 关联规则：基于关键词匹配
    keywords_map = {
        "五路图腾": ["五路", "图腾", "LIU", "SIMON", "GUANYIN", "CONFUCIUS", "HUINENG"],
        "合伙人决策": ["合伙人", "决策", "partner", "decision", "selection"],
        "知识管理": ["知识", "knowledge", "memory", "记忆", "归档"],
        "自动化": ["自动", "cron", "自动化", "automatic", "pipeline"],
        "内容创作": ["内容", "文案", "写作", "content", "writing", "copy"],
        "数据分析": ["数据", "分析", "data", "analyst", "可视化"],
        "决策支持": ["决策", "decision", "治理", "governance", "沙盘"],
        "文档处理": ["文档", "document", "文件", "doc", "pdf"],
    }
    
    # 为每个Skill建立关联
    for skill in skill_data["skills"]:
        skill_id = skill["skill_id"]
        desc = skill.get("description", "")
        title = skill.get("title", "")
        functions = skill.get("core_functions", [])
        
        # 合并文本进行关键词匹配
        text = f"{title} {desc} {' '.join(functions)}".lower()
        
        for concept, keywords in keywords_map.items():
            for keyword in keywords:
                if keyword.lower() in text:
                    if skill_id not in core_concepts[concept]["related"]:
                        core_concepts[concept]["related"].append(skill_id)
                    break
    
    # 构建图谱结构
    graph = {
        "nodes": [],
        "edges": [],
        "stats": {
            "total_nodes": 0,
            "total_edges": 0,
            "concepts": len(core_concepts),
            "skills": len(skill_data["skills"])
        }
    }
    
    # 添加概念节点
    for concept, data in core_concepts.items():
        graph["nodes"].append({
            "id": concept,
            "type": "concept",
            "label": concept,
            "related_count": len(data["related"])
        })
        graph["stats"]["total_nodes"] += 1
        
        # 添加边
        for skill_id in data["related"]:
            graph["edges"].append({
                "source": concept,
                "target": skill_id,
                "type": "relates_to"
            })
            graph["stats"]["total_edges"] += 1
    
    # 添加Skill节点
    for skill in skill_data["skills"]:
        graph["nodes"].append({
            "id": skill["skill_id"],
            "type": "skill",
            "label": skill.get("title", skill["skill_id"]),
            "triggers": skill.get("triggers", []),
            "functions": skill.get("core_functions", [])
        })
        graph["stats"]["total_nodes"] += 1
    
    # 保存图谱
    output_path = "/root/.openclaw/workspace/knowledge/system/knowledge_graph_v2.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(graph, f, ensure_ascii=False, indent=2)
    
    # 保存概念关联索引
    concept_index_path = "/root/.openclaw/workspace/knowledge/system/concept_skill_index.json"
    with open(concept_index_path, 'w', encoding='utf-8') as f:
        json.dump(core_concepts, f, ensure_ascii=False, indent=2)
    
    return graph["stats"]

if __name__ == "__main__":
    stats = build_knowledge_graph()
    print(f"知识图谱构建完成:")
    print(f"  节点: {stats['total_nodes']}")
    print(f"  边: {stats['total_edges']}")
    print(f"  概念: {stats['concepts']}")
    print(f"  Skill: {stats['skills']}")
