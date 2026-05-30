#!/usr/bin/env python3
"""
SRI 知识资产飞轮引擎 v1.0
================================
物理执行层: 读 entities_index.json → 运行五层循环 → 写回
被 Cron 定时调用，每次调用产生一轮微循环事件。

架构原则 (Evolutionary Architecture):
1. 每个方法有独立的 fitness function — 可独立验证
2. 实体之间通过 events 松耦合 — 不直接调用
3. 每次写入追加 change_log — 事件溯源
4. 不依赖任何外部服务 — 纯 JSON 读写
5. Phase 0→Phase 3 只加功能不强重构 — 绞杀者模式

终局容量设计:
- Phase 0 (now): 5客户·单JSON·单进程 — 本脚本直接读写
- Phase 1 (<200客户): +分片JSON·多进程 — 脚本不变，数据层变
- Phase 2 (<1000客户): +Bitable后端·API层 — 脚本改为 API 调用
- Phase 3 (<10000客户): +独立后端 — 脚本演化为 orchestrator
"""

import json
import os
import sys
import time
from datetime import datetime, timezone, timedelta

# ============================================================
# 常量: 可随规模变化调整，不需要改代码
# ============================================================
WORKSPACE = os.environ.get('SRI_WORKSPACE', os.path.expanduser('~/.openclaw/workspace'))
DATA_FILE = os.path.join(WORKSPACE, 'memory/_data/entities_index.json')
# Phase 0: 扫描 site/ 和 memory/ (过渡方案)
# Phase 1: 创建 site/products/ memory/knowledge/ 后只扫这两个目录
SCAN_PATHS = ['site', 'memory']
STALE_THRESHOLD_DAYS = 7
CRITICAL_THRESHOLD_DAYS = 14
MAX_CHANGE_LOG = 5000

# 实体类型→文件扩展名映射
ENTITY_FROM_PATH = {
    'site': 'products',   # site/ HTML → 产品
    'memory': 'documents', # memory/ MD → 文档（知识资产）
}

# 扫描时跳过的目录名
SKIP_DIRS = {'.bak', '.git', '.openclaw', '.clawhub', 'archive', 'node_modules', '对话'}
# 扫描时跳过的文件名模式
SKIP_FILES = {'dashboard', 'admin-windows', 'product-catalog', 'index', 'about', 'gate'}

# 族→路径关键词映射
FAMILY_FROM_PATH = {
    '镜': ['mirror', 'awareness', '觉察', '识别', '温度计', '剧场', '危机', '骑士', '模拟', 'FIN', '匹配'],
    '衡': ['quantify', '衡量', '诊断', '雷达', '分割', '报告', '量表', '检查', '成熟度', '段位', '竞品', '化学', '话术'],
    '契': ['agreement', '约定', '协议', '合伙', '案例', '根脉', '符号', '入职', '族谱', '星光'],
    '觉': ['forge', '淬炼', '驾驶舱', '飞轮', '退出', '向导', '引导', '密码', '认证', '注册', '替身', '分享'],
    '人': ['people', '章·五路', '双翼', '契晋', '轨迹', '蓝军', '围棋', '客户', '决策', '静水', '冬眠'],
    '道': ['about', '关于', '哲学', '咒语', '信念', '道'],
    '章': ['chapter', '传承', '案例', '星月', '宝藏', '失败', '54天', '生命', '新人', '品牌', '量化', '知识', '日志', '归档']
}


def load_data(path=None):
    """加载 entities_index.json"""
    path = path or DATA_FILE
    if not os.path.exists(path):
        return {'entities': {}, 'meta': {'flywheel': {}, 'change_log': []}}
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_data(data, path=None):
    """保存 entities_index.json + 备份"""
    path = path or DATA_FILE
    # 原子写入: 先写临时文件，再替换
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


