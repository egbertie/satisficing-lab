#!/usr/bin/env python3
"""
Skill知识提取器 - 承诺洗澡Phase 1
提取全部144个Skill的核心内容，建立知识索引
"""

import os
import json
import re
from pathlib import Path

def extract_skill_knowledge(skill_path):
    """从单个SKILL.md提取核心知识"""
    try:
        with open(skill_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        skill_name = skill_path.parent.name
        
        # 提取描述
        desc_match = re.search(r'description:\s*\|\s*\n(.*?)(?=triggers:|---|\n\n)', content, re.DOTALL)
        description = desc_match.group(1).strip() if desc_match else ""
        
        # 提取触发条件
        triggers_match = re.search(r'triggers:\s*\n((?:\s*-\s*.*?\n)+)', content)
        triggers = []
        if triggers_match:
            triggers = re.findall(r'-\s*(.+)', triggers_match.group(1))
        
        # 提取标题
        title_match = re.search(r'#\s+(.+?)\n', content)
        title = title_match.group(1) if title_match else skill_name
        
        # 提取核心功能（前3个h2）
        sections = re.findall(r'##\s+(.+?)\n', content)
        core_functions = sections[:3] if sections else []
        
        return {
            "skill_id": skill_name,
            "title": title,
            "description": description[:200] + "..." if len(description) > 200 else description,
            "triggers": triggers[:5],  # 最多5个触发词
            "core_functions": core_functions,
            "path": str(skill_path),
            "extracted": True
        }
    except Exception as e:
        return {
            "skill_id": skill_path.parent.name,
            "error": str(e),
            "extracted": False
        }

def batch_extract_skills():
    """批量提取所有Skill"""
    skills_dir = Path("/root/.openclaw/workspace/skills")
    skill_files = list(skills_dir.glob("*/SKILL.md"))
    
    results = []
    for skill_file in skill_files:
        knowledge = extract_skill_knowledge(skill_file)
        results.append(knowledge)
    
    # 保存结果
    output_path = "/root/.openclaw/workspace/knowledge/system/skill_knowledge_index.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({
            "total_skills": len(results),
            "extracted": sum(1 for r in results if r.get("extracted")),
            "failed": sum(1 for r in results if not r.get("extracted")),
            "skills": results
        }, f, ensure_ascii=False, indent=2)
    
    return len(results), sum(1 for r in results if r.get("extracted"))

if __name__ == "__main__":
    total, success = batch_extract_skills()
    print(f"Skill知识提取完成: {success}/{total}")
