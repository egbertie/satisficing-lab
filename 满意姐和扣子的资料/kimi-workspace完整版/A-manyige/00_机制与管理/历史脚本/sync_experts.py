#!/usr/bin/env python3
"""
专家档案同步脚本
从core/专家档案.yaml生成Working层专家文档
"""

import yaml
import os
from datetime import datetime

def sync_experts():
    # 读取Core定义
    with open('core/专家档案.yaml', 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    experts = data.get('experts', [])
    metadata = data.get('metadata', {})
    progress = data.get('progress_tracking', {})
    
    # 确保输出目录存在
    os.makedirs('working/experts', exist_ok=True)
    
    # 生成专家索引文档
    index_content = f"""# 满意解专家数字替身网络

> 版本: {metadata.get('version', '1.0')} | 更新时间: {metadata.get('last_updated', datetime.now().strftime('%Y-%m-%d'))}
> > 本文件由core/专家档案.yaml自动生成，请勿手动修改

---

## 概览

| 状态 | 数量 |
|------|------|
| 已建档 | {metadata.get('status_distribution', {}).get('established', 0)} |
| 待深化 | {metadata.get('status_distribution', {}).get('developing', 0)} |
| 顶级专家（目标） | {metadata.get('status_distribution', {}).get('top_tier', 0)} |
| **总计** | **{metadata.get('total_experts', 0)}** |

---

## 专家列表

"""
    
    for expert in experts:
        status_emoji = "🟢" if expert.get('status') == 'established' else "🟡"
        priority = expert.get('priority', 'P3')
        index_content += f"{status_emoji} **{expert['name']}{expert.get('title', '')}** ({expert.get('annotation', '')}) - {expert['basic_info']['role']} - {priority}\n\n"
    
    index_content += "\n---\n\n## 能力提升进度\n\n"
    
    overall = progress.get('overall_target', [])
    for metric in overall:
        index_content += f"- {metric.get('metric', '')}: 当前{metric.get('current_average', 'N/A')} → 目标{metric.get('target', '')}\n"
    
    index_content += "\n---\n\n*本文件由sync_experts.py自动生成*\n"
    
    # 写入索引文档
    with open('working/experts/README.md', 'w', encoding='utf-8') as f:
        f.write(index_content)
    
    # 生成每个专家的详细文档
    for expert in experts:
        expert_id = expert['id']
        basic = expert.get('basic_info', {})
        
        content = f"""# {expert['name']}{expert.get('title', '')} ({expert.get('annotation', '')})

**专家ID**: {expert_id}  
**当前状态**: {expert.get('status', '')} → {expert.get('target_status', '')}  
**优先级**: {expert.get('priority', '')}  
**图腾**: {basic.get('totem', 'N/A')}

---

## 基本信息

- **职位**: {basic.get('position', '')}
- **专长**: {basic.get('specialty', '')}
- **角色定位**: {basic.get('role', '')}

---

## 知识领域

"""
        
        for domain in expert.get('knowledge_domains', []):
            content += f"### {domain['name']}\n\n"
            for concept in domain.get('key_concepts', []):
                content += f"- {concept}\n"
            content += "\n"
        
        content += f"""---

## 与满意解的整合

"""
        
        for integration in expert.get('satisfaction_integration', []):
            content += f"- {integration}\n"
        
        content += f"""

---

## 研究任务

"""
        
        for task in expert.get('research_tasks', []):
            content += f"- [ ] {task}\n"
        
        content += f"""

---

## 预期产出

"""
        
        for deliverable in expert.get('deliverables', []):
            content += f"- {deliverable}\n"
        
        content += f"""

---

## 知识图谱进度

- **目标节点数**: {expert.get('knowledge_graph', {}).get('target_nodes', 0)}
- **当前节点数**: {expert.get('knowledge_graph', {}).get('current_nodes', 0)}
- **完成度**: {expert.get('knowledge_graph', {}).get('current_nodes', 0) / expert.get('knowledge_graph', {}).get('target_nodes', 1) * 100:.1f}%

---

*本文件由core/专家档案.yaml自动生成*
"""
        
        with open(f'working/experts/{expert_id}.md', 'w', encoding='utf-8') as f:
            f.write(content)
    
    print(f"✅ 专家档案同步完成")
    print(f"   - 专家索引: working/experts/README.md")
    print(f"   - 专家详情: working/experts/EXPERT-*.md ({len(experts)}个)")

if __name__ == '__main__':
    sync_experts()
