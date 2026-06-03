#!/usr/bin/env python3
"""
cka_meta_library_builder.py
CKA-Meta 文献库构建助手 V1.0
基于《02CKA-Meta文献库构建》的简化可运行实现

功能:
- 102篇AI治理与元伦理顶级文献进度追踪
- 四阶段文献架构（基础理论/前沿进展/方法论/跨学科接口）
- 四层治理层级覆盖（技术/组织/社会/全球）
- 伦理传统覆盖（功利主义/义务论/德性伦理/儒家/混合范式）
- 自我指涉风险分级标注（L/M/H/E）
- Markdown 文献库构建报告生成
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

from defense_base_components import BaseComponent


class CKAMetaLibraryBuilder(BaseComponent):
    """CKA-Meta 文献库构建助手"""

    STAGES = {
        "基础理论": {"目标": 30, "占比": 0.294},
        "前沿进展": {"目标": 41, "占比": 0.402},
        "方法论": {"目标": 20, "占比": 0.196},
        "跨学科接口": {"目标": 11, "占比": 0.108},
    }

    GOVERNANCE_LAYERS = ["技术", "组织", "社会", "全球"]
    ETHICAL_TRADITIONS = ["功利主义", "义务论", "德性伦理", "儒家", "混合范式"]
    RISK_LEVELS = ["L_低风险", "M_中风险", "H_高风险", "E_极高风险"]

    def __init__(self, project_name: str = "CKA-Meta AI治理文献库"):
        super().__init__("cka_meta_library_builder")
        self.project_name = project_name
        self.papers = {}

    def add_paper(self, paper_id: str, title: str, author: str, stage: str, risk_level: str = "L") -> None:
        self.papers[paper_id] = {
            "title": title,
            "author": author,
            "stage": stage,
            "risk_level": risk_level,
            "governance_layers": [],
            "ethical_traditions": [],
            "chunk_summary": "",
        }

    def progress_overview(self) -> Dict[str, Any]:
        total = len(self.papers)
        stage_counts = {}
        risk_counts = {}
        for p in self.papers.values():
            stage_counts[p["stage"]] = stage_counts.get(p["stage"], 0) + 1
            risk_counts[p["risk_level"]] = risk_counts.get(p["risk_level"], 0) + 1

        return {
            "项目名称": self.project_name,
            "总文献数": total,
            "目标文献数": 102,
            "阶段分布": stage_counts,
            "风险分布": risk_counts,
            "完成率": round(total / 102 * 100, 1) if total else 0.0,
        }

    def generate_build_report(self) -> str:
        report = {
            "progress": self.progress_overview(),
            "stages": self.STAGES,
            "governance_layers": self.GOVERNANCE_LAYERS,
            "ethical_traditions": self.ETHICAL_TRADITIONS,
            "risk_levels": self.RISK_LEVELS,
        }
        lines = [
            f"# CKA-Meta 文献库构建报告 — {self.project_name}",
            f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
            "## 一、四阶段文献架构进度",
            "```json",
            json.dumps(report["progress"], ensure_ascii=False, indent=2),
            "```",
            "",
            "## 二、阶段目标",
            "```json",
            json.dumps(report["stages"], ensure_ascii=False, indent=2),
            "```",
            "",
            "## 三、治理层级与伦理传统",
            f"- **四层治理层级**: {', '.join(self.GOVERNANCE_LAYERS)}",
            f"- **五大伦理传统**: {', '.join(self.ETHICAL_TRADITIONS)}",
            f"- **四级风险标注**: {', '.join(self.RISK_LEVELS)}",
        ]
        report_path = Path(self.workspace) / "memory" / f"cka-meta-library-report-{datetime.now().strftime('%Y%m%d-%H%M')}.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return str(report_path)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="CKA-Meta 文献库构建助手")
    parser.add_argument("--project", default="CKA-Meta AI治理文献库", help="项目名称")
    parser.add_argument("--report", action="store_true", help="生成构建报告")
    args = parser.parse_args()

    builder = CKAMetaLibraryBuilder(project_name=args.project)
    # 预加载示例文献
    for i, (title, author, stage, risk) in enumerate([
        ("The global landscape of AI ethics guidelines", "Jobin et al.", "基础理论", "L"),
        ("EU AI Act", "European Commission", "基础理论", "M"),
        ("Fairness in Machine Learning", "Barocas & Selbst", "基础理论", "H"),
        ("A High-Level Expert Group on AI", "EU HLEG", "前沿进展", "M"),
        ("The Mythos of Model Interpretability", "Lipton", "方法论", "L"),
        ("Gödel, Escher, Bach", "Hofstadter", "跨学科接口", "E"),
    ], 1):
        builder.add_paper(f"META-{i:03d}", title, author, stage, risk)

    path = builder.generate_build_report()
    print(f"构建报告已生成: {path}")


if __name__ == "__main__":
    main()
