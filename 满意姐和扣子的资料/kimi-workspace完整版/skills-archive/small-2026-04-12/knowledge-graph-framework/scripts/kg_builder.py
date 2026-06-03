#!/usr/bin/env python3
"""
知识图谱构建器 - 基础版本
"""

import json
import re
from pathlib import Path
from datetime import datetime

WORKSPACE = Path("/root/.openclaw/workspace")
KG_FILE = WORKSPACE / "memory" / "knowledge-graph.json"

# 基础实体类型
ENTITY_TYPES = ['person', 'project', 'skill', 'concept', 'document', 'event']

# 基础关系类型
RELATION_TYPES = ['created_by', 'depends_on', 'related_to', 'part_of', 'uses']

class KnowledgeGraph:
    def __init__(self):
        self.entities = {}
        self.relations = []
        
    def add_entity(self, entity_type, name, attributes=None, sources=None):
        """添加实体"""
        entity_id = f"{entity_type}_{name.lower().replace(' ', '_')}"
        
        self.entities[entity_id] = {
            "id": entity_id,
            "type": entity_type,
            "name": name,
            "attributes": attributes or {},
            "sources": sources or [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        return entity_id
    
    def add_relation(self, rel_type, source, target, weight=1.0):
        """添加关系"""
        relation = {
            "id": f"rel_{len(self.relations)}",
            "type": rel_type,
            "source": source,
            "target": target,
            "weight": weight,
            "created_at": datetime.now().isoformat()
        }
        self.relations.append(relation)
        return relation["id"]
    
    def extract_from_skill(self, skill_path):
        """从Skill文件中提取实体"""
        skill_file = skill_path / "SKILL.md"
        if not skill_file.exists():
            return
        
        skill_name = skill_path.name
        
        # 添加Skill实体
        skill_id = self.add_entity(
            'skill', 
            skill_name,
            {'path': str(skill_path.relative_to(WORKSPACE))},
            [str(skill_file)]
        )
        
        # 读取内容提取关系
        try:
            content = skill_file.read_text(encoding='utf-8')
            
            # 提取依赖的Skill（简单模式匹配）
            for line in content.split('\n'):
                if 'depends' in line.lower() or '依赖' in line:
                    # 尝试提取其他skill名称
                    for other_skill in self.entities:
                        if other_skill.startswith('skill_') and other_skill != skill_id:
                            other_name = other_skill.replace('skill_', '')
                            if other_name in line.lower():
                                self.add_relation('depends_on', skill_id, other_skill)
        except:
            pass
        
        return skill_id
    
    def extract_from_memory(self):
        """从MEMORY.md提取核心实体"""
        memory_file = WORKSPACE / "MEMORY.md"
        if not memory_file.exists():
            return
        
        try:
            content = memory_file.read_text(encoding='utf-8')
            
            # 提取项目名称
            if '满意解研究所' in content:
                self.add_entity('project', '满意解研究所', {}, [str(memory_file)])
            
            # 提取人员（简单匹配）
            person_patterns = ['黎红雷', '罗汉', '谢宝剑', '方翊沣', '陈国祥']
            for person in person_patterns:
                if person in content:
                    self.add_entity('person', person, {}, [str(memory_file)])
                    
        except:
            pass
    
    def build(self):
        """构建知识图谱"""
        print("开始构建知识图谱...")
        
        # 从Skill目录提取
        skills_dir = WORKSPACE / "skills"
        for skill_path in skills_dir.iterdir():
            if skill_path.is_dir() and not skill_path.name.startswith('.'):
                self.extract_from_skill(skill_path)
        
        # 从MEMORY提取
        self.extract_from_memory()
        
        print(f"实体数: {len(self.entities)}")
        print(f"关系数: {len(self.relations)}")
        
        return self
    
    def save(self):
        """保存知识图谱"""
        data = {
            "metadata": {
                "version": "1.0",
                "created_at": datetime.now().isoformat(),
                "entity_count": len(self.entities),
                "relation_count": len(self.relations)
            },
            "entities": self.entities,
            "relations": self.relations
        }
        
        with open(KG_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"知识图谱已保存: {KG_FILE}")
    
    def query(self, entity_type=None, name_pattern=None):
        """查询实体"""
        results = []
        for entity in self.entities.values():
            if entity_type and entity['type'] != entity_type:
                continue
            if name_pattern and name_pattern.lower() not in entity['name'].lower():
                continue
            results.append(entity)
        return results

def main():
    kg = KnowledgeGraph()
    kg.build()
    kg.save()
    
    # 示例查询
    print("\n技能列表:")
    for skill in kg.query(entity_type='skill')[:10]:
        print(f"  - {skill['name']}")

if __name__ == "__main__":
    main()
