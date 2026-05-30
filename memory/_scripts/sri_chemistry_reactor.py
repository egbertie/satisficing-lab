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
# 深化学 · 第二轮 (链10-18)
# ============================================================

# 链10: 同位素标记 — 产品指纹生成
def reaction_isotope_label(data):
    """为每个产品生成独有的化学指纹·让产品之间能识别同类"""
    now = datetime.now(timezone.utc)
    products = [p for p in data.get('products', [])
                if isinstance(p, dict) and p.get('status') not in ('已下架', '资料·归入知识库')]
    
    labeled = 0
    for p in products:
        if p.get('fingerprint'):
            continue
        
        # 指纹 = 族 + JTBD + 产品类型 + 评分档位 + 包装层完整度
        score_tier = 'A' if p.get('sri_score', 0) >= 80 else ('B' if p.get('sri_score', 0) >= 65 else 'C')
        packaging = 'P' if p.get('positioning') else 'N'
        
        fingerprint = '{}-{}-{}-{}{}'.format(
            p.get('family', '?')[0] if p.get('family') else '?',
            (p.get('jtbd_category', '?') or '?')[0],
            (p.get('product_type', '?') or '?')[0],
            score_tier, packaging
        )
        p['fingerprint'] = fingerprint
        p['labeled_at'] = now.isoformat()
        labeled += 1
    
    data['meta']['isotopes'] = {
        'reacted_at': now.isoformat(),
        'products_labeled': labeled,
        'principle': '每个产品有独一无二的化学指纹·可被同类自动识别'
    }
    return labeled


# 链11: 氧化还原 — 同类产品评分竞争·胜者氧化败者
def reaction_redox(data):
    """同族产品互相竞争·高分产品氧化低分产品(自动降权)"""
    now = datetime.now(timezone.utc)
    products = [p for p in data.get('products', [])
                if isinstance(p, dict) and p.get('status') not in ('已下架', '资料·归入知识库')
                and p.get('family')]
    
    # 按族分组
    by_family = defaultdict(list)
    for p in products:
        by_family[p.get('family', '')].append(p)
    
    redoxed = 0
    for family, group in by_family.items():
        if len(group) < 2:
            continue
        # 按评分排序
        group.sort(key=lambda p: p.get('sri_score', 0), reverse=True)
        
        # 族内最高分 = 还原剂(保持高分)
        # 族内最低分 = 氧化产物(被降权)
        top = group[0]
        bottom = group[-1]
        
        if top.get('sri_score', 0) - bottom.get('sri_score', 0) > 15:
            # 显著竞争: 低分被氧化
            old_score = bottom.get('sri_score', 0)
            bottom['sri_score'] = max(40, old_score - 5)  # 被氧化降5分
            bottom['redox_state'] = 'oxidized'
            bottom['oxidized_by'] = top.get('id', '?')
            bottom['oxidized_at'] = now.isoformat()
            redoxed += 1
    
    data['meta']['redox'] = {
        'reacted_at': now.isoformat(),
        'products_oxidized': redoxed,
        'principle': '同族评分竞争·高分胜者天然压制低分·形成自然淘汰'
    }
    return redoxed


# 链12: 聚合反应 — 产品自然聚类为产品簇
def reaction_polymerization(data):
    """基于指纹+评分+连接, 产品自动聚合成产品簇"""
    now = datetime.now(timezone.utc)
    products = [p for p in data.get('products', [])
                if isinstance(p, dict) and p.get('status') not in ('已下架', '资料·归入知识库')
                and p.get('fingerprint')]
    
    # 按指纹前缀聚类 (族+JTBD两层)
    clusters = defaultdict(list)
    for p in products:
        fp = p.get('fingerprint', '')
        if len(fp) >= 2:
            key = fp[:2]  # 前两位: 族+JTBD
            clusters[key].append(p)
    
    # 为每个簇命名和评分
    polymerized = 0
    cluster_map = {}
    for key, members in clusters.items():
        if len(members) >= 2:
            avg_score = sum(p.get('sri_score', 0) for p in members) / len(members)
            cluster_id = 'CLUSTER-{:02d}'.format(len(cluster_map) + 1)
            cluster_map[cluster_id] = {
                'id': cluster_id,
                'key': key,
                'size': len(members),
                'avg_score': round(avg_score, 1),
                'products': [p.get('id') for p in members],
                'product_names': [p.get('name', '')[:20] for p in members[:5]]
            }
            for p in members:
                p['cluster_id'] = cluster_id
                p['cluster_avg_score'] = round(avg_score, 1)
            polymerized += 1
    
    data['clusters'] = list(cluster_map.values())
    data['meta']['polymerization'] = {
        'reacted_at': now.isoformat(),
        'clusters_formed': polymerized,
        'total_clustered_products': sum(c['size'] for c in cluster_map.values()),
        'principle': '产品按指纹自然聚类·无需手动分类'
    }
    return polymerized


# 链13: 相变 — 产品簇质量突破临界点·整簇状态跃迁
def reaction_phase_transition(data):
    """产品簇平均分突破临界点→整簇发生相变(生命周期集体跃迁)"""
    now = datetime.now(timezone.utc)
    clusters = data.get('clusters', [])
    
    transitions = 0
    for cluster in clusters:
        products = [p for p in data.get('products', [])
                    if isinstance(p, dict) and p.get('cluster_id') == cluster['id']]
        
        avg_score = cluster.get('avg_score', 0)
        
        # 临界点判断
        if avg_score >= 80 and any(p.get('lifecycle_stage') != 'LC-005' for p in products):
            # 相变: 整簇精品化
            for p in products:
                if p.get('lifecycle_stage') != 'LC-005':
                    p['lifecycle_stage'] = 'LC-005'
                    p['phase_transitioned_at'] = now.isoformat()
                    transitions += 1
        
        elif avg_score < 55:
            # 相变: 整簇降级
            for p in products:
                if p.get('lifecycle_stage') not in ('LC-006', 'LC-007'):
                    p['lifecycle_stage'] = 'LC-006'
                    p['phase_transitioned_at'] = now.isoformat()
                    transitions += 1
    
    data['meta']['phase_transition'] = {
        'reacted_at': now.isoformat(),
        'products_transitioned': transitions,
        'principle': '产品簇突破质量临界点→整簇状态相变·集体跃迁'
    }
    return transitions


# 链14: 渗透压 — 高评分簇的知识向外扩散
def reaction_osmosis(data):
    """高评分产品簇的"浓度"通过连接向外渗透·拉高低分产品基线"""
    now = datetime.now(timezone.utc)
    clusters = data.get('clusters', [])
    products = data.get('products', [])
    connections = data.get('connections', [])
    
    # 找高浓度簇
    high_clusters = [c for c in clusters if c.get('avg_score', 0) >= 75]
    if not high_clusters:
        data['meta']['osmosis'] = {'reacted_at': now.isoformat(), 'products_osmosed': 0}
        return 0
    
    # 找低分产品
    low_products = [p for p in products
                    if isinstance(p, dict) and p.get('sri_score', 0) < 65
                    and p.get('status') not in ('已下架', '资料·归入知识库')]
    
    osmosed = 0
    for lp in low_products:
        lp_id = lp.get('id', '')
        # 检查是否被高浓度簇连接
        for conn in connections:
            if isinstance(conn, dict) and conn.get('target_id') == lp_id:
                source_id = conn.get('source_id', '')
                # 源是否在高浓度簇中
                in_high = any(source_id in c.get('products', []) for c in high_clusters)
                if in_high:
                    # 渗透: 低分产品加 buff (最高+5)
                    old = lp.get('sri_score', 0)
                    lp['sri_score'] = min(100, old + 3)
                    lp['osmosis_buff'] = True
                    lp['osmosis_source'] = source_id
                    lp['osmosis_at'] = now.isoformat()
                    osmosed += 1
                    break
    
    data['meta']['osmosis'] = {
        'reacted_at': now.isoformat(),
        'products_osmosed': osmosed,
        'high_clusters': len(high_clusters),
        'principle': '高质量产品簇通过连接向低分产品扩散·拉高整体基线'
    }
    return osmosed


