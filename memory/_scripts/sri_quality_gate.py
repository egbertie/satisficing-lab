#!/usr/bin/env python3
"""
SRI 信息质量门禁 v1.0
======================
对每条摄入的知识养料做三道质量检查:
1. 相关性 (domain match)
2. 新鲜度 (recency)
3. 权威度 (source credibility)

综合分 ≥ 阈值 → 通过 · 进入知识库
综合分 < 阈值 → 标记为"待验证" · 不自动入库
"""

import json, os, re
from datetime import datetime, timezone

WORKSPACE = os.environ.get('SRI_WORKSPACE', os.path.expanduser('~/.openclaw/workspace'))
NOURISHMENT_DIR = os.path.join(WORKSPACE, 'memory/nourishment')

# 来源权威度评分
SOURCE_CREDIBILITY = {
    'Nature': 98,
    'Science': 98,
    'arXiv': 85,
    'Nielsen Norman Group': 95,
    'Baymard Institute': 93,
    'McKinsey': 90,
    'HBR': 88,
    'MIT': 90,
    'Stanford': 90,
    'Google AI': 88,
    'Anthropic': 85,
    'Stratechery': 80,
    'First Round Review': 78,
    'a16z': 75,
    'Medium': 50,
    'Substack': 55,
    'Twitter/X': 30,
    'LinkedIn': 40,
    'Reddit': 25,
    'memory/deep': 70,
    'Inkwell': 65,
    '文档库': 60,
    'default': 50
}

# 领域权威度修正 (特定来源在该领域有高权威)
DOMAIN_AUTHORITY_BONUS = {
    ('产品与体验', 'Nielsen Norman Group'): 5,
    ('产品与体验', 'Baymard Institute'): 5,
    ('决策科学', 'HBR'): 5,
    ('AI与自动化', 'Anthropic'): 5,
    ('知识与学习', 'MIT'): 3,
}


def score_credibility(source):
    """评估来源权威度"""
    for key, score in SOURCE_CREDIBILITY.items():
        if key.lower() in source.lower():
            return score
    return SOURCE_CREDIBILITY['default']


def score_quality(item):
    """综合质量评分: 相关性×新鲜度×权威度"""
    issues = []
    
    # 1. 相关性 (已由采集器评分)
    relevance = item.get('relevance_score', 0)
    if relevance < 15:
        issues.append('相关性过低({})'.format(relevance))
    
    # 2. 新鲜度检查
    collected = item.get('collected_at', '')
    is_fresh = True
    if collected:
        try:
            dt = datetime.fromisoformat(collected)
            days_ago = (datetime.now(timezone.utc) - dt).days
            if days_ago > 7:
                issues.append('数据{}天前·可能过时'.format(days_ago))
                is_fresh = False
        except:
            pass
    
    # 3. 权威度评分
    source = item.get('source', 'default')
    credibility = score_credibility(source)
    
    # 领域修正
    domains = item.get('domains', [])
    for d in domains:
        bonus = DOMAIN_AUTHORITY_BONUS.get((d, source), 0)
        credibility += bonus
    
    # 综合分
    freshness_factor = 1.0 if is_fresh else 0.7
    quality_score = round((relevance * 0.4 + credibility * 0.4) * freshness_factor, 1)
    
    quality_score = min(100, quality_score)
    
    return {
        'quality_score': quality_score,
        'credibility': credibility,
        'is_fresh': is_fresh,
        'issues': issues,
        'verdict': 'pass' if quality_score >= 30 else 'reject'
    }


def gate_check_batch(batch_file):
    """对一个批次的养料做质量门禁"""
    if not os.path.exists(batch_file):
        return {'error': 'batch not found'}
    
    with open(batch_file, 'r') as f:
        batch = json.load(f)
    
    results = []
    passed = 0
    rejected = 0
    
    for item in batch.get('items', []):
        quality = score_quality(item)
        item['quality'] = quality
        if quality['verdict'] == 'pass':
            passed += 1
        else:
            rejected += 1
        results.append({'title': item.get('title', '')[:60], **quality})
    
    batch['quality_gate'] = {
        'checked_at': datetime.now(timezone.utc).isoformat(),
        'total': len(results),
        'passed': passed,
        'rejected': rejected
    }
    
    # 保存
    with open(batch_file, 'w') as f:
        json.dump(batch, f, ensure_ascii=False, indent=2)
    
    return batch['quality_gate']


def run_quality_gate(dry_run=False):
    """对最新批次运行质量门禁"""
    now = datetime.now(timezone.utc)
    
    # 找最新批次
    if not os.path.exists(NOURISHMENT_DIR):
        return {'error': 'no nourishment dir'}
    
    batches = sorted([f for f in os.listdir(NOURISHMENT_DIR) if f.endswith('.json')], reverse=True)
    if not batches:
        return {'error': 'no batches'}
    
    latest = os.path.join(NOURISHMENT_DIR, batches[0])
    
    if dry_run:
        with open(latest) as f:
            batch = json.load(f)
        results = []
        for item in batch.get('items', []):
            q = score_quality(item)
            results.append(q['verdict'])
        return {
            'batch': batches[0],
            'dry_run': True,
            'total': len(results),
            'passed': results.count('pass'),
            'rejected': results.count('reject')
        }
    
    gate = gate_check_batch(latest)
    
    # 更新 entities_index
    import sys; sys.path.insert(0, os.path.join(WORKSPACE, 'memory/_scripts'))
    DATA_FILE = os.path.join(WORKSPACE, 'memory/_data/entities_index.json')
    with open(DATA_FILE) as f:
        data = json.load(f)
    
    if 'meta' not in data: data['meta'] = {}
    data['meta']['quality_gate'] = {
        'checked_at': now.isoformat(),
        **gate
    }
    
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return gate


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--dry-run', action='store_true')
    p.add_argument('--save', action='store_true')
    args = p.parse_args()
    
    result = run_quality_gate(dry_run=not args.save)
    print("SRI 信息质量门禁")
    print("=" * 40)
    for k, v in result.items():
        print("  {}: {}".format(k, v))
