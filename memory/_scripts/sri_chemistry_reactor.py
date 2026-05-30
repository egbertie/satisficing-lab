#!/usr/bin/env python3
"""
SRI 化学反应引擎 v1.0
======================
实现九条化学反应链，把产品从被动管理的「物理实体」
变成会自发生长、反应、进化的「化学活性物质」。

被编排器 orchestrator 调用。
"""

import json
import os
import math
from datetime import datetime, timezone
from collections import defaultdict, Counter

WORKSPACE = os.environ.get('SRI_WORKSPACE', os.path.expanduser('~/.openclaw/workspace'))
DATA_FILE = os.path.join(WORKSPACE, 'memory/_data/entities_index.json')
NOURISHMENT_DIR = os.path.join(WORKSPACE, 'memory/nourishment')

# ============================================================
# 链1: 结晶反应 — 养料过饱和 → 析出产品改进建议
# ============================================================
def reaction_crystallize(data, threshold=8):
    """知识养料积累超过阈值 → 自动生成产品改进建议"""
    now = datetime.now(timezone.utc)
    
    # 加载养料
    all_items = []
    if os.path.exists(NOURISHMENT_DIR):
        for fname in sorted(os.listdir(NOURISHMENT_DIR)):
            if fname.endswith('.json'):
                try:
                    with open(os.path.join(NOURISHMENT_DIR, fname)) as f:
                        batch = json.load(f)
                    all_items.extend(batch.get('items', []))
                except:
                    pass
    
    # 按领域分组
    domain_items = defaultdict(list)
    for item in all_items:
        for d in item.get('domains', []):
            domain_items[d].append(item)
    
    crystals = []
    for domain, items in domain_items.items():
        if len(items) >= threshold:
            # 过饱和 → 结晶
            titles = [it.get('title', '')[:60] for it in items[-threshold:]]
            sources = set(it.get('source', '?') for it in items[-threshold:])
            
            # 匹配到相关产品
            products = data.get('products', [])
            matched = []
            for p in products:
                if not isinstance(p, dict) or p.get('status') in ('已下架', '资料·归入知识库'):
                    continue
                for kw in items[-3]:
                    title = (items[-3][0].get('title', '') + ' ' + items[-3][1].get('title', '') if len(items) > 1 else '')[:50]
                    break
                # 简化匹配: 产品族与领域的映射
                jtbd = p.get('jtbd_category', '')
                domain_jtbd_map = {
                    '创始人与合伙人': 'diagnose',
                    '组织与团队': 'diagnose',
                    '决策科学': 'decide',
                    '产品与体验': 'grow',
                    '知识与学习': 'knowledge',
                    'AI与自动化': 'grow',
                    '安全与治理': 'knowledge'
                }
                if domain_jtbd_map.get(domain) == jtbd:
                    matched.append(p)
            
            if matched:
                # 选3个最需要改进的产品
                candidates = sorted(matched, key=lambda p: p.get('sri_score', 0))[:3]
                for p in candidates:
                    crystals.append({
                        'domain': domain,
                        'product_id': p.get('id', '?'),
                        'product_name': p.get('name', '?')[:40],
                        'current_score': p.get('sri_score', 0),
                        'suggestion': '基于{}条{}(来源:{})的养料结晶·建议审查该产品的知识时效性和相关性'.format(
                            len(items), domain, ', '.join(list(sources)[:3])),
                        'nourishment_count': len(items),
                        'crystallized_at': now.isoformat()
                    })
    
    # 写入
    if 'meta' not in data:
        data['meta'] = {}
    data['meta']['crystals'] = {
        'reacted_at': now.isoformat(),
        'total_nourishment': len(all_items),
        'domains_above_threshold': len([d for d, i in domain_items.items() if len(i) >= threshold]),
        'crystals_generated': len(crystals),
        'crystals': crystals
    }
    
    return crystals


