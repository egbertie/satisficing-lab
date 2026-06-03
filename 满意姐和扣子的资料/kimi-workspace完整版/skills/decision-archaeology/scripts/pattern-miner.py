#!/usr/bin/env python3
"""模式挖掘器 - 从决策点中识别重复模式"""
import sys, json, re
from collections import Counter
from pathlib import Path

def mine_patterns(decisions_json_path):
    with open(decisions_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    decisions = data.get('decisions', [])
    
    # 模式1: 关键词频率
    all_text = ' '.join([d['decision_text'] for d in decisions])
    keywords = re.findall(r'\b\w{2,}\b', all_text)
    keyword_freq = Counter(keywords).most_common(20)
    
    # 模式2: 决策类型分类
    type_keywords = {
        '战略型': ['战略', '方向', '目标', '愿景', '规划'],
        '战术型': ['方法', '方案', '策略', '路径', '步骤'],
        '执行型': ['执行', '实施', '推进', '落实', '完成'],
        '评估型': ['评估', '审计', '检查', '验证', '复盘'],
        '资源型': ['资源', '预算', '人力', '时间', '资金']
    }
    
    type_counts = {k: 0 for k in type_keywords}
    for d in decisions:
        text = d['decision_text']
        for dtype, keywords in type_keywords.items():
            if any(kw in text for kw in keywords):
                type_counts[dtype] += 1
    
    output = {
        'total_decisions': len(decisions),
        'top_keywords': keyword_freq,
        'decision_types': type_counts,
        'top_sources': Counter([d['source'] for d in decisions]).most_common(10)
    }
    
    print(json.dumps(output, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python3 pattern-miner.py <decisions.json>")
        return
    mine_patterns(sys.argv[1])
