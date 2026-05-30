#!/usr/bin/env python3
"""
SRI 约束突破引擎 v1.0
======================
基于 Goldratt 约束理论 (Theory of Constraints):
1. 识别系统瓶颈 — 34条死链的根因
2. 全力利用瓶颈 — 把约束的产能用到极致
3. 所有环节服从瓶颈 — 系统的速度 = 瓶颈的速度
4. 打破瓶颈 — 增加瓶颈容量
5. 重复 — 下一个瓶颈浮现

当前瓶颈: LLM替身评分数据不足
- 仅15/172产品有替身评分
- 导致8条化学反应链休眠
- 这些休眠链正是最高价值的高烈度反应

突破方案: 批量触发替身评分 (不是Cron等·是主动出击)
"""

import json, os, sys
from datetime import datetime, timezone
from collections import defaultdict

WORKSPACE = os.environ.get('SRI_WORKSPACE', os.path.expanduser('~/.openclaw/workspace'))
DATA_FILE = os.path.join(WORKSPACE, 'memory/_data/entities_index.json')


def identify_bottlenecks(data):
    """Goldratt Step 1-2: 识别并量化瓶颈"""
    now = datetime.now(timezone.utc)
    
    products = [p for p in data.get('products', [])
                if isinstance(p, dict) and p.get('status') not in ('已下架', '资料·归入知识库')]
    avatars = data.get('avatars', [])
    cogs = data.get('cognition_events', [])
    connections = data.get('connections', [])
    
    # 瓶颈1: LLM评分覆盖率
    total_products = len(products)
    rated_products = len(set(c.get('entity_id', '') for c in cogs if isinstance(c, dict) and c.get('entity_id')))
    llm_coverage = round(100 * rated_products / max(1, total_products), 1)
    
    # 瓶颈2: 产品间连接密度
    connected_products = set()
    for conn in connections:
        if isinstance(conn, dict):
            if conn.get('source_id'): connected_products.add(conn['source_id'])
            if conn.get('target_id'): connected_products.add(conn['target_id'])
    connection_coverage = round(100 * len(connected_products) / max(1, total_products), 1)
    
    # 瓶颈3: 替身激活率
    active_avatars = len(set(c.get('evaluator', '') for c in cogs if isinstance(c, dict) and c.get('evaluator')))
    avatar_activation = round(100 * active_avatars / max(1, len(avatars)), 1)
    
    # 瓶颈4: 死链数量
    chem_results = data.get('meta', {}).get('chemistry', {}).get('results', {})
    dead_chains = sum(1 for r in chem_results.values() if r.get('effect', 0) == 0)
    total_chains = len(chem_results)
    
    # 计算最紧迫瓶颈
    bottlenecks = [
        {'name': 'LLM评分覆盖率', 'current': llm_coverage, 'target': 30, 'gap': 30 - llm_coverage, 'priority': 1},
        {'name': '产品连接密度', 'current': connection_coverage, 'target': 50, 'gap': 50 - connection_coverage, 'priority': 2},
        {'name': '替身激活率', 'current': avatar_activation, 'target': 50, 'gap': 50 - avatar_activation, 'priority': 3},
        {'name': '死链率', 'current': round(100 * dead_chains / max(1, total_chains), 1), 'target': 30, 'gap': round(100 * dead_chains / max(1, total_chains)) - 30, 'priority': 4},
    ]
    
    # 找最大约束
    primary_bottleneck = max(bottlenecks, key=lambda b: b['gap'])
    
    return {
        'identified_at': now.isoformat(),
        'primary_bottleneck': primary_bottleneck,
        'bottlenecks': bottlenecks,
        'dead_chains_detail': [
            {'chain': k, 'name': v.get('name','?'), 'needs': 
             'llm_data' if k in ('crystallize','equilibrium','compound','superposition','avatar_compound','avatar_osmosis','avatar_catalyst','avatar_spin','avatar_field')
             else ('connections' if k in ('gradient','chain','osmosis','fission','tracer')
             else ('score_diversity' if k in ('redox','explosion','combustion','phase','precipitation','symmetry','termination')
             else 'other'))}
            for k, v in chem_results.items() if v.get('effect', 0) == 0
        ]
    }


