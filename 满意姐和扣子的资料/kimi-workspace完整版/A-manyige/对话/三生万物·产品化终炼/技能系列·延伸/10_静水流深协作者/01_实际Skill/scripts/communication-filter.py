#!/usr/bin/env python3
"""沟通姿态过滤器 - 约束AI输出姿态"""
import sys, re, json
from pathlib import Path
from datetime import datetime

# 姿态模式库
FORBIDDEN_PATTERNS = {
    '建议型': [
        r'我建议您', r'建议您', r'建议你可以', r'不妨考虑', r'可以考虑',
        r'最好能够', r'建议你', r'建议可以', r'你可以考虑'
    ],
    '请教型': [
        r'请问您', r'不知道您', r'您是否', r'能否请您', r'您是否愿意',
        r'不知道您是否', r'想请教您', r'想请问'
    ],
    '关心型': [
        r'祝您', r'希望您', r'愿您', r'期待您', r'相信您',
        r'祝您顺利', r'祝您成功', r'希望对你有帮助', r'希望能帮到您'
    ]
}

# 白名单场景（允许使用）
WHITELIST_CONTEXTS = [
    '用户要求建议', '明确要求', '教程', '教学', '指导',
    '书信格式', '正式信函'
]

def filter_communication(text, level='standard', context=''):
    findings = []
    filtered_text = text
    
    # 检查是否在白名单
    is_whitelisted = any(wc in context for wc in WHITELIST_CONTEXTS)
    
    if not is_whitelisted:
        for category, patterns in FORBIDDEN_PATTERNS.items():
            for pattern in patterns:
                matches = list(re.finditer(pattern, filtered_text, re.IGNORECASE))
                for match in matches:
                    findings.append({
                        'category': category,
                        'pattern': pattern,
                        'matched_text': match.group(),
                        'position': match.start(),
                        'severity': 'high' if level == 'strict' else 'medium'
                    })
                
                # 替换（严格级）或标记（标准级）
                if level == 'strict':
                    filtered_text = re.sub(pattern, '[已过滤]', filtered_text, flags=re.IGNORECASE)
                elif level == 'standard':
                    filtered_text = re.sub(pattern, lambda m: f"[待校准:{m.group()}]", filtered_text)
    
    # 统计
    stats = {
        'total_findings': len(findings),
        'by_category': {
            '建议型': len([f for f in findings if f['category'] == '建议型']),
            '请教型': len([f for f in findings if f['category'] == '请教型']),
            '关心型': len([f for f in findings if f['category'] == '关心型'])
        },
        'filter_rate': len(findings) / max(len(text.split()), 1) * 100
    }
    
    # 评级
    if level == 'strict':
        rating = 'PASS' if len(findings) == 0 else 'FAIL'
    else:
        rating = 'PASS' if len(findings) <= 2 else 'WARN' if len(findings) <= 5 else 'FAIL'
    
    return {
        'filtered_at': datetime.now().isoformat(),
        'level': level,
        'context': context,
        'is_whitelisted': is_whitelisted,
        'findings': findings,
        'stats': stats,
        'rating': rating,
        'original_length': len(text),
        'filtered_length': len(filtered_text),
        'filtered_text': filtered_text if level == 'strict' else None
    }

def main():
    if len(sys.argv) < 2:
        print("用法: python3 communication-filter.py --input draft.md [--level standard|strict|loose] [--context '场景说明']")
        return
    
    # 解析参数
    input_file = ''
    level = 'standard'
    context = ''
    
    for i, arg in enumerate(sys.argv):
        if arg == '--input' and i+1 < len(sys.argv):
            input_file = sys.argv[i+1]
        if arg == '--level' and i+1 < len(sys.argv):
            level = sys.argv[i+1]
        if arg == '--context' and i+1 < len(sys.argv):
            context = sys.argv[i+1]
    
    if not input_file:
        print("错误: 必须指定 --input")
        return
    
    text = Path(input_file).read_text(encoding='utf-8', errors='ignore')
    result = filter_communication(text, level, context)
    
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
