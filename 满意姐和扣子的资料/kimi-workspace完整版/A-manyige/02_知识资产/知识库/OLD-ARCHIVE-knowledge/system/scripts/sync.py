#!/usr/bin/env python3
"""
同步脚本 - 从data/自动生成Working文档
保持与V2.0下载包同步
"""

import os
import sys
import yaml
from pathlib import Path
from datetime import datetime

KNOWLEDGE_DIR = Path("/root/.openclaw/workspace/knowledge")
WORKSPACE_DIR = Path("/root/.openclaw/workspace")

def load_all_experts():
    """加载所有专家数据"""
    experts_dir = KNOWLEDGE_DIR / "data" / "experts"
    experts = []
    for yaml_file in sorted(experts_dir.glob("*.yaml")):
        with open(yaml_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            experts.append(data)
    return experts

def generate_experts_markdown(experts):
    """生成专家层Markdown"""
    lines = [
        "# 专家层 (Expert Layer)",
        "",
        "> **自动生成** | 最后更新: {}".format(datetime.now().strftime("%Y-%m-%d %H:%M")),
        "",
        "## 专家列表",
        "",
    ]
    
    for e in experts:
        status_icon = "✅" if e.get('status') == '已确认' else "⏳" if e.get('status') == '拟邀' else "🤔"
        lines.append(f"### {status_icon} {e.get('name', 'Unknown')} ({e.get('title', '')})")
        lines.append("")
        lines.append(f"- **图腾**: {e.get('totem', 'N/A')}")
        lines.append(f"- **元素**: {e.get('element', 'N/A')}")
        lines.append(f"- **领域**: {e.get('field', 'N/A')}")
        lines.append(f"- **角色**: {e.get('role', 'N/A')}")
        lines.append(f"- **状态**: {e.get('status', 'N/A')}")
        lines.append(f"- **描述**: {e.get('description', 'N/A')}")
        lines.append("")
        
        # 关系
        relations = e.get('relations', {})
        if relations.get('创造'):
            lines.append(f"- **创造的方法论**: {', '.join(relations['创造'])}")
        lines.append("")
    
    return "\n".join(lines)

def generate_totem_reference():
    """生成五路图腾参考"""
    return """# 五路图腾参考

| 图腾 | 元素 | 核心能力 | 对应专家 |
|------|------|----------|----------|
| LIU | 火 | 价值纯度 | 罗汉 |
| SIMON | 土 | 理性框架 | 谢宝剑 |
| GUANYIN | 金 | 压力管理/极限测试 | 李泽湘 |
| CONFUCIUS | 木 | 合伙人伦理 | 黎红雷 |
| HUINENG | 水 | 压力管理 | 方翊沣 |

## 决策维度

1. **价值纯度** - 罗汉教授
2. **理性框架** - 谢宝剑研究员
3. **压力管理** - 方翊沣博士
4. **合伙人伦理** - 黎红雷教授
5. **极限测试** - 李泽湘教授
"""

def main():
    """主函数"""
    print("🔄 开始同步数据到Working文档...")
    
    # 加载数据
    experts = load_all_experts()
    print(f"✓ 加载 {len(experts)} 个专家")
    
    # 生成专家层文档
    experts_md = generate_experts_markdown(experts)
    experts_file = WORKSPACE_DIR / "Working_专家层.md"
    with open(experts_file, 'w', encoding='utf-8') as f:
        f.write(experts_md)
    print(f"✓ 生成专家层文档: {experts_file}")
    
    # 生成图腾参考
    totem_md = generate_totem_reference()
    totem_file = WORKSPACE_DIR / "Working_五路图腾.md"
    with open(totem_file, 'w', encoding='utf-8') as f:
        f.write(totem_md)
    print(f"✓ 生成图腾参考: {totem_file}")
    
    print("\n✅ 同步完成！")
    return 0

if __name__ == "__main__":
    sys.exit(main())
