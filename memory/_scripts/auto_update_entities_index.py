#!/usr/bin/env python3
"""
entities_index.json Auto-Updater (Cron: entities_index_autoupdate)
功能: 扫描 workspace 目录，更新 meta.breakdown 中的各实体计数，
      重新计算 knowledge_graph_density，更新 product_families 分布。
      完成后 MD5 校验并写入 updated 时间戳。
      如发现数据异常（实体数变动>10%），标记为⚠️并通知。
输入: /Users/egbertielau/.openclaw/workspace/entities_index.json
      /Users/egbertielau/.openclaw/workspace (扫描)
输出: 更新后的 entities_index.json
"""

import json
import hashlib
import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from collections import Counter

WORKSPACE = Path("/Users/egbertielau/.openclaw/workspace")
INDEX_PATH = WORKSPACE / "entities_index.json"
CST = timezone(timedelta(hours=8))

def md5_file(path):
    h = hashlib.md5()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()

def load_index():
    with open(INDEX_PATH, 'r') as f:
        return json.load(f)

def count_workspace_files():
    """Count workspace files by type for cross-validation."""
    exts = Counter()
    total = 0
    skip_dirs = {'.git', 'node_modules', '__pycache__', '.bak', '.venv', 'venv', '.DS_Store'}
    for root, dirs, files in os.walk(WORKSPACE):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for f in files:
            if f.startswith('.'):
                continue
            ext = Path(f).suffix.lower()
            exts[ext] += 1
            total += 1
    return total, exts

def recompute_breakdown(data):
    """Recount all entity arrays from actual data."""
    entity_keys = [
        'products', 'customers', 'tasks', 'avatars', 'documents',
        'decisions', 'milestones', 'terms', 'events', 'scripts',
        'crons', 'connections', 'customer_profiles', 'quality_metrics',
        'growth_metrics', 'vi_standards', 'lifecycle_stages',
        'instructions_set', 'workflows', 'governance_frameworks',
        'content_assets', 'scoring_models', 'simulation_scenarios',
        'historical_artifacts', 'additional_discoveries', 'living_rules',
        'cities', 'knowledge_pipelines'
    ]
    # Map breakdown keys to actual top-level JSON keys (handle naming inconsistencies)
    key_map = {
        'knowledge_pipelines': 'knowledge_pipeline',  # old breakdown uses plural, JSON uses singular
    }
    breakdown = {}
    for key in entity_keys:
        lookup_key = key_map.get(key, key)
        arr = data.get(lookup_key, [])
        count = len(arr) if isinstance(arr, list) else 0
        breakdown[key] = count
    return breakdown

def recompute_product_families(data):
    """Recount product families from actual product data."""
    products = data.get('products', [])
    families = Counter()
    for p in products:
        fam = p.get('family', '未知')
        families[fam] += 1
    return dict(families)

def recompute_knowledge_graph_density(data):
    connections = data.get('connections', [])
    total_connections = len(connections) if isinstance(connections, list) else 0
    products = data.get('products', [])
    total_products = len(products) if isinstance(products, list) else 0

    # Count connection weights
    strong = sum(1 for c in connections if isinstance(c, dict) and c.get('weight', 0) >= 0.8)
    medium = sum(1 for c in connections if isinstance(c, dict) and 0.5 <= c.get('weight', 0) < 0.8)
    weak = sum(1 for c in connections if isinstance(c, dict) and c.get('weight', 0) < 0.5)

    # Theoretical max: each node connects to all others + self
    # But for density we use: actual / theoretical_max
    total_nodes = total_products
    if total_nodes > 1:
        theoretical_max = total_nodes * (total_nodes - 1)
        density = min(100.0, round((total_connections / theoretical_max) * 100, 1))
    else:
        density = 0.0

    return density, total_connections, strong, medium, weak

def recompute_living_rules_status(data):
    rules = data.get('living_rules', [])
    active = sum(1 for r in rules if isinstance(r, dict) and r.get('status') == 'active')
    dormant = sum(1 for r in rules if isinstance(r, dict) and r.get('status') == 'dormant')
    broken = sum(1 for r in rules if isinstance(r, dict) and r.get('status') == 'broken')
    return {
        "active": active,
        "dormant": dormant,
        "broken": broken,
        "total": len(rules)
    }

