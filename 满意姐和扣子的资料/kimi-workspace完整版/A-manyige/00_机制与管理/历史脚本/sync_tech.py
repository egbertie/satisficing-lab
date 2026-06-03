#!/usr/bin/env python3
"""
技术文档同步脚本
从core/技术架构.yaml生成Working层技术文档
"""

import yaml
import os
from datetime import datetime

def get_status_emoji(status):
    if status == 'completed':
        return '✅'
    elif status == 'in_progress':
        return '🔄'
    else:
        return '⏳'

def sync_tech():
    # 读取Core定义
    with open('core/技术架构.yaml', 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    metadata = data.get('metadata', {})
    architecture = data.get('architecture', {})
    future = data.get('future_phases', {})
    metrics = data.get('performance_metrics', {})
    
    # 确保输出目录存在
    os.makedirs('working/tech', exist_ok=True)
    
    # 获取各层状态
    l7_status = architecture.get('l7_human_ai_collaboration', {}).get('status', '')
    l6_status = architecture.get('l6_decision_governance', {}).get('status', '')
    l5_status = architecture.get('l5_domain_knowledge', {}).get('status', '')
    l4_status = architecture.get('l4_multi_agent_collaboration', {}).get('status', '')
    l3_status = architecture.get('l3_model_inference', {}).get('status', '')
    l2_status = architecture.get('l2_computation_acceleration', {}).get('status', '')
    l1_status = architecture.get('l1_infrastructure', {}).get('status', '')
    
    # 生成技术架构文档
    content = f"""# 满意解技术架构 V{metadata.get('version', '2.0')}

> 阶段: Phase {metadata.get('phase', 1)} | 状态: {metadata.get('status', '')}
> 
> 本文件由core/技术架构.yaml自动生成，请勿手动修改

---

## 七级架构概览

```
L7: 人机协作层        [{get_status_emoji(l7_status)}]
L6: 决策治理层        [{get_status_emoji(l6_status)}]
L5: 领域知识层        [{get_status_emoji(l5_status)}]
L4: 多Agent协作层     [{get_status_emoji(l4_status)}]
L3: 模型推理层        [{get_status_emoji(l3_status)}]
L2: 计算加速层        [{get_status_emoji(l2_status)}]
L1: 基础设施层        [{get_status_emoji(l1_status)}]
```

---

## 各层详情

"""
    
    # L7
    l7 = architecture.get('l7_human_ai_collaboration', {})
    content += f"### L7: {l7.get('name', '')}\n\n"
    for comp in l7.get('components', []):
        content += f"- **{comp['name']}**: {comp['description']} ({comp['implementation']})\n"
    content += "\n"
    
    # L6
    l6 = architecture.get('l6_decision_governance', {})
    content += f"### L6: {l6.get('name', '')}\n\n"
    for comp in l6.get('components', []):
        content += f"- **{comp['name']}**: {comp['description']} ({comp['implementation']})\n"
    content += "\n"
    
    # L5
    l5 = architecture.get('l5_domain_knowledge', {})
    content += f"### L5: {l5.get('name', '')}\n\n"
    for comp in l5.get('components', []):
        content += f"- **{comp['name']}**: {comp['description']} ({comp['implementation']})\n"
    content += "\n"
    
    # L4
    l4 = architecture.get('l4_multi_agent_collaboration', {})
    content += f"### L4: {l4.get('name', '')}\n\n"
    for comp in l4.get('components', []):
        content += f"- **{comp['name']}**: {comp['description']} ({comp['implementation']})\n"
    content += "\n"
    
    # L3
    l3 = architecture.get('l3_model_inference', {})
    content += f"### L3: {l3.get('name', '')}\n\n"
    for comp in l3.get('components', []):
        content += f"- **{comp['name']}**: {comp['description']} ({comp['implementation']})\n"
    content += "\n"
    
    # L2
    l2 = architecture.get('l2_computation_acceleration', {})
    content += f"### L2: {l2.get('name', '')}\n\n"
    for comp in l2.get('components', []):
        content += f"- **{comp['name']}**: {comp['description']} ({comp['implementation']})\n"
    content += "\n"
    
    # L1
    l1 = architecture.get('l1_infrastructure', {})
    content += f"### L1: {l1.get('name', '')}\n\n"
    for comp in l1.get('components', []):
        content += f"- **{comp['name']}**: {comp['description']} ({comp['implementation']})\n"
    content += "\n"
    
    # Phase 2-4
    content += "---\n\n## Phase 2-4 规划（储备技术）\n\n"
    for phase_key, phase in future.items():
        content += f"### {phase.get('name', '')}\n"
        content += f"- **状态**: {phase.get('status', '')}\n"
        content += f"- **预算**: {phase.get('budget', '')}\n"
        content += "- **组件**:\n"
        for comp in phase.get('components', []):
            content += f"  - {comp}\n"
        content += "\n"
    
    # 性能指标
    content += "---\n\n## 性能指标\n\n### Phase 1 已达成\n\n"
    for metric in metrics.get('phase_1_achieved', []):
        content += f"- **{metric['metric']}**: {metric['improvement']} ({metric['status']})\n"
    
    content += f"\n**总提升**: {metrics.get('total_improvement', 'N/A')}\n\n"
    
    content += "### Phase 2-4 目标\n\n"
    for metric in metrics.get('phase_2_4_target', []):
        content += f"- **{metric['metric']}**: 预计{metric['improvement']}\n"
    
    content += "\n---\n\n*本文件由sync_tech.py自动生成*\n"
    
    # 写入文档
    with open('working/tech/architecture.md', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 技术文档同步完成")
    print(f"   - 技术架构: working/tech/architecture.md")

if __name__ == '__main__':
    sync_tech()
