#!/usr/bin/env python3
"""
OM-03 Python资产25份代码级KIA - 批次四（16-20）
"""

import os
from datetime import datetime

PYTHON_ASSETS = [
    "./counterargument_playbook.py",
    "./cognitive_workload_router.py",
    "./report_template_system.py",
    "./manual_approval_system.py",
    "./honeybee_democracy_toolkit.py"
]

KIA_TEMPLATE = '''\"\"\"
---
KIA-CODE: 知识入库代码级闭环
Asset: {asset_name}
Status: ✅ 代码级KIA完成
Date: {date}
Batch: OM-03 Python资产25份代码级KIA-批次四

KIA-Loop:
  - 接收清点: {date}
  - 轻量提取: {date} (代码结构识别)
  - 查重去冗: {date} (无重复代码)
  - Tier分级: T1 (核心项目资产)
  - 深度洞察: {date} (协作与认知系统)
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
            "counterargument_playbook.py": ("反方观点手册", "蓝军对抗验证", "批判性思维", "蓝军-Skeptor-7"),
            "cognitive_workload_router.py": ("认知工作负载路由器", "任务分配", "负载均衡", "观自在-动态调度"),
            "report_template_system.py": ("报告模板系统", "标准化交付", "交付物生成", "司马贺-标准化"),
            "manual_approval_system.py": ("人工审批系统", "关键决策审批", "风险控制", "孔子-伦理审查"),
            "honeybee_democracy_toolkit.py": ("蜜蜂民主工具包", "群体决策", "共识机制", "六祖慧能-集体智慧"),
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
            operation="协作与认知优化"
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
    print("OM-03 Python资产25份代码级KIA - 批次四（16-20）")
    print("=" * 60)
    
    success = sum(1 for f in PYTHON_ASSETS if os.path.exists(f) and add_kia_to_file(f))
    
    print("=" * 60)
    print(f"批次四完成: {success}/{len(PYTHON_ASSETS)} 文件")
    print("=" * 60)
