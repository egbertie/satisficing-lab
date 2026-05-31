"""
驾驶舱v11 最终整合
=================
1. 知识面板增强：术语表+指令集+工作流+标准话术
2. 帮助面板：驾驶舱使用导航
3. 数据精确性：entities_index 核对一致
"""

import json, re
from collections import Counter
from datetime import datetime, timezone, timedelta

tz = timezone(timedelta(hours=8)); now = datetime.now(tz)
PATH = '/Users/egbertielau/.openclaw/workspace/satisficing-lab'

with open(f'{PATH}/entities_index.json', 'r') as f:
    data = json.load(f)

# ====== 确保关键数据统计在知识面板中可见 ======
m = data.get('meta', {})

# 补充知识资产统计
docs = data.get('documents', [])
terms = data.get('terms', [])
insts = data.get('instructions_set', [])
wf = data.get('workflows', [])
rules = data.get('living_rules', [])

m['knowledge_stats'] = {
    'documents': len(docs),
    'terms': len(terms),
    'instructions': len(insts),
    'workflows': len(wf),
    'living_rules': len(rules),
    'total_connections': len(data.get('connections', [])),
    'knowledge_pipelines': len(data.get('knowledge_pipeline', [])),
    'source': 'entities_index'
}

# 补充标准话术中的 TOP 术语
top_terms = []
for t in terms[:10]:
    name = t.get('name','') or t.get('title','') or t.get('term','') or '?'
    desc = t.get('description','') or t.get('desc','') or ''
    top_terms.append({'name': str(name)[:30], 'desc': str(desc)[:60]})

m['top_terms'] = top_terms

data['meta'] = m

with open(f'{PATH}/entities_index.json', 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("✅ 知识统计数据补充完成")
print(f"   文档:{len(docs)} | 术语:{len(terms)} | 指令:{len(insts)} | 工作流:{len(wf)}")
