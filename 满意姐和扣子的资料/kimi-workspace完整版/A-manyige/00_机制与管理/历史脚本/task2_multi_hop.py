#!/usr/bin/env python3
"""
知识图谱多跳推理 - 今日执行任务2
目标: 支持两跳查询（概念→Skill→相关Skill）
"""

import json

def build_multi_hop_graph():
    """构建多跳推理图"""
    
    # 读取概念索引
    with open("/root/.openclaw/workspace/knowledge/system/concept_skill_index_v3.json", 'r') as f:
        concept_index = json.load(f)
    
    # 读取Skill索引
    with open("/root/.openclaw/workspace/knowledge/system/skill_knowledge_index.json", 'r') as f:
        skill_data = json.load(f)
    
    # 构建Skill→概念映射（反向）
    skill_to_concepts = {}
    for concept, skills in concept_index.items():
        for skill in skills:
            if skill not in skill_to_concepts:
                skill_to_concepts[skill] = []
            skill_to_concepts[skill].append(concept)
    
    # 构建两跳关联（Skill → 共享概念的Skill）
    multi_hop_graph = {
        "nodes": [],
        "edges": [],
        "skill_to_concepts": skill_to_concepts,
        "concept_to_skills": concept_index
    }
    
    # 添加节点
    for skill in skill_data["skills"]:
        multi_hop_graph["nodes"].append({
            "id": skill["skill_id"],
            "type": "skill",
            "label": skill.get("title", skill["skill_id"]),
            "concepts": skill_to_concepts.get(skill["skill_id"], [])
        })
    
    # 添加概念节点
    for concept in concept_index.keys():
        multi_hop_graph["nodes"].append({
            "id": concept,
            "type": "concept",
            "label": concept
        })
    
    # 添加边（一跳：概念→Skill）
    for concept, skills in concept_index.items():
        for skill in skills:
            multi_hop_graph["edges"].append({
                "source": concept,
                "target": skill,
                "type": "has_skill",
                "hop": 1
            })
    
    # 添加边（两跳：Skill→共享概念的Skill）
    two_hop_edges = 0
    for skill_id, concepts in skill_to_concepts.items():
        for concept in concepts:
            for related_skill in concept_index[concept]:
                if related_skill != skill_id:
                    multi_hop_graph["edges"].append({
                        "source": skill_id,
                        "target": related_skill,
                        "type": "related_via_" + concept,
                        "hop": 2
                    })
                    two_hop_edges += 1
    
    # 保存多跳图
    with open("/root/.openclaw/workspace/knowledge/system/multi_hop_graph.json", 'w') as f:
        json.dump(multi_hop_graph, f, indent=2, ensure_ascii=False)
    
    print(f"多跳图构建完成:")
    print(f"  节点: {len(multi_hop_graph['nodes'])}")
    print(f"  边: {len(multi_hop_graph['edges'])}")
    print(f"  一跳边: {len([e for e in multi_hop_graph['edges'] if e['hop'] == 1])}")
    print(f"  两跳边: {two_hop_edges}")
    
    return multi_hop_graph

def test_multi_hop_query():
    """测试两跳查询"""
    with open("/root/.openclaw/workspace/knowledge/system/multi_hop_graph.json", 'r') as f:
        graph = json.load(f)
    
    print("\n=== 两跳查询测试 ===")
    
    # 测试1: 概念→Skill→相关Skill
    test_concept = "合伙人决策"
    if test_concept in graph["concept_to_skills"]:
        skills = graph["concept_to_skills"][test_concept][:3]
        print(f"\n查询: '{test_concept}' 相关的Skill:")
        for skill in skills:
            print(f"  - {skill}")
            # 找相关Skill
            related = [e["target"] for e in graph["edges"] if e["source"] == skill and e["hop"] == 2][:3]
            if related:
                print(f"    → 相关: {', '.join(related)}")
    
    # 测试2: Skill→概念→相关Skill
    test_skill = "satisficing-partner-decision"
    if test_skill in graph["skill_to_concepts"]:
        concepts = graph["skill_to_concepts"][test_skill]
        print(f"\n查询: '{test_skill}' 的概念和相关Skill:")
        for concept in concepts[:3]:
            print(f"  - 概念: {concept}")
            related = [e["target"] for e in graph["edges"] if e["source"] == test_skill and e["hop"] == 2][:3]
            if related:
                print(f"    → 相关Skill: {', '.join(related)}")
    
    return True

if __name__ == "__main__":
    graph = build_multi_hop_graph()
    test_multi_hop_query()
    
    # 保存报告
    report = {
        "task": "知识图谱多跳推理",
        "nodes": len(graph["nodes"]),
        "edges": len(graph["edges"]),
        "two_hop_edges": len([e for e in graph["edges"] if e["hop"] == 2]),
        "status": "completed"
    }
    
    with open("/root/.openclaw/workspace/memory/task2_report.json", 'w') as f:
        json.dump(report, f, indent=2)
    
    print("\n✅ 任务2完成: 多跳推理可用")
