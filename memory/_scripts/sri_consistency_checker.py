#!/usr/bin/env python3
"""
SRI 实体去重与一致性检查器 v1.0
================================
自动检测 entities_index 中的:
1. 重复实体 (同名产品·同URL·同源文件)
2. 孤儿实体 (有连接指向不存在的实体ID)
3. 字段缺失 (必需字段为空)
4. ID 冲突 (同类型内 ID 重复)

被飞轮引擎 health() 调用
"""

import json
import os
from datetime import datetime, timezone
from collections import Counter

WORKSPACE = os.environ.get('SRI_WORKSPACE', os.path.expanduser('~/.openclaw/workspace'))
DATA_FILE = os.path.join(WORKSPACE, 'memory/_data/entities_index.json')

REQUIRED_FIELDS = {
    'products': ['id', 'name', 'family', 'status'],
    'customers': ['id', 'name'],
    'cities': ['id', 'name'],
    'avatars': ['id', 'name'],
    'cognition_events': ['id', 'entity_id', 'evaluator'],
    'action_events': ['id'],
    'verification_events': ['id'],
    'learning_events': ['id'],
    'tasks': ['id', 'name'],
    'documents': ['id', 'name'],
}


def check_duplicates(entities, entity_type):
    """检测重复实体"""
    issues = []

    # 按 name 去重
    name_counts = Counter()
    for e in entities:
        if isinstance(e, dict):
            name = e.get('name', '').strip().lower()
            if name:
                name_counts[name] += 1

    for name, count in name_counts.items():
        if count > 1 and entity_type == 'products':
            dups = [e['id'] for e in entities if isinstance(e, dict) and e.get('name', '').strip().lower() == name]
            issues.append({
                'type': 'duplicate_name',
                'entity_type': entity_type,
                'name': name,
                'ids': dups,
                'count': count,
                'suggestion': '检查是否应合并或重命名'
            })

    # 按 url/source_file 去重
    url_counts = Counter()
    for e in entities:
        if isinstance(e, dict):
            url = e.get('url') or e.get('source_file', '')
            if url:
                url_counts[url] += 1

    for url, count in url_counts.items():
        if count > 1 and entity_type == 'products':
            dups = [e['id'] for e in entities if isinstance(e, dict) and (e.get('url') == url or e.get('source_file') == url)]
            if len(dups) > 1:
                issues.append({
                    'type': 'duplicate_url',
                    'entity_type': entity_type,
                    'url': url,
                    'ids': dups,
                    'count': count,
                    'suggestion': '保留一个·删除/归档其他'
                })

    return issues


def check_orphans(data):
    """检测孤儿连接"""
    issues = []

    # 收集所有有效实体ID
    valid_ids = set()
    for entity_type in ['products', 'customers', 'cities', 'avatars', 'tasks', 'documents',
                        'cognition_events', 'action_events', 'verification_events', 'learning_events']:
        for e in data.get(entity_type, []):
            if isinstance(e, dict) and 'id' in e:
                valid_ids.add(e['id'])

    # 检查连接中的 ID 是否有效
    connections = data.get('connections', [])
    orphan_connections = []
    for conn in connections:
        if isinstance(conn, dict):
            source = conn.get('source_id', '')
            target = conn.get('target_id', '')
            if source and source not in valid_ids:
                orphan_connections.append({'connection': conn.get('id', '?'), 'missing': source, 'role': 'source'})
            if target and target not in valid_ids:
                orphan_connections.append({'connection': conn.get('id', '?'), 'missing': target, 'role': 'target'})

    if orphan_connections:
        issues.append({
            'type': 'orphan_connections',
            'count': len(orphan_connections),
            'samples': orphan_connections[:10],
            'suggestion': '删除无效连接或补建缺失实体'
        })

    return issues


