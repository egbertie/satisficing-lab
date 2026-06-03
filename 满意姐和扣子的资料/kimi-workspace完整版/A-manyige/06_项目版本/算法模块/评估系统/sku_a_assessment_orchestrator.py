"""
---
KIA-CODE: 知识入库代码级闭环
Asset: sku_a_assessment_orchestrator.py
Status: ✅ 代码级KIA完成
Date: 2026-04-15
Batch: OM-03 Python资产25份代码级KIA-批次五

KIA-Loop:
  - 接收清点: 2026-04-15
  - 轻量提取: 2026-04-15 (代码结构识别)
  - 查重去冗: 2026-04-15 (无重复代码)
  - Tier分级: T1 (核心项目资产)
  - 深度洞察: 2026-04-15 (伦理与跨文化系统)
  - 血液化: ✅ 完成 (五路图腾映射确认)
  - 归档锁定: 2026-04-15

功能定位:
  - 用途: SKU-A评估编排器
  - 关联: 标准化产品
  - 维护者: 蓝军+满意姐

血液化映射:
  - 五路图腾关联: SKU-A交付编排
  - 产品映射: 司马贺-标准化流程
  - 运营映射: 伦理与跨文化评估

---
"""

#!/usr/bin/env python3
"""
sku_a_assessment_orchestrator.py
SKU-A 轻咨询评估编排器 V1.0

功能:
- 串行调用现有合伙人匹配评估资产
- 统一输出结构化 JSON + Markdown 报告
- 结果持久化到 SQLite
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

import sys
sys.path.insert(0, "/root/.openclaw/workspace")

from hardtech_partner_conflict_window import HardtechPartnerConflictWindow
from hardtech_partner_risk_scanner import HardtechPartnerRiskScanner
from hardtech_partner_selection_casebook import HardtechPartnerSelectionCasebook
from perceptual_decision_knowledge_graph import PerceptualDecisionKnowledgeGraph
import partner_matching_db as db


class SkuAAssessmentOrchestrator:
    """
    SKU-A 评估编排器。
    输入: 企业基本信息 + 合伙人信号数据
    输出: 综合评估报告（JSON + Markdown）
    """

    def __init__(self):
        self.conflict = HardtechPartnerConflictWindow()
        self.casebook = HardtechPartnerSelectionCasebook()
        self.kg = PerceptualDecisionKnowledgeGraph()

    def run(self, payload: Dict[str, Any], duration_seconds: Optional[float] = None) -> Dict[str, Any]:
        """
        payload 字段:
        - company_name: str
        - founded_months: int
        - tech_founder_stake: float (0-1)
        - has_veto: bool
        - resource_milestones: List[Dict] （可选）
        - has_exit_agreement: bool （可选）
        - has_stop_loss: bool （可选）
        - has_stage_vesting: bool （可选）
        - vesting_stages: List[str] （可选）
        - tech_route_disputes_monthly: float （可选）
        - communication_frequency_weekly: float （可选）
        - equity_change_count: int （可选）
        - funding_deviation_rate: float （可选）
        - mentor_involved: bool （可选）
        - stage: str （创业阶段，可选，默认"种子期"）
        - actions_done: List[str] （可选）
        - pattern_flags: Dict[str, bool] （可选，用于 casebook pattern_scan）
        """
        company_name = payload.get("company_name", "未命名企业")
        founded_months = payload.get("founded_months", 0)

        # 1. 冲突窗口评估
        conflict_result = self.conflict.assess(
            company_name=company_name,
            founded_months=founded_months,
            tech_route_disputes_monthly=payload.get("tech_route_disputes_monthly", 0.0),
            communication_frequency_weekly=payload.get("communication_frequency_weekly", 3.0),
            equity_change_count=payload.get("equity_change_count", 0),
            funding_deviation_rate=payload.get("funding_deviation_rate", 0.0),
            mentor_involved=payload.get("mentor_involved", False),
        )
        conflict_export = self.conflict.export_checklist(conflict_result)

        # 2. 风险扫描
        scanner = HardtechPartnerRiskScanner(startup_name=company_name)
        risk_result = scanner.full_scan(
            tech_founder_stake=payload.get("tech_founder_stake", 0.4),
            has_veto=payload.get("has_veto", False),
            resource_milestones=payload.get("resource_milestones", []),
            has_exit_agreement=payload.get("has_exit_agreement", False),
            has_stop_loss=payload.get("has_stop_loss", False),
            has_stage_vesting=payload.get("has_stage_vesting", False),
            stages=payload.get("vesting_stages", []),
        )

        # 3. 案例库模式扫描
        stage = payload.get("stage", "种子期")
        actions_done = payload.get("actions_done", ["能力评估"])
        pattern_flags = payload.get("pattern_flags", {
            "has_tech_biz_complement": True,
            "value_aligned": True,
            "shared_stress_test": False,
            "dynamic_equity": True,
            "transparent_comm": True,
            "equity_imbalanced": False,
            "capability_overlap": False,
            "founder_dependent": False,
        })
        stage_check = self.casebook.check_stage(stage, actions_done)
        pattern_scan = self.casebook.pattern_scan(**pattern_flags)

        # 4. 感知力决策建议（从知识图谱提取 VP 层建议）
        vp_advice = self.kg.query("商业实战层", "决策陪跑服务")

        # 综合评分逻辑
        conflict_score = self._risk_to_score(conflict_export["overall_risk"])
        risk_score = self._risk_level_to_score(risk_result["总体风险等级"])
        pattern_score = pattern_scan["综合评分"]
        overall_score = int((conflict_score + risk_score + pattern_score) / 3)

        # 综合风险标签
        overall_risk = self._score_to_risk(overall_score)

        dimensions = [
            {
                "name": "合伙人冲突窗口",
                "value": conflict_export["overall_risk"],
                "detail": conflict_export,
            },
            {
                "name": "硬科技合伙人风险扫描",
                "value": risk_result["总体风险等级"],
                "detail": risk_result["分项结果"],
            },
            {
                "name": "阶段评估",
                "value": stage,
                "detail": stage_check,
            },
            {
                "name": "成功/失败模式扫描",
                "value": pattern_scan["综合评分"],
                "detail": pattern_scan,
            },
        ]

        raw_json = {
            "company_name": company_name,
            "founded_months": founded_months,
            "sku_type": "SKU-A",
            "overall_score": overall_score,
            "overall_risk": overall_risk,
            "conflict_window": conflict_export,
            "risk_scan": risk_result,
            "casebook": {"stage_check": stage_check, "pattern_scan": pattern_scan},
            "vp_advice": vp_advice,
        }

        # 生成 Markdown 报告
        md_path = self._generate_markdown_report(company_name, raw_json)

        # 保存数据库
        assessment_id = db.save_assessment(
            sku_type="SKU-A",
            company_name=company_name,
            overall_risk=overall_risk,
            overall_score=overall_score,
            dimensions=dimensions,
            raw_json=raw_json,
            markdown_report_path=str(md_path),
            duration_seconds=duration_seconds,
        )

        return {
            "assessment_id": assessment_id,
            "company_name": company_name,
            "sku_type": "SKU-A",
            "overall_score": overall_score,
            "overall_risk": overall_risk,
            "dimensions": dimensions,
            "markdown_report_path": str(md_path),
        }

    @staticmethod
    def _risk_to_score(risk_label: str) -> int:
        mapping = {"绿色": 85, "黄色": 60, "红色": 30}
        return mapping.get(risk_label, 50)

    @staticmethod
    def _risk_level_to_score(level: str) -> int:
        mapping = {"低": 85, "中": 60, "高": 40, "极高": 20}
        return mapping.get(level, 50)

    @staticmethod
    def _score_to_risk(score: int) -> str:
        if score >= 75:
            return "低风险"
        elif score >= 50:
            return "中风险"
        return "高风险"

    def _generate_markdown_report(self, company_name: str, raw_json: Dict[str, Any]) -> Path:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M")
        conflict = raw_json["conflict_window"]
        risk = raw_json["risk_scan"]
        casebook = raw_json["casebook"]
        lines = [
            f"# SKU-A 合伙人匹配诊断报告 — {company_name}",
            f"**评估时间**: {ts}",
            f"**评估类型**: SKU-A 轻咨询",
            f"**综合评分**: {raw_json['overall_score']} / 100",
            f"**综合风险**: {raw_json['overall_risk']}",
            "",
            "## 一、合伙人冲突窗口评估",
            f"- 当前阶段: {conflict['stage']}（成立 {conflict['founded_months']} 个月）",
            f"- 总体风险: {conflict['overall_risk']}",
            f"- 紧迫度: {conflict['urgency']}",
            "",
            "### 早期预警信号",
            "| 指标 | 数值 | 等级 |",
            "|------|------|------|",
        ]
        for s in conflict["signals"]:
            lines.append(f"| {s['metric']} | {s['value']}{s['unit']} | {s['level']} |")
        lines.extend([
            "",
            "### 建议行动",
        ])
        for action in conflict["actions"]:
            lines.append(f"- {action}")

        lines.extend([
            "",
            "## 二、硬科技合伙人风险扫描",
            f"- **总体风险等级**: {risk['总体风险等级']}",
            "",
            "### 分项结果",
        ])
        for key, detail in risk["分项结果"].items():
            lines.append(f"#### {key}")
            lines.append(f"- 风险等级: {detail['风险等级']}")
            if detail.get("问题清单"):
                lines.append("- 问题清单:")
                for issue in detail["问题清单"]:
                    lines.append(f"  - {issue}")
            lines.append("")

        lines.extend([
            "## 三、合伙人选择模式匹配",
            f"- 综合模式评分: {casebook['pattern_scan']['综合评分']} / 100",
            f"- 建议: {casebook['pattern_scan']['建议']}",
            "",
            "### 匹配成功模式",
        ])
        for p in casebook["pattern_scan"]["匹配成功模式"]:
            lines.append(f"- ✅ {p}")
        lines.append("### 命中失败模式")
        for p in casebook["pattern_scan"]["命中失败模式"]:
            lines.append(f"- ⚠️ {p}")

        lines.extend([
            "",
            "## 四、核心建议（基于满意解方法论）",
            "1. 在投入重资产前，用最小成本验证合伙人匹配假设。",
            "2. 若总体风险高于'中风险'，建议优先进行 72 小时压力测试。",
            "3. 技术创始人持股比例与 vesting 机制是硬科技合伙关系的第一道防火墙。",
        ])

        report_path = Path("/root/.openclaw/workspace/memory") / f"sku_a_report_{company_name}_{datetime.now().strftime('%Y%m%d-%H%M')}.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return report_path


def main():
    """命令行示例 + daily runner 入口。"""
    demo_payload = {
        "company_name": "Demo硬科技",
        "founded_months": 14,
        "tech_founder_stake": 0.45,
        "has_veto": False,
        "resource_milestones": [],
        "has_exit_agreement": False,
        "has_stop_loss": False,
        "has_stage_vesting": True,
        "vesting_stages": ["实验室", "工程化", "商业化"],
        "tech_route_disputes_monthly": 1.2,
        "communication_frequency_weekly": 2.0,
        "equity_change_count": 1,
        "funding_deviation_rate": 0.18,
        "mentor_involved": False,
        "stage": "种子期",
        "actions_done": ["能力评估", "价值观测试"],
        "pattern_flags": {
            "has_tech_biz_complement": True,
            "value_aligned": True,
            "shared_stress_test": False,
            "dynamic_equity": True,
            "transparent_comm": True,
            "equity_imbalanced": False,
            "capability_overlap": False,
            "founder_dependent": False,
        },
    }
    orch = SkuAAssessmentOrchestrator()
    result = orch.run(demo_payload)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