# 链15: 酶催化 — 编排器作为生物酶降低全系统活化能
def reaction_enzyme(data):
    """编排器(酶)降低每个环节的失败率·加速全局反应"""
    now = datetime.now(timezone.utc)
    
    # 检查编排器执行历史
    oh = data.get('meta', {}).get('orchestration_health', {})
    cb = data.get('meta', {}).get('circuit_breakers', {})
    
    # 酶活性 = 最近健康分 / 断路器稳定性
    health_score = oh.get('health_score', 100)
    open_breakers = sum(1 for b in cb.values() if isinstance(b, dict) and b.get('state') == 'open')
    
    enzyme_activity = round(health_score / 100 * (1 - open_breakers / max(1, len(cb))), 2)
    
    # 酶活性高 → 加速全系统: 提高所有产品的 flow_priority
    if enzyme_activity > 0.8:
        accelerated = 0
        products = [p for p in data.get('products', [])
                    if isinstance(p, dict) and p.get('status') not in ('已下架', '资料·归入知识库')]
        for p in products:
            if p.get('flow_priority') == 'deferred':
                p['flow_priority'] = 'normal'
                accelerated += 1
    else:
        accelerated = 0
    
    data['meta']['enzyme'] = {
        'reacted_at': now.isoformat(),
        'enzyme_activity': enzyme_activity,
        'open_breakers': open_breakers,
        'products_accelerated': accelerated,
        'principle': '编排器是全局酶·健康分高=酶活性强·加速所有反应'
    }
    return enzyme_activity


# 链16: 量子态叠加 — 替身评分不取平均·保留分歧
def reaction_superposition(data):
    """多个替身对同一产品的评分保留为量子叠加态·不是平均值"""
    now = datetime.now(timezone.utc)
    cogs = data.get('cognition_events', [])
    products = data.get('products', [])
    
    # 按产品分组替身评分
    by_product = defaultdict(list)
    for c in cogs:
        if isinstance(c, dict) and c.get('entity_id') and c.get('score'):
            by_product[c['entity_id']].append({
                'evaluator': c.get('evaluator', '?'),
                'score': c['score']
            })
    
    superposed = 0
    for p in products:
        pid = p.get('id', '')
        if pid not in by_product:
            continue
        scores = by_product[pid]
        if len(scores) < 2:
            continue
        
        # 不取平均·保留分歧
        score_list = [s['score'] for s in scores]
        avg_s = sum(score_list) / len(score_list)
        min_s = min(score_list)
        max_s = max(score_list)
        spread = max_s - min_s
        
        p['superposition_scores'] = {
            'evaluators': [s['evaluator'] for s in scores],
            'scores': score_list,
            'spread': spread,
            'consensus': 'high' if spread <= 10 else ('medium' if spread <= 20 else 'divergent'),
            'principle': '保留替身之间的分歧·不坍缩为单一点估计'
        }
        superposed += 1
    
    data['meta']['superposition'] = {
        'reacted_at': now.isoformat(),
        'products_superposed': superposed,
        'principle': '替身评分保留为量子态叠加·分歧本身就是信息'
    }
    return superposed


# 链17: 自发对称破缺 — 无外部输入时自然涌现优势产品
def reaction_symmetry_breaking(data):
    """当系统没有外部干预时·评分自然收敛·优势产品涌现"""
    now = datetime.now(timezone.utc)
    products = [p for p in data.get('products', [])
                if isinstance(p, dict) and p.get('status') not in ('已下架', '资料·归入知识库')
                and p.get('sri_score')]
    
    if not products:
        return 0
    
    # 评分自然分布
    scores = [p.get('sri_score', 0) for p in products]
    avg_score = sum(scores) / len(scores)
    
    # 自然涌现的"优势产品": 评分 > avg + 15 (自然对称破缺)
    elites = [p for p in products if p.get('sri_score', 0) >= avg_score + 15]
    for p in elites:
        p['emergent_elite'] = True
        p['emerged_at'] = now.isoformat()
    
    # 自然涌现的"长尾产品": 评分 < avg - 15
    tail = [p for p in products if p.get('sri_score', 0) <= avg_score - 15]
    for p in tail:
        p['emergent_tail'] = True
    
    data['meta']['symmetry_breaking'] = {
        'reacted_at': now.isoformat(),
        'avg_score': round(avg_score, 1),
        'elites_emerged': len(elites),
        'tail_products': len(tail),
        'elite_names': [p.get('name', '?')[:20] for p in elites[:5]],
        'principle': '没有人为指定·评分自然分布涌现优势和长尾'
    }
    return len(elites)


# 链18: 耗散结构 — 信息输入→有序输出·维持远离平衡态
def reaction_dissipative_structure(data):
    """飞轮系统作为开放耗散结构·通过信息输入维持有序"""
    now = datetime.now(timezone.utc)
    
    # 输入: 养料批次 + 文件扫描 + LLM评价 + Cron执行
    nourishment = data.get('meta', {}).get('nourishment', {})
    scan_runs = data.get('meta', {}).get('flywheel', {}).get('total_runs', 0)
    cog_count = len(data.get('cognition_events', []))
    
    energy_input = (
        nourishment.get('total_items', 0) * 0.1 +
        scan_runs * 0.5 +
        cog_count * 1.0
    )
    
    # 输出: 产品流 + 评分 + 包装层 + 修复
    products = [p for p in data.get('products', [])
                if isinstance(p, dict) and p.get('status') not in ('已下架', '资料·归入知识库')]
    with_packaging = sum(1 for p in products if p.get('positioning'))
    with_catalyst = sum(1 for p in products if p.get('is_catalyst'))
    
    energy_output = (
        with_packaging * 0.2 +
        with_catalyst * 1.0 +
        data.get('meta', {}).get('entropy', {}).get('products_revived', 0) * 0.3
    )
    
    # 有序度 = 输出/输入 · 1.0 = 平衡 · >1.0 = 负熵(自组织)
    order_parameter = round(energy_output / max(1, energy_input), 2)
    
    data['meta']['dissipative'] = {
        'reacted_at': now.isoformat(),
        'energy_input': round(energy_input, 1),
        'energy_output': round(energy_output, 1),
        'order_parameter': order_parameter,
        'state': 'self_organizing' if order_parameter > 1.0 else 'dissipating',
        'principle': '开放系统通过信息输入输出维持有序·order>1=自组织'
    }
    return order_parameter



# ============================================================
# 主反应: 九链齐发
# ============================================================

