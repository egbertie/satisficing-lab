#!/usr/bin/env python3
"""
SRI 产品全生命周期自动管理引擎 v1.0
=====================================
基于 Stage-Gate 理念 + SRI 标准 v2.0，
自动管理产品的:
1. 晋升 (内测→打磨→精品)
2. 降级 (精品→维护→归档)
3. 日落 (长期低分→自动归档)
4. 复审 (每季度全量审计)

被飞轮引擎 health() 调用。
每次运行根据标准评分自动调整产品生命周期状态。
"""

import json
import os
from datetime import datetime, timezone

WORKSPACE = os.environ.get('SRI_WORKSPACE', os.path.expanduser('~/.openclaw/workspace'))
DATA_FILE = os.path.join(WORKSPACE, 'memory/_data/entities_index.json')
STANDARDS_FILE = os.path.join(WORKSPACE, 'memory/_data/sri_product_standards_v2.json')

# 生命周期阶段定义
LIFECYCLE = {
    'LC-001': {'label': '概念期', 'min_score': 0, 'next': 'LC-002', 'auto_promote': False},
    'LC-002': {'label': '开发中', 'min_score': 0, 'next': 'LC-003', 'auto_promote': False},
    'LC-003': {'label': '内测期', 'min_score': 50, 'next': 'LC-004', 'auto_promote': True},
    'LC-004': {'label': '打磨期', 'min_score': 65, 'next': 'LC-005', 'auto_promote': True},
    'LC-005': {'label': '精品期', 'min_score': 75, 'next': 'LC-005', 'auto_promote': False,
               'demote_threshold': 60, 'demote_to': 'LC-006'},
    'LC-006': {'label': '维护期', 'min_score': 50, 'next': 'LC-006', 'auto_promote': False,
               'demote_threshold': 30, 'demote_to': 'LC-007'},
    'LC-007': {'label': '归档期', 'min_score': 0, 'next': 'LC-007', 'auto_promote': False,
               'archive_after_days': 90}
}

# 产品类型→权重映射
TYPE_WEIGHTS = {
    'diagnostic_tool':    {'completeness': 0.20, 'usability': 0.30, 'clarity': 0.15,
                           'aesthetics': 0.10, 'uniqueness': 0.15, 'maintainability': 0.10},
    'quantitative_tool':  {'completeness': 0.30, 'usability': 0.20, 'clarity': 0.15,
                           'aesthetics': 0.10, 'uniqueness': 0.15, 'maintainability': 0.10},
    'simulation_game':    {'completeness': 0.15, 'usability': 0.30, 'clarity': 0.10,
                           'aesthetics': 0.20, 'uniqueness': 0.20, 'maintainability': 0.05},
    'knowledge_page':     {'completeness': 0.25, 'usability': 0.10, 'clarity': 0.30,
                           'aesthetics': 0.15, 'uniqueness': 0.10, 'maintainability': 0.10},
    'infrastructure':     {'completeness': 0.30, 'usability': 0.15, 'clarity': 0.15,
                           'aesthetics': 0.10, 'uniqueness': 0.10, 'maintainability': 0.20},
    'simple_tool':        {'completeness': 0.25, 'usability': 0.40, 'clarity': 0.15,
                           'aesthetics': 0.05, 'uniqueness': 0.05, 'maintainability': 0.10},
}


def classify_product_type(product):
    """根据产品属性判断产品类型"""
    family = product.get('family', '')
    name = product.get('name', '').lower()
    jtbd = product.get('jtbd_category', '')

    # 按 JTBD 分类映射
    if jtbd == 'diagnose':
        if any(kw in name for kw in ['卡牌', '牌局', '对局', '剧场', '游戏', '模拟']):
            return 'simulation_game'
        return 'diagnostic_tool'

    if jtbd == 'decide':
        return 'quantitative_tool'

    if jtbd == 'grow':
        if any(kw in name for kw in ['驾驶舱', 'admin', '仪表', '飞轮', '密码', '认证', '注册']):
            return 'infrastructure'
        if any(kw in name for kw in ['卡牌', '对局', '剧场', '游戏', '模拟', '演练']):
            return 'simulation_game'
        return 'simple_tool'

    if jtbd == 'knowledge':
        return 'knowledge_page'

    # 默认
    if family == '镜':
        return 'diagnostic_tool'
    if family == '衡':
        return 'quantitative_tool'
    if family == '觉':
        return 'simple_tool'

    return 'simple_tool'


