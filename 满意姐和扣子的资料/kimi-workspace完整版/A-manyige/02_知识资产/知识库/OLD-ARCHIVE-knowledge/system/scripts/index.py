#!/usr/bin/env python3
"""
索引生成脚本 - 扫描所有知识单元，生成全局索引
支持按实体、标签、时间多维度检索
"""

import os
import sys
import yaml
from pathlib import Path
from datetime import datetime
from collections import defaultdict

KNOWLEDGE_DIR = Path("/root/.openclaw/workspace/knowledge")
INDEX_FILE = KNOWLEDGE_DIR / "system" / "index.md"

def scan_experts():
    """扫描专家数据"""
    experts_dir = KNOWLEDGE_DIR / "data" / "experts"
    experts = []
    for yaml_file in experts_dir.glob("*.yaml"):
        with open(yaml_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            data['_file'] = yaml_file.name
            experts.append(data)
    return experts

def scan_cases():
    """扫描案例数据"""
    cases_dir = KNOWLEDGE_DIR / "data" / "cases"
    if not cases_dir.exists():
        return []
    cases = []
    for yaml_file in cases_dir.glob("*.yaml"):
        with open(yaml_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            data['_file'] = yaml_file.name
            cases.append(data)
    return cases

def scan_processed():
    """扫描处理后数据"""
    summaries_dir = KNOWLEDGE_DIR / "processed" / "summaries"
    if not summaries_dir.exists():
        return []
    summaries = []
    for yaml_file in summaries_dir.glob("*.yaml"):
        with open(yaml_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            summaries.append(data)
    return summaries

def generate_index(experts, cases, summaries):
    """生成索引"""
    lines = [
        "# 满意解知识库全局索引",
        "",
        f"> **版本**: V2.0 | **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## 📊 统计概览",
        "",
        f"- **专家数量**: {len(experts)}",
        f"- **案例数量**: {len(cases)}",
        f"- **处理文档**: {len(summaries)}",
        "",
        "## 👥 专家索引",
        "",
        "### 按状态",
        "",
    ]
    
    # 按状态分组
    by_status = defaultdict(list)
    for e in experts:
        by_status[e.get('status', '未知')].append(e)
    
    for status in ['已确认', '拟邀', '潜在']:
        if status in by_status:
            lines.append(f"\n#### {status} ({len(by_status[status])})")
            lines.append("")
            for e in by_status[status]:
                lines.append(f"- **{e.get('name')}** - {e.get('field')} ({e.get('totem', 'N/A')})")
    
    # 按图腾分组
    lines.append("\n### 按图腾\n")
    by_totem = defaultdict(list)
    for e in experts:
        if e.get('totem'):
            by_totem[e['totem']].append(e)
    
    for totem in ['LIU', 'SIMON', 'GUANYIN', 'CONFUCIUS', 'HUINENG']:
        if totem in by_totem:
            names = [e.get('name') for e in by_totem[totem]]
            lines.append(f"- **{totem}**: {', '.join(names)}")
    
    # 按领域分组
    lines.append("\n### 按领域\n")
    by_field = defaultdict(list)
    for e in experts:
        if e.get('field'):
            by_field[e['field']].append(e.get('name'))
    
    for field, names in sorted(by_field.items()):
        lines.append(f"- **{field}**: {', '.join(names)}")
    
    # 案例索引
    lines.append("\n## 📁 案例索引\n")
    if cases:
        for c in cases:
            lines.append(f"- **{c.get('客户代号', 'Unknown')}** - {c.get('决策类型', 'N/A')}")
    else:
        lines.append("*暂无案例数据*")
    
    # 处理文档索引
    lines.append("\n## 📝 处理文档\n")
    if summaries:
        for s in summaries:
            entity_count = s.get('entity_count', 0)
            lines.append(f"- **{s.get('source_file', 'Unknown')}** - 实体: {entity_count}")
    else:
        lines.append("*暂无处理文档*")
    
    # 快速参考
    lines.append("\n## 🔍 快速参考\n")
    lines.append("### 五路图腾\n")
    lines.append("| 图腾 | 元素 | 核心能力 |")
    lines.append("|------|------|----------|")
    lines.append("| LIU | 火 | 价值纯度 |")
    lines.append("| SIMON | 土 | 理性框架 |")
    lines.append("| GUANYIN | 金 | 极限测试 |")
    lines.append("| CONFUCIUS | 木 | 合伙人伦理 |")
    lines.append("| HUINENG | 水 | 压力管理 |")
    
    lines.append("\n### 决策维度\n")
    lines.append("1. 价值纯度 (LIU/火)")
    lines.append("2. 理性框架 (SIMON/土)")
    lines.append("3. 压力管理 (HUINENG/水)")
    lines.append("4. 合伙人伦理 (CONFUCIUS/木)")
    lines.append("5. 极限测试 (GUANYIN/金)")
    
    return "\n".join(lines)

def main():
    """主函数"""
    print("📇 开始生成全局索引...")
    
    # 扫描数据
    experts = scan_experts()
    cases = scan_cases()
    summaries = scan_processed()
    
    print(f"✓ 扫描到 {len(experts)} 个专家")
    print(f"✓ 扫描到 {len(cases)} 个案例")
    print(f"✓ 扫描到 {len(summaries)} 个处理文档")
    
    # 生成索引
    index = generate_index(experts, cases, summaries)
    
    # 保存索引
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        f.write(index)
    
    print(f"✓ 索引已保存: {INDEX_FILE}")
    print("\n✅ 索引生成完成！")
    return 0

if __name__ == "__main__":
    sys.exit(main())
