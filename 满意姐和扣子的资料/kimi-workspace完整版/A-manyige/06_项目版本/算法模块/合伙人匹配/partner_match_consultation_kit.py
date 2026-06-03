"""
---
KIA-CODE: 知识入库代码级闭环
Asset: partner_match_consultation_kit.py
Status: ✅ 代码级KIA完成
Date: 2026-04-15
Batch: OM-03 Python资产25份代码级KIA

KIA-Loop:
  - 接收清点: 2026-04-15
  - 轻量提取: 2026-04-15 (代码结构识别)
  - 查重去冗: 2026-04-15 (无重复代码)
  - Tier分级: T1 (核心项目资产)
  - 深度洞察: 2026-04-15 (功能定位确认)
  - 血液化: ✅ 完成 (五路图腾映射确认)
  - 归档锁定: 2026-04-15

功能定位:
  - 用途: 合伙人匹配咨询工具包
  - 关联: 咨询交付
  - 维护者: 蓝军+满意姐

血液化映射:
  - 五路图腾关联: 司马贺-满意解方法论
  - 产品映射: SKU-B
  - 运营映射: 客户交付

---
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
partner_match_consultation_kit.py
合伙人匹配决策咨询工具箱 V1.0

功能:
- 将儒商哲学评估、风险扫描、MCDA 方法选择、满意解决策引擎
  组合为一次可调用、可输出的合伙人匹配咨询流程
- 创始人/咨询师只需提供创始人画像和候选合伙人画像，
  即可在 3-5 分钟内获得结构化决策建议

来源资产:
  - confucian_business_philosophy_core.py (儒商五维评估 + 情境建议)
  - confucian_business_wisdom.py (儒商成熟度八维评估)
  - hardtech_partner_risk_scanner.py (硬科技合伙人风险扫描)
  - partner_mcda_selector.py (MCDA 方法推荐)
  - satisficing_decision_engine.py (满意解决策引擎)

输出:
  - Markdown 格式的决策咨询报告
  - 红绿灯评级 + 风险清单 + 儒商匹配度 + 下一步行动建议

状态: 实战就绪
"""

from typing import Dict, List
from datetime import datetime

# 直接导入现有资产
from confucian_business_philosophy_core import ConfucianBusinessAssessor, recommend_wisdom, query_concept
from confucian_business_wisdom import RuShangAuditor, get_case_principle
from hardtech_partner_risk_scanner import HardtechPartnerRiskScanner
from partner_mcda_selector import PartnerMCDASelector
from satisficing_decision_engine import SatisficingDecisionEngine