def init_flywheel_meta(data):
    """确保 meta 中有 flywheel 字段"""
    if 'meta' not in data:
        data['meta'] = {}
    if 'flywheel' not in data['meta']:
        data['meta']['flywheel'] = {
            'version': '1.0',
            'last_run': None,
            'total_runs': 0,
            'cycles': {
                'ingestion': {'status': 'idle', 'last_run': None, 'events_this_run': 0},
                'digestion': {'status': 'idle', 'last_run': None, 'events_this_run': 0},
                'product_flow': {'status': 'idle', 'last_run': None, 'events_this_run': 0},
                'llm_perception': {'status': 'idle', 'last_run': None, 'events_this_run': 0},
                'health_audit': {'status': 'idle', 'last_run': None, 'events_this_run': 0}
            },
            'alerts': [],
            'capacity': {
                'phase': 0,
                'max_clients_arch_supports': 50,
                'json_size_mb': round(os.path.getsize(DATA_FILE) / 1048576, 1) if os.path.exists(DATA_FILE) else 0,
                'json_load_threshold_ms': 5000,
                'rating': 'green'
            }
        }
    if 'change_log' not in data['meta']:
        data['meta']['change_log'] = []
    return data


def add_change_log(data, entity_type, entity_id, field, old_value, new_value, trigger, source=None, cycle=None):
    """追加变更日志 — 事件溯源核心"""
    entry = {
        'id': 'CHG-{:04d}'.format(len(data['meta']['change_log']) + 1),
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'entity_type': entity_type,
        'entity_id': entity_id,
        'field': field,
        'old_value': str(old_value)[:200] if old_value is not None else None,
        'new_value': str(new_value)[:200] if new_value is not None else None,
        'trigger': trigger,
        'source': source,
        'cycle': cycle
    }
    data['meta']['change_log'].append(entry)
    # 循环覆盖
    if len(data['meta']['change_log']) > MAX_CHANGE_LOG:
        data['meta']['change_log'] = data['meta']['change_log'][-MAX_CHANGE_LOG:]


# ============================================================
# 循环①: 知识流入 — 扫描文件→发现新实体
# ============================================================
def cycle_scan_new_files(data):
    """扫描监控目录，发现新文件或修改文件→自动注册"""
    events = []
    now = datetime.now(timezone.utc)
    
    # 确保实体列表存在
    for ent in ['products', 'documents', 'tasks']:
        if ent not in data:
            data[ent] = []
    
    known_files = {}
    for ent_type in ['products', 'documents']:
        for item in data.get(ent_type, []):
            if isinstance(item, dict) and 'source_file' in item:
                known_files[item['source_file']] = {'entity': ent_type, 'id': item.get('id', '?')}
    
    for scan_path_rel in SCAN_PATHS:
        scan_path = os.path.join(WORKSPACE, scan_path_rel)
        if not os.path.exists(scan_path):
            continue
        
        for root, dirs, files in os.walk(scan_path):
            # 跳过隐藏目录和已知非产品目录
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in SKIP_DIRS]
            
            for fname in files:
                # 只扫描 HTML 和 MD (但 site/ 只扫 html, memory/ 只扫 md)
                is_html = fname.endswith('.html')
                is_md = fname.endswith('.md')
                if scan_path_rel == 'site' and not is_html:
                    continue
                if scan_path_rel == 'memory' and not is_md:
                    continue
                if not is_html and not is_md:
                    continue
                
                # 跳过管理工具
                fname_lower = fname.lower()
                skip = False
                for sf in SKIP_FILES:
                    if sf in fname_lower:
                        skip = True
                        break
                if skip:
                    continue
                
                fpath = os.path.join(root, fname)
                rel_path = os.path.relpath(fpath, WORKSPACE)
                mtime = datetime.fromtimestamp(os.path.getmtime(fpath), tz=timezone.utc)
                
                # 已注册 → 检查是否有更新
                if rel_path in known_files:
                    ent = known_files[rel_path]
                    existing = None
                    ent_list = data.get(ent['entity'], [])
                    for item in ent_list:
                        if isinstance(item, dict) and item.get('id') == ent['id']:
                            existing = item
                            break
                    if existing:
                        last_scan = existing.get('last_scan_time')
                        if last_scan:
                            try:
                                last_dt = datetime.fromisoformat(last_scan)
                                if mtime > last_dt:
                                    existing['last_scan_time'] = now.isoformat()
                                    existing['file_updated'] = True
                                    events.append({
                                        'type': 'file_updated',
                                        'file': rel_path,
                                        'entity': ent['id'],
                                        'timestamp': now.isoformat()
                                    })
                            except ValueError:
                                pass
                    continue
                
                # 新文件 → 创建实体
                ent_type = ENTITY_FROM_PATH.get(scan_path_rel, 'documents')
                if ent_type not in data:
                    data[ent_type] = []
                
                # 自动检测族
                family = '未知'
                fname_lower = fname.lower()
                for fam, keywords in FAMILY_FROM_PATH.items():
                    for kw in keywords:
                        if kw.lower() in fname_lower:
                            family = fam
                            break
                    if family != '未知':
                        break
                
                # 分配ID
                existing_ids = [item.get('id', '') for item in data[ent_type] if isinstance(item, dict)]
                nums = []
                for eid in existing_ids:
                    import re
                    m = re.match(r'^([A-Z]+)-0*(\d+)$', str(eid))
                    if m:
                        nums.append(int(m.group(2)))
                next_num = max(nums) + 1 if nums else 1
                
                prefix_map = {'products': 'PROD', 'documents': 'DOC', 'tasks': 'TASK'}
                prefix = prefix_map.get(ent_type, 'ENT')
                new_id = '{}-{:03d}'.format(prefix, next_num)
                
                new_entity = {
                    'id': new_id,
                    'name': fname.replace('.html', '').replace('.md', ''),
                    'family': family,
                    'status': '待审核',
                    'source_file': rel_path,
                    'detected_at': now.isoformat(),
                    'last_scan_time': now.isoformat(),
                    'auto_registered': True,
                    'quality_score': 0,
                    'llm_rating': None,
                    'lifecycle_stage': 'LC-001'
                }
                data[ent_type].append(new_entity)
                known_files[rel_path] = {'entity': ent_type, 'id': new_id}
                
                add_change_log(data, ent_type, new_id, 'entity_created', None,
                             'auto_registered_from:{}'.format(rel_path),
                             'flywheel_scan', 'cycle_1')
                
                events.append({
                    'type': 'new_entity',
                    'entity_type': ent_type,
                    'entity_id': new_id,
                    'name': fname,
                    'family': family,
                    'timestamp': now.isoformat()
                })
    
    return events


