#!/usr/bin/env python3
"""满意解谈判辅助 - 寻找共识点"""
import sys, json
from datetime import datetime

def analyze_negotiation(topic, party_a, party_b):
    # 模拟分析
    anchors = {
        'party_a_anchor': party_a,
        'party_b_anchor': party_b,
        'gap': abs(len(party_a) - len(party_b))  # 简化模拟
    }
    
    # 选项生成
    options = [
        {'name': '折中方案', 'a_score': 7, 'b_score': 7, 'type': 'compromise'},
        {'name': '创意方案', 'a_score': 8, 'b_score': 6, 'type': 'creative'},
        {'name': '延期方案', 'a_score': 6, 'b_score': 8, 'type': 'defer'}
    ]
    
    # 满意解筛选（双方≥7）
    satisficing = [o for o in options if o['a_score'] >= 7 and o['b_score'] >= 7]
    
    return {
        'analyzed_at': datetime.now().isoformat(),
        'topic': topic,
        'anchors': anchors,
        'all_options': options,
        'satisficing_options': satisficing,
        'recommendation': satisficing[0]['name'] if satisficing else '需重新设计选项',
        'next_step': '选择满意解选项，或进入利益深挖'
    }

def main():
    if len(sys.argv) < 4:
        print("用法: python3 negotiation-assistant.py --topic '主题' --a '立场A' --b '立场B'")
        return
    result = analyze_negotiation(sys.argv[1], sys.argv[2], sys.argv[3])
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
