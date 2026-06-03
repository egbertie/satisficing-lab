"""
---
KIA-CODE: 知识入库代码级闭环
Asset: hardtech_partner_risk_scanner.py
Status: ✅ 代码级KIA完成
Date: 2026-04-15
Batch: OM-03 Python资产25份代码级KIA-批次二

KIA-Loop:
  - 接收清点: 2026-04-15
  - 轻量提取: 2026-04-15 (代码结构识别)
  - 查重去冗: 2026-04-15 (无重复代码)
  - Tier分级: T1 (核心项目资产)
  - 深度洞察: 2026-04-15 (专家数字替身系统)
  - 血液化: ✅ 完成 (五路图腾映射确认)
  - 归档锁定: 2026-04-15

功能定位:
  - 用途: 硬科技合伙人风险扫描器
  - 关联: SKU-A核心工具
  - 维护者: 蓝军+满意姐

血液化映射:
  - 五路图腾关联: 风险识别
  - 专家体系: 司马贺-满意解方法论
  - 产品映射: SKU-A/B专家系统

---
"""

#!/usr/bin/env python3
"""
hardtech_partner_risk_scanner.py
硬科技合伙人风险扫描器 V1.0
基于《68硬科技合伙人案例》的5条避坑铁律

功能:
- 扫描合伙人股权结构、资源承诺、能力匹配、止损机制、Vesting条款
- 生成风险等级报告（低/中/高/极高）
- 输出针对性避坑建议
- Markdown 风险扫描报告生成
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

from defense_base_components import BaseComponent


class HardtechPartnerRiskScanner(BaseComponent):
    """硬科技合伙人风险扫描器"""

    def __init__(self, startup_name: str = ""):
        super().__init__("hardtech_partner_risk_scanner")
        self.startup_name = startup_name

    def scan_equity_structure(self, tech_founder_stake: float, has_veto: bool) -> Dict[str, Any]:
        risk_level = "低"
        issues = []
        if tech_founder_stake < 0.51:
            risk_level = "极高"
            issues.append("技术创始人持股低于51%，存在334股权陷阱风险")
        elif tech_founder_stake < 0.40:
            risk_level = "高"
            issues.append("技术创始人持股比例过低，控制权薄弱")
        if not has_veto:
            if risk_level == "低":
                risk_level = "中"
            issues.append("未设置技术路线一票否决权")
        return {
            "检查项": "股权结构与控制权",
            "风险等级": risk_level,
            "技术创始人持股": f"{tech_founder_stake*100:.1f}%",
            "技术否决权": "有" if has_veto else "无",
            "问题清单": issues,
        }

    def scan_resource_commitments(self, resource_milestones: List[Dict[str, Any]]) -> Dict[str, Any]:
        issues = []
        risk_level = "低"
        if not resource_milestones:
            risk_level = "高"
            issues.append("资源承诺未写入任何里程碑对赌条款")
        for rc in resource_milestones:
            if not rc.get("milestone"):
                issues.append(f"承诺'{rc.get('item')}'缺少明确的可验证里程碑")
            if not rc.get("penalty"):
                issues.append(f"承诺'{rc.get('item')}'缺少未兑现的惩罚机制")
        if issues and risk_level == "低":
            risk_level = "中"
        return {
            "检查项": "资源承诺与对赌",
            "风险等级": risk_level,
            "承诺数量": len(resource_milestones),
            "问题清单": issues,
        }

    def scan_exit_mechanism(self, has_exit_agreement: bool, has_stop_loss: bool) -> Dict[str, Any]:
        issues = []
        risk_level = "低"
        if not has_exit_agreement:
            risk_level = "高"
            issues.append("缺少预设的技术离婚协议（项目终止/股权回购机制）")
        if not has_stop_loss:
            risk_level = "极高" if risk_level == "高" else "高"
            issues.append("缺少明确的止损线共识")
        return {
            "检查项": "退出与止损机制",
            "风险等级": risk_level,
            "技术离婚协议": "有" if has_exit_agreement else "无",
            "止损线共识": "有" if has_stop_loss else "无",
            "问题清单": issues,
        }

    def scan_vesting_alignment(self, has_stage_vesting: bool, stages: List[str]) -> Dict[str, Any]:
        issues = []
        risk_level = "低"
        if not has_stage_vesting:
            risk_level = "高"
            issues.append("缺少按技术成熟阶段的能力补位Vesting机制")
        expected_stages = ["实验室", "工程化", "商业化"]
        missing = [s for s in expected_stages if s not in stages]
        if missing:
            if risk_level == "低":
                risk_level = "中"
            issues.append(f"Vesting阶段不完整，缺少: {', '.join(missing)}")
        return {
            "检查项": "Vesting与能力补位",
            "风险等级": risk_level,
            "阶段覆盖": stages,
            "问题清单": issues,
        }

    def full_scan(self, tech_founder_stake: float, has_veto: bool,
                  resource_milestones: List[Dict[str, Any]],
                  has_exit_agreement: bool, has_stop_loss: bool,
                  has_stage_vesting: bool, stages: List[str]) -> Dict[str, Any]:
        results = {
            "股权结构": self.scan_equity_structure(tech_founder_stake, has_veto),
            "资源承诺": self.scan_resource_commitments(resource_milestones),
            "退出机制": self.scan_exit_mechanism(has_exit_agreement, has_stop_loss),
            "Vesting机制": self.scan_vesting_alignment(has_stage_vesting, stages),
        }
        overall = max([r["风险等级"] for r in results.values()],
                       key=lambda x: {"低": 0, "中": 1, "高": 2, "极高": 3}.get(x, 0))
        return {
            "企业名称": self.startup_name or "未命名",
            "扫描时间": datetime.now().isoformat(),
            "总体风险等级": overall,
            "分项结果": results,
        }

    def generate_report(self, tech_founder_stake: float, has_veto: bool,
                        resource_milestones: List[Dict[str, Any]],
                        has_exit_agreement: bool, has_stop_loss: bool,
                        has_stage_vesting: bool, stages: List[str]) -> str:
        result = self.full_scan(tech_founder_stake, has_veto, resource_milestones,
                                has_exit_agreement, has_stop_loss, has_stage_vesting, stages)
        lines = [
            f"# 硬科技合伙人风险扫描报告 — {self.startup_name or '未命名企业'}",
            f"**扫描时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"**总体风险等级**: {result['总体风险等级']}",
            "",
            "## 分项扫描结果",
            "```json",
            json.dumps(result['分项结果'], ensure_ascii=False, indent=2),
            "```",
        ]
        report_path = Path(self.workspace) / "memory" / f"hardtech-partner-risk-{self.startup_name or 'draft'}-{datetime.now().strftime('%Y%m%d-%H%M')}.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return str(report_path)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="硬科技合伙人风险扫描器")
    parser.add_argument("--startup", default="", help="企业名称")
    parser.add_argument("--stake", type=float, default=0.4, help="技术创始人持股比例（0-1）")
    parser.add_argument("--veto", action="store_true", help="是否有技术路线一票否决权")
    parser.add_argument("--exit", action="store_true", help="是否有技术离婚协议")
    parser.add_argument("--stoploss", action="store_true", help="是否有止损线共识")
    parser.add_argument("--vesting", action="store_true", help="是否有阶段Vesting")
    parser.add_argument("--report", action="store_true", help="生成风险扫描报告")
    args = parser.parse_args()

    scanner = HardtechPartnerRiskScanner(startup_name=args.startup)
    path = scanner.generate_report(
        tech_founder_stake=args.stake,
        has_veto=args.veto,
        resource_milestones=[],
        has_exit_agreement=args.exit,
        has_stop_loss=args.stoploss,
        has_stage_vesting=args.vesting,
        stages=["实验室", "工程化", "商业化"] if args.vesting else [],
    )
    print(f"风险扫描报告已生成: {path}")


if __name__ == "__main__":
    main()
