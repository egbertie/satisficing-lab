#!/usr/bin/env python3
"""
查询脚本 - 快速检索机制
支持按实体类型查询、按关系查询、全文搜索
"""

import os
import sys
import yaml
import re
from pathlib import Path
from collections import defaultdict

KNOWLEDGE_DIR = Path("/root/.openclaw/workspace/knowledge")

def load_all_experts():
    """加载所有专家数据"""
    experts_dir = KNOWLEDGE_DIR / "data" / "experts"
    experts = []
    for yaml_file in experts_dir.glob("*.yaml"):
        with open(yaml_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            data['_file'] = yaml_file.name
            experts.append(data)
    return experts

def load_all_cases():
    """加载所有案例数据"""
    cases_dir = KNOWLEDGE_DIR / "data" / "cases"
    cases = []
    if cases_dir.exists():
        for yaml_file in cases_dir.glob("*.yaml"):
            with open(yaml_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                cases.append(data)
    return cases

def query_by_entity_type(entity_type):
    """按实体类型查询"""
    results = []
    
    if entity_type == '专家':
        experts = load_all_experts()
        for e in experts:
            results.append({
                'name': e.get('name'),
                'field': e.get('field'),
                'status': e.get('status'),
                'totem': e.get('totem')
            })
    elif entity_type == '案例':
        cases = load_all_cases()
        for c in cases:
            results.append({
                'client': c.get('客户代号'),
                'type': c.get('决策类型'),
                'industry': c.get('行业')
            })
    
    return results

def query_by_relation(relation_type, entity_name=None):
    """按关系查询"""
    results = []
    
    if relation_type == '专家创造方法论':
        experts = load_all_experts()
        for e in experts:
            relations = e.get('relations', {})
            created = relations.get('创造', [])
            if created and (not entity_name or e.get('name') == entity_name):
                results.append({
                    'expert': e.get('name'),
                    'methodologies': created
                })
    
    return results

def full_text_search(keyword):
    """全文搜索"""
    results = []
    
    # 搜索专家
    experts = load_all_experts()
    for e in experts:
        text = f"{e.get('name', '')} {e.get('field', '')} {e.get('description', '')} {e.get('role', '')}"
        if keyword.lower() in text.lower():
            results.append({
                'type': '专家',
                'name': e.get('name'),
                'match': e.get('field')
            })
    
    return results

def query_totem(totem_name):
    """按图腾查询专家"""
    experts = load_all_experts()
    results = [e for e in experts if e.get('totem') == totem_name]
    return results

def print_results(results, title):
    """打印结果"""
    print(f"\n{'='*50}")
    print(f"📋 {title} (共 {len(results)} 条)")
    print('='*50)
    
    for i, r in enumerate(results, 1):
        print(f"\n[{i}]")
        for key, value in r.items():
            if not key.startswith('_'):
                print(f"  {key}: {value}")

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("""满意解知识库查询工具

用法:
  python query.py experts              # 列出所有专家
  python query.py expert <姓名>        # 查询特定专家
  python query.py totem <图腾名>       # 按图腾查询 (LIU/SIMON/GUANYIN/CONFUCIUS/HUINENG)
  python query.py search <关键词>      # 全文搜索
  python query.py status <状态>        # 按状态查询 (已确认/拟邀/潜在)
""")
        return 0
    
    cmd = sys.argv[1]
    
    if cmd == 'experts':
        results = query_by_entity_type('专家')
        print_results(results, "专家列表")
    
    elif cmd == 'expert' and len(sys.argv) >= 3:
        name = sys.argv[2]
        experts = load_all_experts()
        results = [e for e in experts if name in e.get('name', '')]
        print_results(results, f"专家: {name}")
    
    elif cmd == 'totem' and len(sys.argv) >= 3:
        totem = sys.argv[2].upper()
        results = query_totem(totem)
        print_results(results, f"图腾: {totem}")
    
    elif cmd == 'search' and len(sys.argv) >= 3:
        keyword = sys.argv[2]
        results = full_text_search(keyword)
        print_results(results, f"搜索: {keyword}")
    
    elif cmd == 'status' and len(sys.argv) >= 3:
        status = sys.argv[2]
        experts = load_all_experts()
        results = [e for e in experts if e.get('status') == status]
        print_results(results, f"状态: {status}")
    
    else:
        print(f"未知命令: {cmd}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