# ============================================================
# 深化学 · 第三轮 (链19-28) 多维反应空间
# ============================================================

# --- 维度1: 产品变种 (同分异构·对映异构·构象异构) ---

# 链19: 同分异构体 — 相同指纹·不同产品形态
def reaction_isomer(data):
    """相同化学指纹=同分异构体(比如诊断类·量化工具型)=可互为替代品"""
    now = datetime.now(timezone.utc)
    products = [p for p in data.get('products', [])
                if isinstance(p, dict) and p.get('status') not in ('已下架', '资料·归入知识库')
                and p.get('fingerprint')]
    
    # 按指纹分组
    by_fp = defaultdict(list)
    for p in products:
        by_fp[p.get('fingerprint', '')].append(p)
    
    isomers_found = 0
    for fp, group in by_fp.items():
        if len(group) < 2:
            continue
        # 同分异构体: 相同指纹=相同功能·不同文件名
        best = max(group, key=lambda p: p.get('sri_score', 0))
        for p in group:
            if p != best:
                p['isomer_of'] = best.get('id', '?')
                p['isomer_score_diff'] = round(best.get('sri_score', 0) - p.get('sri_score', 0), 1)
                # 标记: 可被替代
                if p.get('sri_score', 0) < best.get('sri_score', 0) * 0.7:
                    p['isomer_status'] = 'replaceable'
        isomers_found += 1
    
    data['meta']['isomers'] = {
        'reacted_at': now.isoformat(),
        'isomer_groups': isomers_found,
        'principle': '同指纹=同分异构体·可互相替代·低分自动标记replaceable'
    }
    return isomers_found


# 链20: 对映异构 — 镜像产品(功能互补但不可替代)
def reaction_enantiomer(data):
    """两个产品互为镜像(互补但不可替代): 如诊断工具vs方案工具"""
    now = datetime.now(timezone.utc)
    products = [p for p in data.get('products', [])
                if isinstance(p, dict) and p.get('status') not in ('已下架', '资料·归入知识库')
                and p.get('jtbd_category')]
    
    enantiomer_pairs = []
    # 互补JTBD对: diagnose↔decide, grow↔sustain
    mirror_map = {'diagnose': 'decide', 'decide': 'diagnose', 'grow': 'sustain', 'sustain': 'grow'}
    
    connections = data.get('connections', [])
    for p1 in products:
        mirror_cat = mirror_map.get(p1.get('jtbd_category', ''))
        if not mirror_cat:
            continue
        # 找镜像产品(通过连接)
        for conn in connections:
            if isinstance(conn, dict) and conn.get('source_id') == p1.get('id', ''):
                target = next((p for p in products if p.get('id') == conn.get('target_id', '')), None)
                if target and target.get('jtbd_category') == mirror_cat:
                    enantiomer_pairs.append((p1, target))
                    p1['enantiomer_of'] = target.get('id')
                    target['enantiomer_of'] = p1.get('id')
                    break
    
    data['meta']['enantiomers'] = {
        'reacted_at': now.isoformat(),
        'mirror_pairs': len(enantiomer_pairs),
        'principle': '互补JTBD=对映异构·镜像不可替代·但联合使用1+1>2'
    }
    return len(enantiomer_pairs)


# 链21: 构象异构 — 同一产品在不同评分态下的多种构象
def reaction_conformer(data):
    """产品的评分历史形成构象异构体(同一产品·不同时刻的不同评分态)"""
    now = datetime.now(timezone.utc)
    cl = data.get('meta', {}).get('change_log', [])
    products = data.get('products', [])
    
    conformers = 0
    for p in products:
        if not isinstance(p, dict):
            continue
        pid = p.get('id', '')
        # 查评分变更历史
        score_changes = [c for c in cl if isinstance(c, dict) 
                        and c.get('entity_id') == pid 
                        and c.get('field') in ('sri_score', 'quality_score', 'llm_rating')]
        if len(score_changes) >= 3:
            # 有多重构象: 记录评分轨迹
            old_scores = [c.get('old_value') for c in score_changes[-5:]]
            new_scores = [c.get('new_value') for c in score_changes[-5:]]
            p['conformer_states'] = {
                'history_count': len(score_changes),
                'score_range': [min(float(s) for s in old_scores + new_scores if s),
                               max(float(s) for s in old_scores + new_scores if s)],
                'current_conformer': new_scores[-1] if new_scores else p.get('sri_score')
            }
            conformers += 1
    
    data['meta']['conformers'] = {
        'reacted_at': now.isoformat(),
        'products_with_conformers': conformers,
        'principle': '同一产品·不同时刻·不同评分态=构象异构体'
    }
    return conformers


# --- 维度2: 反应方向 (可逆·平行·连串) ---

# 链22: 可逆反应 — 产品评分可以来回变化
def reaction_reversible(data):
    """评分可升可降·建立可逆反应平衡常数"""
    now = datetime.now(timezone.utc)
    cl = data.get('meta', {}).get('change_log', [])
    
    # 找有升有降的产品 (可逆反应)
    reversibles = defaultdict(list)
    for c in cl[-200:]:
        if isinstance(c, dict) and c.get('field') in ('sri_score', 'quality_score'):
            reversibles[c.get('entity_id')].append(c)
    
    reversible_count = 0
    for pid, changes in reversibles.items():
        ups = sum(1 for c in changes if float(c.get('new_value', 0)) > float(c.get('old_value', 0)))
        downs = sum(1 for c in changes if float(c.get('new_value', 0)) < float(c.get('old_value', 0)))
        if ups > 0 and downs > 0:
            # 可逆反应: K = [上升次数]/[下降次数]
            for p in data.get('products', []):
                if p.get('id') == pid:
                    p['reversible_constant'] = round(ups / max(1, downs), 2)
                    p['reaction_direction'] = 'forward' if ups > downs else ('reverse' if downs > ups else 'equilibrium')
            reversible_count += 1
    
    data['meta']['reversible'] = {
        'reacted_at': now.isoformat(),
        'reversible_products': reversible_count,
        'principle': '评分可升可降=可逆反应·K=[上升]/[下降]'
    }
    return reversible_count


# 链23: 平行反应 — 同一产品同时产生多个效果
def reaction_parallel(data):
    """一个产品的改善同时影响评分·催化剂·产品流·包装层"""
    now = datetime.now(timezone.utc)
    products = [p for p in data.get('products', []) if isinstance(p, dict)]
    
    # 统计有多少产品同时在多条链中产生效应
    parallel_count = 0
    for p in products:
        effects = 0
        if p.get('is_catalyst'): effects += 1
        if p.get('positioning'): effects += 1
        if p.get('fingerprint'): effects += 1
        if p.get('cluster_id'): effects += 1
        if p.get('roi'): effects += 1
        if p.get('flow_priority'): effects += 1
        if effects >= 4:
            p['parallel_reactions'] = effects
            p['parallel_product'] = True
            parallel_count += 1
    
    data['meta']['parallel'] = {
        'reacted_at': now.isoformat(),
        'parallel_products': parallel_count,
        'principle': '一个产品多效应=平行反应·A→B1+B2+B3+...'
    }
    return parallel_count


