#!/usr/bin/env python3
"""
Skill注册表同步脚本
从core/技能注册.yaml生成Working层Skill目录
"""

import yaml
import os
from datetime import datetime

def sync_skills():
    # 读取Core定义
    with open('core/技能注册.yaml', 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    metadata = data.get('metadata', {})
    registry = data.get('skill_registry', {})
    stats = data.get('statistics', {})
    
    # 确保输出目录存在
    os.makedirs('working/skills', exist_ok=True)
    
    # 生成Skill目录文档
    content = f"""# 满意解技能注册表

> 版本: {metadata.get('version', '1.0')} | 更新时间: {metadata.get('last_updated', datetime.now().strftime('%Y-%m-%d'))}
> 总数: {metadata.get('total_skills', 0)} | 类别: {metadata.get('categories', 0)}+
> > 本文件由core/技能注册.yaml自动生成，请勿手动修改

---

## 统计概览

| 来源 | 数量 |
|------|------|
| 自建核心 | {stats.get('by_source', {}).get('internal', 0)} |
| 外部技能 | {stats.get('by_source', {}).get('external', 0)} |
| **总计** | **{metadata.get('total_skills', 0)}** |

---

## 自建核心技能

"""
    
    for skill in registry.get('core_skills', []):
        content += f"- **{skill['name']}** v{skill['version']}: {skill['description']} ({skill['status']})\n"
    
    content += "\n## 自建替代套件\n\n"
    for skill in registry.get('replacement_suite', []):
        content += f"- **{skill['name']}** v{skill['version']}: 替代{', '.join(skill.get('replaces', []))} ({skill['status']})\n"
    
    content += "\n## 外部技能（按类别）\n\n"
    
    external = registry.get('external_skills', {})
    
    # 信息获取类
    content += "### 信息获取\n\n"
    for skill in external.get('information', []):
        content += f"- **{skill['name']}**: {skill['description']}\n"
    
    # 内容创作类
    content += "\n### 内容创作\n\n"
    for skill in external.get('content_creation', []):
        content += f"- **{skill['name']}**: {skill['description']}\n"
    
    # 数据分析类
    content += "\n### 数据分析\n\n"
    for skill in external.get('data_analysis', []):
        content += f"- **{skill['name']}**: {skill['description']}\n"
    
    # 文档处理类
    content += "\n### 文档处理\n\n"
    for skill in external.get('document', []):
        content += f"- **{skill['name']}**: {skill['description']}\n"
    
    # 飞书生态
    content += "\n### 飞书生态\n\n"
    for skill in external.get('feishu_ecosystem', []):
        content += f"- **{skill['name']}**: {skill['description']}\n"
    
    # 企微生态
    content += "\n### 企业微信生态\n\n"
    for skill in external.get('wecom_ecosystem', []):
        content += f"- **{skill['name']}**: {skill['description']}\n"
    
    # 自动化
    content += "\n### 自动化\n\n"
    for skill in external.get('automation', []):
        content += f"- **{skill['name']}**: {skill['description']}\n"
    
    # 开发工具
    content += "\n### 开发工具\n\n"
    for skill in external.get('development', []):
        content += f"- **{skill['name']}**: {skill['description']}\n"
    
    content += "\n---\n\n*本文件由sync_skills.py自动生成*\n"
    
    # 写入文档
    with open('working/skills/README.md', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Skill注册表同步完成")
    print(f"   - Skill目录: working/skills/README.md")

if __name__ == '__main__':
    sync_skills()