def calculate_sri_score(product, product_type):
    """计算产品六维评分"""
    weights = TYPE_WEIGHTS.get(product_type, TYPE_WEIGHTS['simple_tool'])

    # 从现有字段自动提取维度分
    audit = product.get('audit_score', 0)
    qs = product.get('quality_score', 0)
    llm = product.get('llm_rating', 0)
    issues = product.get('audit_issues', 0)

    # 完整度: 基于审计问题数 + 文件大小 + 有无URL
    completeness = 100
    if not product.get('url'):
        completeness = 0
    else:
        if issues > 5:
            completeness -= 20
        if issues > 10:
            completeness -= 10
        completeness = max(0, completeness)

    # 可用度: 基于LLM替身评分
    usability = llm if llm > 0 else qs

    # 清晰度: 基于审计 + meta描述
    clarity = audit if audit > 0 else 70
    # 检查是否有 meta description
    checks = product.get('checks', {})
    if isinstance(checks, dict) and not checks.get('has_meta_desc'):
        clarity = min(clarity, 80)

    # 美学度: 基于内联样式数
    aesthetics = max(50, 100 - (product.get('inline_styles', 0) if isinstance(product, dict) else 85))

    # 独特性: 基于LLM评分的维度分析
    uniqueness = max(50, llm + 5) if llm > 0 else 65

    # 可维护度: 基于健康状态
    health = product.get('health', 'healthy')
    maintainability = {'healthy': 85, 'degraded': 60, 'critical': 40, 'stale': 30}.get(health, 70)

    # 美学度: 从 product checks 提取
    inline_styles = 0
    if isinstance(product, dict) and isinstance(product.get('checks'), dict):
        inline_styles = product['checks'].get('inline_styles', 0)
    aesthetics_metric = max(50, 100 - min(inline_styles / 2, 50))

    # 加权计算
    score = (
        completeness * weights.get('completeness', 0.25) +
        usability * weights.get('usability', 0.25) +
        clarity * weights.get('clarity', 0.20) +
        aesthetics_metric * weights.get('aesthetics', 0.15) +
        uniqueness * weights.get('uniqueness', 0.10) +
        maintainability * weights.get('maintainability', 0.05)
    )

    return round(score, 1)


def decide_lifecycle_change(product, current_stage, sri_score, days_since_update=None):
    """决策生命周期变更"""
    stage_info = LIFECYCLE.get(current_stage, LIFECYCLE['LC-003'])
    changes = []

    # 晋升检查
    if stage_info.get('auto_promote') and sri_score >= stage_info.get('min_score', 0) + 5:
        next_stage = stage_info.get('next')
        if next_stage and next_stage != current_stage:
            next_info = LIFECYCLE.get(next_stage, {})
            if sri_score >= next_info.get('min_score', 0):
                changes.append({
                    'action': 'promote',
                    'from': current_stage,
                    'to': next_stage,
                    'reason': '评分{}≥{}阈值'.format(sri_score, next_info.get('min_score', 0))
                })

    # 降级检查
    if 'demote_threshold' in stage_info and sri_score < stage_info['demote_threshold']:
        demote_to = stage_info.get('demote_to')
        if demote_to:
            changes.append({
                'action': 'demote',
                'from': current_stage,
                'to': demote_to,
                'reason': '评分{}<{}阈值'.format(sri_score, stage_info['demote_threshold'])
            })

    # 归档检查 (>90天未更新)
    if current_stage == 'LC-007' and days_since_update and days_since_update > 90:
        changes.append({
            'action': 'archive',
            'from': current_stage,
            'to': 'archived',
            'reason': '归档期>90天·建议永久归档'
        })

    return changes


