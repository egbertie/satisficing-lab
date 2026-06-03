#!/usr/bin/env python3
"""
xbotpark_human_factors_analyzer.py
李泽湘硬科技孵化体系人因素分析器 V1.0
基于《30李泽湘硬科技孵化体系的人因素研究》

功能:
- 评估硬科技创业者的"三力"模型（技术力/商业力/心力）
- 追踪ECBM躯体信号识别训练进度
- 合伙人匹配成功模式 vs 失败模式的风险扫描
- 生成人因素评估报告
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

from defense_base_components import BaseComponent


class XbotParkHumanFactorsAnalyzer(BaseComponent):
    """李泽湘硬科技孵化体系人因素分析器"""

    def __init__(self, founder_name: str = ""):
        super().__init__("xbotpark_human_factors_analyzer")
        self.founder_name = founder_name

    def three_forces_assessment(self, tech_score: float, business_score: float, heart_score: float) -> Dict[str, Any]:
        """三力模型评估：技术力、商业力、心力"""
        avg = (tech_score + business_score + heart_score) / 3
        gaps = []
        if tech_score < 60:
            gaps.append("技术力不足，需加强产品化能力或引入技术合伙人")
        if business_score < 60:
            gaps.append("商业力不足，需强化市场洞察与融资叙事能力")
        if heart_score < 60:
            gaps.append("心力不足，需提升压力韧性与团队领导力")

        success_patterns = []
        if tech_score >= 75 and business_score >= 70:
            success_patterns.append("技术-商业互补型（高成功概率）")
        if heart_score >= 75:
            success_patterns.append("高韧心性（抗压能力强）")
        if abs(tech_score - business_score) <= 15 and heart_score >= 65:
            success_patterns.append("平衡型团队领袖（合伙人冲突风险低）")

        return {
            "创始人": self.founder_name or "未命名",
            "技术力": tech_score,
            "商业力": business_score,
            "心力": heart_score,
            "三力平均分": round(avg, 2),
            "能力缺口": gaps,
            "成功模式匹配": success_patterns,
        }

    def partner_match_risk(self, tech_gap: bool, business_gap: bool, value_misalign: bool,
                           equity_unequal: bool, communication_poor: bool) -> Dict[str, Any]:
        """合伙人匹配失败模式风险扫描"""
        risks = []
        if tech_gap and business_gap:
            risks.append("双能力缺口：创始人自身技术力与商业力均不足，合伙人选择压力极大")
        if value_misalign:
            risks.append("价值观错位是硬科技合伙人分手的首要原因")
        if equity_unequal:
            risks.append("股权结构失衡预示控制权争夺风险")
        if communication_poor:
            risks.append("沟通机制缺失将导致冲突升级窗口期缩短")

        level = "低"
        if len(risks) >= 3:
            level = "极高"
        elif len(risks) >= 2:
            level = "高"
        elif len(risks) >= 1:
            level = "中"

        return {
            "风险等级": level,
            "风险项": risks,
            "建议": "建议在签约前引入第三方合伙人匹配评估" if level in ["高", "极高"] else "维持现有合伙人关系管理机制",
        }

    def generate_report(self, tech_score: float, business_score: float, heart_score: float,
                        tech_gap: bool = False, business_gap: bool = False,
                        value_misalign: bool = False, equity_unequal: bool = False,
                        communication_poor: bool = False) -> str:
        three_forces = self.three_forces_assessment(tech_score, business_score, heart_score)
        partner_risk = self.partner_match_risk(tech_gap, business_gap, value_misalign,
                                               equity_unequal, communication_poor)
        lines = [
            f"# 李泽湘体系人因素分析报告 — {self.founder_name or '未命名创始人'}",
            f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
            "## 三力模型评估",
            "```json",
            json.dumps(three_forces, ensure_ascii=False, indent=2),
            "```",
            "",
            "## 合伙人匹配风险",
            "```json",
            json.dumps(partner_risk, ensure_ascii=False, indent=2),
            "```",
        ]
        report_path = Path(self.workspace) / "memory" / f"xbotpark-human-factors-{self.founder_name or 'draft'}-{datetime.now().strftime('%Y%m%d-%H%M')}.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return str(report_path)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="李泽湘体系人因素分析器")
    parser.add_argument("--founder", default="", help="创始人姓名")
    parser.add_argument("--tech", type=float, default=70.0, help="技术力得分")
    parser.add_argument("--business", type=float, default=55.0, help="商业力得分")
    parser.add_argument("--heart", type=float, default=75.0, help="心力得分")
    parser.add_argument("--report", action="store_true", help="生成分析报告")
    args = parser.parse_args()

    analyzer = XbotParkHumanFactorsAnalyzer(founder_name=args.founder)
    path = analyzer.generate_report(
        tech_score=args.tech,
        business_score=args.business,
        heart_score=args.heart,
        tech_gap=args.tech < 60,
        business_gap=args.business < 60,
        value_misalign=False,
        equity_unequal=False,
        communication_poor=False,
    )
    print(f"人因素分析报告已生成: {path}")


if __name__ == "__main__":
    main()
