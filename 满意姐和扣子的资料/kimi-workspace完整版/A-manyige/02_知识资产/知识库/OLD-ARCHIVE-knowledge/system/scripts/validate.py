#!/usr/bin/env python3
"""
一致性检查脚本 - 验证知识库完整性
检查项:
- 实体引用是否符合ontology定义
- 专家标注是否统一
- 五路图腾术语是否一致
- 生成检查报告
"""

import os
import sys
import yaml
from pathlib import Path
from collections import defaultdict

KNOWLEDGE_DIR = Path("/root/.openclaw/workspace/knowledge")
REPORT_FILE = KNOWLEDGE_DIR / "system" / "validation_report.md"

def load_ontology():
    """加载本体定义"""
    core_file = KNOWLEDGE_DIR / "ontology" / "core.yaml"
    with open(core_file, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

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

def validate_experts(experts, ontology):
    """验证专家数据"""
    issues = []
    valid_totems = ontology.get('namespaces', {}).get('五路图腾', [])
    valid_status = ontology.get('entities', {}).get('专家', {}).get('状态枚举', [])
    required_fields = ontology.get('entities', {}).get('专家', {}).get('必填', [])
    
    for expert in experts:
        # 检查必填字段
        for field in required_fields:
            if field == '姓名' and not expert.get('name'):
                issues.append(f"[{expert['_file']}] 缺少必填字段: 姓名")
            if field == '领域' and not expert.get('field'):
                issues.append(f"[{expert['_file']}] 缺少必填字段: 领域")
        
        # 检查图腾有效性
        totem = expert.get('totem')
        if totem and totem not in valid_totems:
            issues.append(f"[{expert['_file']}] 无效图腾: {totem}")
        
        # 检查状态有效性
        status = expert.get('status')
        if status and status not in valid_status:
            issues.append(f"[{expert['_file']}] 无效状态: {status}")
    
    return issues

def check_totem_consistency(experts):
    """检查图腾术语一致性"""
    issues = []
    valid_totems = ['LIU', 'SIMON', 'GUANYIN', 'CONFUCIUS', 'HUINENG']
    
    for expert in experts:
        totem = expert.get('totem')
        if totem and totem not in valid_totems:
            issues.append(f"[{expert['_file']}] 图腾命名不规范: {totem}")
    
    return issues

def generate_report(issues, experts, ontology):
    """生成验证报告"""
    report_lines = [
        "# 知识库验证报告",
        "",
        f"**生成时间**: {__import__('datetime').datetime.now().isoformat()}",
        f"**专家总数**: {len(experts)}",
        f"**发现问题**: {len(issues)} 个",
        "",
        "## 检查项目",
        "",
        "- [x] 实体引用符合ontology定义",
        "- [x] 专家标注统一性",
        "- [x] 五路图腾术语一致性",
        "",
        "## 专家统计",
        "",
    ]
    
    # 按状态统计
    status_count = defaultdict(int)
    for e in experts:
        status_count[e.get('status', '未知')] += 1
    
    report_lines.append("| 状态 | 数量 |")
    report_lines.append("|------|------|")
    for status, count in status_count.items():
        report_lines.append(f"| {status} | {count} |")
    
    report_lines.append("")
    report_lines.append("## 问题列表")
    report_lines.append("")
    
    if issues:
        for issue in issues:
            report_lines.append(f"- ⚠️ {issue}")
    else:
        report_lines.append("✅ 未发现一致性问题")
    
    report_lines.append("")
    report_lines.append("## 专家清单")
    report_lines.append("")
    report_lines.append("| 姓名 | 领域 | 图腾 | 状态 |")
    report_lines.append("|------|------|------|------|")
    
    for e in sorted(experts, key=lambda x: x.get('name', '')):
        report_lines.append(f"| {e.get('name', '-')} | {e.get('field', '-')} | {e.get('totem', '-')} | {e.get('status', '-')} |")
    
    return "\n".join(report_lines)

def main():
    """主函数"""
    print("🔍 开始验证知识库...")
    
    # 加载数据
    ontology = load_ontology()
    experts = load_all_experts()
    
    # 执行检查
    issues = []
    issues.extend(validate_experts(experts, ontology))
    issues.extend(check_totem_consistency(experts))
    
    # 生成报告
    report = generate_report(issues, experts, ontology)
    
    # 保存报告
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write(report)
    
    # 输出结果
    print(f"✓ 已加载 {len(experts)} 个专家")
    print(f"✓ 发现问题: {len(issues)} 个")
    print(f"✓ 报告已保存: {REPORT_FILE}")
    
    if issues:
        print("\n发现的问题:")
        for issue in issues[:10]:
            print(f"  ⚠️ {issue}")
        if len(issues) > 10:
            print(f"  ... 还有 {len(issues) - 10} 个问题")
        return 1
    else:
        print("\n✅ 所有检查通过！")
        return 0

if __name__ == "__main__":
    sys.exit(main())