def run_lifecycle_management(dry_run=False):
    """执行全生命周期自动管理"""
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    products = [p for p in data.get('products', []) if isinstance(p, dict)]
    now = datetime.now(timezone.utc)

    report = {
        'executed_at': now.isoformat(),
        'dry_run': dry_run,
        'total_scanned': len(products),
        'changes': [],
        'summary': {'promoted': 0, 'demoted': 0, 'archived': 0}
    }

    # 加载标准
    import json as _json
    standards_file = os.path.join(WORKSPACE, 'memory/_data/sri_product_standards_v2.json')
    standards_version = '2.0'
    if os.path.exists(standards_file):
        with open(standards_file) as sf:
            standards_version = _json.load(sf).get('version', '2.0')

    for p in products:
        # 跳过已下架的产品
        if p.get('status') in ('已下架', '资料·归入知识库'):
            continue

        ptype = classify_product_type(p)
        p['product_type'] = ptype
        sri_score = calculate_sri_score(p, ptype)
        p['sri_score'] = sri_score

        current_stage = p.get('lifecycle_stage', 'LC-003')
        last_mod = p.get('last_modified') or p.get('last_scan_time')
        days_since = None
        if last_mod:
            try:
                last_dt = datetime.fromisoformat(last_mod)
                days_since = (now - last_dt).days
            except (ValueError, TypeError):
                pass

        changes = decide_lifecycle_change(p, current_stage, sri_score, days_since)

        for ch in changes:
            if not dry_run:
                if ch['action'] == 'promote':
                    p['lifecycle_stage'] = ch['to']
                    p['promoted_at'] = now.isoformat()
                elif ch['action'] == 'demote':
                    p['lifecycle_stage'] = ch['to']
                    p['demoted_at'] = now.isoformat()
                elif ch['action'] == 'archive':
                    p['status'] = '已归档'
                    p['archived_at'] = now.isoformat()

            ch['product_id'] = p.get('id', '?')
            ch['product_name'] = p.get('name', '?')[:40]
            ch['sri_score'] = sri_score
            ch['product_type'] = ptype
            report['changes'].append(ch)
            a = ch['action']; report['summary']['promoted' if a == 'promote' else 'demoted' if a == 'demote' else 'archived'] += 1

        p['last_lifecycle_check'] = now.isoformat()
        p['standards_version'] = standards_version

    # 写入 meta
    if 'meta' not in data:
        data['meta'] = {}
    data['meta']['lifecycle_management'] = {
        'executed_at': now.isoformat(),
        'standards_version': standards_version,
        **report['summary']
    }

    if not dry_run:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    return report


def print_report(report):
    print("=" * 60)
    print("SRI 产品全生命周期管理报告")
    print("=" * 60)
    print(f"时间: {report['executed_at'][:19]}")
    print(f"扫描产品: {report['total_scanned']}")
    print(f"模式: {'DRY RUN' if report.get('dry_run') else '已执行'}")

    s = report['summary']
    print(f"\n📊 变更摘要:")
    print(f"  ⬆️ 晋升: {s.get('promoted', 0)}")
    print(f"  ⬇️ 降级: {s.get('demoted', 0)}")
    print(f"  📦 归档: {s.get('archived', 0)}")

    if report['changes']:
        print(f"\n📋 变更详情:")
        for ch in report['changes'][:20]:
            icon = {'promote': '⬆️', 'demote': '⬇️', 'archive': '📦'}.get(ch['action'], '?')
            print(f"  {icon} {ch['product_id']}: {ch['product_name']} "
                  f"({ch['from']}→{ch['to']}) 评分={ch.get('sri_score', '?')}")


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser(description='SRI 产品全生命周期自动管理')
    p.add_argument('--dry-run', action='store_true')
    p.add_argument('--save', action='store_true')
    args = p.parse_args()
    report = run_lifecycle_management(dry_run=not args.save)
    print_report(report)