# ============================================================
# 循环②: 知识消化 — 检测实体状态变化·标记异常
# ============================================================
def cycle_detect_stale_entities(data):
    """检测腐烂实体 — 超过阈值天数未更新"""
    events = []
    now = datetime.now(timezone.utc)
    alerts = []
    
    for ent_type in ['products', 'documents', 'tasks']:
        for item in data.get(ent_type, []):
            if not isinstance(item, dict):
                continue
            
            # 检查 last_modified 或 last_scan_time
            last_mod = item.get('last_modified') or item.get('last_scan_time')
            if not last_mod:
                # 从未被扫描过 → 标记
                old_health = item.get('health', 'unknown')
                item['health'] = 'stale'
                item['days_since_update'] = 'unknown'
                if old_health != 'stale':
                    add_change_log(data, ent_type, item.get('id', '?'), 'health',
                                 old_health, 'stale', 'freshness_check', 'cycle_2')
                continue
            
            try:
                last_dt = datetime.fromisoformat(last_mod)
                days = (now - last_dt).days
            except (ValueError, TypeError):
                continue
            
            old_health = item.get('health', 'healthy')
            if days > CRITICAL_THRESHOLD_DAYS:
                item['health'] = 'critical'
                alerts.append({'entity': item.get('id'), 'name': item.get('name', '?'),
                               'days': days, 'severity': 'critical'})
            elif days > STALE_THRESHOLD_DAYS:
                item['health'] = 'degraded'
                alerts.append({'entity': item.get('id'), 'name': item.get('name', '?'),
                               'days': days, 'severity': 'warning'})
            
            if old_health != item.get('health'):
                add_change_log(data, ent_type, item.get('id', '?'), 'health',
                             old_health, item.get('health'), 'freshness_check', 'cycle_2')
    
    if alerts:
        events.append({
            'type': 'stale_entities',
            'count': len(alerts),
            'alerts': alerts,
            'timestamp': now.isoformat()
        })
    
    return events