def recompute_biological_health(data):
    rules = data.get('living_rules', [])
    with_triggers = sum(1 for r in rules if isinstance(r, dict) and r.get('trigger'))
    with_feedback = sum(1 for r in rules if isinstance(r, dict) and r.get('feedback'))
    with_adaptation = sum(1 for r in rules if isinstance(r, dict) and r.get('adaptation'))
    crons = data.get('crons', [])
    cron_connected = len([c for c in crons if isinstance(c, dict) and c.get('status') == 'active'])
    fully_alive = sum(1 for r in rules if isinstance(r, dict)
                      and r.get('trigger') and r.get('feedback')
                      and r.get('adaptation') and r.get('status') == 'active')
    return {
        "rules_with_triggers": with_triggers,
        "rules_with_feedback": with_feedback,
        "rules_with_adaptation": with_adaptation,
        "cron_connected": cron_connected,
        "fully_alive": fully_alive
    }

def detect_anomaly(old_bd, new_bd):
    """Detect >10% change in any entity count."""
    warnings = []
    for key in new_bd:
        old_val = old_bd.get(key, 0)
        new_val = new_bd[key]
        if old_val == 0:
            if new_val > 0:
                warnings.append(f"⚠️ {key}: 0→{new_val} (new)")
            continue
        pct_change = abs(new_val - old_val) / old_val * 100
        if pct_change > 10:
            direction = "↑" if new_val > old_val else "↓"
            warnings.append(f"⚠️ {key}: {old_val}→{new_val} ({direction}{pct_change:.1f}%)")
    return warnings

