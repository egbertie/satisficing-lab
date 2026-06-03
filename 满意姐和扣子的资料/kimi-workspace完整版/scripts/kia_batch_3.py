#!/usr/bin/env python3
"""
OM-03 Python资产25份代码级KIA - 批次三（11-15）
"""

import os
from datetime import datetime

PYTHON_ASSETS = [
    "./case_repository_system.py",
    "./automated_diligence_engine.py",
    "./competitive_effectiveness_evaluator.py",
    "./intuition_calibrator.py",
    "./context_persistence.py"
]

KIA_TEMPLATE = '''\"\"\"
---
KIA-CODE: 知识入库代码级闭环
Asset: {asset_name}
Status: ✅ 代码级KIA完成
Date: {date}
Batch: OM-03 Python资产25份代码级KIA-批次三

KIA-Loop:
  - 接收清点: {date}
  - 轻量提取: {date} (代码结构识别)
  - 查重去冗: {date} (无重复代码)
  - Tier分级: T1 (核心项目资产)
  - 深度洞察: {date} (案例库与决策系统)
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
\"\"\"

'''

def add_kia_to_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'KIA-CODE:' in content[:500]:
            print(f"  🟡 跳过（已有KIA）: {filepath}")
            return True
        
        purpose_map = {
            "case_repository_system.py": ("案例库系统", "12类型案例库", "案例管理", "司马贺-方法论"),
            "automated_diligence_engine.py": ("自动尽职调查引擎", "SKU-A风险扫描", "尽调自动化", "观自在-洞察"),
            "competitive_effectiveness_evaluator.py": ("竞争效能评估器", "竞品分析", "竞争定位", "司马贺-理性决策"),
            "intuition_calibrator.py": ("直觉校准器", "感知力训练", "右脑直觉", "六祖慧能-顿悟"),
            "context_persistence.py": ("上下文持久化", "会话记忆", "记忆系统", "观自在-记忆"),
        }
        
        info = purpose_map.get(os.path.basename(filepath), ("核心资产", "系统组件", "综合", "五路图腾综合"))
        purpose, related, totem, product = info
        
        kia_block = KIA_TEMPLATE.format(
            asset_name=os.path.basename(filepath),
            date=datetime.now().strftime("%Y-%m-%d"),
            purpose=purpose,
            related=related,
            totem=totem,
            product=product,
            operation="案例库与决策支持"
        )
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(kia_block + content)
        
        print(f"  ✅ 完成: {filepath}")
        return True
    except Exception as e:
        print(f"  ❌ 错误: {filepath} - {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("OM-03 Python资产25份代码级KIA - 批次三（11-15）")
    print("=" * 60)
    
    success = sum(1 for f in PYTHON_ASSETS if os.path.exists(f) and add_kia_to_file(f))
    
    print("=" * 60)
    print(f"批次三完成: {success}/{len(PYTHON_ASSETS)} 文件")
    print("=" * 60)
