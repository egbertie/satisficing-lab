#!/usr/bin/env node
/**
 * entities_index.json 自动更新脚本 v3 (final)
 * Cron: entities_index_autoupdate
 * 
 * 扫描 entities_index.json 内部数据数组，更新 meta.breakdown 实体计数
 * 重新计算 knowledge_graph_density
 * 更新 product_families 分布
 * 标记 >10% 变动并通知
 */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const WORKSPACE = '/Users/egbertielau/.openclaw/workspace';
const ENTITIES_PATH = path.join(WORKSPACE, 'entities_index.json');
const BACKUP_DIR = path.join(WORKSPACE, '.bak');

function md5(data) { return crypto.createHash('md5').update(data).digest('hex'); }
function md5File(p) { return md5(fs.readFileSync(p)); }

// ── Main ────────────────────────────────────────
console.log('═'.repeat(60));
console.log('🔍 entities_index.json 自动更新 v3');
console.log(`⏰ ${new Date().toISOString()}`);
console.log('═'.repeat(60));

const entities = JSON.parse(fs.readFileSync(ENTITIES_PATH, 'utf8'));
if (!entities?.meta) { console.error('❌ meta 缺失'); process.exit(1); }

const oldBreakdown = { ...entities.meta.breakdown };
const oldDensity = entities.meta.knowledge_graph_density;
const oldFamilies = { ...(entities.meta.product_families || {}) };

// ── Entity types to scan ──
const ENTITY_KEYS = [
  'products', 'customers', 'tasks', 'avatars', 'documents', 'decisions',
  'milestones', 'terms', 'events', 'scripts', 'crons', 'connections',
  'customer_profiles', 'quality_metrics', 'growth_metrics', 'vi_standards',
  'lifecycle_stages', 'instructions_set', 'workflows', 'governance_frameworks',
  'content_assets', 'scoring_models', 'simulation_scenarios',
  'historical_artifacts', 'additional_discoveries', 'living_rules'
];

// ── 1. Count entities from internal arrays ──
const newBreakdown = {};
for (const key of ENTITY_KEYS) {
  const arr = entities[key];
  if (arr === undefined || arr === null) {
    newBreakdown[key] = oldBreakdown[key] || 0;
  } else if (Array.isArray(arr)) {
    newBreakdown[key] = arr.length;
  } else if (typeof arr === 'object') {
    newBreakdown[key] = Object.keys(arr).length;
  } else {
    newBreakdown[key] = oldBreakdown[key] || 0;
  }
}

// ── 2. Product families ──
const newFamilies = {};
if (Array.isArray(entities.products)) {
  for (const p of entities.products) {
    const fam = p.family || p.product_family || '未知';
    newFamilies[fam] = (newFamilies[fam] || 0) + 1;
  }
}

// ── 3. Connection classification & density ──
let strongC = 0, mediumC = 0, weakC = 0;
const conns = entities.connections || [];
if (Array.isArray(conns)) {
  for (const c of conns) {
    const w = c.weight ?? 0;
    if (w >= 0.7) strongC++;
    else if (w >= 0.3) mediumC++;
    else weakC++;
  }
}
const meaningful = strongC + mediumC;
const totalConns = conns.length || 1;
const newDensity = Math.min(99.9, Math.round((meaningful / totalConns) * 1000) / 10);

// ── 4. Check variations ──
const alerts = [];
const changes = [];

for (const key of ENTITY_KEYS) {
  const oldV = oldBreakdown[key] || 0;
  const newV = newBreakdown[key] || 0;
  if (oldV === newV) continue;
  
  const pct = oldV > 0 ? Math.abs((newV - oldV) / oldV * 100) : 100;
  const arrow = newV > oldV ? '↑' : '↓';
  const msg = `${key}: ${oldV} ${arrow}→ ${newV} (${pct.toFixed(1)}%)`;
  
  if (pct > 10) alerts.push(`⚠️ ${msg}`);
  changes.push(msg);
}

// Also check density change
const densityPct = oldDensity > 0 ? Math.abs((newDensity - oldDensity) / oldDensity * 100) : 0;
if (densityPct > 10) {
  alerts.push(`⚠️ knowledge_graph_density: ${oldDensity}% → ${newDensity}% (${densityPct.toFixed(1)}%)`);
}

// Check product_families change
for (const [k, v] of Object.entries(newFamilies)) {
  const ov = oldFamilies[k] || 0;
  if (ov > 0 && Math.abs(v - ov) / ov > 0.1 && v !== ov) {
    alerts.push(`⚠️ product_family.${k}: ${ov} → ${v}`);
  }
}
// Check for removed families
for (const k of Object.keys(oldFamilies)) {
  if (!(k in newFamilies) && oldFamilies[k] > 0) {
    alerts.push(`⚠️ product_family.${k}: ${oldFamilies[k]} → 0 (removed)`);
  }
}