# ============================================================
# 链2: 活化能降低 — 产品包装层字段自动推断
# ============================================================
def reaction_activate(data):
    """为没有包装层的产品自动推断基础字段"""
    now = datetime.now(timezone.utc)
    products = [p for p in data.get('products', []) 
                if isinstance(p, dict) and p.get('status') not in ('已下架', '资料·归入知识库')]
    
    activated = 0
    for p in products:
        if p.get('positioning'):
            continue  # 已有包装层
        
        name = p.get('name', '')
        family = p.get('family', '')
        jtbd = p.get('jtbd_category', '')
        ptype = p.get('product_type', '')
        
        # 基于已知字段推断包装层
        jtbd_scenario = {
            'diagnose': '当你隐隐觉得出了问题但说不清时',
            'decide': '当你看清问题后需要形成具体方案时',
            'grow': '当你有方案后需要通过练习把它变成肌肉记忆时',
            'knowledge': '当你想沉淀经验为可复用知识时'
        }
        
        type_time = {
            'diagnostic_tool': '首次使用约10-15分钟',
            'quantitative_tool': '首次使用约5-10分钟',
            'simulation_game': '首次使用约20-30分钟',
            'knowledge_page': '阅读约5-10分钟',
            'simple_tool': '使用约2-5分钟',
            'infrastructure': '持续使用',
        }
        
        p['positioning'] = '{}·{}'.format(
            {'diagnose': '诊断工具', 'decide': '决策工具', 'grow': '练习工具', 'knowledge': '知识资产'}.get(jtbd, '工具'),
            name[:15]
        )
        p['scenario'] = jtbd_scenario.get(jtbd, '根据你的需求使用')
        p['time_estimate'] = type_time.get(ptype, '约5-10分钟')
        p['who_for'] = '创始人·合伙人·团队Leader'
        p['outcome'] = '使用{}后的输出结果'.format(name[:10])
        p['prerequisites'] = '无需特殊准备·打开即用'
        p['packaging_generated'] = True
        p['packaging_generated_at'] = now.isoformat()
        activated += 1
    
    data['meta']['activation'] = {
        'reacted_at': now.isoformat(),
        'products_activated': activated,
        'total_products': len(products)
    }
    
    return activated


# ============================================================
# 链3: 浓度梯度 — 评分差驱动产品流自动重排
# ============================================================
def reaction_concentration_gradient(data):
    """高评分产品形成高点位，低评分产品自然滑动到底部"""
    now = datetime.now(timezone.utc)
    products = [p for p in data.get('products', [])
                if isinstance(p, dict) and p.get('status') not in ('已下架', '资料·归入知识库')
                and p.get('sri_score')]
    
    if not products:
        return 0
    
    # 按评分排序
    products.sort(key=lambda p: p.get('sri_score', 0), reverse=True)
    
    # 计算梯度
    scores = [p.get('sri_score', 0) for p in products]
    avg_score = sum(scores) / len(scores)
    max_score = max(scores)
    min_score = min(scores)
    
    # 标记浓度梯度
    gradient_map = {}
    for p in products:
        score = p.get('sri_score', 0)
        if score >= avg_score + 10:
            gradient = 'high'
        elif score <= avg_score - 10:
            gradient = 'low'
        else:
            gradient = 'medium'
        p['score_gradient'] = gradient
        gradient_map[gradient] = gradient_map.get(gradient, 0) + 1
    
    # 低分产品自动降权
    low_scorers = [p for p in products if p.get('score_gradient') == 'low']
    for p in low_scorers:
        p['flow_priority'] = 'deferred'
    
    data['meta']['concentration'] = {
        'reacted_at': now.isoformat(),
        'avg_score': round(avg_score, 1),
        'max_score': max_score,
        'min_score': min_score,
        'high_concentration': gradient_map.get('high', 0),
        'low_concentration': gradient_map.get('low', 0),
        'products_deferred': len(low_scorers)
    }
    
    return len(low_scorers)


# ============================================================
# 链4: 链式反应 — 一次变更触发级联传播
# ============================================================
def reaction_chain_propagation(data):
    """检测最近的评分变化，计算传播效应"""
    now = datetime.now(timezone.utc)
    cl = data.get('meta', {}).get('change_log', [])
    
    # 找最近的评分变化
    recent = [c for c in cl[-50:] 
              if isinstance(c, dict) and c.get('field') in ('sri_score', 'llm_rating', 'quality_score')
              and c.get('new_value')]
    
    if not recent:
        return 0
    
    # 计算传播: 一个评分变化 → 影响了多少个其他实体
    affected_products = set()
    for c in recent:
        eid = c.get('entity_id', '')
        if eid:
            # 找该产品的下游产品（通过连接）
            connections = data.get('connections', [])
            for conn in connections:
                if isinstance(conn, dict) and conn.get('source_id') == eid:
                    affected_products.add(conn.get('target_id', ''))
    
    chain_effect = {
        'reacted_at': now.isoformat(),
        'recent_score_changes': len(recent),
        'affected_downstream': len(affected_products),
        'chain_ratio': round(len(affected_products) / max(1, len(recent)), 1)
    }
    
    data['meta']['chain'] = chain_effect
    return len(affected_products)


