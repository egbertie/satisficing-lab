"""
驾驶舱关键修复脚本 - 确保显示最新数据
"""
import json, re

PATH = '/Users/egbertielau/.openclaw/workspace/satisficing-lab'

# ====== 1. 确保 entities_index meta 数据完善 ======
with open(f'{PATH}/entities_index.json', 'r') as f:
    data = json.load(f)

m = data.get('meta', {})
prods = data.get('products', [])

# 确保关键字段存在
from collections import Counter
statuses = Counter(p.get('status','?') for p in prods)
m['premium_count'] = statuses.get('精品', 0)
m['online_count'] = statuses.get('线上', 0)
m['launchable'] = sum(1 for p in prods if p.get('url'))
m['total_products'] = len(prods)

# 补产品族分布
families = Counter(p.get('family','未归类') for p in prods)
m['product_families'] = dict(families)

# 补 breakdown
bd = m.get('breakdown', {})
bd['products'] = len(prods)
bd['customers'] = len(data.get('customers', []))
bd['avatars'] = len(data.get('avatars', []))
bd['tasks'] = len(data.get('tasks', []))
bd['crons'] = len(data.get('crons', []))
m['breakdown'] = bd

# 补任务统计
tasks = data.get('tasks', [])
task_statuses = Counter(t.get('status','?') for t in tasks)
m['task_stats'] = {
    'total': len(tasks),
    'completed': task_statuses.get('✅ 已完成', 0) + task_statuses.get('已完成', 0),
    'in_progress': task_statuses.get('⏳ 进行中', 0) + task_statuses.get('进行中', 0),
    'pending': task_statuses.get('⬜ 待执行', 0) + task_statuses.get('待启动', 0),
}

with open(f'{PATH}/entities_index.json', 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("✅ Meta 数据更新完成")
print(f"   产品: {len(prods)} (精品{m['premium_count']}·线上{m['online_count']})")
print(f"   任务: {m['task_stats']}")

# ====== 2. 驾驶舱 renderTasks 增强 ======
with open(f'{PATH}/dashboard-v3.html', 'r') as f:
    html = f.read()

m2 = re.search(r'(<script>)(.*?)(</script>)', html, re.DOTALL)
js = m2.group(2)

# 增强 renderTasks - 添加表头和筛选标签
old_tasks = """function renderTasks(filt) {
  taskFilt = filt;
  var tasks = (EIDX.tasks || []).slice();"""

# 找 renderTasks 完整函数
idx_start = js.find('function renderTasks(filt) {')
idx_end = js.find('\nfunction renderHealth() {')

old_fn = js[idx_start:idx_end]

new_fn = """function renderTasks(filt) {
  taskFilt = filt;
  var tasks = (EIDX.tasks || []).slice();
  var allTasks = tasks;

  // 任务统计
  var taskStats = (EIDX.meta || {}).task_stats || {};
  var h = '<div class="stat-grid" style="grid-template-columns:repeat(4,1fr);margin-bottom:12px">';
  h += '<div class="stat-card"><div class="stat-num">' + (taskStats.total || tasks.length) + '</div><div class="stat-label">📋 总任务</div></div>';
  h += '<div class="stat-card"><div class="stat-num" style="color:#3D7A4F">' + (taskStats.completed || 0) + '</div><div class="stat-label">✅ 已完成</div></div>';
  h += '<div class="stat-card"><div class="stat-num" style="color:#C2780A">' + (taskStats.in_progress || 0) + '</div><div class="stat-label">⏳ 进行中</div></div>';
  h += '<div class="stat-card"><div class="stat-num" style="color:var(--accent-red)">' + (taskStats.pending || 0) + '</div><div class="stat-label">⬜ 待执行</div></div>';
  h += '</div>';

  // 筛选按钮
  var filts = ['全部', 'P0', 'P1', 'P2', '已完成', '进行中', '待执行'];
  h += '<div class="task-filters">';
  for (var i = 0; i < filts.length; i++) {
    h += '<button class="btn-outline' + (taskFilt === filts[i] ? ' active' : '') + '" onclick="renderTasks(\\'' + filts[i] + '\\')" style="margin:2px;font-size:0.75em;padding:4px 12px">' + filts[i] + '</button>';
  }
  h += '</div>';

  // 筛选
  if (taskFilt === 'P0') tasks = tasks.filter(function(t) { var p = t.priority || ''; return p.indexOf('P0') === 0; });
  else if (taskFilt === 'P1') tasks = tasks.filter(function(t) { var p = t.priority || ''; return p.indexOf('P1') === 0; });
  else if (taskFilt === 'P2') tasks = tasks.filter(function(t) { var p = t.priority || ''; return p.indexOf('P2') === 0; });
  else if (taskFilt === '已完成') tasks = tasks.filter(function(t) { var s = t.status || ''; return s.indexOf('已完成') >= 0; });
  else if (taskFilt === '进行中') tasks = tasks.filter(function(t) { var s = t.status || ''; return s.indexOf('进行中') >= 0; });
  else if (taskFilt === '待执行') tasks = tasks.filter(function(t) { var s = t.status || ''; return s.indexOf('待执行') >= 0 || s.indexOf('待启动') >= 0; });

  // 表格
  h += '<div style="overflow-x:auto"><table class="data-table" style="width:100%;font-size:0.78em">';
  h += '<thead><tr><th>任务名</th><th>优先级</th><th>状态</th><th>负责人</th><th>截止</th></tr></thead><tbody>';"""

# Replace the old function content
new_js = js[:idx_start] + new_fn + js[idx_end-1:]

# 确保新代码语法检查
html2 = html[:m2.start(2)] + new_js + html[m2.end(2):]

with open(f'{PATH}/dashboard-v3.html', 'w') as f:
    f.write(html2)

# 检查语法
import subprocess
r = subprocess.run(['node', '-e', f'''
const vm = require("vm");
const fs = require("fs");
const js = fs.readFileSync("{PATH}/dashboard-v3.html","utf8").match(/<script>([\\\\s\\\\S]*?)<\\\\/script>/)[1];
try {{ new vm.Script(js); console.log("OK"); }} catch(e) {{ console.log("ERROR:", e.message); }}
'''], capture_output=True, text=True, timeout=10)
print("JS语法:", r.stdout.strip())
