#!/usr/bin/env python3
"""信源验证器 - 交叉验证研究来源"""
import sys, json, re
from pathlib import Path
from datetime import datetime

def validate_sources(sources_file):
    """验证信源质量"""
    text = Path(sources_file).read_text(encoding='utf-8', errors='ignore')
    
    # 简单启发式验证
    checks = {
        'has_url': bool(re.search(r'https?://', text)),
        'has_date': bool(re.search(r'20\d{2}[-/年]', text)),
        'has_author': bool(re.search(r'作者|撰文|来源[:：]', text)),
        'source_count': len(re.findall(r'https?://[^\s]+', text)),
        'gov_cn_count': len(re.findall(r'\.gov\.cn', text)),
        'edu_count': len(re.findall(r'\.edu', text))
    }
    
    # 评级
    score = 0
    if checks['has_url']: score += 2
    if checks['has_date']: score += 2
    if checks['has_author']: score += 1
    score += min(checks['source_count'], 5)  # 最多5分
    score += checks['gov_cn_count'] * 2  # 政府来源加权
    score += checks['edu_count'] * 2  # 学术来源加权
    
    rating = 'A' if score >= 15 else 'B' if score >= 10 else 'C' if score >= 5 else 'D'
    
    return {
        'validated_at': datetime.now().isoformat(),
        'file': sources_file,
        'checks': checks,
        'score': score,
        'rating': rating,
        'recommendation': '信源可靠，可使用' if rating in ['A','B'] else '建议补充更多权威来源'
    }

def main():
    if len(sys.argv) < 2:
        print("用法: python3 source-validator.py <sources.md>")
        return
    result = validate_sources(sys.argv[1])
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
