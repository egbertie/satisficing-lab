#!/usr/bin/env python3
"""
xbotpark_synergy_evaluator.py
XbotPark 协同策略评估器 V1.0
基于《满意解研究所与李泽湘体系协同策略研究报告》

功能:
- 评估硬科技创业企业与 XbotPark 体系的协同匹配度
- 从地理位置、技术领域、发展阶段、合伙人需求四个维度打分
- 识别"后孵化缺口"（合伙人团队搭建、商业模式优化、战略决策）
- 生成协同策略建议报告
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

from defense_base_components import BaseComponent


class XbotParkSynergyEvaluator(BaseComponent):
    """XbotPark 协同策略评估器"""

    BASES = {
        "东莞松山湖": {"定位": "总部，综合硬件创业", "优势领域": ["机器人", "智能硬件", "消费电子"]},
        "深圳": {"定位": "AI硬件，快速转化", "优势领域": ["AI硬件", "电子产业链", "物联网"]},
        "宁波": {"定位": "工业互联网与智能制造", "优势领域": ["工业互联网", "智能制造", "制造业升级"]},
        "重庆明月湖": {"定位": "西部硬科技创新", "优势领域": ["汽车电子", "装备制造", "智慧城市"]},
        "香港": {"定位": "国际研发窗口", "优势领域": ["国际化", "前沿技术", "跨境合作"]},
    }

    POST_INCUBATION_GAPS = {
        "合伙人团队搭建": "满意解研究所核心切入领域",
        "商业模式优化": "需要战略导师深度介入",
        "战略决策支持": "涉及满意解评估与决策教练",
        "组织能力建设": "从创业团队到公司化的转型",
    }

    def __init__(self, company_name: str = ""):
        super().__init__("xbotpark_synergy_evaluator")
        self.company_name = company_name

    def evaluate_synergy(self, location: str, tech_field: str, stage: str, has_partner_gap: bool) -> Dict[str, Any]:
        best_base = None
        best_score = -1
        for base, info in self.BASES.items():
            score = 0
            if location in base or base in location:
                score += 3
            if any(field in tech_field for field in info["优势领域"]):
                score += 2
            if score > best_score:
                best_score = score
                best_base = base

        stage_fit = {
            "0→1 原型验证": {"匹配度": "极高", "说明": "XbotPark在0→1阶段服务最密集"},
            "1→10 产品量产": {"匹配度": "高", "说明": "共享工厂和供应链支持强大"},
            "10→100 规模化": {"匹配度": "中", "说明": "后孵化缺口明显，满意解可切入"},
            "100+ 成熟期": {"匹配度": "低", "说明": "体系服务密度下降"},
        }.get(stage, {"匹配度": "未知", "说明": ""})

        return {
            "企业名称": self.company_name or "未命名",
            "地理位置": location,
            "技术领域": tech_field,
            "发展阶段": stage,
            "最佳匹配基地": best_base,
            "阶段匹配度": stage_fit,
            "后孵化缺口": self.POST_INCUBATION_GAPS if stage in ["10→100 规模化", "100+ 成熟期"] or has_partner_gap else None,
            "优先合作建议": self._recommend(best_base, has_partner_gap),
        }

    def _recommend(self, best_base: str, has_partner_gap: bool) -> List[str]:
        recs = [f"优先对接 {best_base} 基地"]
        if has_partner_gap:
            recs.append("引入满意解研究所合伙人匹配服务（XbotPark后孵化缺口的精准补位）")
        recs.append("申请科创训练营或探索基金")
        return recs

    def generate_report(self, location: str, tech_field: str, stage: str, has_partner_gap: bool) -> str:
        result = self.evaluate_synergy(location, tech_field, stage, has_partner_gap)
        lines = [
            f"# XbotPark 协同策略评估报告 — {self.company_name or '未命名企业'}",
            f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
            "## 评估结果",
            "```json",
            json.dumps(result, ensure_ascii=False, indent=2),
            "```",
        ]
        report_path = Path(self.workspace) / "memory" / f"xbotpark-synergy-report-{datetime.now().strftime('%Y%m%d-%H%M')}.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return str(report_path)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="XbotPark 协同策略评估器")
    parser.add_argument("--company", default="", help="企业名称")
    parser.add_argument("--location", default="深圳", help="地理位置")
    parser.add_argument("--field", default="AI硬件", help="技术领域")
    parser.add_argument("--stage", default="1→10 产品量产", choices=["0→1 原型验证", "1→10 产品量产", "10→100 规模化", "100+ 成熟期"], help="发展阶段")
    parser.add_argument("--partner-gap", action="store_true", help="是否存在合伙人缺口")
    parser.add_argument("--report", action="store_true", help="生成评估报告")
    args = parser.parse_args()

    evaluator = XbotParkSynergyEvaluator(company_name=args.company)
    path = evaluator.generate_report(
        location=args.location,
        tech_field=args.field,
        stage=args.stage,
        has_partner_gap=args.partner_gap,
    )
    print(f"协同策略评估报告已生成: {path}")


if __name__ == "__main__":
    main()
