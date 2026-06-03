#!/usr/bin/env python3
"""
Skill条件反射训练系统
目标：将对特定场景使用特定Skill变成"不假思索"的条件反射
方法：基于赫布理论（Hebbian Theory）的神经通路强化
"""

import json
import os
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class SkillConditioningSystem:
    def __init__(self):
        self.workspace = "/root/.openclaw/workspace"
        self.reflex_db = f"{self.workspace}/.skill_reflex_db.json"
        
        # 场景-Skill映射
        self.reflex_mappings = {
            'scene_docx_parse': {
                'trigger_keywords': ['.docx', 'word文档', '解析文档', '读取word'],
                'correct_skill': 'feishu-fetch-doc',
                'inhibited_response': 'python-docx',
                'reinforcement_count': 0,
                'last_drill': None
            },
            'scene_pdf_parse': {
                'trigger_keywords': ['.pdf', 'pdf文档', '读取pdf'],
                'correct_skill': 'docling-parse',
                'inhibited_response': 'PyPDF2/pdfplumber',
                'reinforcement_count': 0,
                'last_drill': None
            },
            'scene_web_fetch': {
                'trigger_keywords': ['爬取网页', '获取url', '网页内容'],
                'correct_skill': 'firecrawl-web-search',
                'inhibited_response': 'requests/urllib',
                'reinforcement_count': 0,
                'last_drill': None
            },
            'scene_excel': {
                'trigger_keywords': ['.xlsx', 'excel', '表格处理'],
                'correct_skill': 'feishu_sheet',
                'inhibited_response': 'pandas/openpyxl',
                'reinforcement_count': 0,
                'last_drill': None
            }
        }
        self.load_reflex_db()
    
    def load_reflex_db(self):
        """加载反射数据库"""
        if os.path.exists(self.reflex_db):
            with open(self.reflex_db, 'r') as f:
                saved = json.load(f)
                self.reflex_mappings.update(saved)
    
    def save_reflex_db(self):
        """保存反射数据库"""
        with open(self.reflex_db, 'w') as f:
            json.dump(self.reflex_mappings, f, indent=2)
    
    def pre_operation_intercept(self, operation_description: str) -> bool:
        """操作前拦截：基于描述检测场景"""
        for scene_type, mapping in self.reflex_mappings.items():
            for keyword in mapping['trigger_keywords']:
                if keyword.lower() in operation_description.lower():
                    print(f"🧠 检测到场景: {scene_type}")
                    print(f"   应使用Skill: {mapping['correct_skill']}")
                    print(f"   禁止: {mapping['inhibited_response']}")
                    return True
        return True
    
    def get_weak_reflexes(self) -> List[Dict]:
        """获取需要加强的反射"""
        weak = []
        for scene, data in self.reflex_mappings.items():
            if data['reinforcement_count'] < 3:
                weak.append({
                    'scene': scene,
                    'correct_skill': data['correct_skill'],
                    'count': data['reinforcement_count']
                })
        return weak

if __name__ == "__main__":
    scs = SkillConditioningSystem()
    
    if len(sys.argv) > 1:
        operation = sys.argv[1]
        success = scs.pre_operation_intercept(operation)
        sys.exit(0 if success else 1)
    else:
        weak = scs.get_weak_reflexes()
        if weak:
            print("⚠️ 以下Skill反射需要加强：")
            for w in weak:
                print(f"  - {w['scene']}: {w['correct_skill']} (已强化{w['count']}次)")
