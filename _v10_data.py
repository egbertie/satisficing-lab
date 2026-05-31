"""
一人公司驾驶舱 v10.0 · 精准数据修复
=====================================
核心理念: 数据溯源·一人视角·昨天对比·安心感知
每一个展示的数字都必须可以回溯到源数据
"""

import json, subprocess
from collections import Counter
from datetime import datetime, timezone, timedelta

tz = timezone(timedelta(hours=8)); now = datetime.now(tz)

PATH = '/Users/egbertielau/.openclaw/workspace/satisficing-lab'

with open(f'{PATH}/entities_index.json', 'r') as f:
    data = json.load(f)

m = data.get('meta', {})

# ═══════════════════════════════════
# 精准数据统计（从源数据直接计算）
# ═══════════════════════════════════

# --- 产品 ---
prods = data.get('products', [])
ps = Counter(p.get('status','?') for p in prods)
pf = Counter(p.get('family','未归类') for p in prods)
plc = Counter(p.get('lifecycle_stage','?') for p in prods)
with_llm = sum(1 for p in prods if p.get('llm_rating'))
with_url = sum(1 for p in prods if p.get('url'))

# --- 任务 ---
tasks = data.get('tasks', [])
t_status = Counter(t.get('status','?') for t in tasks)
t_pri = Counter((t.get('priority','') or '?').replace('P0·立即','P0').replace('P1·本周','P1').replace('P2·两周','P2') for t in tasks)

# 精确算法：已完成 = 包含"完成" | 进行中 = 包含"进行中" | 待执行 = 包含"待执"或"待启动"
completed = sum(1 for t in tasks if '完成' in str(t.get('status','')))
in_progress = sum(1 for t in tasks if '进行中' in str(t.get('status','')))
pending = sum(1 for t in tasks if '待执' in str(t.get('status','')) or '待启动' in str(t.get('status','')))

# --- 连接 ---
conns = data.get('connections', [])
strong = sum(1 for c in conns if (c.get('weight', 0) or 0) >= 0.9)
medium = sum(1 for c in conns if 0.5 <= (c.get('weight', 0) or 0) < 0.9)
weak = sum(1 for c in conns if (c.get('weight', 0) or 0) < 0.5)

# --- 规则 ---
rules = data.get('living_rules', [])
rl = Counter(r.get('status','?') for r in rules)

# --- 客户 ---
customers = data.get('customers', [])
cp_count = len(data.get('customer_profiles', []))
flows_count = len(data.get('individual_customer_flows', []))

# --- 城市 ---
cities = data.get('cities', [])
city_tiers = Counter(c.get('tier','?') for c in cities)

# --- 替身 ---
avatars = data.get('avatars', [])

# --- 管道/飞轮 ---
crons = data.get('crons', [])
active_crons = sum(1 for c in crons if c.get('status') == 'active')
scripts_count = len(data.get('scripts', []))
workflows_count = len(data.get('workflows', []))
docs_count = len(data.get('documents', []))
kp_count = len(data.get('knowledge_pipeline', []))

# --- R&D ---
rd = data.get('rd_pipeline', {})
rd_projects = rd.get('active_projects', [])

# --- 闭环 ---
cl = data.get('closed_loops', {})

# --- 获客 ---
acq = data.get('acquisition_engine', {})

# --- 免疫 ---
imm = data.get('immune_system', {})

# --- 治理 ---
gov = data.get('decision_governance', {})

# ═══════════════════════════════════
# 写入 meta（所有字段都有溯源注释）
# ═══════════════════════════════════
m['product_stats'] = {
    'total': len(prods),
    'premium': ps.get('精品', 0),
    'online': ps.get('线上', 0),
    'offline': ps.get('已下架', 0),
    'archive': ps.get('资料·归入知识库', 0),
    'families': dict(pf),
    'family_count': len(pf),
    'lifecycle': dict(plc),
    'with_llm_rating': with_llm,
    'with_url': with_url,
    'source': 'entities_index.products[].status|family|lifecycle_stage|llm_rating|url',
}