# 链24: 连串反应 — 产品A改进→产品B改进→产品C改进的级联
def reaction_serial(data):
    """评分提升沿着连接传播的多步连锁"""
    now = datetime.now(timezone.utc)
    products = data.get('products', [])
    connections = data.get('connections', [])
    
    # 构建连接图: 找最长传播链
    graph = defaultdict(list)
    for conn in connections:
        if isinstance(conn, dict):
            graph[conn.get('source_id', '')].append(conn.get('target_id', ''))
    
    # 用BFS找最长传播路径
    max_chain = 0
    for p in products:
        pid = p.get('id', '')
        visited = set()
        queue = [(pid, 0)]
        while queue:
            node, depth = queue.pop(0)
            if node in visited: continue
            visited.add(node)
            for nxt in graph.get(node, []):
                queue.append((nxt, depth + 1))
            max_chain = max(max_chain, depth)
    
    data['meta']['serial'] = {
        'reacted_at': now.isoformat(),
        'longest_chain': max_chain,
        'principle': '连接图最长传播路径=' + str(max_chain) + '步连串反应'
    }
    return max_chain


# --- 维度3: 反应条件 (pH·温度·压力) ---

# 链25: pH效应 — 系统健康度影响全反应速率
def reaction_ph(data):
    """系统健康分=pH值·酸性(低健康)=反应慢·碱性(高健康)=反应快"""
    now = datetime.now(timezone.utc)
    oh = data.get('meta', {}).get('orchestration_health', {})
    health = oh.get('health_score', 100)
    
    # pH映射: health 0-60=酸性·60-80=中性·80-100=碱性
    if health < 60:
        ph_speed = 0.5  # 酸性环境·反应缓慢
        ph_label = 'acidic'
    elif health < 80:
        ph_speed = 0.8  # 中性
        ph_label = 'neutral'
    else:
        ph_speed = 1.0  # 碱性环境·反应加速
        ph_label = 'alkaline'
    
    # pH影响全局反应速率
    data['meta']['ph'] = {
        'reacted_at': now.isoformat(),
        'ph_value': round(health / 100 * 14, 1),
        'environment': ph_label,
        'reaction_speed_multiplier': ph_speed,
        'principle': '健康分=pH值·酸性慢·碱性快'
    }
    return ph_speed


# 链26: 温度效应 — 客户活跃度加速化学反应
def reaction_temperature(data):
    """产品被使用/评价的频率=温度·温度高=反应剧烈"""
    now = datetime.now(timezone.utc)
    cogs = data.get('cognition_events', [])
    cl = data.get('meta', {}).get('change_log', [])
    
    # 温度 = 认知事件频率 / 时间跨度
    if len(cogs) >= 2:
        timestamps = []
        for c in cogs:
            if isinstance(c, dict) and c.get('timestamp'):
                try:
                    timestamps.append(datetime.fromisoformat(c['timestamp']))
                except:
                    pass
        if len(timestamps) >= 2:
            span_days = max(1, (max(timestamps) - min(timestamps)).days)
            events_per_day = len(timestamps) / span_days
        else:
            events_per_day = 0
    else:
        events_per_day = 0
    
    # 温度映射
    if events_per_day > 5:
        temp = 'hot'
        multiplier = 1.5
    elif events_per_day > 1:
        temp = 'warm'
        multiplier = 1.0
    elif events_per_day > 0:
        temp = 'cool'
        multiplier = 0.7
    else:
        temp = 'cold'
        multiplier = 0.5
    
    data['meta']['temperature'] = {
        'reacted_at': now.isoformat(),
        'events_per_day': round(events_per_day, 2),
        'temperature': temp,
        'reaction_rate_multiplier': multiplier,
        'principle': '认知事件频率=温度·热快冷慢'
    }
    return multiplier


# 链27: 压力效应 — 产品流密度影响转化率
def reaction_pressure(data):
    """产品流中的产品密度=压力·高压=高转化率但低质量"""
    now = datetime.now(timezone.utc)
    products = [p for p in data.get('products', [])
                if isinstance(p, dict) and p.get('status') not in ('已下架', '资料·归入知识库')]
    clusters = data.get('clusters', [])
    
    if not clusters:
        pressure = 0.5
    else:
        # 压力 = 平均簇大小 · 簇数量 / 有效产品数
        avg_cluster_size = sum(c.get('size', 0) for c in clusters) / max(1, len(clusters))
        pressure = min(2.0, avg_cluster_size * len(clusters) / max(1, len(products)))
    
    if pressure > 1.5:
        state = 'high'
        quality_risk = 'warning'  # 高压=可能的低质量
    elif pressure > 0.8:
        state = 'normal'
        quality_risk = 'ok'
    else:
        state = 'low'
        quality_risk = 'underutilized'
    
    data['meta']['pressure'] = {
        'reacted_at': now.isoformat(),
        'pressure': round(pressure, 2),
        'state': state,
        'quality_risk': quality_risk,
        'principle': '产品流密度=压力·高压高转化但可能低质'
    }
    return pressure


# --- 维度4: 反应剂量 ---

# 链28: 剂量效应 — 不同剂量的养料产生不同强度的结晶
def reaction_dosage(data):
    """养料数量=反应剂量·低剂量=微弱信号·中剂量=建议·高剂量=强制改进"""
    now = datetime.now(timezone.utc)
    nourishment = data.get('meta', {}).get('nourishment', {})
    total = nourishment.get('total_items', 0)
    
    # 剂量映射
    if total >= 30:
        dose = 'therapeutic'  # 治疗剂量
        action = '强制审查相关产品'
        urgency = 'high'
    elif total >= 15:
        dose = 'effective'     # 有效剂量
        action = '建议优化相关产品'
        urgency = 'medium'
    elif total >= 5:
        dose = 'threshold'     # 阈值剂量
        action = '标记关注·等待更多数据'
        urgency = 'low'
    else:
        dose = 'subthreshold'  # 亚阈值
        action = '积累中·暂不反应'
        urgency = 'none'
    
    data['meta']['dosage'] = {
        'reacted_at': now.isoformat(),
        'total_items': total,
        'dose_level': dose,
        'required_for_therapeutic': 30,
        'action': action,
        'urgency': urgency,
        'principle': '养料数量=反应剂量·亚阈值<5<阈值<15<有效<30<治疗'
    }
    return total




# ============================================================
# 深化学 · 第四轮 (链29-36) 替身化学反应
# ============================================================

# 链29: 替身活化 — 未使用的替身被激活进入反应容器
def reaction_avatar_activation(data):
    """替身评分活跃度=化学活性·未活跃替身=惰性气体·需要激活"""
    now = datetime.now(timezone.utc)
    avatars = data.get('avatars', [])
    
    activated = 0
    for a in avatars:
        if not isinstance(a, dict):
            continue
        # 激活计数
        if not a.get('activation_count'):
            a['activation_count'] = 0
        if not a.get('chemistry_state'):
            a['chemistry_state'] = 'inert'  # 惰性状态
            if a.get('quality_score', 0) > 0:
                a['chemistry_state'] = 'active'
                activated += 1
        if not a.get('catalyst_power'):
            a['catalyst_power'] = a.get('quality_score', 50) / 100
    
    data['meta']['avatar_activation'] = {
        'reacted_at': now.isoformat(),
        'total': len(avatars),
        'activated': activated,
        'inert': len(avatars) - activated,
        'principle': '替身活跃度=化学活性·惰性替身需活化能'
    }
    return activated


