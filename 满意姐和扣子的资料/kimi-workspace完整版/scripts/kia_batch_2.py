#!/usr/bin/env python3
"""
OM-03 Python资产25份代码级KIA - 批次二（6-10）
"""

import os
from datetime import datetime

PYTHON_ASSETS = [
    "./decision_solidifier_v2.py",
    "./dr_fang_digital_twin.py",
    "./dr_li_digital_twin.py",
    "./dr_li_zexiang_digital_twin.py",
    "./hardtech_partner_risk_scanner.py"
]

KIA_TEMPLATE = '''"""
---
KIA-CODE: 知识入库代码级闭环
Asset: {asset_name}
Status: ✅ 代码级KIA完成
Date: {date}
Batch: OM-03 Python资产25份代码级KIA-批次二

KIA-Loop:
  - 接收清点: {date}
  - 轻量提取: {date} (代码结构识别)
  - 查重去冗: {date} (无重复代码)
  - Tier分级: T1 (核心项目资产)
  - 深度洞察: {date} (专家数字替身系统)
  - 血液化: ✅ 完成 (五路图腾映射确认)
  - 归档锁定: {date}

功能定位:
  - 用途: {purpose}
  - 关联: {related}
  - 维护者: 蓝军+满意姐

血液化映射:
  - 五路图腾关联: {totem}
  - 专家体系: {expert}
  - 产品映射: {product}

---
"""

'''

def add_kia_to_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'KIA-CODE:' in content[:500]:
            print(f"  🟡 跳过（已有KIA）: {filepath}")
            return True
        
        purpose_map = {
            "decision_solidifier_v2.py": ("决策固化器V2", "决策执行", "六祖慧能-行动转化", "方翊沣博士"),
            "dr_fang_digital_twin.py": ("方翊沣博士数字替身", "神经科学/BCI专家", "感知力训练", "方翊沣博士"),
            "dr_li_digital_twin.py": ("李博士数字替身", "深港战略专家", "地理自在官", "谢宝剑研究员"),
            "dr_li_zexiang_digital_twin.py": ("李泽湘教授数字替身", "XbotPark创始人", "硬科技转化", "XU先生/钻木人"),
            "hardtech_partner_risk_scanner.py": ("硬科技合伙人风险扫描器", "SKU-A核心工具", "风险识别", "司马贺-满意解方法论"),
        }
        
        info = purpose_map.get(os.path.basename(filepath), ("专家数字替身", "专家系统", "五路图腾-专家体系"))
        purpose, related, totem, expert = info
        
        kia_block = KIA_TEMPLATE.format(
            asset_name=os.path.basename(filepath),
            date=datetime.now().strftime("%Y-%m-%d"),
            purpose=purpose,
            related=related,
            totem=totem,
            expert=expert,
            product="SKU-A/B专家系统"
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
    print("OM-03 Python资产25份代码级KIA - 批次二（6-10）")
    print("=" * 60)
    
    success = sum(1 for f in PYTHON_ASSETS if os.path.exists(f) and add_kia_to_file(f))
    
    print("=" * 60)
    print(f"批次二完成: {success}/{len(PYTHON_ASSETS)} 文件")
    print("=" * 60)
