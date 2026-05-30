#!/usr/bin/env python3
"""
SRI 产品体系重构引擎 v1.0
==========================
基于 JTBD (Jobs-to-be-Done) 客户视角,
执行 Keep-Kill-Combine-Merge 四步产品体系重构。

目标:
1. 从 315 产品缩减到 ~80-120 个有效产品
2. 从 7 族(Igor命名) → 5个客户场景类别
3. 75 个幽灵产品归档
4. 重复产品合并
5. 建立清晰的产品金字塔: 精品(20) → 标准品(40) → 工具箱(40) → 归档(其余)

物理产出:
- entities_index.json 更新 (产品状态·新分类·新字段)
- 归档清单 (ghost_products.txt)
- 合并清单 (merge_log.json)
- 新分类体系 (jtbd_taxonomy.json)
"""

import json
import os
import re
from datetime import datetime, timezone
from collections import defaultdict, Counter

WORKSPACE = os.environ.get('SRI_WORKSPACE', os.path.expanduser('~/.openclaw/workspace'))
DATA_FILE = os.path.join(WORKSPACE, 'memory/_data/entities_index.json')


# ============================================
# 客户视角分类体系 (JTBD-based)
# ============================================
SRI_PRODUCT_TAXONOMY = {
    'version': '2.0',
    'name': '满意红产品分类体系 (客户视角)',
    'principle': '按客户想解决的问题分类，而非内部族名',

    'categories': {
        'diagnose': {
            'label': '🔍 看清问题',
            'description': '当你隐隐觉得不对但说不清时，帮你精确诊断',
            'jtbd': '我想知道我的团队/关系/决策到底哪里出了问题',
            'target_role': ['创始人', '合伙人', '团队Leader'],
            'examples': ['决策剧场', '四骑士识别', 'Pre-0身体觉察', '五维雷达图', '关系温度计'],
            'expected_count': '15-25'
        },
        'decide': {
            'label': '🧰 做对决策',
            'description': '当你看清问题后，帮你形成具体可执行的方案',
            'jtbd': '我知道了问题，但我不知道该怎么做',
            'target_role': ['创始人', '合伙人'],
            'examples': ['元合伙', '分割饼', '匹配引擎', 'FIN诚实验证器', '危机模拟'],
            'expected_count': '15-25'
        },
        'grow': {
            'label': '🔥 淬炼成长',
            'description': '当你有了方案，通过模拟和练习把它变成肌肉记忆',
            'jtbd': '我有方案了，但怎么确保执行不出错',
            'target_role': ['创始人', '团队Leader', '合伙人'],
            'examples': ['卡牌对局', '决策剧场', '退出仪式', '段位体系', '驾驶舱'],
            'expected_count': '10-20'
        },
        'sustain': {
            'label': '🔄 持续巩固',
            'description': '当一切在运行时，持续监控和优化',
            'jtbd': '我们在跑，但怎么知道不会悄悄偏离轨道',
            'target_role': ['创始人', '团队Leader'],
            'examples': ['关系温度计', '飞轮引擎', '成熟度体系', '自检清单'],
            'expected_count': '10-15'
        },
        'knowledge': {
            'label': '📚 知识传承',
            'description': '把经验和洞见沉淀为可复用的知识资产',
            'jtbd': '我想把学到的东西保存下来，让后来的人也能受益',
            'target_role': ['所有人'],
            'examples': ['案例库', '宝藏库', '量化体系', '星光方法论', '关于我们'],
            'expected_count': '20-30'
        }
    },

    'product_tiers': {
        'tier_1_premium': {'label': '⭐ 精品', 'count': 20, 'criteria': '六维评分≥80·LLM评分≥70·有完整详情页·面向客户'},
        'tier_2_core': {'label': '✅ 标准品', 'count': 40, 'criteria': '完整度≥60·有URL·有明确JTBD归属'},
        'tier_3_toolkit': {'label': '🔧 工具箱', 'count': 40, 'criteria': '功能简单·单页工具·辅助场景'},
        'tier_4_archive': {'label': '📦 归档', 'count': '其余', 'criteria': '无URL·低评分·重复·过期'}
    }
}