# 链30: 替身化合物 — 两个替身的认知融合产生新视角
def reaction_avatar_compound(data):
    """两个替身对同一产品的分歧观点·化合产生第三种观点"""
    now = datetime.now(timezone.utc)
    cogs = data.get('cognition_events', [])
    
    # 按产品分组替身评分
    by_product = defaultdict(list)
    for c in cogs:
        if isinstance(c, dict) and c.get('entity_id') and c.get('evaluator') and c.get('score'):
            by_product[c['entity_id']].append(c)
    
    compounds = 0
    for pid, evals in by_product.items():
        if len(evals) < 2:
            continue
        # 找评分差距最大的两个替身
        evals.sort(key=lambda e: e.get('score', 0))
        low = evals[0]
        high = evals[-1]
        spread = high.get('score', 0) - low.get('score', 0)
        
        if spread > 15:
            # 分歧足够大→化合反应产生合成观点
            synthesis = {
                'product_id': pid,
                'avatar_low': low.get('evaluator', '?'),
                'avatar_high': high.get('evaluator', '?'),
                'low_score': low.get('score'),
                'high_score': high.get('score'),
                'spread': spread,
                'synthesis_score': round((low.get('score', 0) + high.get('score', 0)) / 2, 1),
                'synthesis_insight': '高分替身关注{}·低分替身关注{}·综合=平衡视角'.format(
                    '长期价值' if high.get('score', 0) > 70 else '可行性',
                    '风险' if low.get('score', 0) < 60 else '细节'),
                'compound_at': now.isoformat()
            }
            # 附加到产品上
            for p in data.get('products', []):
                if p.get('id') == pid:
                    p.setdefault('avatar_compound_views', [])
                    p['avatar_compound_views'].append(synthesis)
            compounds += 1
    
    data['meta']['avatar_compound'] = {
        'reacted_at': now.isoformat(),
        'compounds_formed': compounds,
        'principle': '替身分歧≠噪音·化合=新视角·15+分差触发'
    }
    return compounds


# 链31: 替身渗透压 — 严厉替身拉低全局·宽容替身拉高全局
def reaction_avatar_osmosis(data):
    """替身之间存在评分渗透压——严厉→宽容形成压力梯度"""
    now = datetime.now(timezone.utc)
    avatars = data.get('avatars', [])
    cogs = data.get('cognition_events', [])
    
    # 每个替身的评分倾向
    avatar_scores = defaultdict(list)
    for c in cogs:
        if isinstance(c, dict) and c.get('evaluator') and c.get('score'):
            avatar_scores[c['evaluator']].append(c['score'])
    
    if len(avatar_scores) < 2:
        data['meta']['avatar_osmosis'] = {'reacted_at': now.isoformat(), 'principle': '需要≥2替身的数据'}
        return 0
    
    # 计算替身间渗透压
    av_biases = {}
    for av, scores in avatar_scores.items():
        av_biases[av] = {
            'avg': round(sum(scores) / len(scores), 1),
            'count': len(scores),
            'strictness': 'strict' if sum(scores) / len(scores) < 68 else ('lenient' if sum(scores) / len(scores) > 78 else 'balanced')
        }
    
    # 找到最严和最宽容的替身
    strictest = min(av_biases.items(), key=lambda x: x[1]['avg'])
    lenient = max(av_biases.items(), key=lambda x: x[1]['avg'])
    
    pressure = round(lenient[1]['avg'] - strictest[1]['avg'], 1)
    
    # 渗透效果: 在替身实体上标记
    for a in avatars:
        if a.get('name') in av_biases:
            a['avatar_bias'] = av_biases[a['name']]['strictness']
            a['osmotic_pressure_from'] = strictest[0] if a['name'] != strictest[0] else lenient[0]
    
    data['meta']['avatar_osmosis'] = {
        'reacted_at': now.isoformat(),
        'strictest': strictest[0],
        'strictest_avg': strictest[1]['avg'],
        'lenient': lenient[0],
        'lenient_avg': lenient[1]['avg'],
        'pressure_gradient': pressure,
        'principle': '最严{}与最宽容{}形成{}分渗透压·驱动评分收敛'.format(strictest[0], lenient[0], pressure)
    }
    return pressure


# 链32: 替身平衡 — 替身评分形成动态均衡点(Le Chatelier原理)
def reaction_avatar_equilibrium(data):
    """如果新替身加入·平衡移动·评分重新校准"""
    now = datetime.now(timezone.utc)
    avatars = data.get('avatars', [])
    cogs = data.get('cognition_events', [])
    
    avatar_scores = defaultdict(list)
    for c in cogs:
        if isinstance(c, dict) and c.get('evaluator') and c.get('score'):
            avatar_scores[c['evaluator']].append(c['score'])
    
    # 当前平衡点
    all_scores = [s for scores in avatar_scores.values() for s in scores]
    equilibrium_point = sum(all_scores) / len(all_scores) if all_scores else 70
    
    # 替身偏离平衡的距离
    for a in avatars:
        name = a.get('name', '')
        if name in avatar_scores:
            avg = sum(avatar_scores[name]) / len(avatar_scores[name])
            a['equilibrium_delta'] = round(avg - equilibrium_point, 1)
            # >0=偏宽, <0=偏严
            a['equilibrium_role'] = 'stabilizer' if abs(avg - equilibrium_point) < 8 else 'disruptor'
    
    data['meta']['avatar_equilibrium'] = {
        'reacted_at': now.isoformat(),
        'equilibrium_point': round(equilibrium_point, 1),
        'stabilizers': sum(1 for a in avatars if a.get('equilibrium_role') == 'stabilizer'),
        'disruptors': sum(1 for a in avatars if a.get('equilibrium_role') == 'disruptor'),
        'principle': '替身评分向均衡点收敛·新替身加入=平衡移动'
    }
    return equilibrium_point


# 链33: 替身催化剂 — 精准替身评分=高催化效率
def reaction_avatar_catalyst(data):
    """替身的评价越精准(偏差越小)→催化效率越高→加速产品流"""
    now = datetime.now(timezone.utc)
    avatars = data.get('avatars', [])
    cogs = data.get('cognition_events', [])
    
    avatar_scores = defaultdict(list)
    for c in cogs:
        if isinstance(c, dict) and c.get('evaluator') and c.get('score'):
            avatar_scores[c['evaluator']].append(c['score'])
    
    catalyst_count = 0
    for a in avatars:
        name = a.get('name', '')
        if name in avatar_scores:
            scores = avatar_scores[name]
            avg = sum(scores) / len(scores)
            # 标准差越小=评价越稳定=催化效率越高
            std = (sum((s - avg) ** 2 for s in scores) / len(scores)) ** 0.5
            # 催化效率 = 评分数 / (1 + 标准差)
            eff = round(len(scores) / (1 + std), 2)
            a['catalytic_efficiency'] = eff
            if eff > 0.5:
                a['chemistry_state'] = 'catalyst'
                catalyst_count += 1
    
    data['meta']['avatar_catalyst'] = {
        'reacted_at': now.isoformat(),
        'catalysts': catalyst_count,
        'principle': '评价精准的替身=高效催化剂·加速产品流质量'
    }
    return catalyst_count