m['task_stats'] = {
    'total': len(tasks),
    'completed': completed,
    'in_progress': in_progress,
    'pending': pending,
    'p0': t_pri.get('P0', 0),
    'p1': t_pri.get('P1', 0),
    'p2': t_pri.get('P2', 0),
    'source': 'entities_index.tasks[].status|priority',
    'verified_at': now.isoformat(),
}

m['connection_stats'] = {
    'total': len(conns),
    'strong': strong,
    'medium': medium,
    'weak': weak,
    'source': 'entities_index.connections[].weight',
}

m['rule_stats'] = {
    'total': len(rules),
    'active': rl.get('active', rl.get('活', 0)),
    'dormant': rl.get('dormant', rl.get('休眠', 0)),
    'broken': rl.get('broken', rl.get('坏', 0)),
    'source': 'entities_index.living_rules[].status',
}

m['customer_stats'] = {
    'total': len(customers),
    'profiles': cp_count,
    'individual_flows': flows_count,
    'source': 'entities_index.customers[]|customer_profiles[]|individual_customer_flows[]',
}

m['city_stats'] = {
    'total': len(cities),
    'by_tier': {str(k): v for k, v in city_tiers.items()},
    'source': 'entities_index.cities[].tier',
}

m['avatar_stats'] = {
    'total': len(avatars),
    'source': 'entities_index.avatars[]',
}

m['flywheel_stats'] = {
    'knowledge_pipelines': kp_count,
    'crons_total': len(crons),
    'crons_active': active_crons,
    'scripts_total': scripts_count,
    'workflows_total': workflows_count,
    'documents_total': docs_count,
    'rules_total': len(rules),
    'source': 'entities_index.crons[]|scripts[]|workflows[]|documents[]|knowledge_pipeline[]|living_rules[]',
}

m['rd_stats'] = {
    'stages': len(rd.get('stages', [])),
    'active_projects': len(rd_projects),
    'source': 'entities_index.rd_pipeline.stages[]|active_projects[]',
}

m['loop_stats'] = {
    'small': len(cl.get('small_loops', [])),
    'medium': len(cl.get('medium_loops', [])),
    'big': 1,
    'source': 'entities_index.closed_loops',
}

m['acquisition_stats'] = {
    'channels': len(acq.get('channels', [])),
    'funnel_stages': len(acq.get('funnel_targets', {})),
    'source': 'entities_index.acquisition_engine',
}

m['immune_stats'] = {
    'components': len(imm.get('components', [])),
    'score': (imm.get('health', {}) or {}).get('score', 0),
    'source': 'entities_index.immune_system',
}

m['governance_stats'] = {
    'decision_types': len(gov.get('types', [])),
    'model': gov.get('model', 'DACI'),
    'source': 'entities_index.decision_governance',
}

# 时间戳
m['stats_generated'] = now.isoformat()
m['updated'] = now.isoformat()

data['meta'] = m

with open(f'{PATH}/entities_index.json', 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("✅ 精准数据层完成")
print(f"   产品: {len(prods)} (精品{ps.get('精品',0)}·线上{ps.get('线上',0)})")
print(f"   任务: {len(tasks)} (完成{completed}·进行中{in_progress}·待执行{pending})")
print(f"   连接: {len(conns)} (强{strong}·中{medium}·弱{weak})")
print(f"   规则: {len(rules)} (活{rl.get('活',rl.get('active',0))}·休眠{rl.get('休眠',rl.get('dormant',0))}·坏{rl.get('坏',rl.get('broken',0))})")
print(f"   客户: {len(customers)}·画像{cp_count}·独立流{flows_count}")
print(f"   城市: {len(cities)} | 替身: {len(avatars)}")
print(f"   管道:{kp_count}·Cron:{len(crons)}/{active_crons}活·脚本:{scripts_count}·工作流:{workflows_count}")
print(f"   R&D: {len(rd_projects)}项目·{len(rd.get('stages',[]))}阶段")
print(f"   闭环: 小{len(cl.get('small_loops',[]))}·中{len(cl.get('medium_loops',[]))}·大1")
print(f"   免疫: {len(imm.get('components',[]))}组件·{(imm.get('health',{}) or {}).get('score',0)}分")
print(f"   治理: {len(gov.get('types',[]))}决策类型·{gov.get('model','DACI')}")
