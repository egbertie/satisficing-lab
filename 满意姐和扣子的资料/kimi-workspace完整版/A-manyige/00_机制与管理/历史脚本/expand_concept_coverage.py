#!/usr/bin/env python3
"""
知识图谱优化器 - 扩展概念覆盖
将覆盖率从38.9%提升至≥80%
"""

import json

def expand_concept_coverage():
    """扩展概念覆盖"""
    
    # 读取现有Skill索引
    with open("/root/.openclaw/workspace/knowledge/system/skill_knowledge_index.json", 'r') as f:
        skill_data = json.load(f)
    
    # 扩展概念维度（从8个扩展到15个）
    expanded_concepts = {
        # 原有概念
        "五路图腾": {"type": "methodology", "keywords": ["五路", "图腾", "LIU", "SIMON", "GUANYIN", "CONFUCIUS", "HUINENG", "satisficing", "partner", "decision"]},
        "合伙人决策": {"type": "domain", "keywords": ["合伙人", "决策", "partner", "decision", "selection", "合伙", "matching"]},
        "知识管理": {"type": "system", "keywords": ["知识", "knowledge", "memory", "记忆", "归档", "管理", "index"]},
        "自动化": {"type": "system", "keywords": ["自动", "cron", "自动化", "automatic", "pipeline", "workflow", "schedule"]},
        "内容创作": {"type": "capability", "keywords": ["内容", "文案", "写作", "content", "writing", "copy", "creative", "social", "media"]},
        "数据分析": {"type": "capability", "keywords": ["数据", "分析", "data", "analyst", "可视化", "chart", "dashboard", "metrics"]},
        "决策支持": {"type": "capability", "keywords": ["决策", "decision", "治理", "governance", "沙盘", "framework", "strategy"]},
        "文档处理": {"type": "capability", "keywords": ["文档", "document", "文件", "doc", "pdf", "markdown", "convert"]},
        
        # 新增概念
        "技术开发": {"type": "capability", "keywords": ["代码", "开发", "coding", "programming", "git", "github", "docker", "api", "script", "开发"]},
        "AI智能": {"type": "capability", "keywords": ["AI", "智能", "agent", "llm", "model", "chat", "gpt", "claude", "kimi", "大模型"]},
        "研究分析": {"type": "capability", "keywords": ["研究", "research", "分析", "study", "调研", "report", "academic", "论文"]},
        "社媒运营": {"type": "capability", "keywords": ["社媒", "social", "media", "运营", "marketing", "redbook", "xiaohongshu", "content", "calendar"]},
        "飞书集成": {"type": "platform", "keywords": ["飞书", "feishu", "lark", "wiki", "doc", "多维表格", "bitable"]},
        "企业微信": {"type": "platform", "keywords": ["企业微信", "wecom", "微信", "work", "todo", "schedule", "meeting"]},
        "安全防护": {"type": "system", "keywords": ["安全", "security", "guardian", "backup", "recovery", "audit", "风控", "risk"]},
    }
    
    # 为每个Skill建立关联
    covered_skills = set()
    concept_skill_map = {k: [] for k in expanded_concepts.keys()}
    
    for skill in skill_data["skills"]:
        skill_id = skill["skill_id"]
        desc = skill.get("description", "").lower()
        title = skill.get("title", "").lower()
        functions = [f.lower() for f in skill.get("core_functions", [])]
        
        # 合并文本
        text = f"{title} {desc} {' '.join(functions)} {skill_id.lower()}"
        
        # 匹配概念
        matched = False
        for concept, data in expanded_concepts.items():
            for keyword in data["keywords"]:
                if keyword.lower() in text:
                    concept_skill_map[concept].append(skill_id)
                    covered_skills.add(skill_id)
                    matched = True
                    break
        
        # 未匹配的Skill，基于skill_id推断
        if not matched:
            # 基于skill_id关键词推断
            if any(k in skill_id for k in ["git", "code", "docker", "script"]):
                concept_skill_map["技术开发"].append(skill_id)
                covered_skills.add(skill_id)
            elif any(k in skill_id for k in ["ai", "agent", "llm", "gpt"]):
                concept_skill_map["AI智能"].append(skill_id)
                covered_skills.add(skill_id)
            elif any(k in skill_id for k in ["research", "study", "academic"]):
                concept_skill_map["研究分析"].append(skill_id)
                covered_skills.add(skill_id)
            elif any(k in skill_id for k in ["social", "media", "redbook", "marketing"]):
                concept_skill_map["社媒运营"].append(skill_id)
                covered_skills.add(skill_id)
            elif any(k in skill_id for k in ["feishu", "lark"]):
                concept_skill_map["飞书集成"].append(skill_id)
                covered_skills.add(skill_id)
            elif any(k in skill_id for k in ["wecom", "wechat"]):
                concept_skill_map["企业微信"].append(skill_id)
                covered_skills.add(skill_id)
            elif any(k in skill_id for k in ["security", "guardian", "backup"]):
                concept_skill_map["安全防护"].append(skill_id)
                covered_skills.add(skill_id)
    
    # 计算覆盖率
    total_skills = len(skill_data["skills"])
    coverage = len(covered_skills) / total_skills * 100
    
    # 保存扩展后的概念索引
    output_path = "/root/.openclaw/workspace/knowledge/system/concept_skill_index_v2.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(concept_skill_map, f, ensure_ascii=False, indent=2)
    
    # 输出统计
    print("=== 概念覆盖扩展报告 ===")
    print(f"\n概念维度: {len(expanded_concepts)} 个")
    print(f"\n概念覆盖统计:")
    for concept, skills in sorted(concept_skill_map.items(), key=lambda x: -len(x[1])):
        print(f"   {concept}: {len(skills)} 个Skill")
    
    print(f"\n覆盖率: {len(covered_skills)}/{total_skills} ({coverage:.1f}%)")
    
    if coverage >= 80:
        print("\n🎉 覆盖率目标达成！")
    else:
        print(f"\n⚠️ 覆盖率未达目标，还需覆盖 {int(total_skills * 0.8 - len(covered_skills))} 个Skill")
    
    return coverage, concept_skill_map

if __name__ == "__main__":
    coverage, concept_map = expand_concept_coverage()