def generate_bottleneck_action_plan(bottleneck_report, data):
    """Goldratt Step 3-4: 生成突破行动计划"""
    products = [p for p in data.get('products', [])
                if isinstance(p, dict) and p.get('status') not in ('已下架', '资料·归入知识库')]
    
    # 哪些产品最需要评分
    unscored = [p for p in products if not p.get('llm_rating')]
    # 优先级: 精品 > 有包装层 > 有审计分 > 其他
    unscored.sort(key=lambda p: (
        p.get('status', '') == '精品',
        p.get('positioning') is not None,
        p.get('audit_score', 0)
    ), reverse=True)
    
    # 生成批次
    batch_size = 5
    batches = []
    for i in range(0, min(len(unscored), 25), batch_size):
        batch = unscored[i:i+batch_size]
        batches.append({
            'batch_id': i // batch_size + 1,
            'products': [{'id': p['id'], 'name': p.get('name', '')[:30], 'family': p.get('family', '')} for p in batch],
            'product_count': len(batch),
            'estimated_avatar_count': min(5, len(data.get('avatars', []))),
            'total_evaluations': len(batch) * min(5, len(data.get('avatars', [])))
        })
    
    return {
        'primary_action': '批量LLM替身评分·突破覆盖率瓶颈',
        'batches': batches,
        'total_evaluations_needed': sum(b['total_evaluations'] for b in batches),
        'estimated_chains_to_activate': 8,  # 这8条链会在评分数据到位后自动激活
        'impact': '评分覆盖率每+10%·激活约3条休眠化学反应链'
    }


def run_bottleneck_breakthrough(dry_run=False):
    """执行约束突破分析·识别瓶颈·生成计划"""
    now = datetime.now(timezone.utc)
    
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Step 1-2: 识别瓶颈
    bottleneck_report = identify_bottlenecks(data)
    
    # Step 3-4: 生成行动计划
    action_plan = generate_bottleneck_action_plan(bottleneck_report, data)
    
    # 保存
    if 'meta' not in data:
        data['meta'] = {}
    
    data['meta']['bottleneck_analysis'] = {
        'executed_at': now.isoformat(),
        'primary_bottleneck': bottleneck_report['primary_bottleneck'],
        'action_plan': {
            'primary_action': action_plan['primary_action'],
            'total_evaluations_needed': action_plan['total_evaluations_needed'],
            'estimated_chains_to_activate': action_plan['estimated_chains_to_activate'],
            'batch_count': len(action_plan['batches']),
        }
    }
    
    if not dry_run:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    return {
        **bottleneck_report,
        'action_plan': action_plan
    }


def print_report(report):
    print("=" * 60)
    print("🎯 SRI 约束突破分析 · Goldratt TOC")
    print("=" * 60)
    print("时间:", report['identified_at'][:19])
    
    pb = report['primary_bottleneck']
    print(f"\n🔴 最大瓶颈: {pb['name']}")
    print(f"   当前: {pb['current']}% · 目标: {pb['target']}% · 差距: {pb['gap']}%")
    
    print(f"\n📊 全部瓶颈:")
    for b in report['bottlenecks']:
        icon = '🔴' if b['name'] == pb['name'] else '🟡'
        bar = '█' * int(b['current']) + '░' * (100 - int(b['current']))
        print(f"  {icon} {b['name']}: {b['current']}% (目标{b['target']}%)")
    
    ap = report['action_plan']
    print(f"\n🎯 行动计划:")
    print(f"  {ap['primary_action']}")
    print(f"  需评分: {ap['total_evaluations_needed']} 次")
    print(f"  预计激活: {ap['estimated_chains_to_activate']} 条休眠链")
    print(f"  批次: {len(ap['batches'])} 批")
    print(f"  效应: {ap['impact']}")


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--dry-run', action='store_true')
    p.add_argument('--save', action='store_true')
    args = p.parse_args()
    
    report = run_bottleneck_breakthrough(dry_run=not args.save)
    print_report(report)
