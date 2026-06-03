"""
---
KIA-CODE: 知识入库代码级闭环
Asset: hardtech_investment_policy_scanner.py
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
  - 用途: 硬科技投资政策扫描器
  - 关联: 政策情报
  - 维护者: 蓝军+满意姐

血液化映射:
  - 五路图腾关联: 政府关系
  - 产品映射: 观自在-外部扫描
  - 运营映射: 伦理与跨文化评估

---
"""

#!/usr/bin/env python3
"""
hardtech_investment_policy_scanner.py
硬科技投资趋势与政策环境扫描器 V1.0
基于《25硬科技早期投资趋势与政策环境研究报告_2025-2026》

功能:
- 硬科技投资政策要点扫描（国家创投引导基金、区域基金、子基金）
- 投资机构类型匹配（国资/民营/外资/产业CVC）
- 融资阶段与基金适配建议
- 生成政策环境扫描报告
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

from defense_base_components import BaseComponent


class HardtechInvestmentPolicyScanner(BaseComponent):
    """硬科技投资趋势与政策环境扫描器"""

    POLICY_LANDSCAPE = {
        "国家创业投资引导基金": {
            "规模": "1000亿元",
            "架构": "基金公司—区域基金—子基金",
            "存续期": "20年（10年投资期+10年退出期）",
            "投向约束": "种子期、初创期不低于70%，标的估值≤5亿元，单笔≤5000万元",
            "撬动效应": "预计带动近1万亿社会资本",
        },
        "区域基金": {
            "京津冀": "296.46亿元",
            "长三角": "471亿元",
            "粤港澳大湾区": "450.5亿元",
        },
        "重点赛道": ["半导体", "人工智能", "生物医药", "新能源", "机器人", "低空经济"],
    }

    INVESTOR_TYPES = {
        "国资创投": {
            "优势": "资金规模大、政策背书、耐心资本",
            "劣势": "决策流程长、对估值敏感、治理要求多",
            "适配阶段": "B轮及以后/国家战略项目",
        },
        "民营市场化VC": {
            "优势": "决策灵活、行业专长、增值服务",
            "劣势": "存续期压力、对退出路径要求高",
            "适配阶段": "A-C轮",
        },
        "外资基金": {
            "优势": "全球化资源、估值体系成熟、品牌背书",
            "劣势": "地缘政治敏感、对赌/回购条款严格",
            "适配阶段": "成长期/出海企业",
        },
        "产业CVC": {
            "优势": "产业协同、应用场景、供应链资源",
            "劣势": "战略控制意图、排他性要求",
            "适配阶段": "技术验证后/产业化前期",
        },
    }

    def __init__(self, startup_name: str = ""):
        super().__init__("hardtech_investment_policy_scanner")
        self.startup_name = startup_name

    def match_investor(self, stage: str, track: str, need_gov_backing: bool) -> Dict[str, Any]:
        recs = []
        if stage in ["种子期", "天使轮"] and need_gov_backing:
            recs.append("国家创业投资引导基金子基金（符合估值≤5亿、单笔≤5000万约束）")
        if stage in ["A轮", "B轮"]:
            recs.extend(["民营市场化VC", "产业CVC"])
        if stage in ["B轮", "C轮", "成长期"]:
            recs.extend(["国资创投", "外资基金"])
        if track in self.POLICY_LANDSCAPE["重点赛道"]:
            recs.append(f"区域政策基金（长三角/大湾区优先，{track}为重点扶持方向）")
        return {
            "企业": self.startup_name or "未命名",
            "当前阶段": stage,
            "赛道": track,
            "建议对接机构类型": list(set(recs)),
        }

    def policy_checklist(self) -> List[str]:
        return [
            "确认企业是否属于六大重点赛道（半导体/AI/生物医药/新能源/机器人/低空经济）",
            "评估当前估值是否在国家引导基金单笔5000万/标的5亿的约束范围内",
            "梳理创始团队是否有高校/科研院所背景（政策基金偏好）",
            "准备至少3-5年的技术路线图和里程碑（匹配20年耐心资本）",
            "确认是否需要产业协同资源（如需要则优先CVC）",
        ]

    def generate_report(self, stage: str, track: str, need_gov_backing: bool = True) -> str:
        match = self.match_investor(stage, track, need_gov_backing)
        lines = [
            f"# 硬科技投资政策环境扫描报告 — {self.startup_name or '未命名企业'}",
            f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
            "## 政策环境概览",
            "```json",
            json.dumps(self.POLICY_LANDSCAPE, ensure_ascii=False, indent=2),
            "```",
            "",
            "## 投资机构匹配建议",
            "```json",
            json.dumps(match, ensure_ascii=False, indent=2),
            "```",
            "",
            "## 融资准备检查清单",
            "- " + "\n- ".join(self.policy_checklist()),
        ]
        report_path = Path(self.workspace) / "memory" / f"investment-policy-report-{self.startup_name or 'draft'}-{datetime.now().strftime('%Y%m%d-%H%M')}.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return str(report_path)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="硬科技投资趋势与政策环境扫描器")
    parser.add_argument("--startup", default="", help="企业名称")
    parser.add_argument("--stage", default="种子期", help="融资阶段")
    parser.add_argument("--track", default="半导体", help="赛道")
    parser.add_argument("--report", action="store_true", help="生成扫描报告")
    args = parser.parse_args()

    scanner = HardtechInvestmentPolicyScanner(startup_name=args.startup)
    path = scanner.generate_report(stage=args.stage, track=args.track)
    print(f"投资政策扫描报告已生成: {path}")


if __name__ == "__main__":
    main()
