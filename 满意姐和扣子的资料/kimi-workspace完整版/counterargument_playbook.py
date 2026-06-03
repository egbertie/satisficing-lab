"""
---
KIA-CODE: 知识入库代码级闭环
Asset: counterargument_playbook.py
Status: ✅ 代码级KIA完成
Date: 2026-04-15
Batch: OM-03 Python资产25份代码级KIA-批次四

KIA-Loop:
  - 接收清点: 2026-04-15
  - 轻量提取: 2026-04-15 (代码结构识别)
  - 查重去冗: 2026-04-15 (无重复代码)
  - Tier分级: T1 (核心项目资产)
  - 深度洞察: 2026-04-15 (协作与认知系统)
  - 血液化: ✅ 完成 (五路图腾映射确认)
  - 归档锁定: 2026-04-15

功能定位:
  - 用途: 反方观点手册
  - 关联: 蓝军对抗验证
  - 维护者: 蓝军+满意姐

血液化映射:
  - 五路图腾关联: 批判性思维
  - 产品映射: 蓝军-Skeptor-7
  - 运营映射: 协作与认知优化

---
"""

#!/usr/bin/env python3
"""
counterargument_playbook.py
反方质疑应对手册 V1.0
基于《V0.9反方》

功能:
- 整理对"感知力决策"和"合伙人匹配服务"的常见质疑
- 提供结构化回应框架（承认/限定/转化/回击）
- 生成按场景分类的应对话术
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

from defense_base_components import BaseComponent


class CounterargumentPlaybook(BaseComponent):
    """反方质疑应对手册"""

    COUNTERARGUMENTS = {
        "科学性质疑": {
            "质疑": "感知力不就是玄学吗？有什么科学依据？",
            "回应框架": "承认+重新定义+证据",
            "回应话术": "这正是我们想澄清的。感知力不是玄学，而是具身认知和躯体标记假说的应用。Damasio的研究表明，VMF损伤患者因缺乏躯体标记而无法做出有利决策。我们的训练体系已将这一过程操作化。",
        },
        "效果质疑": {
            "质疑": "你们能保证我选对合伙人吗？",
            "回应框架": "限定+诚实+数据",
            "回应话术": "我们不能保证'绝对正确'，但可以将合伙人冲突导致创业失败的概率显著降低。Wasserman的研究显示65%的失败归因于创始人冲突，而我们的目标是通过系统评估将这个风险前置识别出来。",
        },
        "价格质疑": {
            "质疑": "你们的服务太贵了。",
            "回应框架": "转化+对比+算账",
            "回应话术": "我理解。但合伙人翻车的平均直接和间接成本，通常是服务费用的100倍以上。一次失败的股权纠纷，可能让公司停摆半年、估值腰斩，甚至直接解体。这不是支出，是风险对冲。",
        },
        "可替代性质疑": {
            "质疑": "我自己也能判断，为什么要找你们？",
            "回应框架": "承认+盲区+协同",
            "回应话术": "您当然能判断。但我们最难识别的，往往是自己的认知盲区。双系统决策的价值在于：AI不替代人，而是帮人看见自己看不到的东西。",
        },
        "样本质疑": {
            "质疑": "你们才做了多少案例，有什么经验？",
            "回应框架": "诚实+方法论+长期",
            "回应话术": "我们目前处于方法论的验证和 refinement 阶段。但支撑这套方法的基础——满意解理论、躯体标记假说、五路图腾框架——都有深厚的学术和实践根基。我们更在意的是长期正确，而非短期规模。",
        },
    }

    def __init__(self):
        super().__init__("counterargument_playbook")

    def query(self, category: str) -> Dict[str, Any]:
        return self.COUNTERARGUMENTS.get(category, {"错误": "未找到该类质疑"})

    def generate_report(self) -> str:
        lines = [
            "# 反方质疑应对手册",
            f"**版本**: V0.9 | **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
        ]
        for category, content in self.COUNTERARGUMENTS.items():
            lines.append(f"## {category}")
            lines.append(f"**质疑**：{content['质疑']}")
            lines.append(f"**回应框架**：{content['回应框架']}")
            lines.append(f"**回应话术**：{content['回应话术']}")
            lines.append("")
        report_path = Path(self.workspace) / "memory" / f"counterargument-playbook-{datetime.now().strftime('%Y%m%d-%H%M')}.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return str(report_path)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="反方质疑应对手册")
    parser.add_argument("--report", action="store_true", help="生成应对手册")
    args = parser.parse_args()

    playbook = CounterargumentPlaybook()
    path = playbook.generate_report()
    print(f"反方质疑应对手册已生成: {path}")


if __name__ == "__main__":
    main()
