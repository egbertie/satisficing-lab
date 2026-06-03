#!/usr/bin/env python3
"""
xbotpark_evidence_validator.py
XbotPark 协同策略证据验证器 V1.0
基于《满意解研究所与XbotPark体系协同策略研究报告_2.0_学术版》

功能:
- 标注 XbotPark 相关核心主张的证据来源与置信度
- 区分高置信度事实、待人工验证项、模拟数据警告
- 生成证据地图与合规检查摘要
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

from defense_base_components import BaseComponent


class XbotParkEvidenceValidator(BaseComponent):
    """XbotPark 协同策略证据验证器"""

    EVIDENCE_MAP = {
        "XbotPark孵化企业数量达270家": {
            "来源": "广东省高质量发展大会（2026-02-24）",
            "置信度": "高",
            "备注": "早期报道口径不同（60余家/140余家），源于统计时点差异",
        },
        "孵化企业存活率80%": {
            "来源": "36氪（2025-08）、新浪财经（2023-12）",
            "置信度": "高",
            "备注": "存活率定义未披露（是否含并购/转型）",
        },
        "总估值突破3500亿元": {
            "来源": "广东省高质量发展大会（2026-02-24）",
            "置信度": "中",
            "备注": "数量级与早期'超100亿美元'差异大，估值方法未披露",
        },
        "李泽湘收获3家IPO": {
            "来源": "36氪/希迪智驾（2024-12）、新浪财经（固高2023-08）",
            "置信度": "高",
            "备注": "港股上市（希迪智驾）、科创板上市（固高科技）",
        },
    }

    VALIDATION_STATUS = {
        "需人工验证": 12,
        "模拟数据警告": 18,
        "提案方自述": 15,
        "参考文献": "27条（近5年100%，学术期刊占比不足）",
    }

    RISK_WARNINGS = {
        "数据口径差异": "不同报道中的企业数量/估值存在显著差异",
        "独立审计缺失": "存活率和3500亿估值缺乏独立第三方审计",
        "模拟内容": "18处为AI生成或推测性内容，需谨慎引用",
    }

    def __init__(self):
        super().__init__("xbotpark_evidence_validator")

    def validate_claim(self, claim: str) -> Dict[str, Any]:
        return self.EVIDENCE_MAP.get(claim, {"错误": "未找到该主张"})

    def list_high_confidence(self) -> List[str]:
        return [k for k, v in self.EVIDENCE_MAP.items() if v["置信度"] == "高"]

    def generate_report(self) -> str:
        lines = [
            "# XbotPark 协同策略证据验证报告",
            f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
            "## 证据地图",
            "```json",
            json.dumps(self.EVIDENCE_MAP, ensure_ascii=False, indent=2),
            "```",
            "",
            "## 验证状态汇总",
            "```json",
            json.dumps(self.VALIDATION_STATUS, ensure_ascii=False, indent=2),
            "```",
            "",
            "## 风险警示",
            "- " + "\n- ".join([f"{k}：{v}" for k, v in self.RISK_WARNINGS.items()]),
            "",
            "## 高置信度事实",
            "- " + "\n- ".join(self.list_high_confidence()),
        ]
        report_path = Path(self.workspace) / "memory" / f"xbotpark-evidence-{datetime.now().strftime('%Y%m%d-%H%M')}.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return str(report_path)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="XbotPark 协同策略证据验证器")
    parser.add_argument("--report", action="store_true", help="生成证据验证报告")
    args = parser.parse_args()

    validator = XbotParkEvidenceValidator()
    path = validator.generate_report()
    print(f"证据验证报告已生成: {path}")


if __name__ == "__main__":
    main()
