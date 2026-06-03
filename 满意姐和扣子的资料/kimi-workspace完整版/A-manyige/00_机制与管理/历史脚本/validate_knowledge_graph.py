#!/usr/bin/env python3
"""
知识图谱验证器 - 承诺洗澡Phase 1验证
验证知识图谱是否可用，支持推理
"""

import json

def validate_knowledge_graph():
    """验证知识图谱可用性"""
    
    # 读取图谱
    with open("/root/.openclaw/workspace/knowledge/system/knowledge_graph_v2.json", 'r') as f:
        graph = json.load(f)
    
    # 验证1: 节点数量
    total_nodes = len(graph["nodes"])
    concept_nodes = sum(1 for n in graph["nodes"] if n["type"] == "concept")
    skill_nodes = sum(1 for n in graph["nodes"] if n["type"] == "skill")
    
    print("=== 知识图谱验证报告 ===")
    print(f"\n1. 节点统计")
    print(f"   总节点: {total_nodes}")
    print(f"   概念节点: {concept_nodes}")
    print(f"   Skill节点: {skill_nodes}")
    
    # 验证2: 边数量
    total_edges = len(graph["edges"])
    print(f"\n2. 关联统计")
    print(f"   总关联: {total_edges}")
    
    # 验证3: 概念覆盖
    with open("/root/.openclaw/workspace/knowledge/system/concept_skill_index.json", 'r') as f:
        concept_index = json.load(f)
    
    print(f"\n3. 概念覆盖")
    for concept, data in concept_index.items():
        print(f"   {concept}: {len(data['related'])} 个Skill")
    
    # 验证4: 推理能力测试（一跳查询）
    print(f"\n4. 推理能力测试（一跳查询）")
    test_queries = [
        ("合伙人决策", "哪些Skill支持合伙人决策？"),
        ("内容创作", "哪些Skill支持内容创作？"),
        ("数据分析", "哪些Skill支持数据分析？"),
    ]
    
    for concept, question in test_queries:
        if concept in concept_index:
            related = concept_index[concept]["related"]
            print(f"   {question}")
            for skill in related[:3]:  # 只显示前3个
                print(f"      - {skill}")
            if len(related) > 3:
                print(f"      ... 共 {len(related)} 个")
    
    # 验证5: 覆盖率计算
    total_skills = 144
    covered_skills = set()
    for data in concept_index.values():
        covered_skills.update(data["related"])
    coverage = len(covered_skills) / total_skills * 100
    
    print(f"\n5. 覆盖率")
    print(f"   Skill被概念覆盖: {len(covered_skills)}/{total_skills} ({coverage:.1f}%)")
    
    # 总结
    print(f"\n=== 验证结论 ===")
    checks = [
        ("节点数量 > 0", total_nodes > 0),
        ("概念节点 > 0", concept_nodes > 0),
        ("Skill节点 > 0", skill_nodes > 0),
        ("边数量 > 0", total_edges > 0),
        ("概念覆盖 > 50%", coverage > 50),
    ]
    
    passed = sum(1 for _, result in checks if result)
    total = len(checks)
    
    for check_name, result in checks:
        status = "✅" if result else "❌"
        print(f"   {status} {check_name}")
    
    print(f"\n   通过: {passed}/{total}")
    
    return passed == total, coverage

if __name__ == "__main__":
    all_passed, coverage = validate_knowledge_graph()
    if all_passed:
        print("\n🎉 知识图谱验证通过！")
    else:
        print("\n⚠️ 知识图谱部分验证未通过")