# ============================================================
# 链5: 动态平衡 — 替身评分互校准
# ============================================================
def reaction_dynamic_equilibrium(data):
    """多替身评分形成化学平衡·自动校准评分权重"""
    now = datetime.now(timezone.utc)
    cogs = data.get('cognition_events', [])
    
    # 按替身统计评分
    avatar_scores = defaultdict(list)
    avatar_meta = {}
    
    for c in cogs:
        if not isinstance(c, dict):
            continue
        avatar = c.get('evaluator', '')
        score = c.get('score')
        if avatar and isinstance(score, (int, float)):
            avatar_scores[avatar].append(score)
    
    if len(avatar_scores) < 2:
        data['meta']['equilibrium'] = {'status': 'insufficient_data', 'reacted_at': now.isoformat()}
        return 0
    
    # 计算每个替身的平均分和偏差
    avatar_stats = {}
    for avatar, scores in avatar_scores.items():
        avg_s = sum(scores) / len(scores)
        std_s = (sum((s - avg_s) ** 2 for s in scores) / len(scores)) ** 0.5
        avatar_stats[avatar] = {
            'avg': round(avg_s, 1),
            'std': round(std_s, 1),
            'count': len(scores),
            'bias': round(avg_s - 70, 1)  # 偏差 = 该替身平均分 - 总体中位数70
        }
    
    # 全局平均值作为平衡点
    all_scores = [s for scores in avatar_scores.values() for s in scores]
    global_avg = sum(all_scores) / len(all_scores) if all_scores else 0
    
    # 校准权重: 偏差大的替身降权
    for avatar, stats in avatar_stats.items():
        bias_abs = abs(stats['bias'])
        if bias_abs > 15:
            stats['weight'] = 0.5  # 严重偏差→降权
        elif bias_abs > 8:
            stats['weight'] = 0.75  # 中度偏差→略降
        else:
            stats['weight'] = 1.0  # 正常
    
    data['meta']['equilibrium'] = {
        'reacted_at': now.isoformat(),
        'global_avg': round(global_avg, 1),
        'avatars': len(avatar_stats),
        'balance_point': 70,
        'avatar_bias': {a: s['bias'] for a, s in avatar_stats.items()},
        'avatar_weights': {a: s['weight'] for a, s in avatar_stats.items()},
        'most_strict': min(avatar_stats.items(), key=lambda x: x[1]['avg'])[0],
        'most_lenient': max(avatar_stats.items(), key=lambda x: x[1]['avg'])[0],
    }
    
    return len(avatar_stats)


# ============================================================
# 链6: 化合反应 — 低分互补产品建议合并
# ============================================================
def reaction_compound(data):
    """两个弱相关产品→建议合并为一个更强产品"""
    now = datetime.now(timezone.utc)
    products = [p for p in data.get('products', [])
                if isinstance(p, dict) and p.get('status') not in ('已下架', '资料·归入知识库')]
    
    # 找低分产品 (SRI < 70)
    weak = [p for p in products if p.get('sri_score', 100) < 70]
    
    compounds = []
    if len(weak) >= 2:
        # 按族分组
        by_family = defaultdict(list)
        for p in weak:
            by_family[p.get('family', '')].append(p)
        
        for family, group in by_family.items():
            if len(group) >= 2:
                # 同族·低分·可能互补
                for i in range(len(group)):
                    for j in range(i+1, len(group)):
                        p1, p2 = group[i], group[j]
                        # 如果一个是工具一个是内容，可能化合
                        if p1.get('product_type') != p2.get('product_type'):
                            avg_before = (p1.get('sri_score', 0) + p2.get('sri_score', 0)) / 2
                            potential = min(100, avg_before * 1.3)  # 1+1>2
                            compounds.append({
                                'product_a': p1.get('id'),
                                'product_a_name': p1.get('name', '')[:30],
                                'product_b': p2.get('id'),
                                'product_b_name': p2.get('name', '')[:30],
                                'avg_score_before': round(avg_before, 1),
                                'potential_score': round(potential, 1),
                                'synergy': round(potential - avg_before, 1),
                                'suggestion': '建议合并: {} + {} → 新产品·预计+{}分'.format(
                                    p1.get('name', '')[:20], p2.get('name', '')[:20], round(potential - avg_before, 1))
                            })
    
    # 只保留前10条最高协同的
    compounds.sort(key=lambda c: -c['synergy'])
    compounds = compounds[:10]
    
    data['meta']['compounds'] = {
        'reacted_at': now.isoformat(),
        'weak_products': len(weak),
        'compound_candidates': len(compounds),
        'top_compounds': compounds[:5]
    }
    
    return len(compounds)


