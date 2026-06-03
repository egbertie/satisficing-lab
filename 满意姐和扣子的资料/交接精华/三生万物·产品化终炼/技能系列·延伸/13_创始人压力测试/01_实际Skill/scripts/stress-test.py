#!/usr/bin/env python3
"""创始人压力测试 - 模拟拷问"""
import sys, json
from datetime import datetime

def generate_stress_test(project, stage='seed', level='standard'):
    # 问题库
    question_bank = {
        '商业模式': [
            '你的护城河是什么？',
            '如果BAT抄你怎么办？',
            '收入模式验证了吗？'
        ],
        '财务预测': [
            '如果收入只有预测的30%怎么办？',
            '烧钱率是多少？ runway多长？',
            '单位经济模型算过吗？'
        ],
        '团队风险': [
            '如果CTO离职你怎么办？',
            '你们三个创始人怎么分工？',
            '股权结构合理吗？'
        ],
        '竞争格局': [
            '市面上已经有5家在做，你凭什么？',
            '如果巨头免费做，你怎么办？',
            '技术壁垒有多高？'
        ]
    }
    
    counts = {'gentle': 10, 'standard': 20, 'hard': 30}
    count = counts.get(level, 20)
    
    # 生成问题列表
    questions = []
    for category, qs in question_bank.items():
        for q in qs:
            questions.append({'category': category, 'question': q, 'difficulty': 'medium'})
    
    selected = questions[:count]
    
    return {
        'generated_at': datetime.now().isoformat(),
        'project': project,
        'stage': stage,
        'level': level,
        'question_count': len(selected),
        'questions': selected,
        'instruction': '请逐题回答，要求：1. 30秒内组织语言 2. 用数据支撑 3. 承认不知道的比瞎说好'
    }

def main():
    if len(sys.argv) < 2:
        print("用法: python3 stress-test.py --project '项目名' [--stage seed|a|b] [--level gentle|standard|hard]")
        return
    result = generate_stress_test(sys.argv[1])
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
