#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""任务路由器 - 根据任务内容判断最佳协同模式

增强版：支持多关键词匹配、置信度评分、混合模式建议
用法: python3 task-router.py "任务描述" [--verbose]
"""
import sys

KEYWORDS = {
    'mode_c_blue': ['审计','检查','复盘','审查','验证','风控','合规','安全','红线'],
    'mode_b_parallel': ['决策','评估','选择','判断','投','并购','合伙','定价','战略'],
    'mode_a_sequential': ['写','创作','生成','制作','整理','归档','清理','备份']
}

def route_task(task_description, verbose=False):
    task = task_description.lower()
    scores = {'C': 0, 'B': 0, 'A': 0}
    
    for k in KEYWORDS['mode_c_blue']:
        if k in task: scores['C'] += 1
    for k in KEYWORDS['mode_b_parallel']:
        if k in task: scores['B'] += 1
    for k in KEYWORDS['mode_a_sequential']:
        if k in task: scores['A'] += 1
    
    if scores['C'] > 0:
        mode = '模式C（蓝军主导审计）'
        confidence = min(scores['C'] * 25, 100)
    elif scores['B'] > 0:
        mode = '模式B（并行协同-决策需双视角）'
        confidence = min(scores['B'] * 25, 100)
    elif scores['A'] > 0:
        mode = '模式A（顺序协同-先流程后审计）'
        confidence = min(scores['A'] * 25, 100)
    else:
        mode = '模式A（顺序协同-默认）'
        confidence = 50
    
    if verbose:
        return f"""[任务路由结果]
任务: {task_description}
模式: {mode}
置信度: {confidence}%
得分详情: C={scores['C']} B={scores['B']} A={scores['A']}
建议: 按{mode}执行，如遇冲突使用conflict-resolver.py裁决"""
    return mode

if __name__ == '__main__':
    if len(sys.argv) > 1:
        verbose = '--verbose' in sys.argv
        task_desc = ' '.join([a for a in sys.argv[1:] if not a.startswith('--')])
        print(route_task(task_desc, verbose))
    else:
        print(__doc__)
