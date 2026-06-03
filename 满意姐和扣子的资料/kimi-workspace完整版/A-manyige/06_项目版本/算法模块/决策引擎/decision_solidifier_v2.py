"""
---
KIA-CODE: 知识入库代码级闭环
Asset: decision_solidifier_v2.py
Status: ✅ 代码级KIA完成
Date: 2026-04-15
Batch: OM-03 Python资产25份代码级KIA-批次二

KIA-Loop:
  - 接收清点: 2026-04-15
  - 轻量提取: 2026-04-15 (代码结构识别)
  - 查重去冗: 2026-04-15 (无重复代码)
  - Tier分级: T1 (核心项目资产)
  - 深度洞察: 2026-04-15 (专家数字替身系统)
  - 血液化: ✅ 完成 (五路图腾映射确认)
  - 归档锁定: 2026-04-15

功能定位:
  - 用途: 决策固化器V2
  - 关联: 决策执行
  - 维护者: 蓝军+满意姐

血液化映射:
  - 五路图腾关联: 六祖慧能-行动转化
  - 专家体系: 方翊沣博士
  - 产品映射: SKU-A/B专家系统

---
"""

#!/usr/bin/env python3
"""
决策即时固化系统 V2.0
基于基础组件库重构
"""

import sys
import re
sys.path.insert(0, '/root/.openclaw/workspace')

from defense_base_components import BaseComponent, IndexManager
from typing import Dict, List, Optional

