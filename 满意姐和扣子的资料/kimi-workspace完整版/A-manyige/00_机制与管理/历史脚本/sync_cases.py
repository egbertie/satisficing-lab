#!/usr/bin/env python3
"""
案例库同步脚本
从core/案例库.yaml生成Working层案例文档
"""

import yaml
import os
from datetime import datetime

def sync_cases():
    # 读取Core定义
    with open('core/案例库.yaml', 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    cases = data.get('cases', [])
    metadata = data.get('metadata', {})
    
    # 确保输出目录存在
    os.makedirs('working/cases', exist_ok=True)
    
    # 统计各类案例数量
    success_count = sum(1 for c in cases if c.get('category') == 'success')
    failure_count = sum(1 for c in cases if c.get('category') == 'failure')
    ongoing_count = sum(1 for c in cases if c.get('category') == 'ongoing')
    
    # 生成案例索引文档
    index_content = f"""# 满意解案例库

> 版本: {metadata.get('version', '1.0')} | 更新时间: {metadata.get('last_updated', datetime.now().strftime('%Y-%m-%d'))}
> 
> 本文件由core/案例库.yaml自动生成，请勿手动修改

---

## 概览

| 类别 | 数量 |
|------|------|
| 成功案例 | {success_count} |
| 失败案例 | {failure_count} |
| 进行中 | {ongoing_count} |
| **总计** | **{len(cases)}** |

---

## 案例列表

"""
    
    # 成功案例
    index_content += "### 成功案例\n\n"
    for case in cases:
        if case.get('category') == 'success':
            index_content += f"- **{case['id']}**: {case['name']} - {case.get('outcome', '')}\n"
    
    # 失败案例
    index_content += "\n### 失败案例\n\n"
    for case in cases:
        if case.get('category') == 'failure':
            index_content += f"- **{case['id']}**: {case['name']} - {case.get('lessons', '')}\n"
    
    # 进行中
    index_content += "\n### 进行中\n\n"
    for case in cases:
        if case.get('category') == 'ongoing':
            index_content += f"- **{case['id']}**: {case['name']} - {case.get('current_status', '')}\n"
    
    index_content += "\n---\n\n*本文件由sync_cases.py自动生成*\n"
    
    # 写入索引文档
    with open('working/cases/README.md', 'w', encoding='utf-8') as f:
        f.write(index_content)
    
    # 生成每个案例的详细文档
    for case in cases:
        case_id = case['id']
        case_content = f"""# {case['name']}

**案例ID**: {case_id}  
**类别**: {case.get('category', '')}  
**行业**: {case.get('industry', '')}  
**阶段**: {case.get('stage', '')}

---

## 创始人画像

- **类型**: {case.get('founder_type', '')}
- **合伙人类型**: {case.get('partner_type', '')}
- **匹配度评分**: {case.get('match_score', 'N/A')}

"""
        
        if case.get('category') == 'success':
            case_content += """
## 成功因素

"""
            for factor in case.get('key_factors', []):
                case_content += f"- {factor}\n"
            
            case_content += f"""
## 成果

{case.get('outcome', '')}

## 核心启示

> {case.get('lessons', '')}
"""
        
        elif case.get('category') == 'failure':
            case_content += """
## 失败因素

"""
            for factor in case.get('failure_factors', []):
                case_content += f"- {factor}\n"
            
            case_content += f"""
## 结果

{case.get('outcome', '')}

## 教训

> {case.get('lessons', '')}
"""
        
        elif case.get('category') == 'ongoing':
            case_content += f"""
## 当前状态

{case.get('current_status', '')}

## 挑战

"""
            for challenge in case.get('challenges', []):
                case_content += f"- {challenge}\n"
        
        case_content += """

---

*本文件由core/案例库.yaml自动生成*
"""
        
        with open(f'working/cases/{case_id}.md', 'w', encoding='utf-8') as f:
            f.write(case_content)
    
    print(f"✅ 案例库同步完成")
    print(f"   - 案例索引: working/cases/README.md")
    print(f"   - 案例详情: working/cases/CASE-*.md ({len(cases)}个)")

if __name__ == '__main__':
    sync_cases()
