#!/usr/bin/env python3
"""合伙人匹配评估器 - 五维评估"""
import sys, json
from datetime import datetime

def evaluate_partners(a_profile, b_profile):
    # 五维评分（模拟）
    dimensions = {
        '土(根基)': {'a': 85, 'b': 78, 'weight': 0.25},
        '金(标尺)': {'a': 90, 'b': 82, 'weight': 0.25},
        '水(流动)': {'a': 75, 'b': 88, 'weight': 0.20},
        '木(生长)': {'a': 80, 'b': 85, 'weight': 0.15},
        '火(洞察)': {'a': 88, 'b': 76, 'weight': 0.15}
    }
    
    # 计算互补度
    complementarity = {}
    total_score = 0
    for dim, scores in dimensions.items():
        diff = abs(scores['a'] - scores['b'])
        comp = min(scores['a'], scores['b']) + (100 - diff) * 0.3
        complementarity[dim] = round(comp, 1)
        total_score += comp * scores['weight']
    
    return {
        'evaluated_at': datetime.now().isoformat(),
        'dimensions': dimensions,
        'complementarity': complementarity,
        'overall_score': round(total_score, 1),
        'rating': 'A' if total_score >= 80 else 'B' if total_score >= 65 else 'C',
        'recommendation': '高度匹配，建议推进' if total_score >= 80 else '基本匹配，建议深入磨合' if total_score >= 65 else '存在明显差异，需谨慎评估'
    }

def main():
    if len(sys.argv) < 3:
        print("用法: python3 partner-evaluator.py --a profileA.md --b profileB.md")
        return
    result = evaluate_partners(sys.argv[1], sys.argv[2])
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