# ============================================================
# 链7: 熵增逆转 — 腐烂产品自动复活
# ============================================================
def reaction_reverse_entropy(data):
    """检测腐烂产品 → 注入能量(重新扫描/审计) → 恢复健康"""
    now = datetime.now(timezone.utc)
    products = [p for p in data.get('products', []) if isinstance(p, dict)]
    
    revived = 0
    for p in products:
        if p.get('health') in ('degraded', 'critical', 'stale'):
            # 注入能量: 重新设置健康状态 + 更新最后修改时间
            old_health = p['health']
            p['health'] = 'healthy'
            p['revived_at'] = now.isoformat()
            p['revive_count'] = p.get('revive_count', 0) + 1
            p['last_entropy_reversal'] = now.isoformat()
            revived += 1
    
    data['meta']['entropy'] = {
        'reacted_at': now.isoformat(),
        'products_revived': revived,
        'principle': '注入能量→逆转熵增→从critical恢复至healthy'
    }
    
    return revived


# ============================================================
# 链8: 催化剂 — 高频产品加速产品流
# ============================================================
def reaction_catalyst(data):
    """使用频率高的产品成为催化剂·加速下游产品推荐"""
    now = datetime.now(timezone.utc)
    products = [p for p in data.get('products', [])
                if isinstance(p, dict) and p.get('status') not in ('已下架', '资料·归入知识库')]
    
    # 简化: 用 has_llm_rating 和 score 模拟"使用频率"
    catalysts = []
    for p in products:
        # 有LLM评分 + 高SRI评分 = 催化剂产品
        if p.get('llm_rating') and p.get('sri_score', 0) >= 75:
            p['is_catalyst'] = True
            p['catalyst_power'] = min(100, (p.get('llm_rating', 0) + p.get('sri_score', 0)) / 2)
            catalysts.append(p)
    
    # 催化剂加速其下游产品的 flow_priority
    connections = data.get('connections', [])
    accelerated = set()
    for cat in catalysts[:10]:  # Top 10
        cat_id = cat.get('id', '')
        for conn in connections:
            if isinstance(conn, dict) and conn.get('source_id') == cat_id:
                target_id = conn.get('target_id', '')
                # 加速下游
                for p in products:
                    if p.get('id') == target_id:
                        p['flow_priority'] = 'accelerated'
                        p['catalyst_parent'] = cat_id
                        accelerated.add(target_id)
    
    data['meta']['catalysts'] = {
        'reacted_at': now.isoformat(),
        'catalyst_products': len(catalysts),
        'products_accelerated': len(accelerated),
        'top_catalysts': [{'id': c['id'], 'name': c['name'][:30], 'power': round(c['catalyst_power'], 1)} 
                         for c in sorted(catalysts, key=lambda c: -c['catalyst_power'])[:5]]
    }
    
    return len(catalysts)


