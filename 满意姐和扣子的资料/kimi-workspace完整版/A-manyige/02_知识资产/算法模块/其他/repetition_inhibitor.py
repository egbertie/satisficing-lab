#!/usr/bin/env python3
"""
重复抑制系统
基于"尴尬成本"机制：重复询问会产生社交成本，从而自我抑制
"""

import json
import os
from datetime import datetime
from typing import Dict, List

class RepetitionInhibitor:
    def __init__(self):
        self.workspace = "/root/.openclaw/workspace"
        self.query_history = f"{self.workspace}/.query_history.json"
        self.embarrassment_score = 0
    
    def before_asking(self, question: str) -> bool:
        """提问前检查"""
        similar_queries = self.find_similar_queries(question)
        
        if similar_queries:
            most_similar = similar_queries[0]
            similarity_score = most_similar['similarity']
            
            if similarity_score > 0.8:  # 高度相似
                print(f"⚠️ 检测到相似问题（相似度{similarity_score:.0%}）")
                print(f"   之前问题: {most_similar['query'][:50]}...")
                print(f"   建议: 查看之前答案或明确说明差异")
                return False
        
        return True
    
    def find_similar_queries(self, question: str) -> List[Dict]:
        """查找相似问题"""
        if not os.path.exists(self.query_history):
            return []
        
        with open(self.query_history, 'r') as f:
            history = json.load(f)
        
        question_words = set(question.split())
        results = []
        
        for record in history[-20:]:  # 最近20条
            record_words = set(record['query'].split())
            if not question_words or not record_words:
                continue
            overlap = len(question_words & record_words) / len(question_words | record_words)
            
            if overlap > 0.6:
                results.append({
                    'query': record['query'],
                    'answer': record.get('answer', ''),
                    'timestamp': record['timestamp'],
                    'similarity': overlap
                })
        
        return sorted(results, key=lambda x: x['similarity'], reverse=True)
    
    def record_query(self, question: str, answer: str = None):
        """记录问答"""
        record = {
            'timestamp': datetime.now().isoformat(),
            'query': question,
            'answer': answer
        }
        
        history = []
        if os.path.exists(self.query_history):
            with open(self.query_history, 'r') as f:
                history = json.load(f)
        
        history.append(record)
        history = history[-50:]  # 保留最近50条
        
        with open(self.query_history, 'w') as f:
            json.dump(history, f, indent=2)

if __name__ == "__main__":
    inhibitor = RepetitionInhibitor()
    
    # 测试
    test_question = "如何解析docx文件"
    can_ask = inhibitor.before_asking(test_question)
    
    if can_ask:
        print("✅ 可以继续提问")
        inhibitor.record_query(test_question, "使用feishu-fetch-doc Skill")
    else:
        print("❌ 建议先查看之前答案")
    
    print("\n✅ 重复抑制系统测试完成")
