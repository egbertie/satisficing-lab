#!/usr/bin/env python3
"""
SRI 化学调控引擎 v1.0
======================
不是增加更多反应链。是给现有60条链加上负反馈调控。
- 自适应烈度: 热度过高→自动降速
- 自清理: 一次性产物过期→自动移除
- 自限: 链不活跃持续N天→自动休眠
- 自优: 只保留高ROI链·低效链降权
- 控制论闭环: 设定点·传感器·执行器
"""

import json, os
from datetime import datetime, timezone

WORKSPACE = os.environ.get('SRI_WORKSPACE', os.path.expanduser('~/.openclaw/workspace'))
DATA_FILE = os.path.join(WORKSPACE, 'memory/_data/entities_index.json')


def run_chemical_governor(dry_run=False):
    """化学调控器: 控制反应烈度·清理熵增·保持精益"""
    now = datetime.now(timezone.utc)
    
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    meta = data.get('meta', {})
    actions = {'pruned': 0, 'damped': 0, 'dormant': 0, 'cleaned': 0}
    
    # ============================================
    # 1. 自限: 热度过高→全链降速
    # ============================================
    heat = meta.get('heating', {}).get('total_heat', 0)
    
    # 设定点: 理想烈度控制在 200-500 之间
    if heat > 800:
        speed_multiplier = 0.3  # 高温→大幅降速
        state = 'critical'
    elif heat > 500:
        speed_multiplier = 0.6  # 中高温→适度降速
        state = 'braking'
    elif heat > 200:
        speed_multiplier = 1.0  # 理想区→保持
        state = 'optimal'
    else:
        speed_multiplier = 1.2  # 低温→适度提温
        state = 'heating'
    
    actions['damped'] = 1 if speed_multiplier < 1 else 0
    
    # ============================================
    # 2. 自清理: 移除一次性产物
    # ============================================
    one_shot_keys = [
        'dream_layers', 'dream_recent_2weeks', 'dev_batches',
        'batch_review_r1', 'batch_review_r3', 'batch_review_r4',
        'deduplicated', 'final_deduplication_pass', 'quality_gate_batch4',
        'snowball_completed_at', 'scan_notes', 'deploy_note',
        'metadata_layer', 'product_value_distribution', 'q_confidence_distribution',
        'q_confidence_note', 'quality_confidence', 'quality_framework',
        'maturity_levels', 'nucleus_count', 'online_count', 'premium_count',
        'doc_count', 'product_total', 'standard',
        'synergy', 'verified_connections', 'total_connections', 'total_entities',
        'strong_connections', 'weak_connections', 'medium_connections',
        'bidirectional_count', 'relation_types_count', 'launchable',
    ]
    
    pruned = 0
    for key in one_shot_keys:
        if key in meta:
            # 检查是否超过7天
            val = meta[key]
            is_old = False
            if isinstance(val, dict):
                for time_field in ['reacted_at', 'at', 'completed_at', 'timestamp', 'created', 'updated']:
                    if time_field in val:
                        try:
                            dt = datetime.fromisoformat(str(val[time_field])[:19])
                            if (now - dt).days > 7:
                                is_old = True
                        except:
                            pass
            
            if is_old or not isinstance(val, dict):
                del meta[key]
                pruned += 1
    
    actions['pruned'] = pruned
    
    # ============================================
    # 3. 自休眠: 不活跃链→标记休眠·降低执行频率
    # ============================================
    chem = meta.get('chemistry', {})
    chem_results = chem.get('results', {})
    
    dormant_log = []
    for chain_id, result in chem_results.items():
        if isinstance(result, dict) and result.get('effect', 0) == 0:
            # 检查是否连续多个周期无产出
            if chain_id not in meta.get('_chain_dormancy', {}):
                if '_chain_dormancy' not in meta:
                    meta['_chain_dormancy'] = {}
                meta['_chain_dormancy'][chain_id] = 0
            
            meta['_chain_dormancy'][chain_id] = meta['_chain_dormancy'].get(chain_id, 0) + 1
            
            # 连续5个周期无产出→休眠
            if meta['_chain_dormancy'][chain_id] >= 5:
                dormant_log.append(chain_id)
        else:
            # 有功→重置计数
            if '_chain_dormancy' in meta and chain_id in meta['_chain_dormancy']:
                meta['_chain_dormancy'][chain_id] = 0
    
    actions['dormant'] = len(dormant_log)
    
    # ============================================
    # 4. 自优: 只保留高价值meta键
    # ============================================
    essential_keys = {
        'flywheel', 'change_log', 'product_audit', 'consistency_check',
        'lifecycle_management', 'portfolio_rationalization', 'nourishment',
        'quality_gate', 'standards_iteration', 'orchestration_health',
        'circuit_breakers', 'chemistry', 'auto_heal', 'heating',
        # 实时追踪的化学产物
        'activation', 'catalysts', 'energy', 'polymerization', 'isomers',
        'parallel', 'ph', 'temperature', 'pressure', 'dosage',
        'avatar_activation', 'avatar_decay', 'info_synthesis',
        'isotopes', 'metabolism', 'osmosis', 'reversible',
        'enzyme', 'dissipative', 'symmetry_breaking',
        'stage_nourish_chem', 'stage_gate_chem', 'stage_heal_chem',
        'stage_audit_chem', 'stage_report_chem', 'global_cross',
        'fission', 'combustion', 'explosion', 'precipitation',
        'sublimation', 'termination', 'recrystallization',
    }
    
    cleaned = 0
    chem_prod_keys = [k for k in meta 
                     if k not in essential_keys 
                     and k not in ['version', '_chain_dormancy']
                     and isinstance(meta[k], dict)
                     and any(t in str(meta[k]).lower()[:50] for t in ['reacted_at', 'principle'])]
    
    for key in chem_prod_keys:
        if key not in essential_keys:
            del meta[key]
            cleaned += 1
    
    actions['cleaned'] = cleaned
    
    # ============================================
    # 5. 控制论闭环: 设定点·感知·执行·反馈
    # ============================================
    meta['chemical_governor'] = {
        'executed_at': now.isoformat(),
        'state': state,
        'setpoint': '200-500 heat',
        'current_heat': round(heat, 1),
        'speed_multiplier': speed_multiplier,
        'actions': actions,
        'active_chains': sum(1 for r in chem_results.values() if r.get('effect', 0) > 0),
        'dormant_chains': len(dormant_log),
        'meta_keys_before': len(meta),
        'principle': '不追求更多链·追求精确调控·精益化学·控制论闭环'
    }
    
    if not dry_run:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    return meta['chemical_governor']


def print_report(report):
    print("=" * 60)
    print("🧬 SRI 化学调控报告")
    print("=" * 60)
    print("时间:", report['executed_at'][:19])
    print("状态:", report['state'])
    print(f"热力: {report['current_heat']} → 设定点: {report['setpoint']}")
    print(f"速率: {report['speed_multiplier']}x")
    print(f"\n调控动作:")
    a = report['actions']
    print(f"  自限降速: {'✅' if a.get('damped') else '—'}")
    print(f"  自清理: {a.get('pruned', 0)}个过期meta键")
    print(f"  自休眠: {a.get('dormant', 0)}条链进入休眠")
    print(f"  自优化: {a.get('cleaned', 0)}个冗余键移除")
    print(f"\n精益度: {report['active_chains']}活跃/{report['active_chains']+report['dormant_chains']}总链")
    print(f"meta键: 清理后{report['meta_keys_before']}个")


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--dry-run', action='store_true')
    p.add_argument('--save', action='store_true')
    args = p.parse_args()
    
    report = run_chemical_governor(dry_run=not args.save)
    print_report(report)