def classify_by_jtbd(product):
    """按客户视角重新分类产品"""
    name = (product.get('name', '') or '').lower()
    family = product.get('family', '')
    url = (product.get('url', '') or '').lower()

    # 优先按族映射
    jtbd_from_family = {
        '镜': 'diagnose',
        '衡': 'diagnose',  # 衡族多数是量化诊断工具
        '契': 'decide',
        '觉': 'grow',
        '章': 'knowledge',
        '人': 'decide',
        '道': 'knowledge',
    }

    if family in jtbd_from_family:
        return jtbd_from_family[family]

    # 关键词匹配
    kws = {
        'diagnose': ['觉察', '诊断', '扫描', '检测', '识别', '审计', '身体', '温度', '骑士', '镜', '检查', '量表',
                     'pre0', 'FIN', '诚实', '雷达', '观局', '眼睛', '关系', '危机信号', '报告', '评估', '评分条'],
        'decide': ['协议', '匹配', '合伙', '约束', '规则', '方案', '决策', '选择', '契约', '条款', '约定', '模板',
                   '提案', '向导', '引导', '分割', 'FIN', '元', '蓝军', '通道', '立信', '定价'],
        'grow': ['淬炼', '练习', '模拟', '演练', '卡牌', '牌局', '对局', '博弈', '剧场', '工作坊', '危机', '压力',
                 '课程', '退出', '段位', '游戏', '竞品', '挑战', '飞行', '引擎', '驾驶', '仪表', '飞轮'],
        'sustain': ['跟踪', '监测', '持续', '监控', '日志', '日记', '追踪', '记分', '打卡', '日常', '周期', '习惯',
                    '飞轮', '管道', '成熟度', '认证', '审查', '巡检', '健康'],
        'knowledge': ['知识', '学习', '资料', '案例', '文档', '目录', '库', '收集', '索引', '归档', '族谱', '根脉',
                      '溯', '历史', '考古', '记忆', '手册', '指南', '新人', '入职', '品牌', '关于', '体系', '量化',
                      '星光', '宝藏', '星月', '传奇', '课程', '大学', '标准', '规范', '编码', '共识', '咒语']
    }

    for cat, keywords in kws.items():
        for kw in keywords:
            if kw in name or kw in url:
                return cat

    return 'knowledge'


def classify_product_tier(product):
    """分配产品层级"""
    if not product.get('url'):
        return 'tier_4_archive'

    qs = product.get('quality_score', 0)
    llm = product.get('llm_rating', 0)
    audit = product.get('audit_score', 0)

    if llm and llm >= 70 and qs >= 80 and audit >= 80:
        return 'tier_1_premium'
    elif qs >= 75 and audit >= 60:
        return 'tier_2_core'
    elif qs >= 60:
        return 'tier_3_toolkit'
    else:
        return 'tier_4_archive'


def decide_keep_kill_combine(product):
    """产品四态决策: keep / kill / combine / merge"""
    # 幽灵产品 → kill
    if not product.get('url'):
        return 'kill', '无URL，幽灵产品'

    qs = product.get('quality_score', 0)
    llm = product.get('llm_rating')
    audit = product.get('audit_score', 0)
    name = product.get('name', '')
    status = product.get('status', '')
    family = product.get('family', '')

    # 明确精品 → keep
    if status == '精品' and llm and llm >= 70:
        return 'keep', '精品·已LLM验证'

    # LLM评分低 → kill
    if llm and llm < 55:
        return 'kill', 'LLM评分<55·质量不足'

    # 审计分很低 → kill
    if audit > 0 and audit < 60:
        return 'kill', '审计分<60·物理质量差'

    # 章族大量内容页 — 归入知识库
    if family == '章' and qs < 85:
        return 'combine', '内容/资料页·归入知识库'

    # 衡族大量重复诊断页 — 低分合并
    if family == '衡' and (not llm or llm < 65) and qs < 80:
        return 'combine', '低分支线·合并到主工具'
    
    # 觉族大量工具页面
    if family == '觉' and qs < 75 and (not llm or llm < 60):
        return 'combine', '辅助工具·合并'

    # 多人族工具页
    if family == '人' and qs < 75:
        return 'combine', '辅助工具·合并'
    
    # 契族数量多但很多是小页面
    if family == '契' and qs < 75 and (not llm or llm < 60):
        return 'combine', '辅助页面·合并'

    return 'keep', '通过'


