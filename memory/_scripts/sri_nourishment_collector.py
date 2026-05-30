#!/usr/bin/env python3
"""
SRI 知识养料采集引擎 v1.0
==========================
基于 CODE (Capture→Organize→Distill→Express) 框架，
自动化采集、过滤、提炼外部信息，转化为内部知识资产。

被 Cron 每日调用。
Phase 1: 利用现有 Inkwell 数据 + 飞书数据（不做新爬虫，减少复杂度）
Phase 2: 增加 GitHub/arXiv/竞品 API 源
"""

import json
import os
from datetime import datetime, timezone
from collections import Counter

WORKSPACE = os.environ.get('SRI_WORKSPACE', os.path.expanduser('~/.openclaw/workspace'))
DATA_FILE = os.path.join(WORKSPACE, 'memory/_data/entities_index.json')
NOURISHMENT_DIR = os.path.join(WORKSPACE, 'memory/nourishment')

# 满意红的领域关键词——用于过滤相关性
SRI_DOMAINS = {
    '创始人与合伙人': ['founder', 'co-founder', 'partnership', '创业', '创始人', '合伙人', 'startup',
                   'equity split', '股权分配', 'vesting', 'cofounder conflict', 'partner dispute'],
    '组织与团队': ['team', 'culture', '组织', '团队', '管理', 'leadership', 'remote work',
                  'psychological safety', '心理安全', 'decision making', 'OKR', '绩效'],
    '决策科学': ['decision', '决策', 'bias', 'cognitive', '认知偏差', 'choice architecture',
                'behavioral economics', '博弈', 'game theory', 'scenario planning'],
    '产品与体验': ['product management', 'UX', 'usability', '产品设计', '用户体验', 'JTBD',
                  'onboarding', 'activation', 'retention', 'PLG', 'product-led', '前端', 'frontend',
                  'UI', 'dashboard', '交互', '性能优化', 'design system'],
    '知识与学习': ['knowledge management', '知识管理', 'learning', 'second brain', 'PKM',
                  'memory', 'cognitive load', 'mental model', '思维模型', '经验总结', '教训',
                  '复盘', '方法论', '架构', '范式', '框架', '模式', '系统设计', '信息架构'],
    'AI与自动化': ['AI agent', 'LLM', 'automation', 'autonomous', 'agentic', 'cursor',
                  'claude code', 'coding agent', 'prompt engineering', 'RAG', '飞轮', 'auto',
                  'self-healing', 'cron', 'agent', 'bot', '自动化', '推理', '流水线'],
    '安全与治理': ['security', '安全', '免疫', 'governance', '治理', '合规', '审计',
                  'monitoring', '权限', '认证', 'risk', '威胁', '防御', '防护', '韧性']
}


def load_inbox():
    """加载 Inkwell 阅读数据（来自 Coze API 或本地缓存）"""
    # 读取 Inkwell 数据
    inkwell_file = os.path.join(WORKSPACE, 'memory/_data/inkwell_reading_log.json')
    if os.path.exists(inkwell_file):
        with open(inkwell_file, 'r') as f:
            return json.load(f)
    return []


def load_memory_deep():
    """加载 memory/deep/ 中的深度笔记"""
    deep_dir = os.path.join(WORKSPACE, 'memory/deep')
    if not os.path.exists(deep_dir):
        return []
    notes = []
    for fname in os.listdir(deep_dir):
        if fname.endswith('.md'):
            fpath = os.path.join(deep_dir, fname)
            with open(fpath, 'r', encoding='utf-8') as f:
                content = f.read()
            notes.append({
                'file': fname,
                'size': len(content),
                'first_line': content.split('\n')[0][:100] if content else ''
            })
    return notes


def classify_relevance(text, title=''):
    """评定信息与满意红的相关性"""
    text_lower = (text + ' ' + title).lower()
    score = 0
    matched_domains = []

    for domain, keywords in SRI_DOMAINS.items():
        domain_score = 0
        for kw in keywords:
            if kw.lower() in text_lower:
                domain_score += 1
        if domain_score > 0:
            matched_domains.append(domain)
            score += domain_score * 2

    return min(100, score * 5), matched_domains


