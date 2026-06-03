#!/usr/bin/env python3
"""研究质量评估器 - 评估最终产出质量"""
import sys, json, re
from pathlib import Path

def assess_quality(research_file):
    text = Path(research_file).read_text(encoding='utf-8', errors='ignore')
    
    # 质量维度
    dimensions = {
        'completeness': {
            'score': 0,
            'checks': [
                ('有明确结论', bool(re.search(r'结论|总结|综上所述', text))),
                ('有引用标注', bool(re.search(r'\[\d+\]|来源[:：]|出处', text))),
                ('有结构标题', bool(re.search(r'^##?\s', text, re.MULTILINE))),
                ('有摘要', bool(re.search(r'摘要|概要|概述', text)))
            ]
        },
        'density': {
            'score': 0,
            'checks': [
                ('字数充足', len(text) > 2000),
                ('信息密度高', len(re.findall(r'[。！？]', text)) > 20)
            ]
        },
        'traceability': {
            'score': 0,
            'checks': [
                ('有来源列表', bool(re.search(r'参考|来源|引用', text))),
                ('有URL', bool(re.search(r'https?://', text)))
            ]
        }
    }
    
    # 计算各维度得分
    total_score = 0
    for dim_name, dim_data in dimensions.items():
        dim_score = sum(1 for _, check in dim_data['checks'] if check)
        dim_data['score'] = dim_score
        total_score += dim_score
    
    # 评级
    max_score = sum(len(d['checks']) for d in dimensions.values())
    percentage = total_score / max_score * 100
    rating = 'A' if percentage >= 80 else 'B' if percentage >= 60 else 'C' if percentage >= 40 else 'D'
    
    return {
        'file': research_file,
        'dimensions': {k: {'score': v['score'], 'checks': [c[0] for c in v['checks'] if c[1]]} for k, v in dimensions.items()},
        'total_score': f"{total_score}/{max_score}",
        'percentage': f"{percentage:.1f}%",
        'rating': rating,
        'pass': rating in ['A', 'B']
    }

def main():
    if len(sys.argv) < 2:
        print("用法: python3 research-quality-check.py <research.md>")
        return
    result = assess_quality(sys.argv[1])
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