def run_portfolio_rationalization(dry_run=False):
    """执行完整的产品体系重构"""
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    products = [p for p in data.get('products', []) if isinstance(p, dict)]
    now = datetime.now(timezone.utc)

    report = {
        'executed_at': now.isoformat(),
        'dry_run': dry_run,
        'total_before': len(products),
        'decisions': Counter(),
        'changes': []
    }

    for p in products:
        p['jtbd_category'] = classify_by_jtbd(p)
        p['product_tier'] = classify_product_tier(p)
        decision, reason = decide_keep_kill_combine(p)

        old_status = p.get('status', '?')
        report['decisions'][decision] += 1

        if decision == 'kill':
            p['status'] = '已下架'
            p['archived_at'] = now.isoformat()
            p['archive_reason'] = reason

        elif decision == 'combine':
            p['status'] = '资料·归入知识库'
            p['archived_at'] = now.isoformat()
            p['archive_reason'] = reason

        elif decision == 'merge':
            p['status'] = '待合并'
            p['merge_reason'] = reason

        report['changes'].append({
            'id': p.get('id', '?'),
            'name': p.get('name', '?')[:40],
            'decision': decision,
            'reason': reason,
            'old_status': old_status,
            'new_status': p.get('status'),
            'new_category': p.get('jtbd_category'),
            'new_tier': p.get('product_tier')
        })

    # 更新 meta
    if 'meta' not in data:
        data['meta'] = {}
    data['meta']['portfolio_rationalization'] = {
        'executed_at': now.isoformat(),
        'version': '2.0',
        'total_before': len(products),
        'total_after': report['decisions']['keep'],
        'killed': report['decisions']['kill'],
        'combined': report['decisions']['combine'],
        'merged': report['decisions']['merge'],
        'taxonomy': SRI_PRODUCT_TAXONOMY
    }

    if not dry_run:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    return report


def print_report(report):
    """打印重构报告"""
    dec = report['decisions']
    total = report['total_before']

    print("=" * 60)
    print("SRI 产品体系重构 · Keep-Kill-Combine 报告")
    print("=" * 60)
    print(f"时间: {report['executed_at'][:19]}")
    print(f"重构前: {total} 产品")
    print(f"重构后: {dec.get('keep',0)} 有效产品\n")

    print(f"📊 决策分布:")
    for d in ['keep', 'kill', 'combine', 'merge']:
        c = dec.get(d, 0)
        bar = '█' * (c // 5)
        label = {'keep': '保留', 'kill': '下架', 'combine': '归入知识库', 'merge': '待合并'}.get(d, d)
        print(f"  {label}: {c} {bar} ({100*c//total}%)")

    print(f"\n📋 JTBD 客户类别分布:")
    jtbd_dist = Counter()
    for ch in report['changes']:
        if ch['decision'] == 'keep':
            jtbd_dist[ch['new_category']] += 1

    cat_labels = {
        'diagnose': '🔍 看清问题',
        'decide': '🧰 做对决策',
        'grow': '🔥 淬炼成长',
        'sustain': '🔄 持续巩固',
        'knowledge': '📚 知识传承'
    }
    for cat in ['diagnose', 'decide', 'grow', 'sustain', 'knowledge']:
        c = jtbd_dist.get(cat, 0)
        bar = '█' * c
        print(f"  {cat_labels[cat]}: {c} {bar}")

    print(f"\n⭐ 产品层级分布:")
    tier_dist = Counter()
    for ch in report['changes']:
        if ch['decision'] == 'keep':
            tier_dist[ch['new_tier']] += 1

    tier_labels = {
        'tier_1_premium': '精品(20)',
        'tier_2_core': '标准品(40)',
        'tier_3_toolkit': '工具箱(40)',
        'tier_4_archive': '归档(其余)'
    }
    for tier in ['tier_1_premium', 'tier_2_core', 'tier_3_toolkit', 'tier_4_archive']:
        c = tier_dist.get(tier, 0)
        print(f"  {tier_labels[tier]}: {c}")

    # 被下架的产品样本
    killed = [ch for ch in report['changes'] if ch['decision'] == 'kill']
    if killed:
        print(f"\n❌ 下架产品样本 (前20):")
        for ch in killed[:20]:
            print(f"  {ch['id']}: {ch['name']} — {ch['reason']}")

    combined = [ch for ch in report['changes'] if ch['decision'] == 'combine']
    if combined:
        print(f"\n📦 归入知识库样本 (前20):")
        for ch in combined[:20]:
            print(f"  {ch['id']}: {ch['name']} — {ch['reason']}")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='SRI 产品体系重构引擎')
    parser.add_argument('--dry-run', action='store_true', help='只分析不写入')
    parser.add_argument('--save', action='store_true', help='写入entities_index')
    args = parser.parse_args()

    report = run_portfolio_rationalization(dry_run=not args.save)
    print_report(report)
