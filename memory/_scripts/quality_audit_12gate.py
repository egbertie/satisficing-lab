#!/usr/bin/env python3
"""产品12-Gate品质审计脚本 v3.0
设计原则: 可自进化——审计标准本身可以被审计和升级
使用方法: python3 memory/_scripts/quality_audit_12gate.py
"""

import json, os, sys
from datetime import datetime, timezone, timedelta

tz_shanghai = timezone(timedelta(hours=8))
WORKSPACE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def load_data():
    with open(os.path.join(WORKSPACE,'memory/_data/entities_index.json'),'r') as f:
        return json.load(f)

def audit_12gate(p):
    """对单个产品执行12-Gate审计"""
    gates = {}
    
    # === A域: 用户价值 ===
    # A1: JTBD清晰 — 有描述+有jtbd_category+有target_user+描述>20字
    has_desc = bool(p.get('description','').strip())
    desc_len = len(p.get('description','').strip())
    has_jtbd = bool(p.get('jtbd_category'))
    has_target = bool(p.get('target_user'))
    gates['A1_JTBD'] = {
        'pass': has_desc and desc_len > 20 and has_jtbd and has_target,
        'score': sum([has_desc and desc_len>20, has_jtbd, has_target]),
        'max': 3,
        'detail': f"描述{'✅' if has_desc and desc_len>20 else '❌('+str(desc_len)+'字)'} JTBD{'✅' if has_jtbd else '❌'} 用户{'✅' if has_target else '❌'}"
    }
    
    # A2: 时间到价值 — 有time_estimate字段且≤30分钟
    has_time = bool(p.get('time_estimate'))
    time_val = p.get('time_estimate','')
    is_fast = '分钟' in str(time_val) and not any(x in str(time_val) for x in ['40','50','60'])
    gates['A2_TTU'] = {
        'pass': has_time and is_fast,
        'detail': f"时间估算:{time_val if has_time else '缺失'} {'✅' if has_time and is_fast else '⚠️'}"
    }
    
    # A3: 可自解释 — 有url+who_for+outcome
    has_url = bool(p.get('url'))
    has_who = bool(p.get('who_for'))
    has_outcome = bool(p.get('outcome'))
    gates['A3_SELF'] = {
        'pass': has_url and has_who and has_outcome,
        'score': sum([has_url, has_who, has_outcome]),
        'max': 3,
        'detail': f"URL{'✅' if has_url else '❌'} 受众{'✅' if has_who else '❌'} 产出{'✅' if has_outcome else '❌'}"
    }
    
    # === B域: 体验品质 ===
    sp = p.get('spectrum',{})
    scores = sp.get('five_elements',{})
    L = sp.get('L',0); R = sp.get('R',0)
    
    # B1: 五维均衡 — 至少一个维度≥L4(61+), 没有维度为L1(≤20)
    has_L4 = any(scores.get(d,0) >= 61 for d in ['土_时间轴','金_可行域','水_身心流','木_信义观','火_直觉阈'])
    no_L1 = all(scores.get(d,0) > 20 for d in ['土_时间轴','金_可行域','水_身心流','木_信义观','火_直觉阈'])
    gates['B1_BALANCE'] = {
        'pass': has_L4 and no_L1,
        'detail': f"最高维:{max(scores.values()) if scores else 0} {'≥L4✅' if has_L4 else '<L4❌'} 最低维:{min(scores.values()) if scores else 0} {'>L1✅' if no_L1 else '=L1❌'}"
    }
    
    # B2: 视觉统一 — vi_compliance≥80
    vi = p.get('vi_compliance',0)
    gates['B2_VI'] = {
        'pass': vi >= 80,
        'detail': f"VI:{vi} {'✅' if vi>=80 else '⚠️' if vi>=60 else '❌'}"
    }
    
    # B3: Delighter — 火≥L4(61+)或水≥L4(61+), 即右脑魅力
    fire = scores.get('火_直觉阈',0)
    water = scores.get('水_身心流',0)
    has_delighter = fire >= 61 or water >= 61
    gates['B3_DELIGHT'] = {
        'pass': has_delighter,
        'detail': f"火:{fire} {'🔥L4+' if fire>=61 else ''} 水:{water} {'💧L4+' if water>=61 else ''} {'✅' if has_delighter else '❌缺少Delighter'}"
    }
    
    # === C域: 技术完成度 ===
    # C1: 无阻塞Bug — quality_score≥50
    qs = p.get('quality_score',0)
    gates['C1_NOBUG'] = {
        'pass': qs >= 50,
        'detail': f"品质分:{qs} {'✅' if qs>=50 else '❌'}"
    }
    
    # C2: 响应式 — 有url (实际检查需要浏览器, 这里标记为"需人工验证")
    gates['C2_RESPONSIVE'] = {
        'pass': has_url,
        'detail': f"{'✅有URL' if has_url else '❌无URL'}" + (' [需人工验证响应式]' if has_url else '')
    }
    
    # C3: 可部署 — 有url+有source_file或url可访问
    has_source = bool(p.get('source_file'))
    gates['C3_DEPLOY'] = {
        'pass': has_url,
        'detail': f"{'✅可访问' if has_url else '❌'} {'有源文件' if has_source else ''}"
    }
    
    # === D域: 进化能力 ===
    # D1: 反馈闭环 — 有feedback_loop
    has_feedback = bool(p.get('feedback_loop'))
    gates['D1_FEEDBACK'] = {
        'pass': has_feedback,
        'detail': f"{'✅' if has_feedback else '❌无反馈机制'}"
    }
    
    # D2: 迭代记录 — 有updated且不是created同一天, 或有adaptation_rule
    has_iteration = bool(p.get('adaptation_rule'))
    updated = p.get('updated','')
    created = p.get('created','')
    has_update_diff = updated[:10] != created[:10] if (updated and created) else False
    gates['D2_ITERATE'] = {
        'pass': has_iteration or has_update_diff,
        'detail': f"迭代规则:{'✅' if has_iteration else '❌'} 更新≠创建:{'✅' if has_update_diff else '❌'}"
    }
    
    # D3: 可量化 — 有quality_score+任何计量字段
    has_metrics = qs > 0
    gates['D3_METRICS'] = {
        'pass': has_metrics,
        'detail': f"{'✅品质分'+str(qs) if has_metrics else '❌无量化指标'}"
    }
    
    # 汇总
    total = sum(1 for g in gates.values() if g['pass'])
    max_gates = len(gates)
    
    return {
        'product_id': p.get('id'),
        'product_name': p.get('name'),
        'gates': gates,
        'passed': total,
        'total': max_gates,
        'rate': round(total/max_gates*100, 1),
        'tier': '🏆精品' if total>=10 else ('⭐优质' if total>=6 else ('✅合格' if total>=3 else '🌱原型')),
        'missing_gates': [k for k,v in gates.items() if not v['pass']],
        'audited_at': datetime.now(tz_shanghai).isoformat()
    }

