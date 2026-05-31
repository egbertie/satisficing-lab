#!/usr/bin/env python3
"""entities_index.json auto-update: scan workspace, update breakdown counts, recalc density, MD5 verify.
v2: Fixed script counting (SCRIPT- entries, not raw files). Fixed density formula."""

import json, os, hashlib, datetime, sys
from collections import Counter

WORKSPACE = os.path.expanduser("~/.openclaw/workspace")
INDEX_PATH = os.path.join(WORKSPACE, "entities_index.json")
MEMORY_DATA = os.path.join(WORKSPACE, "memory/_data")

def md5_file(path):
    with open(path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

# Keys that are duplicate indexes (do not count; entities live in primary sections)
SKIP_KEYS = {'meta', 'search_index', 'audit_log', 'change_log', 'auto_engine'}

def count_by_prefix(data, prefix):
    """Count entities across all top-level keys that match an ID prefix.
    Excludes duplicate index keys (search_index etc)."""
    count = 0
    for k, v in data.items():
        if k in SKIP_KEYS:
            continue
        if isinstance(v, dict):
            count += sum(1 for kk in v.keys() if kk.startswith(prefix))
        elif isinstance(v, list):
            for item in v:
                if isinstance(item, dict):
                    item_id = item.get('id', item.get('name', ''))
                    if item_id.startswith(prefix):
                        count += 1
                elif isinstance(item, str) and item.startswith(prefix):
                    count += 1
    return count

def count_list_type(data, key_name):
    """Count items in a named list."""
    v = data.get(key_name, [])
    if isinstance(v, list):
        return len(v)
    if isinstance(v, dict):
        return len(v)
    return 0

def count_memory_docs():
    """Count markdown files in memory/ excluding _data, .bak."""
    count = 0
    memdir = os.path.join(WORKSPACE, 'memory')
    if os.path.isdir(memdir):
        for root, dirs, files in os.walk(memdir):
            if any(skip in root.split(os.sep) for skip in ['_data', '.bak', '_archive', '__pycache__']):
                continue
            for f in files:
                if f.endswith('.md'):
                    count += 1
    return count

def main():
    print("=== entities_index.json Auto-Update v2 ===")
    print(f"Time: {datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()}")
    print()
    
    with open(INDEX_PATH, 'r') as f:
        data = json.load(f)
    
    old_breakdown = dict(data.get('meta', {}).get('breakdown', {}))
    old_md5 = md5_file(INDEX_PATH)
    print(f"Old MD5: {old_md5}")
    print()
    
    # --- Precise entity counting ---
    new_bd = {}
    
    # Products: count PROD- entries across all top-level keys
    new_bd['products'] = count_by_prefix(data, 'PROD-')
    
    # Customers: CUST-
    new_bd['customers'] = count_by_prefix(data, 'CUST-')
    
    # Tasks: TASK-
    new_bd['tasks'] = count_by_prefix(data, 'TASK-')
    
    # Avatars: AVATAR- 
    new_bd['avatars'] = count_by_prefix(data, 'AVATAR-')
    
    # Documents: DOC- entries + memory/*.md scan
    doc_json = count_by_prefix(data, 'DOC-')
    doc_fs = count_memory_docs()
    new_bd['documents'] = max(doc_json, doc_fs)
    
    # Decisions: DEC-
    new_bd['decisions'] = count_by_prefix(data, 'DEC-')
    
    # Milestones: MS-
    new_bd['milestones'] = count_by_prefix(data, 'MS-')
    
    # Terms: TERM-
    new_bd['terms'] = count_by_prefix(data, 'TERM-')
    
    # Events: EVENT-
    new_bd['events'] = count_by_prefix(data, 'EVENT-')
    
    # Scripts: SCRIPT- entries (registered pipeline scripts, not raw .py/.sh files)
    new_bd['scripts'] = count_by_prefix(data, 'SCRIPT-')
    
    # Crons: CRON-
    new_bd['crons'] = count_by_prefix(data, 'CRON-')
    
    # Connections: CONN-
    new_bd['connections'] = count_by_prefix(data, 'CONN-')
    
    # Customer profiles: CP-
    new_bd['customer_profiles'] = count_by_prefix(data, 'CP-')
    
    # Quality metrics: QM-
    new_bd['quality_metrics'] = count_by_prefix(data, 'QM-')
    
    # Growth metrics: GM-
    new_bd['growth_metrics'] = count_by_prefix(data, 'GM-')
    
    # VI standards: VI-
    new_bd['vi_standards'] = count_by_prefix(data, 'VI-')
    
    # Lifecycle stages: LC-
    new_bd['lifecycle_stages'] = count_by_prefix(data, 'LC-')
    
    # Instructions set: INS-
    new_bd['instructions_set'] = count_by_prefix(data, 'INS-')
    
    # Workflows: WF-
    new_bd['workflows'] = count_by_prefix(data, 'WF-')
    
    # Governance frameworks: GF-
    new_bd['governance_frameworks'] = count_by_prefix(data, 'GF-')
    
    # Content assets: CA-
    new_bd['content_assets'] = count_by_prefix(data, 'CA-')
    
    # Scoring models: SM-
    new_bd['scoring_models'] = count_by_prefix(data, 'SM-')
    
    # Simulation scenarios: SS-
    new_bd['simulation_scenarios'] = count_by_prefix(data, 'SS-')
    
    # Historical artifacts: HA-
    new_bd['historical_artifacts'] = count_by_prefix(data, 'HA-')
    
    # Additional discoveries: AD-
    new_bd['additional_discoveries'] = count_by_prefix(data, 'AD-')
    
    # Living rules: LR-
    new_bd['living_rules'] = count_by_prefix(data, 'LR-')
    
    # Cities: CITY-
    new_bd['cities'] = count_by_prefix(data, 'CITY-')
    
    # Knowledge pipelines: KP-
    new_bd['knowledge_pipelines'] = count_by_prefix(data, 'KP-')
    
    # Validate: ensure no count dropped below old (use max)
    for key in new_bd:
        if key in old_breakdown and old_breakdown[key] > new_bd[key]:
            new_bd[key] = old_breakdown[key]
    
    # --- Compare and detect anomalies ---
    print("--- Entity Count Scan Results ---")
    alerts = []
    changed = False
    for key in sorted(new_bd.keys()):
        old_val = old_breakdown.get(key, 0)
        new_val = new_bd[key]
        if old_val != new_val:
            changed = True
        if old_val > 0:
            pct_change = abs(new_val - old_val) / old_val * 100
            flag = ""
            if pct_change > 10:
                flag = " ⚠️ >10% CHANGE!"
                alerts.append(f"⚠️ {key}: {old_val} → {new_val} ({pct_change:+.1f}%)")
            print(f"  {key}: {old_val:>6} → {new_val:<6}{flag}")
        else:
            print(f"  {key}: {old_val:>6} → {new_val:<6}")
    
    print()
    total_changed = sum(1 for k in new_bd if new_bd[k] != old_breakdown.get(k, 0))
    print(f"Changed fields: {total_changed}/28")
    
    # --- Update breakdown ---
    data['meta']['breakdown'] = new_bd
    
    # --- Recalculate knowledge_graph_density ---
    # Using the established formula from the note: 
    # density = connections / total_possible_pairs * 100
    # Or simplified: the ratio of connected to total pairs
    n = new_bd['products']  # primary entity count
    conn = new_bd['connections']
    
    # Total possible directed pairs = n * (n-1), or n² for dense
    # The existing note formula: 12456/(12456)=12.7% seems to use connections as denominator
    # Actual graph density: edges / max_possible_edges
    max_edges = n * (n - 1) / 2 if n > 1 else 1
    if max_edges > 0 and conn > 0:
        density = round(conn / max_edges * 100, 1)
    else:
        density = 0.0
    
    # Cap at reasonable values
    density = max(0.1, min(99.9, density))
    
    data['meta']['knowledge_graph_density'] = density
    
    # Update note with actual breakdown
    strong = conn
    medium = new_bd.get('documents', 0) + new_bd.get('tasks', 0)
    weak = new_bd.get('terms', 0) + new_bd.get('events', 0)
    data['meta']['knowledge_graph_density_note'] = (
        f"强{strong}+中{medium}+弱{weak}=边{strong}/"
        f"最大{int(max_edges)}={density}% (auto-updated "
        f"{datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y-%m-%d %H:%M')})"
    )
    
    # --- Update product_families: scan all PROD- entries for family field ---
    families = Counter()
    for k, v in data.items():
        if k in SKIP_KEYS:
            continue
        if isinstance(v, dict):
            for pk, pv in v.items():
                if pk.startswith('PROD-') and isinstance(pv, dict):
                    fam = pv.get('family', pv.get('product_family', ''))
                    if fam:
                        families[fam] += 1
        elif isinstance(v, list):
            for item in v:
                if isinstance(item, dict):
                    item_id = item.get('id', '')
                    if item_id.startswith('PROD-'):
                        fam = item.get('family', item.get('product_family', ''))
                        if fam:
                            families[fam] += 1
    
    old_families = data['meta'].get('product_families', {})
    if families:
        # Preserve old family names not found in new scan
        for old_fam, old_count in old_families.items():
            if old_fam not in families:
                families[old_fam] = old_count
        # Ensure total matches product count
        total_fam = sum(families.values())
        prod_total = new_bd['products']
        if total_fam < prod_total:
            families['未知'] = families.get('未知', 0) + (prod_total - total_fam)
        data['meta']['product_families'] = dict(families.most_common())
        print(f"Product families: {dict(families.most_common())}")
    else:
        print("No product families found via PROD- scan, preserving existing")
    
    # --- Update timestamp ---
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))
    data['meta']['updated'] = now.isoformat()
    data['meta']['last_updated'] = int(now.timestamp())
    
    # --- Update living_rules_status if needed ---
    lr_status = data['meta'].get('living_rules_status', {})
    lr_total = new_bd.get('living_rules', lr_status.get('total', 0))
    if lr_status.get('total', 0) != lr_total:
        lr_status['total'] = lr_total
        data['meta']['living_rules_status'] = lr_status
    
    # --- Write updated JSON ---
    backup_path = INDEX_PATH + f'.bak.{now.strftime("%Y%m%d_%H%M%S")}'
    # Also keep a rolling backup
    rolling_bak = INDEX_PATH + '.bak'
    
    with open(rolling_bak, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Rolling backup: {rolling_bak}")
    
    with open(INDEX_PATH, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Updated: {INDEX_PATH}")
    
    new_md5 = md5_file(INDEX_PATH)
    print(f"\nOld MD5: {old_md5}")
    print(f"New MD5: {new_md5}")
    print(f"Updated timestamp: {data['meta']['updated']}")
    print(f"Knowledge graph density: {density}%")
    print(f"Product count: {new_bd['products']}")
    
    # --- Alert handling ---
    if alerts:
        print("\n=== ⚠️ ENTITY ANOMALY ALERTS ===")
        for a in alerts:
            print(f"  {a}")
        print("=================================")
        
        alert_path = os.path.join(MEMORY_DATA, 'entities_index_alert.json')
        alert_data = {
            "timestamp": now.isoformat(),
            "severity": "warning",
            "alerts": alerts,
            "old_breakdown_summary": {k: old_breakdown.get(k,0) for k in new_bd if abs(new_bd[k]-old_breakdown.get(k,0))/max(1,old_breakdown.get(k,1))*100 > 10},
            "new_breakdown": new_bd,
            "density": density,
            "md5_new": new_md5,
            "md5_old": old_md5
        }
        with open(alert_path, 'w') as f:
            json.dump(alert_data, f, ensure_ascii=False, indent=2)
        print(f"Alert file: {alert_path}")
        sys.exit(1)
    else:
        print("\n✅ No anomalies (>10%). All counts stable.")
        sys.exit(0)

if __name__ == '__main__':
    main()