class DecisionSolidifier(BaseComponent):
    """
    决策即时固化系统 V2.0
    基于记忆巩固理论：将工作记忆即时转化为陈述性记忆
    """
    
    def __init__(self):
        super().__init__("decision_solidifier")
        self.episodic_dir = self.ensure_dir("memory", "episodic")
        self.semantic_dir = self.ensure_dir("memory", "semantic")
        self.index = IndexManager("decision")
    
    # 决策模式定义（类变量，避免重复定义）
    DECISION_PATTERNS = {
        'priority': {
            'patterns': [
                r'先[做做弄](\w+)',
                r'(\w+)[最优优先]',
                r'重点[是做在](\w+)',
            ],
            'weight': 0.8
        },
        'rule': {
            'patterns': [
                r'[以禁止不要别绝].{0,3}(\w+)',
                r'必须[要需].{0,3}(\w+)',
                r'只能[是用做].{0,3}(\w+)',
            ],
            'weight': 1.0
        },
        'correction': {
            'patterns': [
                r'不对[，,].{0,10}应该[是做的](\w+)',
                r'错了[，,].{0,10}正确[是做](\w+)',
                r'不是(\w+)，而是(\w+)',
            ],
            'weight': 1.2
        },
        'explicit_memory': {
            'patterns': [
                r'记住.{0,10}(\w+)',
                r'别忘了.{0,10}(\w+)',
                r'重要[的的是].{0,5}(\w+)',
            ],
            'weight': 0.9
        }
    }
    
    def extract_decisions(self, text: str) -> List[Dict]:
        """从文本中提取决策模式"""
        decisions = []
        
        for dec_type, config in self.DECISION_PATTERNS.items():
            for pattern in config['patterns']:
                matches = re.finditer(pattern, text)
                for match in matches:
                    target = match.group(1) if match.groups() else match.group(0)
                    decisions.append({
                        'type': dec_type,
                        'content': match.group(0)[:100],
                        'target': target[:50] if target else '',
                        'weight': config['weight'],
                        'timestamp': self.get_timestamp()
                    })
        
        return decisions
    
    def solidify(self, text: str, source: str = "unknown") -> List[Dict]:
        """即时固化决策"""
        decisions = self.extract_decisions(text)
        
        if not decisions:
            return []
        
        print(f"🔒 检测到 {len(decisions)} 个决策点，正在固化...")
        
        for decision in decisions:
            # 生成唯一ID
            memory_id = self.generate_checksum(decision)[:12]
            
            # 1. 保存到情景记忆
            episode_file = f"{self.episodic_dir}/{self.get_date_string()}_episodes.jsonl"
            self.append_jsonl(episode_file, {
                'memory_id': memory_id,
                'source': source,
                'decision': decision
            })
            
            # 2. 提取语义规则（高权重决策）
            if decision['weight'] >= 1.0:
                self._extract_rule(decision, memory_id)
            
            # 3. 更新索引
            keywords = self._extract_keywords(decision['content'])
            for keyword in keywords:
                self.index.add(keyword, {
                    'memory_id': memory_id,
                    'type': decision['type'],
                    'weight': decision['weight'],
                    'timestamp': decision['timestamp'],
                    'content': decision['content'][:50]
                })
            
            print(f"   ✓ [{decision['type']}] {decision['content'][:40]}... "
                  f"[权重:{decision['weight']}]")
        
        return decisions
    
    def _extract_rule(self, decision: Dict, memory_id: str):
        """提取语义规则"""
        rule = {
            'trigger': decision['target'],
            'type': decision['type'],
            'context': decision['content'],
            'weight': decision['weight'],
            'created_at': decision['timestamp'],
            'memory_id': memory_id
        }
        
        rule_file = f"{self.semantic_dir}/rule_{decision['target']}.json"
        self.save_json(rule_file, rule)
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # 简单的关键词提取：长度>1的词，排除常见虚词
        stop_words = {'的', '了', '是', '在', '和', '或', '与', '要', '做', '用'}
        words = text.split()
        keywords = [w for w in words if len(w) > 1 and w not in stop_words]
        return list(dict.fromkeys(keywords))[:5]  # 去重并限制数量
    
    def search_related(self, query: str) -> List[Dict]:
        """搜索相关决策"""
        keywords = self._extract_keywords(query)
        results = []
        
        for keyword in keywords:
            matches = self.index.get(keyword)
            results.extend(matches)
        
        # 按权重排序
        results.sort(key=lambda x: x.get('weight', 0), reverse=True)
        return results[:10]
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        # 统计今天的记录
        today_file = f"{self.episodic_dir}/{self.get_date_string()}_episodes.jsonl"
        today_count = 0
        if os.path.exists(today_file):
            with open(today_file, 'r') as f:
                today_count = sum(1 for _ in f)
        
        return {
            'today_decisions': today_count,
            'total_keywords': len(self.index.get_all_keys()),
            'semantic_rules': len([f for f in os.listdir(self.semantic_dir) 
                                  if f.startswith('rule_')]) if os.path.exists(self.semantic_dir) else 0
        }

if __name__ == "__main__":
    import os
    
    print("=" * 60)
    print("🔒 决策即时固化系统 V2.0 - 测试")
    print("=" * 60)
    
    solidifier = DecisionSolidifier()
    
    # 测试决策提取
    print("\n[测试1] 决策提取与固化")
    test_text = """
    用户要求：必须先完成Skill盘点，禁止手动实现代码，
    优先使用飞书Skill。记住这个规则，别忘了检查重复文件。
    不对，应该先做代码组件化。
    """
    
    decisions = solidifier.solidify(test_text, "test")
    print(f"\n共固化 {len(decisions)} 个决策点")
    
    # 测试搜索
    print("\n[测试2] 相关决策搜索")
    related = solidifier.search_related("代码实现")
    if related:
        print(f"   找到 {len(related)} 条相关决策")
        for r in related[:3]:
            print(f"   - [{r['type']}] {r['content'][:40]}...")
    
    # 测试统计
    print("\n[测试3] 统计信息")
    stats = solidifier.get_stats()
    print(f"   今日决策: {stats['today_decisions']}")
    print(f"   索引关键词: {stats['total_keywords']}")
    print(f"   语义规则: {stats['semantic_rules']}")
    
    print("\n" + "=" * 60)
    print("✅ 决策即时固化系统 V2.0 测试完成")
    print("=" * 60)