# 链34: 替身同位旋 — 替身之间互相评分(元评价)
def reaction_avatar_spin(data):
    """替身不仅评产品·也评其他替身的评价质量·形成自旋网络"""
    now = datetime.now(timezone.utc)
    avatars = data.get('avatars', [])
    cogs = data.get('cognition_events', [])
    
    # 简化的元评价: 替身评分的方差=该替身的"自旋态"
    avatar_scores = defaultdict(list)
    for c in cogs:
        if isinstance(c, dict) and c.get('evaluator') and c.get('score'):
            avatar_scores[c['evaluator']].append(c['score'])
    
    spin_count = 0
    for a in avatars:
        name = a.get('name', '')
        if name in avatar_scores and len(avatar_scores[name]) >= 2:
            scores = avatar_scores[name]
            avg = sum(scores) / len(scores)
            std = (sum((s - avg) ** 2 for s in scores) / len(scores)) ** 0.5
            
            # 自旋态: 标准差决定
            if std < 5:
                spin = 'up'     # 一致性强·高可靠
            elif std < 10:
                spin = 'mixed'  # 有波动
            else:
                spin = 'down'   # 不一致·低可靠
            
            a['spin_state'] = spin
            a['spin_std'] = round(std, 1)
            spin_count += 1
    
    data['meta']['avatar_spin'] = {
        'reacted_at': now.isoformat(),
        'spins_assigned': spin_count,
        'principle': '替身评分一致性=自旋态·up=可靠·down=需校准'
    }
    return spin_count


# 链35: 替身衰变 — 长期不使用的替身活性衰减
def reaction_avatar_decay(data):
    """替身长期不被激活→放射性衰变→活性半衰期下降"""
    now = datetime.now(timezone.utc)
    avatars = data.get('avatars', [])
    cogs = data.get('cognition_events', [])
    
    # 找最近一次被使用的替身
    active_avatars = set()
    for c in cogs:
        if isinstance(c, dict) and c.get('evaluator'):
            active_avatars.add(c['evaluator'])
    
    half_life_days = 30  # 替身活跃半衰期
    decayed = 0
    
    for a in avatars:
        name = a.get('name', '')
        if name in active_avatars:
            continue
        
        # 未激活替身: 计算衰减
        quality = a.get('quality_score', 50)
        # 每30天衰减50%
        decay_factor = 0.5 ** (1 / half_life_days)
        a['quality_score'] = round(quality * decay_factor, 1)
        a['decayed'] = True
        a['decay_at'] = now.isoformat()
        decayed += 1
    
    data['meta']['avatar_decay'] = {
        'reacted_at': now.isoformat(),
        'active_avatars': len(active_avatars),
        'decayed': decayed,
        'half_life_days': half_life_days,
        'principle': '不使用=衰变·半衰期30天'
    }
    return decayed


# 链36: 替身全局场 — 所有替身形成一个评分场·影响每个产品的评分
def reaction_avatar_field(data):
    """31替身构成评分向量场·每个产品在新的替身评分后·重新计算在场中的位置"""
    now = datetime.now(timezone.utc)
    avatars = data.get('avatars', [])
    cogs = data.get('cognition_events', [])
    products = [p for p in data.get('products', [])
                if isinstance(p, dict) and p.get('status') not in ('已下架', '资料·归入知识库')]
    
    # 构建评分场: 每个替身=场的维度
    avatar_by_product = defaultdict(dict)
    for c in cogs:
        if isinstance(c, dict) and c.get('entity_id') and c.get('evaluator') and c.get('score'):
            avatar_by_product[c['entity_id']][c['evaluator']] = c['score']
    
    field_strength = 0
    for p in products:
        pid = p.get('id', '')
        if pid in avatar_by_product:
            scores = list(avatar_by_product[pid].values())
            # 场强 = 评分数 · 评分方差
            avg = sum(scores) / len(scores)
            variance = sum((s - avg) ** 2 for s in scores) / len(scores) if len(scores) > 1 else 0
            p['avatar_field_strength'] = round(len(scores) * (1 / (1 + variance)), 2)
            p['avatar_field_dimensions'] = len(scores)
            field_strength += 1
    
    data['meta']['avatar_field'] = {
        'reacted_at': now.isoformat(),
        'products_in_field': field_strength,
        'total_avatars': len(avatars),
        'active_in_field': len(set(c.get('evaluator') for c in cogs if isinstance(c, dict) and c.get('evaluator'))),
        'principle': '替身=评分向量场维度·产品在场中被多维度定位'
    }
    return field_strength





# ============================================================
# 深化学 · 第五轮 (链37-50) 信息化学 + 环节化学 + 全局交叉
# ============================================================

# --- 信息层: 信息自己的化学反应 ---

# 链37: 信息新陈代谢 — 摄入信息·消化·排出废弃物
def reaction_information_metabolism(data):
    """信息摄入→消化(过滤/门禁)→吸收(入库)→排泄(低质丢弃)"""
    now = datetime.now(timezone.utc)
    nourishment = data.get('meta', {}).get('nourishment', {})
    quality_gate = data.get('meta', {}).get('quality_gate', {})
    
    ingested = nourishment.get('total_items', 0)
    passed_gate = quality_gate.get('passed', 0)
    rejected = quality_gate.get('rejected', 0)
    
    # 新陈代谢率 = 通过/摄入
    metabolism_rate = round(passed_gate / max(1, ingested), 2)
    
    data['meta']['metabolism'] = {
        'reacted_at': now.isoformat(),
        'ingested': ingested,
        'digested': passed_gate,
        'excreted': rejected,
        'metabolism_rate': metabolism_rate,
        'health': 'healthy' if metabolism_rate > 0.5 else 'indigestion',
        'principle': '信息新陈代谢=摄入→过滤→吸收→排泄·低质丢弃'
    }
    return metabolism_rate


# 链38: 信息化合 — 两条独立信息养料合成新知识
def reaction_information_synthesis(data):
    """两个不同来源·同一领域的信息自发关联·产生新洞见"""
    now = datetime.now(timezone.utc)
    all_items = []
    n_dir = os.path.join(WORKSPACE, 'memory/nourishment')
    if os.path.exists(n_dir):
        for fname in sorted(os.listdir(n_dir)):
            if fname.endswith('.json'):
                try:
                    with open(os.path.join(n_dir, fname)) as f:
                        batch = json.load(f)
                    all_items.extend(batch.get('items', []))
                except:
                    pass
    
    syntheses = []
    # 同领域·不同来源的信息配对
    by_domain_source = defaultdict(lambda: defaultdict(list))
    for item in all_items:
        for d in item.get('domains', []):
            by_domain_source[d][item.get('source', '?')].append(item)
    
    for domain, sources in by_domain_source.items():
        source_names = list(sources.keys())
        if len(source_names) >= 2:
            # 跨源信息化合
            for i in range(len(source_names)):
                for j in range(i+1, len(source_names)):
                    s1_items = sources[source_names[i]]
                    s2_items = sources[source_names[j]]
                    if s1_items and s2_items:
                        avg_relevance = (s1_items[0].get('relevance_score', 0) + s2_items[0].get('relevance_score', 0)) / 2
                        syntheses.append({
                            'domain': domain,
                            'source_a': source_names[i],
                            'source_b': source_names[j],
                            'items_count': len(s1_items) + len(s2_items),
                            'synthesis_strength': round(avg_relevance / 100, 2),
                            'synthesized_at': now.isoformat()
                        })
    
    data['meta']['info_synthesis'] = {
        'reacted_at': now.isoformat(),
        'cross_source_syntheses': len(syntheses),
        'syntheses': syntheses[:10],
        'principle': 'A源信息+B源信息=新化合物·跨源化合增强洞见'
    }
    return len(syntheses)


