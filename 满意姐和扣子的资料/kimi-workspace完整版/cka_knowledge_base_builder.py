#!/usr/bin/env python3
"""
cka_knowledge_base_builder.py
CKA 知识库构建助手 V1.0
基于《06CKA知识库构建》的简化可运行实现

功能:
- 102篇案例研究知识库进度追踪
- 四阶段执行协议（文献需求图谱→顶级来源→向量化处理→质量闸口）
- 三Chunk向量化结构生成（情境/决策/理论）
- 六大质量检查点评分
- 分布验证统计（战略/组织/创新/运营/营销/伦理）
- Markdown 知识库构建报告生成
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

from defense_base_components import BaseComponent


class CKAKnowledgeBaseBuilder(BaseComponent):
    """CKA 知识库构建助手"""

    REQUIREMENT_MAP = {
        "基础理论": {"目标": 30, "占比": 0.294},
        "前沿进展": {"目标": 40, "占比": 0.392},
        "方法论": {"目标": 20, "占比": 0.196},
        "跨学科接口": {"目标": 12, "占比": 0.118},
    }

    DISTRIBUTION_REQUIREMENTS = {
        "战略案例": 0.30,
        "组织_创新案例": 0.30,
        "运营案例": 0.15,
        "营销案例": 0.10,
        "伦理_社会责任案例": 0.10,
        "失败_转型案例": 0.05,
    }

    QUALITY_GATES = {
        "数据三角验证": "访谈+档案+观察+二手数据",
        "情境深度": "充分组织背景理解决策约束",
        "决策点明确": "清晰Decision Point供教学思考",
        "理论贡献": "Eisenhardt标准：构建而非仅描述",
        "可教学性": "HBS标准：目标+问题+理论链接",
        "伦理审查": "脱敏处理与隐私保护",
    }

    def __init__(self, project_name: str = "满意解研究所CKA知识库"):
        super().__init__("cka_knowledge_base_builder")
        self.project_name = project_name
        self.cases = {}

    def add_case(self, case_id: str, title: str, category: str, source: str) -> None:
        self.cases[case_id] = {
            "title": title,
            "category": category,
            "source": source,
            "stage": {
                "文献需求": True,
                "来源确认": bool(source),
                "向量化": False,
                "质量闸口": False,
            },
            "chunks": {
                "情境": {},
                "决策": {},
                "理论": {},
            },
            "quality_scores": {k: None for k in self.QUALITY_GATES.keys()},
        }

    def progress_overview(self) -> Dict[str, Any]:
        total = len(self.cases)
        category_counts = {}
        for c in self.cases.values():
            category_counts[c["category"]] = category_counts.get(c["category"], 0) + 1

        stage_completion = {
            "文献需求": sum(1 for c in self.cases.values() if c["stage"]["文献需求"]),
            "来源确认": sum(1 for c in self.cases.values() if c["stage"]["来源确认"]),
            "向量化": sum(1 for c in self.cases.values() if c["stage"]["向量化"]),
            "质量闸口": sum(1 for c in self.cases.values() if c["stage"]["质量闸口"]),
        }

        return {
            "项目名称": self.project_name,
            "总案例数": total,
            "目标案例数": 102,
            "类别分布": category_counts,
            "阶段完成度": stage_completion,
            "完成率": round(total / 102 * 100, 1) if total else 0.0,
        }

    def distribution_validation(self) -> Dict[str, Any]:
        total = len(self.cases)
        if total == 0:
            return {"说明": "尚未添加任何案例"}
        counts = {}
        for c in self.cases.values():
            counts[c["category"]] = counts.get(c["category"], 0) + 1
        validation = {}
        for cat, req_ratio in self.DISTRIBUTION_REQUIREMENTS.items():
            actual = counts.get(cat, 0) / total
            validation[cat] = {
                "实际比例": round(actual, 3),
                "要求比例": req_ratio,
                "状态": "PASS" if actual >= req_ratio - 0.02 else "FAIL",
            }
        return validation

    def generate_build_report(self) -> str:
        report = {
            "progress": self.progress_overview(),
            "distribution": self.distribution_validation(),
            "quality_gates": list(self.QUALITY_GATES.keys()),
        }
        lines = [
            f"# CKA 知识库构建报告 — {self.project_name}",
            f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
            "## 一、四阶段执行协议进度",
            "```json",
            json.dumps(report["progress"], ensure_ascii=False, indent=2),
            "```",
            "",
            "## 二、分布验证统计",
            "```json",
            json.dumps(report["distribution"], ensure_ascii=False, indent=2),
            "```",
            "",
            "## 三、六大质量闸口",
            "- " + "\n- ".join([f"{k}（{v}）" for k, v in self.QUALITY_GATES.items()]),
        ]
        report_path = Path(self.workspace) / "memory" / f"cka-kb-build-report-{datetime.now().strftime('%Y%m%d-%H%M')}.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return str(report_path)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="CKA 知识库构建助手")
    parser.add_argument("--project", default="满意解研究所CKA知识库", help="项目名称")
    parser.add_argument("--report", action="store_true", help="生成构建报告")
    args = parser.parse_args()

    builder = CKAKnowledgeBaseBuilder(project_name=args.project)
    # 预加载示例数据（模拟 6 个典型案例）
    for i, (title, cat, src) in enumerate([
        ("Yin案例研究设计", "基础理论", "经典文献"),
        ("华为TUP股权激励", "前沿进展", "CMCC"),
        ("Kodak数字化转型失败", "失败_转型案例", "HBS"),
        ("Patagonia使命驱动", "伦理_社会责任案例", "Ivey"),
        ("Netflix颠覆Blockbuster", "战略案例", "HBS"),
        ("阿里中台组织变革", "组织_创新案例", "CMCC"),
    ], 1):
        builder.add_case(f"CASE-{i:03d}", title, cat, src)

    path = builder.generate_build_report()
    print(f"构建报告已生成: {path}")


if __name__ == "__main__":
    main()