def collect_nourishment_batch(dry_run=False):
    """执行一轮养料采集流水线"""
    os.makedirs(NOURISHMENT_DIR, exist_ok=True)
    now = datetime.now(timezone.utc)
    batch = {
        'collected_at': now.isoformat(),
        'dry_run': dry_run,
        'sources_checked': [],
        'items': [],
        'stats': {'total_sources': 0, 'relevant': 0, 'ingested': 0}
    }

    # ============================================
    # Phase 1: 利用现有数据源
    # ============================================

    # 1. Inkwell 阅读数据
    inkwell = load_inbox()
    if inkwell:
        batch['sources_checked'].append({'name': 'Inkwell RSS', 'items': len(inkwell), 'status': 'ok'})
        for item in inkwell[:20]:  # 处理最近20条
            title = item.get('title', '') if isinstance(item, dict) else str(item)[:100]
            score, domains = classify_relevance(title)
            if score >= 30:
                batch['items'].append({
                    'source': 'Inkwell',
                    'title': title[:120],
                    'relevance_score': score,
                    'domains': domains,
                    'url': item.get('url', '') if isinstance(item, dict) else '',
                    'collected_at': now.isoformat()
                })
                batch['stats']['relevant'] += 1
    else:
        batch['sources_checked'].append({'name': 'Inkwell RSS', 'items': 0, 'status': 'no_data'})

    # 2. memory/deep/ 中的深度笔记
    deep_notes = load_memory_deep()
    if deep_notes:
        batch['sources_checked'].append({'name': 'memory/deep/', 'items': len(deep_notes), 'status': 'ok'})
        batch['stats']['total_sources'] += len(deep_notes)
        for note in deep_notes:
            score, domains = classify_relevance(note['first_line'], note['file'])
            if score >= 20:
                batch['items'].append({
                    'source': 'memory/deep',
                    'title': note['file'],
                    'relevance_score': score,
                    'domains': domains,
                    'local_file': note['file'],
                    'collected_at': now.isoformat()
                })
                batch['stats']['relevant'] += 1

    # 3. entities_index 中的新文档
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    docs = data.get('documents', [])
    recent_docs = sorted(
        [d for d in docs if isinstance(d, dict) and d.get('detected_at')],
        key=lambda d: d.get('detected_at', ''), reverse=True
    )[:20]

    if recent_docs:
        batch['sources_checked'].append({'name': 'entities_index/documents', 'items': len(recent_docs), 'status': 'ok'})
        for doc in recent_docs:
            name = doc.get('name', '')
            score, domains = classify_relevance(name)
            if score >= 20:
                batch['items'].append({
                    'source': '文档库',
                    'title': name[:120],
                    'relevance_score': score,
                    'domains': domains,
                    'entity_id': doc.get('id', '?'),
                    'collected_at': now.isoformat()
                })
                batch['stats']['relevant'] += 1

    batch['stats']['ingested'] = len(batch['items'])

    # 保存批次到 nourishment 目录
    if not dry_run and batch['items']:
        batch_id = now.strftime('%Y%m%d_%H%M')
        batch_file = os.path.join(NOURISHMENT_DIR, 'batch_{}.json'.format(batch_id))
        with open(batch_file, 'w', encoding='utf-8') as f:
            json.dump(batch, f, ensure_ascii=False, indent=2)

    # 更新 entities_index meta
    if not dry_run:
        if 'meta' not in data:
            data['meta'] = {}
        if 'nourishment' not in data['meta']:
            data['meta']['nourishment'] = {'batches': [], 'total_items': 0, 'last_collected': None}

        data['meta']['nourishment']['batches'].append({
            'batch_id': now.strftime('%Y%m%d_%H%M'),
            'items': batch['stats']['ingested'],
            'collected_at': now.isoformat()
        })
        # 只保留最近30批
        data['meta']['nourishment']['batches'] = data['meta']['nourishment']['batches'][-30:]
        data['meta']['nourishment']['total_items'] += batch['stats']['ingested']
        data['meta']['nourishment']['last_collected'] = now.isoformat()

        # 养料统计
        domain_counts = Counter()
        for item in batch['items']:
            for d in item.get('domains', []):
                domain_counts[d] += 1
        data['meta']['nourishment']['domain_stats'] = dict(domain_counts)

        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    return batch


def print_report(batch):
    """打印采集报告"""
    print("=" * 60)
    print("SRI 知识养料采集报告")
    print("=" * 60)
    print("时间: {}".format(batch['collected_at'][:19]))
    print("模式: {}".format('DRY RUN' if batch.get('dry_run') else '已执行'))

    # 来源检查
    print("\n📡 来源检查:")
    for src in batch.get('sources_checked', []):
        icon = '✅' if src['status'] == 'ok' else '⚠️'
        print("  {} {}: {} 项".format(icon, src['name'], src['items']))

    # 统计
    s = batch['stats']
    print("\n📊 采集统计:")
    print("  总扫描: {} 条".format(s.get('total_sources', 0)))
    print("  相关: {} 条 (过滤后)".format(s.get('relevant', 0)))
    print("  摄入: {} 条".format(s.get('ingested', 0)))

    # 领域分布
    domain_counts = Counter()
    for item in batch.get('items', []):
        for d in item.get('domains', []):
            domain_counts[d] += 1

    if domain_counts:
        print("\n🏷️ 领域分布:")
        for domain, count in domain_counts.most_common():
            bar = '█' * min(count, 30)
            print("  {}: {} {}".format(count, bar, domain))

    # Top 条目
    top = sorted(batch.get('items', []), key=lambda x: x.get('relevance_score', 0), reverse=True)[:5]
    if top:
        print("\n⭐ 最高相关性:")
        for item in top:
            print("  [{}分] {} (来源: {})".format(
                item.get('relevance_score', 0),
                item.get('title', '?')[:60],
                item.get('source', '?')))


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser(description='SRI 知识养料采集引擎')
    p.add_argument('--dry-run', action='store_true')
    p.add_argument('--save', action='store_true')
    args = p.parse_args()

    batch = collect_nourishment_batch(dry_run=not args.save)
    print_report(batch)
