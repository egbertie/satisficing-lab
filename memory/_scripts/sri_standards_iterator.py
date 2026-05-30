#!/usr/bin/env python3
"""
SRI 标准自动迭代引擎 v1.0
===========================
基于新摄入的知识养料 (nourishment batches)，
自动对比现有产品审核标准 (sri_product_standards_v2.json)，
发现差距 → 生成迭代提案 → 自动审计所有产品。

被飞轮引擎 health() 调用。
"""

import json
import os
from datetime import datetime, timezone
from collections import Counter

WORKSPACE = os.environ.get('SRI_WORKSPACE', os.path.expanduser('~/.openclaw/workspace'))
DATA_FILE = os.path.join(WORKSPACE, 'memory/_data/entities_index.json')
STANDARDS_FILE = os.path.join(WORKSPACE, 'memory/_data/sri_product_standards_v2.json')
NOURISHMENT_DIR = os.path.join(WORKSPACE, 'memory/nourishment')

# 标准→养料领域映射 (用于判断新知识是否影响特定标准)
STANDARD_TO_DOMAIN = {
    'completeness': ['产品与体验', '安全与治理'],
    'usability': ['产品与体验', 'AI与自动化'],
    'clarity': ['产品与体验', '知识与学习'],
    'aesthetics': ['产品与体验'],
    'uniqueness': ['创始人与合伙人', '决策科学'],
    'maintainability': ['AI与自动化', '知识与学习']
}


def load_recent_nourishment(days=7):
    """加载最近的养料批次"""
    items = []
    if not os.path.exists(NOURISHMENT_DIR):
        return items
    
    cutoff = datetime.now(timezone.utc).timestamp() - days * 86400
    for fname in sorted(os.listdir(NOURISHMENT_DIR), reverse=True):
        if not fname.endswith('.json'):
            continue
        fpath = os.path.join(NOURISHMENT_DIR, fname)
        mtime = os.path.getmtime(fpath)
        if mtime < cutoff:
            continue
        try:
            with open(fpath, 'r') as f:
                batch = json.load(f)
            items.extend(batch.get('items', []))
        except:
            pass
    return items


def propose_standard_updates(nourishment_items, current_standards):
    """基于新养料，生成标准更新提案"""
    proposals = []
    now = datetime.now(timezone.utc)

    # 统计养料覆盖的领域
    domain_hits = Counter()
    for item in nourishment_items:
        for d in item.get('domains', []):
            domain_hits[d] += 1

    # 检查每个标准维度是否需要审查
    sri_dim = current_standards.get('sri_six_dimensions', {})
    for dim_key, dim_info in sri_dim.items():
        relevant_domains = STANDARD_TO_DOMAIN.get(dim_key, [])
        hits = sum(domain_hits.get(d, 0) for d in relevant_domains)
        
        # 该维度有相关养料涌入 → 建议审查
        if hits >= 3:
            proposals.append({
                'dimension': dim_key,
                'label': dim_info.get('label', dim_key),
                'action': 'review',
                'reason': '{}条相关新知识·建议审查权重/评分规则'.format(hits),
                'current_weight': dim_info.get('weight'),
                'triggered_at': now.isoformat()
            })
        
        # 该维度长期无养料 → 可能被忽视
        elif domain_hits and hits == 0:
            proposals.append({
                'dimension': dim_key,
                'label': dim_info.get('label', dim_key),
                'action': 'attention',
                'reason': '近7天无相关新知识·该维度可能被忽视',
                'triggered_at': now.isoformat()
            })

    return proposals


def audit_products_against_standards(data, dry_run=False):
    """标准变更后，重新审计所有产品"""
    products = [p for p in data.get('products', []) 
                if isinstance(p, dict) and p.get('status') not in ('已下架', '资料·归入知识库')]
    
    changes = []
    for p in products:
        old_score = p.get('sri_score', 0)
        # 这里调用 lifecycle_manager 中的评分逻辑
        from sri_lifecycle_manager import calculate_sri_score, classify_product_type
        ptype = classify_product_type(p)
        new_score = calculate_sri_score(p, ptype)
        
        if abs(new_score - old_score) > 2:  # 变化>2分才记录
            p['sri_score'] = new_score
            if not dry_run:
                p['standards_version'] = '2.0.1'  # 标准迭代版本号
            
            changes.append({
                'product_id': p.get('id', '?'),
                'product_name': p.get('name', '?')[:40],
                'old_score': old_score,
                'new_score': new_score,
                'delta': round(new_score - old_score, 1)
            })

    return changes


def run_standards_iteration(dry_run=False):
    """执行一轮标准迭代检查"""
    now = datetime.now(timezone.utc)

    # 加载
    items = load_recent_nourishment()
    
    if os.path.exists(STANDARDS_FILE):
        with open(STANDARDS_FILE) as f:
            standards = json.load(f)
    else:
        standards = {'sri_six_dimensions': {}}

    proposals = propose_standard_updates(items, standards)

    # 更新 entities_index
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if 'meta' not in data:
        data['meta'] = {}

    data['meta']['standards_iteration'] = {
        'checked_at': now.isoformat(),
        'nourishment_items_scanned': len(items),
        'proposals': len(proposals),
        'proposals_detail': proposals,
        'standards_version': standards.get('version', '?')
    }

    if not dry_run:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    return {
        'checked_at': now.isoformat(),
        'dry_run': dry_run,
        'nourishment_items': len(items),
        'proposals': proposals
    }


def print_report(report):
    print("=" * 60)
    print("SRI 标准自动迭代报告")
    print("=" * 60)
    print("时间: {}".format(report['checked_at'][:19]))
    print("养料: {} 条".format(report['nourishment_items']))
    print("提案: {} 条".format(len(report['proposals'])))

    for p in report['proposals']:
        icon = '📝' if p['action'] == 'review' else '⚠️'
        print("  {} {}: {} (权重:{})".format(icon, p['label'], p['reason'], p.get('current_weight', '?')))


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser(description='SRI 标准自动迭代引擎')
    p.add_argument('--dry-run', action='store_true')
    p.add_argument('--save', action='store_true')
    args = p.parse_args()

    report = run_standards_iteration(dry_run=not args.save)
    print_report(report)
