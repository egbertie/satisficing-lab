#!/usr/bin/env python3
"""
Skill状态修正器 - R4整改通道
批量修正Skill虚报状态
"""

import os
import json
from pathlib import Path
from datetime import datetime

WORKSPACE_ROOT = "/root/.openclaw/workspace"
SKILLS_DIR = f"{WORKSPACE_ROOT}/skills"

def load_fraud_report():
    """加载虚报报告"""
    report_path = f"{WORKSPACE_ROOT}/SKILL_FRAUD_SCAN_REPORT.json"
    with open(report_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def correct_skill_status(skill_result):
    """修正单个Skill状态"""
    name = skill_result['name']
    path = skill_result['path']
    fraud_type = skill_result['fraud_type']
    correction_action = skill_result['correction_action']
    
    if fraud_type == "NONE":
        return None, "无需修正"
    
    skill_md_path = Path(path) / "SKILL.md"
    if not skill_md_path.exists():
        return None, "SKILL.md不存在"
    
    try:
        content = skill_md_path.read_text(encoding='utf-8')
        original_content = content
        corrections = []
        
        # 1. 删除FIN标记，改为WIP
        if "删除FIN标记，改为WIP" in correction_action:
            # 替换各种完成标记
            if 'FIN' in content or '运行中' in content or '✅' in content:
                content = content.replace('FIN', 'WIP')
                content = content.replace('运行中', '开发中')
                content = content.replace('✅', '🔄')
                corrections.append("FIN→WIP")
        
        # 2. 添加诚实声明（如果适用）
        if fraud_type in ["MAJOR_FRAUD", "CRITICAL_FRAUD"]:
            # 在文件开头添加诚实声明
            if "## 状态" not in content and "## 当前状态" not in content:
                honesty_note = f"""## 当前状态
> **状态**: WIP (开发中)
> **最后更新**: {datetime.now().strftime('%Y-%m-%d')}
> **诚实声明**: 此Skill当前为文档或初步实现阶段，核心功能待完成

"""
                content = honesty_note + content
                corrections.append("添加诚实声明")
        
        # 3. 写入修正后的内容
        if content != original_content:
            skill_md_path.write_text(content, encoding='utf-8')
            return corrections, "修正完成"
        else:
            return None, "内容未变化"
            
    except Exception as e:
        return None, f"错误: {str(e)}"

def correct_super_system_skill(skill_result):
    """修正超级系统框架Skill"""
    name = skill_result['name']
    path = skill_result['path']
    skill_md_path = Path(path) / "SKILL.md"
    
    try:
        # 读取当前内容
        content = skill_md_path.read_text(encoding='utf-8')
        
        # 创建新的诚实SKILL.md
        new_content = f"""---
name: {name}
description: {name.replace('-suite', ' Suite')} - 超级系统组件【WIP - 开发中】
---

# {name.replace('-', ' ').title()}

## 当前状态
- **状态**: WIP (开发中)
- **诚实声明**: 此Skill目前为空壳实现，核心功能待开发
- **创建日期**: {datetime.now().strftime('%Y-%m-%d')}
- **预计完成**: TBD

## 计划功能
- 待定义

## 实际现状
- SKILL.md: 模板
- 代码: 空壳/模板代码
- 测试: 无

## 开发计划
1. 定义核心功能
2. 实现核心代码
3. 编写测试
4. 集成验证

## Token管理
- 成本估算: 待评估
- 效益红线: 待定义
- 优化空间: 待分析
"""
        
        skill_md_path.write_text(new_content, encoding='utf-8')
        return True, "重写为诚实状态"
        
    except Exception as e:
        return False, f"错误: {str(e)}"

def main():
    """主函数"""
    print("🔧 Skill状态修正开始...")
    
    # 加载报告
    report = load_fraud_report()
    
    # 分类结果
    super_system_skills = report['super_system_analysis']
    major_fraud = report['fraud_by_severity']['MAJOR']
    moderate_fraud = report['fraud_by_severity']['MODERATE']
    minor_fraud = report['fraud_by_severity']['MINOR']
    
    corrections_log = []
    
    # 1. 优先修正超级系统框架（10个）
    print("\n" + "="*60)
    print("🎯 修正超级系统框架 (10个)")
    print("="*60)
    
    for skill in super_system_skills:
        name = skill['name']
        success, msg = correct_super_system_skill(skill)
        status = "✅" if success else "❌"
        print(f"{status} {name}: {msg}")
        corrections_log.append({
            "name": name,
            "type": "super_system",
            "result": msg
        })
    
    # 2. 修正MAJOR级别虚报
    print("\n" + "="*60)
    print(f"🚨 修正MAJOR级别虚报 ({len(major_fraud)}个)")
    print("="*60)
    
    for skill in major_fraud:
        name = skill['name']
        corrections, msg = correct_skill_status(skill)
        status = "✅" if corrections else "⚠️"
        print(f"{status} {name}: {msg}")
        if corrections:
            print(f"   修正内容: {', '.join(corrections)}")
        corrections_log.append({
            "name": name,
            "type": "major",
            "result": msg,
            "corrections": corrections
        })
    
    # 3. 修正MODERATE级别虚报
    print("\n" + "="*60)
    print(f"⚠️ 修正MODERATE级别虚报 ({len(moderate_fraud)}个)")
    print("="*60)
    
    for skill in moderate_fraud:
        name = skill['name']
        corrections, msg = correct_skill_status(skill)
        status = "✅" if corrections else "⚠️"
        print(f"{status} {name}: {msg}")
        corrections_log.append({
            "name": name,
            "type": "moderate",
            "result": msg,
            "corrections": corrections
        })
    
    # 4. 修正MINOR级别虚报
    print("\n" + "="*60)
    print(f"ℹ️ 修正MINOR级别虚报 ({len(minor_fraud)}个)")
    print("="*60)
    
    for skill in minor_fraud:
        name = skill['name']
        corrections, msg = correct_skill_status(skill)
        status = "✅" if corrections else "⚠️"
        print(f"{status} {name}: {msg}")
        corrections_log.append({
            "name": name,
            "type": "minor",
            "result": msg,
            "corrections": corrections
        })
    
    # 保存修正日志
    log_path = f"{WORKSPACE_ROOT}/SKILL_CORRECTION_LOG.json"
    with open(log_path, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "total_corrected": len([x for x in corrections_log if '修正' in x.get('result', '')]),
            "corrections": corrections_log
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n📁 修正日志已保存: {log_path}")
    print(f"\n✅ 修正完成! 共修正 {len([x for x in corrections_log if '修正' in x.get('result', '')])} 个Skill")

if __name__ == "__main__":
    main()
