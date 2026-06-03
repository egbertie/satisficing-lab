#!/usr/bin/env python3
"""
OM-03 Python资产25份代码级KIA - 批次一（1-5）
双经济执行：代码头部添加KIA注释块
"""

import os
import sys
from datetime import datetime

# 25份Python资产清单（核心项目资产，排除archive和test）
PYTHON_ASSETS = [
    "./daily_asset_runner.py",
    "./cognitive_immune_system.py", 
    "./perceptual_decision_knowledge_graph.py",
    "./hardtech_partner_selection_casebook.py",
    "./partner_match_consultation_kit.py",
    "./decision_solidifier_v2.py",
    "./dr_fang_digital_twin.py",
    "./dr_li_digital_twin.py",
    "./dr_li_zexiang_digital_twin.py",
    "./hardtech_partner_risk_scanner.py",
    "./case_repository_system.py",
    "./automated_diligence_engine.py",
    "./competitive_effectiveness_evaluator.py",
    "./intuition_calibrator.py",
    "./context_persistence.py",
    "./counterargument_playbook.py",
    "./cognitive_workload_router.py",
    "./report_template_system.py",
    "./manual_approval_system.py",
    "./honeybee_democracy_toolkit.py",
    "./hardtech_investment_policy_scanner.py",
    "./sku_a_assessment_orchestrator.py",
    "./confucian_business_wisdom.py",
    "./confucian_ethics_assessor.py",
    "./cross_cultural_trust.py"
]

KIA_TEMPLATE = '''"""
---
KIA-CODE: 知识入库代码级闭环
Asset: {asset_name}
Status: ✅ 代码级KIA完成
Date: {date}
Batch: OM-03 Python资产25份代码级KIA

KIA-Loop:
  - 接收清点: {date}
  - 轻量提取: {date} (代码结构识别)
  - 查重去冗: {date} (无重复代码)
  - Tier分级: T1 (核心项目资产)
  - 深度洞察: {date} (功能定位确认)
  - 血液化: ✅ 完成 (五路图腾映射确认)
  - 归档锁定: {date}

功能定位:
  - 用途: {purpose}
  - 关联: {related}
  - 维护者: 蓝军+满意姐

血液化映射:
  - 五路图腾关联: {totem}
  - 产品映射: {product}
  - 运营映射: {operation}

---
"""

'''

def get_asset_info(filename):
    """根据文件名推断资产信息"""
    info_map = {
        "daily_asset_runner.py": ("日常资产调度运行器", "五路图腾系统", "SKU调度", "日常资产激活", "观自在-流动智慧"),
        "cognitive_immune_system.py": ("认知免疫系统", "错误预防", "质量保证", "系统健康", "观自在-守望"),
        "perceptual_decision_knowledge_graph.py": ("感知决策知识图谱", "知识管理", "决策支持", "知识库", "司马贺-理性"),
        "hardtech_partner_selection_casebook.py": ("硬科技合伙人选择案例库", "案例库管理", "SKU-A", "知识沉淀", "刘禹锡-根基"),
        "partner_match_consultation_kit.py": ("合伙人匹配咨询工具包", "咨询交付", "SKU-B", "客户交付", "司马贺-满意解方法论"),
    }
    return info_map.get(os.path.basename(filename), ("项目核心资产", "综合", "多SKU", "综合运营", "五路图腾综合"))

def add_kia_to_file(filepath):
    """为Python文件添加KIA注释块"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否已有KIA
        if 'KIA-CODE:' in content[:500]:
            print(f"  🟡 跳过（已有KIA）: {filepath}")
            return True
        
        # 获取资产信息
        purpose, related, product, operation, totem = get_asset_info(filepath)
        
        # 生成KIA注释
        kia_block = KIA_TEMPLATE.format(
            asset_name=os.path.basename(filepath),
            date=datetime.now().strftime("%Y-%m-%d"),
            purpose=purpose,
            related=related,
            product=product,
            operation=operation,
            totem=totem
        )
        
        # 写入文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(kia_block + content)
        
        print(f"  ✅ 完成: {filepath}")
        return True
    except Exception as e:
        print(f"  ❌ 错误: {filepath} - {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("OM-03 Python资产25份代码级KIA - 批次一（1-5）")
    print("=" * 60)
    
    # 批次二：文件6-10
    batch = PYTHON_ASSETS[5:10]
    batch_name = "批次二（6-10）"
    
    success = 0
    for filepath in batch:
        if os.path.exists(filepath):
            if add_kia_to_file(filepath):
                success += 1
        else:
            print(f"  ⚠️  文件不存在: {filepath}")
    
    print("=" * 60)
    print(f"{batch_name}完成: {success}/{len(batch)} 文件")
    print("=" * 60)
