#!/usr/bin/env python3
"""
决策即时固化系统
基于记忆巩固理论：将工作记忆（短期）即时转化为陈述性记忆（长期）
"""

import json
import os
import re
import hashlib
from datetime import datetime
from typing import Dict, List, Optional

class DecisionSolidifier:
    def __init__(self):
        self.workspace = "/root/.openclaw/workspace"
        self.episodic_memory = f"{self.workspace}/memory/episodic"
        self.semantic_memory = f"{self.workspace}/memory/semantic"
        self.index_file = f"{self.workspace}/memory/.decision_index.json"
        
        for path in [self.episodic_memory, self.semantic_memory]:
            os.makedirs(path, exist_ok=True)
    
    def extract_decision_patterns(self, text: str) -> List[Dict]:
        """从文本中提取决策模式"""
        decisions = []
        
        # 模式1：优先级决策
        priority_patterns = [
            r'先[做做弄](\w+)',
            r'(\w+)[最优优先]',
        ]
        for pattern in priority_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                decisions.append({
                    'type': 'priority',
                    'content': match.group(0),
                    'target': match.group(1) if match.groups() else None,
                    'timestamp': datetime.now().isoformat(),
                    'weight': 0.8
                })
        
        # 模式2：规则决策
        rule_patterns = [
            r'[以禁止不要别绝].{0,3}(\w+)',
            r'必须[要需].{0,3}(\w+)',
        ]
        for pattern in rule_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                decisions.append({
                    'type': 'rule',
                    'content': match.group(0),
                    'target': match.group(1) if match.groups() else None,
                    'timestamp': datetime.now().isoformat(),
                    'weight': 1.0
                })
        
        return decisions
    
    def solidify_immediately(self, conversation_text: str, source: str):
        """即时固化：对话结束后立即执行"""
        decisions = self.extract_decision_patterns(conversation_text)
        
        if not decisions:
            return
        
        print(f"🔒 检测到{len(decisions)}个决策点，正在即时固化...")
        
        for decision in decisions:
            memory_id = self.hash_decision(decision)
            
            # 写入情景记忆
            episode_file = f"{self.episodic_memory}/{datetime.now().strftime('%Y%m%d')}_episodes.jsonl"
            with open(episode_file, 'a') as f:
                f.write(json.dumps({
                    'memory_id': memory_id,
                    'source': source,
                    'decision': decision,
                }, ensure_ascii=False) + '\n')
            
            # 更新索引
            self.update_index(decision, memory_id)
            
            print(f"  ✓ 固化: {decision['content'][:30]}... [权重:{decision['weight']}]")
    
    def hash_decision(self, decision: Dict) -> str:
        """生成决策哈希"""
        content = f"{decision['type']}{decision['content']}{decision['timestamp']}"
        return hashlib.sha256(content.encode()).hexdigest()[:12]
    
    def update_index(self, decision: Dict, memory_id: str):
        """更新决策索引"""
        index = {}
        if os.path.exists(self.index_file):
            with open(self.index_file, 'r') as f:
                index = json.load(f)
        
        keywords = self.extract_keywords(decision['content'])
        for keyword in keywords:
            if keyword not in index:
                index[keyword] = []
            index[keyword].append({
                'memory_id': memory_id,
                'type': decision['type'],
                'weight': decision['weight'],
                'timestamp': decision['timestamp']
            })
        
        with open(self.index_file, 'w') as f:
            json.dump(index, f, indent=2)
    
    def extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        words = text.split()
        return [w for w in words if len(w) > 1][:5]

if __name__ == "__main__":
    solidifier = DecisionSolidifier()
    
    # 测试模式
    test_text = "必须先完成Skill盘点，禁止手动实现，优先使用现有Skill"
    solidifier.solidify_immediately(test_text, "test")
    print("\n✅ 决策固化系统测试完成")