# ============================================================
# 循环③: 产品流重排 — 评分变化 → 自动重排推荐
# ============================================================
def cycle_rerank_flows(data):
    """基于评分变化自动重排产品流推荐"""
    events = []
    now = datetime.now(timezone.utc)
    
    products = data.get('products', [])
    if not products:
        return events
    
    # 统计评分变化
    products_with_llm = [p for p in products if isinstance(p, dict) and p.get('llm_rating')]
    if not products_with_llm:
        events.append({
            'type': 'flow_rerank',
            'status': 'skipped',
            'reason': 'no_llm_rated_products',
            'timestamp': now.isoformat()
        })
        return events
    
    # 按 LLM 评分排序
    sorted_products = sorted(products_with_llm, key=lambda p: p.get('llm_rating', 0), reverse=True)
    
    # 计算评分分布
    scores = [p.get('llm_rating', 0) for p in sorted_products]
    avg_score = round(sum(scores) / len(scores), 1) if scores else 0
    
    # 更新 meta.llm_stats
    if 'llm_stats' not in data['meta']:
        data['meta']['llm_stats'] = {}
    
    old_avg = data['meta']['llm_stats'].get('llm_avg', 0)
    data['meta']['llm_stats']['llm_avg'] = avg_score
    data['meta']['llm_stats']['products_evaluated'] = len(sorted_products)
    data['meta']['llm_stats']['last_rerank'] = now.isoformat()
    
    if old_avg != avg_score:
        add_change_log(data, 'meta', 'llm_stats', 'llm_avg', old_avg, avg_score,
                      'flow_rerank', 'cycle_3')
    
    events.append({
        'type': 'flow_rerank',
        'products_evaluated': len(sorted_products),
        'avg_llm_score': avg_score,
        'top_product': sorted_products[0].get('name') if sorted_products else None,
        'top_score': sorted_products[0].get('llm_rating') if sorted_products else None,
        'bottom_product': sorted_products[-1].get('name') if sorted_products else None,
        'bottom_score': sorted_products[-1].get('llm_rating') if sorted_products else None,
        'timestamp': now.isoformat()
    })
    
    return events


# ============================================================
# 循环④: LLM 评分缺口 — 检测未评产品
# ============================================================
def cycle_detect_llm_gaps(data):
    """检测需要 LLM 评分的产品缺口"""
    events = []
    now = datetime.now(timezone.utc)
    
    products = data.get('products', [])
    if not products:
        return events
    
    # 精品+线上产品中，还没有 LLM 评分的
    needs_eval = [p for p in products
                  if isinstance(p, dict)
                  and p.get('status') in ('精品', '线上')
                  and not p.get('llm_rating')
                  and p.get('lifecycle_stage') in ('LC-004', 'LC-005')]
    
    # 标记为 needs_evaluation
    for p in needs_eval:
        if p.get('evaluation_status') != 'queued':
            p['evaluation_status'] = 'queued'
            p['evaluation_queued_at'] = now.isoformat()
    
    events.append({
        'type': 'llm_gap_detection',
        'needs_evaluation': len(needs_eval),
        'sample_ids': [p.get('id') for p in needs_eval[:5]],
        'total_products': len(products),
        'evaluated_count': len([p for p in products if isinstance(p, dict) and p.get('llm_rating')]),
        'timestamp': now.isoformat()
    })
    
    return events