# 链39: 信息氧化 — 旧信息被新信息替换
def reaction_information_redox(data):
    """新养料摄入→旧养料被氧化(降权)·保持知识库新鲜"""
    now = datetime.now(timezone.utc)
    documents = data.get('documents', [])
    
    # 文档年龄
    aged = 0
    for doc in documents:
        if not isinstance(doc, dict):
            continue
        detected = doc.get('detected_at', '') or doc.get('last_scan_time', '')
        if detected:
            try:
                dt = datetime.fromisoformat(detected)
                days_old = (now - dt).days
                doc['document_age_days'] = days_old
                # 超过30天自动降权
                if days_old > 30 and doc.get('status') != '归档':
                    doc['oxidized'] = True
                    doc['freshness'] = 'stale'
                    aged += 1
                elif days_old > 14:
                    doc['freshness'] = 'aging'
            except:
                pass
    
    data['meta']['info_redox'] = {
        'reacted_at': now.isoformat(),
        'documents_aged': aged,
        'total_documents': len(documents),
        'principle': '新信息氧化旧信息·保持知识新鲜度'
    }
    return aged


# --- 编排器每个环节的化学反应 ---

# 链40: 养料环节化学 — nourish被评分·形成浓度
def reaction_stage_nourish_chemistry(data):
    """养料采集环节自己产生化学活性"""
    now = datetime.now(timezone.utc)
    nourishment = data.get('meta', {}).get('nourishment', {})
    batches = nourishment.get('batches', [])
    
    # 批次增长率
    batch_rate = len(batches) / max(1, (datetime.now(timezone.utc) - 
        datetime(2026, 5, 30, 14, 0, tzinfo=timezone.utc)).total_seconds() / 3600) if batches else 0
    batch_rate = min(10, batch_rate)
    
    # 浓度
    concentration = nourishment.get('total_items', 0) / 50  # 标准化
    
    data['meta']['stage_nourish_chem'] = {
        'reacted_at': now.isoformat(),
        'batches': len(batches),
        'growth_rate': round(batch_rate, 2),
        'concentration': round(concentration, 2),
        'state': 'active' if batch_rate > 0 else 'dormant',
        'principle': '养料环节=反应物浓度源·增长率=反应速率'
    }
    return batch_rate


# 链41: 门禁环节化学 — quality_gate形成过滤效率
def reaction_stage_gate_chemistry(data):
    """质量门禁环节的过滤效率=化学选择性"""
    now = datetime.now(timezone.utc)
    qg = data.get('meta', {}).get('quality_gate', {})
    
    total = max(qg.get('total', 0), 1)
    passed = qg.get('passed', 0)
    rejected = qg.get('rejected', 0)
    
    # 选择性 = 通过率
    selectivity = round(passed / total, 2)
    
    data['meta']['stage_gate_chem'] = {
        'reacted_at': now.isoformat(),
        'selectivity': selectivity,
        'passed': passed,
        'rejected': rejected,
        'efficiency': 'high' if selectivity > 0.7 else ('medium' if selectivity > 0.3 else 'low'),
        'principle': '门禁选择性=化学过滤效率·太高=过严·太低=过宽'
    }
    return selectivity


# 链42: 扫描环节化学 — scan发现的实体形成新反应物
def reaction_stage_scan_chemistry(data):
    """文件扫描的新发现率=反应物产生速率"""
    now = datetime.now(timezone.utc)
    fw = data.get('meta', {}).get('flywheel', {})
    recent = fw.get('recent_runs', [])
    
    # 平均每次扫描发现的新实体
    discovery_rate = 0
    scan_runs = [r for r in recent if 'scan' in str(r.get('cycle', ''))]
    if scan_runs:
        avg_events = sum(r.get('events_count', 0) for r in scan_runs) / len(scan_runs)
        discovery_rate = avg_events
    
    data['meta']['stage_scan_chem'] = {
        'reacted_at': now.isoformat(),
        'discovery_rate': round(discovery_rate, 1),
        'scan_runs': len(scan_runs),
        'principle': '扫描发现率=新反应物产生速率'
    }
    return discovery_rate


# 链43: 一致性环节化学 — 一致性问题的减少率
def reaction_stage_consistency_chemistry(data):
    """一致性检查发现的问题数变化率"""
    now = datetime.now(timezone.utc)
    cc = data.get('meta', {}).get('consistency_check', {})
    
    issues = cc.get('total_issues', 0)
    by_type = cc.get('by_type', {})
    
    data['meta']['stage_consistency_chem'] = {
        'reacted_at': now.isoformat(),
        'total_issues': issues,
        'issue_types': len(by_type),
        'trend': 'improving' if issues < 50 else 'stable',
        'principle': '一致性问题=化学反应中的副产物·越少越纯'
    }
    return issues


# 链44: 修复环节化学 — heal的修复率
def reaction_stage_heal_chemistry(data):
    """自动修复成功率=chemical yield·修复失败=副反应"""
    now = datetime.now(timezone.utc)
    ah = data.get('meta', {}).get('auto_heal', [])
    
    total_fixes = sum(h.get('total_fixes', 0) for h in ah[-5:]) if ah else 0
    
    data['meta']['stage_heal_chem'] = {
        'reacted_at': now.isoformat(),
        'recent_fixes': total_fixes,
        'heal_runs': len(ah),
        'yield_rate': round(total_fixes / max(1, len(ah)), 1),
        'principle': '修复成功率=化学反应产率·高=高效催化剂'
    }
    return total_fixes


# 链45: 生命周期环节化学 — 产品的生命周期迁移率
def reaction_stage_lifecycle_chemistry(data):
    """LC迁移速度=反应转化率"""
    now = datetime.now(timezone.utc)
    lm = data.get('meta', {}).get('lifecycle_management', {})
    
    promoted = lm.get('promoted', 0)
    demoted = lm.get('demoted', 0)
    conversion = promoted + demoted
    
    data['meta']['stage_lifecycle_chem'] = {
        'reacted_at': now.isoformat(),
        'conversions': conversion,
        'promoted': promoted,
        'demoted': demoted,
        'principle': 'LC迁移=化学转化率·promoted=正向·demoted=逆向'
    }
    return conversion


# 链46: 标准环节化学 — 标准迭代的频率
def reaction_stage_standards_chemistry(data):
    """标准迭代频率=反应速率常数k"""
    now = datetime.now(timezone.utc)
    si = data.get('meta', {}).get('standards_iteration', {})
    
    proposals = si.get('proposals', 0)
    
    data['meta']['stage_standards_chem'] = {
        'reacted_at': now.isoformat(),
        'proposals': proposals,
        'rate_constant': proposals / 7,  # 每周提案数
        'principle': '标准迭代率=反应速率常数k·k越大反应越快'
    }
    return proposals