// ── 5. Update entities_index.json ──
const now = new Date();
const ts = now.toISOString();

entities.meta.breakdown = newBreakdown;
entities.meta.updated = `${ts.split('.')[0]}+08:00`;
entities.meta.knowledge_graph_density = newDensity;
entities.meta.knowledge_graph_density_note = 
  `强${strongC}+中${mediumC}=${meaningful}/${totalConns}=${newDensity}% (auto-updated ${ts.split('T')[0]})`;

// Update product_families
entities.meta.product_families = newFamilies;

// Update total_entities_covered
const nonConnKeys = ENTITY_KEYS.filter(k => k !== 'connections');
const totalCovered = nonConnKeys.reduce((sum, k) => sum + (newBreakdown[k] || 0), 0);
if (entities.meta.four_layer_coverage) {
  entities.meta.four_layer_coverage.total_entities_covered = totalCovered;
  entities.meta.four_layer_coverage.updated = ts;
}

// Connection stats
entities.meta.connection_stats = {
  total: totalConns,
  strong: strongC,
  medium: mediumC,
  weak: weakC,
  computed_at: ts,
};

// Auto-update log
if (!entities.meta.auto_update_log) entities.meta.auto_update_log = [];
entities.meta.auto_update_log.push({
  id: `AUTOUPDATE-${String(entities.meta.auto_update_log.length + 1).padStart(4, '0')}`,
  timestamp: ts,
  source: 'cron:entities_index_autoupdate',
  duration_ms: Date.now() - now.getTime(),
  density: { before: oldDensity, after: newDensity },
  connection_classification: { strong: strongC, medium: mediumC, weak: weakC },
  alerts: alerts.length > 0 ? alerts : [],
  changes: changes,
  product_families_diff: Object.keys(newFamilies).filter(k => (oldFamilies[k]||0) !== newFamilies[k]).map(k => `${k}: ${oldFamilies[k]||0}→${newFamilies[k]}`),
});

// Keep last 30 log entries
if (entities.meta.auto_update_log.length > 30) {
  entities.meta.auto_update_log = entities.meta.auto_update_log.slice(-30);
}

// ── 6. Backup ──
if (!fs.existsSync(BACKUP_DIR)) fs.mkdirSync(BACKUP_DIR, { recursive: true });
const backupName = `entities_index_${ts.replace(/[:.]/g, '-').slice(0, 19)}.json`;
fs.copyFileSync(ENTITIES_PATH, path.join(BACKUP_DIR, backupName));

// ── 7. Write ──
fs.writeFileSync(ENTITIES_PATH, JSON.stringify(entities, null, 2), 'utf8');

// ── 8. Verify ──
const newMD5 = md5File(ENTITIES_PATH);
const sizeMB = (fs.statSync(ENTITIES_PATH).size / 1024 / 1024).toFixed(2);

// ── Report ──
console.log('\n✅ 更新完成');
console.log(`📅 ${ts}`);
console.log(`🔐 MD5: ${newMD5}`);
console.log(`📦 ${sizeMB} MB`);
console.log(`📊 知识图谱密度: ${oldDensity}% → ${newDensity}%`);
console.log(`🔗 连接: ${totalConns} (强${strongC} + 中${mediumC} + 弱${weakC})`);

console.log('\n📈 breakdown:');
const displayKeys = ['products','customers','tasks','avatars','documents','decisions','milestones','terms','events','scripts','crons','connections','customer_profiles','quality_metrics','growth_metrics','vi_standards','lifecycle_stages','instructions_set','workflows','governance_frameworks','living_rules'];
for (const k of displayKeys) {
  const o = oldBreakdown[k] || 0, n = newBreakdown[k] || 0;
  const a = n === o ? ' ' : (n > o ? '↑' : '↓');
  console.log(`  ${String(k).padEnd(22)} ${String(o).padStart(5)} ${a} ${String(n).padStart(5)}`);
}

if (changes.length > 0) {
  console.log('\n📝 变动:');
  changes.forEach(c => console.log(`  ${c}`));
}

if (alerts.length > 0) {
  console.log('\n⚠️ 异常 (>10%):');
  alerts.forEach(a => console.log(`  ${a}`));
} else {
  console.log('\n✅ 所有变动在正常范围内');
}

console.log('\n📦 product_families:');
const allFams = new Set([...Object.keys(oldFamilies), ...Object.keys(newFamilies)]);
for (const k of [...allFams].sort((a,b) => (newFamilies[b]||0) - (newFamilies[a]||0))) {
  const o = oldFamilies[k] || 0, n = newFamilies[k] || 0;
  const a = n === o ? ' ' : (n > o ? '↑' : '↓');
  console.log(`  ${k}: ${String(o).padStart(3)} ${a} ${String(n).padStart(3)}`);
}

console.log('\n' + '═'.repeat(60));
console.log('🏁 完成\n');