# ============================================================
# 循环⑤: 健康自检 — 五层流·Cron状态·一致性
# ============================================================
def cycle_health_audit(data):
    """全面的飞轮健康检查"""
    events = []
    now = datetime.now(timezone.utc)
    alerts = []
    
    # 1. 五层流完整性
    flow_layers = {
        'L1_signals': len(data.get('signals', [])),
        'L2_cognition': len(data.get('cognition_events', [])),
        'L3_actions': len(data.get('action_events', [])),
        'L4_verification': len(data.get('verification_events', [])),
        'L5_learning': len(data.get('learning_events', []))
    }
    
    min_events = min(flow_layers.values())
    if min_events == 0:
        alerts.append({
            'type': 'flow_incomplete',
            'severity': 'warning',
            'detail': '至少一层流事件为0',
            'layers': flow_layers
        })
    
    # 2. 连接一致性检查
    products = data.get('products', [])
    broken_links = 0
    for p in products:
        if isinstance(p, dict):
            url = p.get('url', '')
            if url and '..' in url:
                broken_links += 1
    
    # 3. JSON 大小检查
    json_size_mb = round(os.path.getsize(DATA_FILE) / 1048576, 1) if os.path.exists(DATA_FILE) else 0
    if json_size_mb > 15:
        alerts.append({
            'type': 'json_size_warning',
            'severity': 'warning',
            'size_mb': json_size_mb,
            'detail': 'JSON超过15MB，建议分片'
        })

    # 3.5. 触发自动修复 (低风险操作)
    heal_fixes = 0
    try:
        healer_path = os.path.join(WORKSPACE, 'memory/_scripts/sri_auto_healer.py')
        if os.path.exists(healer_path):
            result = __import__('subprocess').run(
                ['python3', healer_path, '--limit', '30'],
                capture_output=True, text=True, timeout=120, cwd=WORKSPACE)
            import re as _re
            m = _re.search(r'([0-9]+) 个修复', result.stdout)
            heal_fixes = int(m.group(1)) if m else 0
    except Exception:
        pass
    if heal_fixes > 0:
        events.append({
            'type': 'auto_heal',
            'fixes': heal_fixes,
            'timestamp': now.isoformat()
        })
    
    # 4. 更新 meta.flywheel
    fw = data['meta']['flywheel']
    fw['last_health_audit'] = now.isoformat()
    fw['health_audit_report'] = {
        'flow_layers': flow_layers,
        'flow_complete': all(v > 0 for v in flow_layers.values()),
        'broken_links': broken_links,
        'json_size_mb': json_size_mb,
        'alerts': len(alerts),
        'timestamp': now.isoformat()
    }
    fw['alerts'] = alerts
    
    # 5. 实体一致性检查 (从 entities_index meta 读取)
    cc = data.get('meta', {}).get('consistency_check', {})
    cc_issues = cc.get('total_issues', 0)
    if cc_issues > 0:
        alerts.append({
            'type': 'consistency_issues',
            'severity': 'warning',
            'detail': '{} 个一致性异常 (重复·孤儿·缺失·冲突)'.format(cc_issues),
            'by_type': cc.get('by_type', {})
        })
    
    # 6. 产品审计检查
    pa = data.get('meta', {}).get('product_audit', {})
    pa_avg = pa.get('avg_score', 0)
    pa_under60 = pa.get('products_under_60', 0)
    if pa_under60 > 0:
        alerts.append({
            'type': 'low_quality_products',
            'severity': 'info',
            'detail': '{} 个产品审计分<60'.format(pa_under60)
        })
    
    # 7. 更新容量评级
    if json_size_mb < 10:
        fw['capacity']['rating'] = 'green'
    elif json_size_mb < 15:
        fw['capacity']['rating'] = 'yellow'
    else:
        fw['capacity']['rating'] = 'red'
    fw['capacity']['json_size_mb'] = json_size_mb
    
    events.append({
        'type': 'health_audit',
        'flow_layers': flow_layers,
        'flow_complete': all(v > 0 for v in flow_layers.values()),
        'broken_links': broken_links,
        'json_size_mb': json_size_mb,
        'alerts': len(alerts),
        'capacity_rating': fw['capacity']['rating'],
        'consistency_issues': cc_issues,
        'product_audit_avg': pa_avg,
        'product_audit_under60': pa_under60,
        'timestamp': now.isoformat()
    })
    
    return events


# ============================================================
# 主入口: 执行全部循环或指定循环
# ============================================================
def run(cycle=None, dry_run=False):
    """
    执行飞轮循环
    
    Args:
        cycle: None=全部, 'scan'=循环①, 'health'=循环②⑤, 'llm-gap'=循环④, 'report'=生成报告
        dry_run: True=只读不写
    """
    start_time = time.time()
    data = load_data()
    data = init_flywheel_meta(data)
    
    now = datetime.now(timezone.utc)
    all_events = []
    
    # 确定要执行的循环
    cycles_to_run = {
        'scan': [cycle_scan_new_files],
        'health': [cycle_detect_stale_entities, cycle_health_audit],
        'llm-gap': [cycle_detect_llm_gaps],
        'report': [],
        None: [cycle_scan_new_files, cycle_detect_stale_entities,
               cycle_rerank_flows, cycle_detect_llm_gaps, cycle_health_audit]
    }
    
    funcs = cycles_to_run.get(cycle)
    if funcs is None:
        print('Unknown cycle: {}'.format(cycle))
        print('Available: scan, health, llm-gap, report')
        return []
    
    for func in funcs:
        events = func(data)
        all_events.extend(events)
    
    # 更新飞轮状态
    fw = data['meta']['flywheel']
    fw['last_run'] = now.isoformat()
    fw['total_runs'] = fw.get('total_runs', 0) + 1
    
    elapsed_ms = int((time.time() - start_time) * 1000)
    fw['last_run_elapsed_ms'] = elapsed_ms
    
    # 记录本轮事件
    run_entry = {
        'run_id': fw['total_runs'],
        'timestamp': now.isoformat(),
        'cycle': cycle or 'all',
        'events_count': len(all_events),
        'elapsed_ms': elapsed_ms,
        'dry_run': dry_run
    }
    
    if 'recent_runs' not in fw:
        fw['recent_runs'] = []
    fw['recent_runs'].insert(0, run_entry)
    fw['recent_runs'] = fw['recent_runs'][:20]  # 只保留最近20条
    
    if not dry_run:
        save_data(data)
    
    return all_events