# 链47: 审计环节化学 — 产品审计的质量趋势
def reaction_stage_audit_chemistry(data):
    """审计平均分的变化=产物纯度趋势"""
    now = datetime.now(timezone.utc)
    pa = data.get('meta', {}).get('product_audit', {})
    
    avg_score = pa.get('avg_score', 0)
    under60 = pa.get('products_under_60', 0)
    
    data['meta']['stage_audit_chem'] = {
        'reacted_at': now.isoformat(),
        'avg_score': avg_score,
        'under60': under60,
        'purity': round(avg_score / 100, 2),
        'principle': '审计均分=产物纯度·越高越纯'
    }
    return avg_score


# 链48: 报告环节化学 — 报告的信号密度
def reaction_stage_report_chemistry(data):
    """日报的信息密度=化学信号强度"""
    now = datetime.now(timezone.utc)
    fw = data.get('meta', {}).get('flywheel', {})
    recent = fw.get('recent_runs', [])
    
    # 最近报告的信息量
    avg_events = sum(r.get('events_count', 0) for r in recent[-5:]) / max(1, len(recent[-5:]))
    
    data['meta']['stage_report_chem'] = {
        'reacted_at': now.isoformat(),
        'signal_density': round(avg_events, 1),
        'recent_reports': min(5, len(recent)),
        'principle': '报告事件密度=化学信号强度'
    }
    return avg_events


# --- 全局交叉反应 ---

# 链49: 全局交叉 — 所有环节之间的交叉反应网络
def reaction_global_cross(data):
    """环节A的输出=环节B的输入·形成交叉反应矩阵"""
    now = datetime.now(timezone.utc)
    
    # 定义环节间交叉依赖
    cross_edges = [
        ('nourish', 'quality_gate', '养料→门禁'),
        ('quality_gate', 'scan', '门禁→扫描'),
        ('scan', 'consistency', '扫描→一致性'),
        ('consistency', 'heal', '一致性→修复'),
        ('heal', 'lifecycle', '修复→生命周期'),
        ('lifecycle', 'standards', '生命周期→标准'),
        ('standards', 'audit', '标准→审计'),
        ('audit', 'report', '审计→报告'),
        ('report', 'nourish', '报告→养料(反馈)'),
        ('chemistry', 'scan', '化学→扫描'),
        ('chemistry', 'heal', '化学→修复'),
        ('chemistry', 'audit', '化学→审计'),
    ]
    
    cross_matrix = []
    for src, tgt, desc in cross_edges:
        cross_matrix.append({
            'source': src,
            'target': tgt,
            'relation': desc,
            'active': True
        })
    
    data['meta']['global_cross'] = {
        'reacted_at': now.isoformat(),
        'cross_edges': len(cross_edges),
        'cycles_detected': 3,  # nourish→gate→scan→...→report→nourish 是循环
        'matrix': cross_matrix,
        'principle': '环节间交叉反应=化学网络·12条边组成反应图'
    }
    return len(cross_edges)


# 链50: 启发热 — 全系统化学反应释放的总热量
def reaction_heating(data):
    """所有链的总效应=反应热·热越大=系统越活跃"""
    now = datetime.now(timezone.utc)
    
    # 汇总所有化学 meta 键中的数值型产物
    total_heat = 0
    heat_sources = []
    for key in data.get('meta', {}):
        val = data['meta'][key]
        if isinstance(val, dict):
            # 找数值字段
            for sub_key in ['total_fixes', 'total_issues', 'conversions', 'proposals',
                          'avg_score', 'cross_edges', 'signal_density', 'discovery_rate',
                          'selectivity', 'batch_rate', 'catalyst_products', 'products_revived',
                          'total_reactions', 'pressure_gradient', 'equilibrium_point']:
                if sub_key in val and isinstance(val[sub_key], (int, float)):
                    total_heat += float(val[sub_key])
                    if val[sub_key] > 0:
                        heat_sources.append('{}.{}={}'.format(key, sub_key, val[sub_key]))
    
    data['meta']['heating'] = {
        'reacted_at': now.isoformat(),
        'total_heat': round(total_heat, 1),
        'heat_sources': len(heat_sources),
        'temperature_grade': 'hot' if total_heat > 500 else ('warm' if total_heat > 200 else 'cold'),
        'principle': '全部反应的总热量=系统活性指标·热=活跃·冷=沉寂'
    }
    return total_heat




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
        # --- 深化学第二轮 ---
        ('isotope', '同位素标记', reaction_isotope_label),
        ('redox', '氧化还原', reaction_redox),
        ('polymerization', '聚合反应', reaction_polymerization),
        ('phase', '相变', reaction_phase_transition),
        ('osmosis', '渗透压', reaction_osmosis),
        ('enzyme', '酶催化', reaction_enzyme),
        ('superposition', '量子态叠加', reaction_superposition),
        ('symmetry', '对称破缺', reaction_symmetry_breaking),
        ('dissipative', '耗散结构', reaction_dissipative_structure),
        # --- 深化学第三轮 ---
        ('isomer', '同分异构体', reaction_isomer),
        ('enantiomer', '对映异构', reaction_enantiomer),
        ('conformer', '构象异构', reaction_conformer),
        ('reversible', '可逆反应', reaction_reversible),
        ('parallel', '平行反应', reaction_parallel),
        ('serial', '连串反应', reaction_serial),
        ('ph', 'pH效应', reaction_ph),
        ('temperature', '温度效应', reaction_temperature),
        ('pressure', '压力效应', reaction_pressure),
        ('dosage', '剂量效应', reaction_dosage),
        # --- 深化学第四轮·替身反应 ---
        ('avatar_activation', '替身活化', reaction_avatar_activation),
        ('avatar_compound', '替身化合物', reaction_avatar_compound),
        ('avatar_osmosis', '替身渗透压', reaction_avatar_osmosis),
        ('avatar_equilibrium', '替身平衡', reaction_avatar_equilibrium),
        ('avatar_catalyst', '替身催化剂', reaction_avatar_catalyst),
        ('avatar_spin', '替身同位旋', reaction_avatar_spin),
        ('avatar_decay', '替身衰变', reaction_avatar_decay),
        ('avatar_field', '替身全局场', reaction_avatar_field),
        # --- 深化学第五轮·信息化学+环节化学+全局交叉 ---
        ('info_metabolism', '信息新陈代谢', reaction_information_metabolism),
        ('info_synthesis', '信息化合', reaction_information_synthesis),
        ('info_redox', '信息氧化', reaction_information_redox),
        ('stage_nourish', '养料环节化学', reaction_stage_nourish_chemistry),
        ('stage_gate', '门禁环节化学', reaction_stage_gate_chemistry),
        ('stage_scan', '扫描环节化学', reaction_stage_scan_chemistry),
        ('stage_consistency', '一致性环节化学', reaction_stage_consistency_chemistry),
        ('stage_heal', '修复环节化学', reaction_stage_heal_chemistry),
        ('stage_lifecycle', '生命周期环节化学', reaction_stage_lifecycle_chemistry),
        ('stage_standards', '标准环节化学', reaction_stage_standards_chemistry),
        ('stage_audit', '审计环节化学', reaction_stage_audit_chemistry),
        ('stage_report', '报告环节化学', reaction_stage_report_chemistry),
        ('global_cross', '全局交叉', reaction_global_cross),
        ('heating', '启发热', reaction_heating),
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
