#!/usr/bin/env python3
"""
legal_as_code.py - 法律合伙人条款代码化（B5）
来源: 系统深度优化方案.docx - 第十一轮
功能: Good Leaver / Bad Leaver 条款自动生成器
"""
from typing import Dict, List
from dataclasses import dataclass
import sys


@dataclass
class TermClause:
    clause_type: str
    title: str
    content: str
    enforceability_score: float  # 0-1


class LegalAsCodeEngine:
    """
    B5实现：将法律条款转化为可配置、可验证的代码
    核心功能：根据合伙人画像自动生成退出条款草案
    """

    def __init__(self):
        self.templates = {
            "good_leaver": {
                "trigger_events": ["身故", "永久丧失行为能力", "被迫离职（无过错）", "退休"],
                "treatment": "已归属股权100%保留，未归属股权按时间比例加速归属",
                "non_compete": "12个月，标准补偿",
                "info_rights": "保留知情权至出售完成"
            },
            "bad_leaver": {
                "trigger_events": ["欺诈", "挪用资金", "严重违反竞业限制", "刑事犯罪", "重大过失"],
                "treatment": "已归属股权按公允价值50%回购，未归属股权全部取消",
                "non_compete": "24个月，无补偿",
                "info_rights": "立即终止"
            }
        }

    def generate_exit_clauses(self, company_valuation: float, partner_contribution: float,
                               partner_equity_pct: float, scenarios: List[str]) -> Dict:
        clauses = []
        for scenario in scenarios:
            template = self.templates.get(scenario)
            if not template:
                continue
            equity_value = company_valuation * (partner_equity_pct / 100)
            if scenario == "good_leaver":
                content = (
                    f"1. 触发条件：{', '.join(template['trigger_events'])}\n"
                    f"2. 股权处理：{template['treatment']}，预估总价值约{equity_value:,.0f}元\n"
                    f"3. 竞业限制：{template['non_compete']}\n"
                    f"4. 信息权利：{template['info_rights']}"
                )
                clauses.append(TermClause(scenario, "Good Leaver 条款", content, 0.92))
            elif scenario == "bad_leaver":
                recovery_value = equity_value * 0.5
                content = (
                    f"1. 触发条件：{', '.join(template['trigger_events'])}\n"
                    f"2. 股权处理：{template['treatment']}，回购价值约{recovery_value:,.0f}元\n"
                    f"3. 竞业限制：{template['non_compete']}\n"
                    f"4. 信息权利：{template['info_rights']}"
                )
                clauses.append(TermClause(scenario, "Bad Leaver 条款", content, 0.88))
        return {
            "generated_clauses": [
                {"type": c.clause_type, "title": c.title, "content": c.content,
                 "enforceability_score": c.enforceability_score}
                for c in clauses
            ],
            "legal_review_required": True,
            "jurisdiction_notes": "本条款草案需经执业律师根据实际注册地法律修订"
        }

    def equity_split_calculator(self, total_equity_pct: float,
                                founder_premium: float,
                                vesting_years: int) -> Dict:
        partner_share = total_equity_pct * (1 - founder_premium)
        return {
            "founder_share_pct": round(total_equity_pct * founder_premium, 2),
            "partner_share_pct": round(partner_share, 2),
            "vesting_schedule": f"{vesting_years}年，每月归属1/{vesting_years*12}，1年cliff",
            "advice": "建议预留10-15%期权池用于后续人才激励"
        }


if __name__ == "__main__":
    lace = LegalAsCodeEngine()
    result = lace.generate_exit_clauses(
        company_valuation=50_000_000,
        partner_contribution=5_000_000,
        partner_equity_pct=15,
        scenarios=["good_leaver", "bad_leaver"]
    )
    assert len(result["generated_clauses"]) == 2, "应生成两条条款"
    for c in result["generated_clauses"]:
        print(f"✓ {c['title']} (可执行性评分: {c['enforceability_score']})")
    split = lace.equity_split_calculator(40, 0.6, 4)
    assert split["founder_share_pct"] + split["partner_share_pct"] == 40
    print(f"✓ 股权设计: 创始人{split['founder_share_pct']}% / 合伙人{split['partner_share_pct']}%")
    print("\n✓ 法律代码化引擎验证通过")
    sys.exit(0)