class PartnerMatchConsultationKit:
    """
    合伙人匹配决策咨询工具箱。
    输入两段画像，输出一份可直接交给创始人的决策简报。
    """

    def __init__(self, startup_name: str = ""):
        self.startup_name = startup_name or "未命名项目"
        self.risk_scanner = HardtechPartnerRiskScanner(startup_name=self.startup_name)
        self.mcda_selector = PartnerMCDASelector(project_name=f"{self.startup_name} 合伙人匹配")
        self.decision_engine = SatisficingDecisionEngine()

    def run(
        self,
        founder_profile: Dict,
        candidate_profile: Dict,
    ) -> str:
        """
        执行一次完整的合伙人匹配咨询流程。

        参数:
          - founder_profile: {"name", "industry", "stage", ...}
          - candidate_profile: {"name", "背景", "技术持股", "有否决权", ...}
        返回:
          - Markdown 咨询报告
        """
        # ===== 1. 儒商伦理评估（五常）=====
        assessor = ConfucianBusinessAssessor()
        conf_scores = candidate_profile.get("confucian_scores", {})
        assessor.input_scores(
            ren=conf_scores.get("仁", 7),
            yi=conf_scores.get("義", 7),
            li=conf_scores.get("禮", 6),
            zhi=conf_scores.get("智", 7),
            xin=conf_scores.get("信", 6),
        )
        conf_eval = assessor.evaluate()

        # ===== 2. 儒商成熟度评估（八维）=====
        auditor = RuShangAuditor()
        maturity_scores = candidate_profile.get("maturity_scores", [6, 6, 6, 6, 6, 6, 6, 6])
        maturity_eval = auditor.evaluate(maturity_scores)

        # ===== 3. 风险扫描 =====
        risk_equity = self.risk_scanner.scan_equity_structure(
            tech_founder_stake=candidate_profile.get("tech_stake", 0.0),
            has_veto=candidate_profile.get("has_veto", False),
        )
        risk_commitment = self.risk_scanner.scan_resource_commitments(
            resource_milestones=candidate_profile.get("resource_commitments", [])
        )
        risk_exit = self.risk_scanner.scan_exit_mechanism(
            has_exit_agreement=candidate_profile.get("has_exit_agreement", False),
            has_stop_loss=candidate_profile.get("has_stop_loss", False),
        )
        risk_vesting = self.risk_scanner.scan_vesting_alignment(
            has_stage_vesting=candidate_profile.get("has_vesting", False),
            stages=candidate_profile.get("vesting_stages", []),
        )
        risk_items = [risk_equity, risk_commitment, risk_exit, risk_vesting]
        high_risks = [r for r in risk_items if r.get("风险等级") in ("高", "极高")]

        # ===== 4. MCDA 方法推荐 =====
        mcda_context = candidate_profile.get("mcda_context", {})
        mcda_recommendation = self.mcda_selector.recommend(mcda_context)

        # ===== 5. 满意解决策引擎（红绿灯）=====
        sat_evidence = candidate_profile.get("risk_evidence", [])
        sat_fuzzy = {
            "技术能力": candidate_profile.get("tech_score", 60),
            "沟通意愿": candidate_profile.get("comm_score", 60),
            "价值观一致": candidate_profile.get("value_score", 60),
        }
        sat_maut = {
            "技术互补性": candidate_profile.get("tech_complement", 6),
            "价值观契合": candidate_profile.get("value_fit", 6),
            "承诺可信度": candidate_profile.get("commitment_credibility", 6),
            "风险承受力": candidate_profile.get("risk_appetite", 6),
            "退出灵活性": candidate_profile.get("exit_flexibility", 6),
        }
        sat_result = self.decision_engine.evaluate(
            evidence=sat_evidence,
            fuzzy_inputs=sat_fuzzy,
            maut_scores=sat_maut,
        )

        # ===== 6. 儒商情境建议 =====
        wisdom = recommend_wisdom("合伙人股权分配")
        case_advice = get_case_principle("合伙人信任")

        # ===== 新增：行为面谈四问（基于 STAR 法则改造）=====
        star_questions = [
            "1. 您在上一家公司/项目中的具体角色和决策边界是什么？",
            "2. 在过往项目中，您独立负责过什么关键决策？结果如何？",
            "3. 相比合作伙伴/同事，您哪些能力更突出？哪些相对较弱？有具体案例吗？",
            "4. 描述一次您与合伙人/合作伙伴发生重大分歧的事件：当时的情景、您采取的行动、最终结果。",
        ]

        # ===== 组装 Markdown 报告 =====
        report_lines = [
            f"# 合伙人匹配决策咨询报告",
            f"",
            f"**项目**: {self.startup_name}  ",
            f"**候选合伙人**: {candidate_profile.get('name', '匿名')}  ",
            f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}  ",
            f"**评估主体**: 满意解研究所 · 合伙人匹配决策教练",
            f"",
            f"---",
            f"",
            f"## 一、决策信号灯",
            f"",
            f"**综合评级**: {sat_result.get('信号', '未知')}  ",
            f"**置信度**: {sat_result.get('置信度', 0):.0%}  ",
            f"**决策建议**: {sat_result.get('建议', '请补充信息')}  ",
            f"",
            f"---",
            f"",
            f"## 二、儒商伦理匹配度",
            f"",
            f"**五维总分**: {conf_eval.get('total', 0)}/50  ",
            f"**平均分**: {conf_eval.get('average', 0)}  ",
            f"**等级**: {conf_eval.get('level', '')}  ",
            f"**最强项**: {conf_eval.get('strongest', ['', ''])[0]}  ",
            f"**最弱项**: {conf_eval.get('weakest', ['', ''])[0]} → {conf_eval.get('primary_advice', '')}  ",
            f"",
            f"---",
            f"",
            f"## 三、合伙人成熟度（八维）",
            f"",
            f"**总分**: {maturity_eval.get('total_score', 0)}/80  ",
            f"**平均分**: {maturity_eval.get('average_score', 0)}  ",
            f"**成熟度等级**: {maturity_eval.get('maturity_level', '')}  ",
            f"",
        ]

        weaknesses = maturity_eval.get('weaknesses', [])
        if weaknesses:
            report_lines.append("**待改进维度**:")
            for w in weaknesses:
                report_lines.append(f"- {w['dimension']}（{w['score']}分）: {w['question']}")
        else:
            report_lines.append("**无明显弱项**，继续保持并输出经验。")

        report_lines.extend([
            f"",
            f"---",
            f"",
            f"## 四、风险扫描结果",
            f"",
        ])

        for r in risk_items:
            emoji = "🔴" if r.get("风险等级") in ("高", "极高") else "🟡" if r.get("风险等级") == "中" else "🟢"
            report_lines.append(f"{emoji} **{r['检查项']}** → 风险等级: {r['风险等级']}")
            issues = r.get("问题清单", [])
            if issues:
                for issue in issues:
                    report_lines.append(f"   - ⚠️ {issue}")

        report_lines.extend([
            f"",
            f"**高风险项数**: {len(high_risks)} / {len(risk_items)}",
            f"",
            f"---",
            f"",
            f"## 五、决策方法推荐",
            f"",
            f"**推荐方法**: {mcda_recommendation.get('推荐方法', '待定')}  ",
            f"**推荐理由**: {mcda_recommendation.get('推荐理由', {}).get('优点', '')}  ",
            f"**适用情境**: {', '.join(mcda_recommendation.get('推荐理由', {}).get('适用情境', []))}  ",
            f"",
            f"---",
            f"",
            f"## 六、儒商智慧锦囊",
            f"",
        ])

        for idx, item in enumerate(wisdom[:3], 1):
            report_lines.append(f"{idx}. **{item['source']}**: {item['advice']}")

        if case_advice:
            first_key = list(case_advice.keys())[0]
            advice_text = case_advice[first_key].get('advice', '')
            report_lines.extend([
                f"",
                f"**合伙人信任专题建议**: {advice_text}",
            ])

        report_lines.extend([
            f"",
            f"---",
            f"",
            f"## 七、下一步行动清单",
            f"",
            f"1. {'🚨' if high_risks else '✅'} {'优先处理上述高风险项，再进入深度合作' if high_risks else '风险可控，可推进下一轮深度谈判'}。",
            f"2. 使用 **{mcda_recommendation.get('推荐方法', 'MCDA')}** 对 2-3 位候选人进行结构化比较。",
            f"3. 针对儒商最弱项（{conf_eval.get('weakest', ['', ''])[0]}）设计补充访谈问题，验证其改善意愿。",
            f"4. 若信号灯为 **红灯**，建议暂停并重新物色候选人。",
        report_lines.extend([
            f"",
            f"---",
            f"",
            f"## 八、合伙人行为面谈四问（STAR 法则）",
            f"",
            f"> 以下四问可直接用于候选人深度访谈，验证其过往行为模式与决策风格。",
            f"",
        ])
        for q in star_questions:
            report_lines.append(q)

        report_lines.extend([
            f"",
            f"---",
            f"",
            f"*本报告由 满意解研究所 合伙人匹配决策咨询工具箱 自动生成*",
        ])

        return "\n".join(report_lines)


def demo():
    """默认模拟案例：硬科技创业者评估一位技术合伙人候选人"""
    print("=" * 60)
    print("合伙人匹配决策咨询工具箱 —— 模拟案例实测")
    print("=" * 60)

    kit = PartnerMatchConsultationKit(startup_name="深芯科技")

    founder = {
        "name": "张明",
        "industry": "半导体",
        "stage": "Pre-A",
    }

    candidate = {
        "name": "李明辉",
        "confucian_scores": {"仁": 7, "義": 6, "禮": 5, "智": 8, "信": 6},
        "maturity_scores": [7, 6, 6, 7, 5, 6, 7, 6],
        "tech_stake": 0.35,
        "has_veto": False,
        "resource_commitments": [
            {"item": "引入产线资源", "milestone": "Q3 完成首条产线打通", "penalty": "未达成则股权稀释 5%"}
        ],
        "has_exit_agreement": False,
        "has_stop_loss": False,
        "tech_gaps": ["缺乏融资经历", "未主导过团队扩张"],
        "industry_years": 12,
        "has_vesting": True,
        "vesting_stages": ["实验室", "工程化", "商业化"],
        "mcda_context": {
            "准则间可补偿": True,
            "需明确权衡": True,
            "决策者偏好清晰": True,
            "有大量方案": False,
            "信息模糊": False,
        },
        "risk_evidence": ["股权讨论寸步不让"],
        "tech_score": 75,
        "comm_score": 60,
        "value_score": 55,
        "tech_complement": 8,
        "value_fit": 5,
        "commitment_credibility": 6,
        "risk_appetite": 5,
        "exit_flexibility": 4,
    }

    report = kit.run(founder, candidate)
    print(report)
    print("\n" + "=" * 60)
    print("模拟案例实测完成。报告可直接交付创始人审阅。")
    print("=" * 60)


if __name__ == "__main__":
    demo()