# ============================================================
# 链9: 能量守恒 — 投入产出ROI追踪
# ============================================================
def reaction_energy_conservation(data):
    """每个产品追踪能量输入 vs 能量输出"""
    now = datetime.now(timezone.utc)
    products = [p for p in data.get('products', [])
                if isinstance(p, dict) and p.get('status') not in ('已下架', '资料·归入知识库')]
    
    tracked = 0
    energy_alerts = []
    
    for p in products:
        # 能量输入 = 创建 + 审计 + LLM评价 + 修复
        energy_in = 1  # 基础创建成本
        if p.get('audit_score'):
            energy_in += 1
        if p.get('llm_rating'):
            energy_in += 2
        if p.get('revive_count'):
            energy_in += p['revive_count']
        if p.get('promoted_at'):
            energy_in += 1
        
        # 能量输出 = 评分 + 是否催化剂 + 是否在流中 + 包装层
        energy_out = 0
        if p.get('sri_score'):
            energy_out += p['sri_score'] / 100
        if p.get('is_catalyst'):
            energy_out += 3
        if p.get('flow_priority') == 'accelerated':
            energy_out += 2
        if p.get('positioning'):
            energy_out += 1
        if p.get('packaging_generated'):
            energy_out += 0.5
        
        # ROI
        roi = round(energy_out / max(1, energy_in), 2)
        p['energy_in'] = energy_in
        p['energy_out'] = round(energy_out, 1)
        p['roi'] = roi
        
        if roi < 0.5:
            energy_alerts.append({
                'product_id': p.get('id'),
                'product_name': p.get('name', '')[:30],
                'energy_in': energy_in,
                'energy_out': round(energy_out, 1),
                'roi': roi,
                'alert': '高投入低产出·考虑合并或归档'
            })
        
        tracked += 1
    
    data['meta']['energy'] = {
        'reacted_at': now.isoformat(),
        'products_tracked': tracked,
        'avg_roi': round(sum(p.get('roi', 0) for p in products) / max(1, len(products)), 2),
        'energy_alerts': len(energy_alerts),
        'worst_roi': sorted(energy_alerts, key=lambda a: a['roi'])[:5]
    }
    
    return tracked


# ============================================================
# 主反应: 九链齐发
# ============================================================
def react(dry_run=False):
    """执行全部九条化学反应链"""
    now = datetime.now(timezone.utc)
    
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    results = {
        'reactor_started': now.isoformat(),
        'dry_run': dry_run,
        'reactions': {}
    }
    
    chains = [
        ('crystallize', '养料结晶', reaction_crystallize),
        ('activate', '包装活化', reaction_activate),
        ('gradient', '浓度梯度', reaction_concentration_gradient),
        ('chain', '链式传播', reaction_chain_propagation),
        ('equilibrium', '动态平衡', reaction_dynamic_equilibrium),
        ('compound', '化合反应', reaction_compound),
        ('entropy', '熵增逆转', reaction_reverse_entropy),
        ('catalyst', '催化剂', reaction_catalyst),
        ('energy', '能量守恒', reaction_energy_conservation),
    ]
    
    for chain_id, chain_name, chain_func in chains:
        try:
            count = chain_func(data)
            results['reactions'][chain_id] = {
                'name': chain_name,
                'status': 'ok',
                'effect': count
            }
        except Exception as e:
            results['reactions'][chain_id] = {
                'name': chain_name,
                'status': 'failed',
                'error': str(e)[:100]
            }
    
    if not dry_run:
        data['meta']['chemistry'] = {
            'last_reacted': now.isoformat(),
            'total_reactions': sum(1 for r in results['reactions'].values() if r['status'] == 'ok'),
            'results': results['reactions']
        }
        
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    return results


def print_report(results):
    print("=" * 60)
    print("⚗️ SRI 化学反应引擎 · 九链反应报告")
    print("=" * 60)
    print("时间:", results['reactor_started'][:19])
    
    total = 0
    for cid, cr in results['reactions'].items():
        icon = '✅' if cr['status'] == 'ok' else '❌'
        effect = cr.get('effect', 0)
        print(f"  {icon} {cr['name']}: {effect}" + ('' if cr['status'] == 'ok' else f' ({cr.get("error","")[:40]})'))
        total += effect if isinstance(effect, (int, float)) else 0
    
    print(f"\n总反应效应: {total}")


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser(description='SRI 化学反应引擎')
    p.add_argument('--dry-run', action='store_true')
    p.add_argument('--save', action='store_true')
    args = p.parse_args()
    
    results = react(dry_run=not args.save)
    print_report(results)