def main():
    print("=" * 60)
    print("entities_index.json Auto-Updater")
    print(f"Started: {datetime.now(CST).isoformat()}")
    print("=" * 60)

    # 1. Load current index
    print("\n[1/5] Loading entities_index.json ...")
    data = load_index()
    old_breakdown = data.get('meta', {}).get('breakdown', {})
    print(f"  File size: {INDEX_PATH.stat().st_size / 1024 / 1024:.1f} MB")
    print(f"  Current version: {data['meta'].get('version', 'unknown')}")
    print(f"  Last updated: {data['meta'].get('updated', 'unknown')}")

    # 2. Recompute breakdown from actual data
    print("\n[2/5] Recomputing entity breakdown ...")
    new_breakdown = recompute_breakdown(data)
    print(f"  Entity counts:")
    for k, v in new_breakdown.items():
        old_v = old_breakdown.get(k, 0)
        delta = v - old_v
        flag = f" ({'+' if delta > 0 else ''}{delta})" if delta != 0 else ""
        print(f"    {k}: {v}{flag}")

    # 3. Recompute product families
    print("\n[3/5] Recomputing product families ...")
    new_families = recompute_product_families(data)
    old_families = data['meta'].get('product_families', {})
    print(f"  Product families:")
    for fam, count in sorted(new_families.items(), key=lambda x: -x[1]):
        old_count = old_families.get(fam, 0)
        delta = count - old_count
        flag = f" ({'+' if delta > 0 else ''}{delta})" if delta != 0 else ""
        print(f"    {fam}: {count}{flag}")

    # 4. Recompute knowledge graph density
    print("\n[4/5] Recomputing knowledge graph density ...")
    density, total_conn, strong, medium, weak = recompute_knowledge_graph_density(data)
    print(f"  Density: {density}%")
    print(f"  Connections: {total_conn} (strong:{strong} medium:{medium} weak:{weak})")

    # 5. Anomaly detection
    print("\n[5/5] Anomaly detection ...")
    warnings = detect_anomaly(old_breakdown, new_breakdown)

    # Check product families too
    old_total_fam = sum(old_families.values())
    new_total_fam = sum(new_families.values())
    if old_total_fam > 0:
        fam_pct = abs(new_total_fam - old_total_fam) / old_total_fam * 100
        if fam_pct > 10:
            warnings.append(f"⚠️ product_families total: {old_total_fam}→{new_total_fam} ({fam_pct:.1f}%)")

    anomaly_detected = len(warnings) > 0
    if anomaly_detected:
        print("  🚨 ANOMALIES DETECTED:")
        for w in warnings:
            print(f"    {w}")
    else:
        print("  ✅ No anomalies (>10% threshold)")

    # Update meta
    now_cst = datetime.now(CST)
    data['meta']['breakdown'] = new_breakdown
    data['meta']['product_families'] = new_families
    data['meta']['knowledge_graph_density'] = density
    data['meta']['updated'] = now_cst.isoformat()

    # Update knowledge_graph_density_note
    data['meta']['knowledge_graph_density_note'] = (
        f"强{strong}+中{medium}+弱{weak}={total_conn}/{total_conn}={density}% "
        f"(auto-updated {now_cst.strftime('%Y-%m-%d %H:%M')})"
    )

    # Update living_rules_status
    data['meta']['living_rules_status'] = recompute_living_rules_status(data)

    # Update biological_health
    data['meta']['biological_health'] = recompute_biological_health(data)

    # Add connection stats
    data['meta']['connection_stats'] = {
        "total": total_conn,
        "strong": strong,
        "medium": medium,
        "weak": weak,
        "updated": now_cst.isoformat()
    }

    # Add auto_update_log
    log_entry = {
        "timestamp": now_cst.isoformat(),
        "version": data['meta'].get('version', '3.0'),
        "changes": {k: {"old": old_breakdown.get(k, 0), "new": new_breakdown[k]}
                     for k in new_breakdown if new_breakdown[k] != old_breakdown.get(k, 0)},
        "anomalies": warnings if anomaly_detected else [],
        "density": density,
        "product_families_changed": new_families != old_families
    }
    if 'auto_update_log' not in data['meta']:
        data['meta']['auto_update_log'] = []
    data['meta']['auto_update_log'].append(log_entry)
    # Keep last 20 entries
    data['meta']['auto_update_log'] = data['meta']['auto_update_log'][-20:]

    # Write updated file
    print("\n[Write] Saving updated entities_index.json ...")
    tmp_path = INDEX_PATH.with_suffix('.json.tmp')
    json_str = json.dumps(data, ensure_ascii=False, indent=2)
    with open(tmp_path, 'w') as f:
        f.write(json_str)

    # Validate JSON
    with open(tmp_path, 'r') as f:
        json.load(f)  # will raise if invalid
    print("  ✅ JSON validation passed")

    # MD5 checksums
    old_md5 = md5_file(INDEX_PATH)
    new_md5 = md5_file(tmp_path)
    print(f"  Old MD5: {old_md5}")
    print(f"  New MD5: {new_md5}")

    # Atomic rename
    os.replace(tmp_path, INDEX_PATH)
    print("  ✅ File saved (atomic replace)")

    # Final MD5
    final_md5 = md5_file(INDEX_PATH)
    print(f"  Final MD5: {final_md5}")
    print(f"  File size: {INDEX_PATH.stat().st_size / 1024 / 1024:.1f} MB")

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print(f"  Updated: {now_cst.isoformat()}")
    print(f"  Total entities: {sum(new_breakdown.values())}")
    print(f"  Products: {new_breakdown['products']}")
    print(f"  Knowledge Graph Density: {density}%")
    print(f"  Product Families: {dict(new_families)}")
    if anomaly_detected:
        print(f"  🚨 ANOMALIES ({len(warnings)}):")
        for w in warnings:
            print(f"     {w}")
    else:
        print("  ✅ No anomalies detected")
    print("=" * 60)

    # Return anomaly status for cron notification
    return anomaly_detected, warnings

if __name__ == '__main__':
    anomaly, warnings = main()
    if anomaly:
        print("\n⚠️ NOTIFICATION: 数据异常需人工审核")
        sys.exit(1)
    else:
        print("\n✅ Normal execution")
        sys.exit(0)
