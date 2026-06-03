#!/usr/bin/env python3
"""
hardtech_equity_dispute_casebook.py
硬科技股权纠纷案例库 V1.0
基于《08硬科股权与创始人画像》

功能:
- 硬科技创业经典股权纠纷案例解析（比特大陆、寒武纪、地平线等）
- Good Leaver / Bad Leaver 条款范本
- 合伙人贡献值量化评分卡
- 生成股权设计建议报告
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

from defense_base_components import BaseComponent


class HardtechEquityDisputeCasebook(BaseComponent):
    """硬科技股权纠纷案例库"""

    CASES = {
        "比特大陆_吴忌寒vs詹克团": {
            "时间": "2019-2021",
            "冲突根源": "AB股设计缺陷+控制权争夺",
            "关键节点": "詹克团离司、吴忌寒更换法人、工商攻防战、AI芯片分拆",
            "最终结局": "和解，比特大陆分拆为两家独立公司",
            "治理教训": "AB股需设置日落条款，创始人离婚/失能需有预案",
        },
        "寒武纪_陈天石vs陈云霁": {
            "时间": "2018-2020",
            "冲突根源": "兄弟分家+技术股权分配争议",
            "关键节点": "陈云霁淡出管理、寒武纪IPO前股权清理",
            "最终结局": "陈天石主导上市，陈云霁保留少量股份",
            "治理教训": "亲属合伙需提前明确角色边界和退出机制",
        },
        "地平线_余凯团队": {
            "时间": "2015-至今",
            "冲突根源": "早期合伙人变动与股权稀释",
            "关键节点": "采用A类股10倍投票权保证余凯控制权56%",
            "最终结局": "余凯维持稳定控制，团队基本稳定",
            "治理教训": "通过双层股权结构防止稀释失控",
        },
    }

    GL_BL_TEMPLATE = {
        "Good_Leaver": {
            "定义": "因残疾/重病、协商解除、公司无故解雇、降薪>20%被迫离职",
            "处理": [
                "保留已归属全部股权",
                "未归属股权按净资产或最近融资估值的80%回购",
                "回购款分12个月支付",
            ],
        },
        "Bad_Leaver": {
            "定义": "主动辞职（未经同意）、严重违纪/欺诈/挪用资金/泄露商业秘密/违反竞业",
            "处理": [
                "公司以原始出资额（或象征性1元）回购全部股权",
                "未归属股权自动无偿收回",
                "造成损失的，公司有权追偿",
            ],
        },
    }

    CONTRIBUTION_WEIGHTS = {
        "资金投入": 0.20,
        "时间投入（月）": 0.20,
        "技术/专利价值": 0.20,
        "行业经验": 0.15,
        "资源网络": 0.15,
        "全职承诺": 0.10,
    }

    def __init__(self, startup_name: str = ""):
        super().__init__("hardtech_equity_dispute_casebook")
        self.startup_name = startup_name

    def get_lessons(self, case_name: str = None) -> Dict[str, Any]:
        if case_name:
            return {case_name: self.CASES.get(case_name, {"错误": "未找到该案例"})}
        return self.CASES

    def calculate_equity(self, contributions: Dict[str, Dict[str, float]]) -> Dict[str, Any]:
        """contributions: {合伙人A: {资金投入: x, 时间投入: y, ...}}"""
        totals = {}
        for partner, scores in contributions.items():
            total = sum(scores.get(k, 0) * w for k, w in self.CONTRIBUTION_WEIGHTS.items())
            totals[partner] = total
        total_sum = sum(totals.values())
        if total_sum == 0:
            return {"错误": "总分为0，无法计算股权比例"}
        equity = {k: round(v / total_sum, 3) for k, v in totals.items()}
        return {
            "加权总分": totals,
            "建议股权比例": equity,
        }

    def generate_report(self, contributions: Dict[str, Dict[str, float]] = None) -> str:
        lines = [
            f"# 硬科技股权纠纷案例库报告 — {self.startup_name or '未命名企业'}",
            f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
            "## 经典案例与教训",
            "```json",
            json.dumps(self.CASES, ensure_ascii=False, indent=2),
            "```",
            "",
            "## Good Leaver / Bad Leaver 条款范本",
            "```json",
            json.dumps(self.GL_BL_TEMPLATE, ensure_ascii=False, indent=2),
            "```",
        ]
        if contributions:
            equity = self.calculate_equity(contributions)
            lines.extend([
                "",
                "## 合伙人贡献值与股权比例",
                "```json",
                json.dumps(equity, ensure_ascii=False, indent=2),
                "```",
            ])
        report_path = Path(self.workspace) / "memory" / f"equity-casebook-{self.startup_name or 'draft'}-{datetime.now().strftime('%Y%m%d-%H%M')}.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return str(report_path)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="硬科技股权纠纷案例库")
    parser.add_argument("--startup", default="", help="企业名称")
    parser.add_argument("--report", action="store_true", help="生成案例库报告")
    args = parser.parse_args()

    casebook = HardtechEquityDisputeCasebook(startup_name=args.startup)
    contrib = {
        "合伙人A": {"资金投入": 80, "时间投入（月）": 90, "技术/专利价值": 95, "行业经验": 70, "资源网络": 60, "全职承诺": 100},
        "合伙人B": {"资金投入": 60, "时间投入（月）": 85, "技术/专利价值": 40, "行业经验": 80, "资源网络": 90, "全职承诺": 100},
    }
    path = casebook.generate_report(contributions=contrib)
    print(f"股权纠纷案例库报告已生成: {path}")


if __name__ == "__main__":
    main()