def check_missing_fields(data):
    """检测必需字段缺失"""
    issues = []
    for entity_type, required in REQUIRED_FIELDS.items():
        for e in data.get(entity_type, []):
            if not isinstance(e, dict):
                continue
            missing = [f for f in required if not e.get(f)]
            if missing:
                issues.append({
                    'type': 'missing_fields',
                    'entity_type': entity_type,
                    'entity_id': e.get('id', '?'),
                    'missing': missing,
                    'suggestion': '补全缺失字段'
                })
    return issues


def check_id_conflicts(data):
    """检测 ID 冲突"""
    all_ids = Counter()
    for entity_type in data:
        if entity_type == 'meta' or entity_type == 'connections':
            continue
        for e in data.get(entity_type, []):
            if isinstance(e, dict) and 'id' in e:
                all_ids[e['id']] += 1

    conflicts = {k: v for k, v in all_ids.items() if v > 1}
    issues = []
    if conflicts:
        issues.append({
            'type': 'id_conflicts',
            'conflicts': [{'id': k, 'count': v} for k, v in list(conflicts.items())[:10]],
            'total': len(conflicts),
            'suggestion': '全局 ID 空间冲突·需重新分配'
        })
    return issues


def run_consistency_check(dry_run=False):
    """运行全部一致性检查"""
    if not os.path.exists(DATA_FILE):
        return {'error': 'entities_index.json 不存在'}

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    all_issues = []

    # 1. 重复检测
    for entity_type in ['products', 'documents', 'tasks', 'customers', 'avatars']:
        entities = data.get(entity_type, [])
        all_issues.extend(check_duplicates(entities, entity_type))

    # 2. 孤儿连接
    all_issues.extend(check_orphans(data))

    # 3. 缺失字段
    all_issues.extend(check_missing_fields(data))

    # 4. ID 冲突
    all_issues.extend(check_id_conflicts(data))

    summary = {
        'checked_at': datetime.now(timezone.utc).isoformat(),
        'total_issues': len(all_issues),
        'by_type': {},
        'issues': all_issues
    }

    for issue in all_issues:
        t = issue.get('type', 'unknown')
        summary['by_type'][t] = summary['by_type'].get(t, 0) + 1

    if not dry_run:
        # 写回
        if 'meta' not in data:
            data['meta'] = {}
        data['meta']['consistency_check'] = summary

        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    return summary


def print_report(summary):
    """打印一致性报告"""
    print('=' * 60)
    print('SRI 实体一致性检查报告')
    print('=' * 60)
    print('检查时间: {}'.format(summary.get('checked_at', '?')[:19]))
    print('总问题数: {}'.format(summary.get('total_issues', 0)))
    print()

    if summary.get('by_type'):
        print('📊 问题类型分布:')
        for t, count in sorted(summary['by_type'].items(), key=lambda x: -x[1]):
            bar = '█' * min(count, 40)
            print('  {}: {} {}'.format(t, bar, count))
        print()

    # 按实体类型统计
    entity_issues = {}
    for issue in summary.get('issues', []):
        et = issue.get('entity_type', 'global')
        entity_issues[et] = entity_issues.get(et, 0) + 1
    if entity_issues:
        print('⚡ 按实体类型:')
        for et, count in sorted(entity_issues.items(), key=lambda x: -x[1])[:10]:
            print('  {}: {} 问题'.format(et, count))
        print()

    # 展示样本
    print('🔍 问题样本 (前10条):')
    for issue in summary.get('issues', [])[:10]:
        t = issue.get('type', '?')
        et = issue.get('entity_type', '?')
        eid = issue.get('entity_id', issue.get('name', '?'))
        sug = issue.get('suggestion', '')
        print('  [{}] {}/{} · {}'.format(t, et, eid[:40], sug))


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='SRI 实体去重与一致性检查')
    parser.add_argument('--dry-run', action='store_true', help='只读不写')
    parser.add_argument('--save', action='store_true', help='写入 entities_index')
    args = parser.parse_args()

    summary = run_consistency_check(dry_run=not args.save)
    print_report(summary)