def generate_report(data=None):
    """生成飞轮日报"""
    data = data or load_data()
    init_flywheel_meta(data)
    fw = data.get('meta', {}).get('flywheel', {})
    
    lines = []
    lines.append('=' * 50)
    lines.append('SRI 知识资产飞轮 · 每日报告')
    lines.append('=' * 50)
    lines.append('时间: {}'.format(datetime.now(timezone.utc).isoformat()))
    lines.append('')
    
    # 容量状态
    cap = fw.get('capacity', {})
    lines.append('📊 容量状态')
    lines.append('  规模: Phase {} · 评级: {}'.format(cap.get('phase', 0), cap.get('rating', '?')))
    lines.append('  JSON: {}MB · 加载阈值: {}ms'.format(cap.get('json_size_mb', '?'), cap.get('json_load_threshold_ms', '?')))
    lines.append('')
    
    # 循环状态
    lines.append('🔄 五层循环')
    ha = fw.get('health_audit_report', {})
    layers = ha.get('flow_layers', {})
    for layer, count in layers.items():
        icon = '✅' if count > 0 else '⚠️'
        lines.append('  {} {}: {} 事件'.format(icon, layer, count))
    lines.append('')
    
    # 最近运行
    recent = fw.get('recent_runs', [])[:5]
    if recent:
        lines.append('📋 最近运行')
        for r in recent:
            lines.append('  Run#{}: {} · {}事件 · {}ms · {}'.format(
                r.get('run_id', '?'), r.get('timestamp', '?')[:19],
                r.get('events_count', 0), r.get('elapsed_ms', 0),
                'DRY' if r.get('dry_run') else 'LIVE'))
        lines.append('')
    
    # 告警
    alerts = fw.get('alerts', [])
    if alerts:
        lines.append('⚠️ 告警 ({}条)'.format(len(alerts)))
        for a in alerts[:10]:
            lines.append('  [{}] {}: {}'.format(a.get('severity', '?'), a.get('type', '?'), a.get('detail', '')))
        lines.append('')
    else:
        lines.append('✅ 无告警')
        lines.append('')
    
    # 实体统计
    lines.append('📦 实体统计')
    for key in ['products', 'customers', 'cities', 'avatars', 'flows', 'cognition_events']:
        v = data.get(key, [])
        lines.append('  {}: {}'.format(key, len(v) if isinstance(v, list) else '?'))
    
    return '\n'.join(lines)


# ============================================================
# CLI 入口
# ============================================================
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='SRI 知识资产飞轮引擎')
    parser.add_argument('action', nargs='?', default='all',
                       choices=['all', 'scan', 'health', 'llm-gap', 'report'],
                       help='执行动作')
    parser.add_argument('--dry-run', action='store_true', help='只读不写')
    parser.add_argument('--json', action='store_true', help='JSON格式输出')
    
    args = parser.parse_args()
    
    if args.action == 'report':
        data = load_data()
        print(generate_report(data))
    else:
        cycle_map = {'all': None, 'scan': 'scan', 'health': 'health', 'llm-gap': 'llm-gap'}
        events = run(cycle=cycle_map.get(args.action), dry_run=args.dry_run)
        
        if args.json:
            print(json.dumps(events, ensure_ascii=False, indent=2))
        else:
            print('飞轮 {}: {} 事件 · {}'.format(
                args.action,
                len(events),
                'DRY RUN·未保存' if args.dry_run else '已保存'))
            for e in events[:10]:
                print('  [{}] {}'.format(e.get('type', '?'),
                      str(e.get('entity_id', e.get('count', '')))[:60]))
            if len(events) > 10:
                print('  ... 还有 {} 条'.format(len(events) - 10))