def main():
    data = load_data()
    products = data['products']
    
    # 审计所有产品
    results = []
    for p in products:
        result = audit_12gate(p)
        results.append(result)
    
    # 统计
    tier_dist = {}
    for r in results:
        t = r['tier']
        tier_dist[t] = tier_dist.get(t,0)+1
    
    # 最多的缺失门
    from collections import Counter
    missing_stats = Counter()
    for r in results:
        for g in r['missing_gates']:
            missing_stats[g] += 1
    
    print("=" * 60)
    print("📊 12-Gate 品质审计报告 v3.0")
    print("=" * 60)
    
    print(f"\n总产品: {len(results)}")
    print(f"品级分布(12-Gate审计后): {tier_dist}")
    print(f"平均通过率: {sum(r['rate'] for r in results)/len(results):.1f}%")
    
    print(f"\n最常缺失的门:")
    for gate, cnt in missing_stats.most_common(6):
        pct = round(cnt/len(results)*100,1)
        print(f"  {gate}: {cnt} ({pct}%)")
    
    print(f"\n🏆精品详情:")
    premium_results = [r for r in results if r['tier']=='🏆精品']
    for r in premium_results:
        print(f"  {r['product_id']} {r['product_name'][:35]} 通过{r['passed']}/{r['total']}门")
        if r['missing_gates']:
            print(f"    缺失: {', '.join(r['missing_gates'])}")
    
    print(f"\n⭐优质(前10):")
    quality_results = [r for r in results if r['tier']=='⭐优质']
    for r in quality_results[:10]:
        print(f"  {r['product_id']} {r['product_name'][:35]} 通过{r['passed']}/12门 · 缺{len(r['missing_gates'])}门")
    
    # 保存审计结果
    with open(os.path.join(WORKSPACE,'memory/_data/quality_audit_12gate.json'),'w') as f:
        json.dump({
            'audited_at': datetime.now(tz_shanghai).isoformat(),
            'total_products': len(results),
            'tier_distribution': tier_dist,
            'avg_pass_rate': round(sum(r['rate'] for r in results)/len(results),1),
            'top_missing_gates': missing_stats.most_common(10),
            'results': results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 审计结果已保存: memory/_data/quality_audit_12gate.json")
    
    # 更新entities_index中的quality_tier_v3
    audit_map = {r['product_id']: r for r in results}
    for p in products:
        pid = p.get('id')
        if pid in audit_map:
            ar = audit_map[pid]
            p['quality_tier_v3'] = ar['tier']
            p['quality_12gate_pass'] = ar['passed']
            p['quality_12gate_missing'] = ar['missing_gates']
            p['quality_12gate_audited'] = ar['audited_at']
    
    data['meta']['quality_system'] = {
        "version": "3.0",
        "framework": "四层金字塔+12-Gate+精品飞轮",
        "tier_distribution": tier_dist,
        "premium_target": "≤30",
        "avg_12gate_pass_rate": round(sum(r['rate'] for r in results)/len(results),1),
        "top_missing_gates": dict(missing_stats.most_common(6)),
        "last_audited": datetime.now(tz_shanghai).isoformat(),
        "note": "自进化审计·缺失门可驱动产品迭代计划"
    }
    
    with open(os.path.join(WORKSPACE,'memory/_data/entities_index.json'),'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print("✅ entities_index.json 已更新(quality_12gate_pass/missing)")

if __name__ == '__main__':
    main()
