#!/usr/bin/env python3
"""
simon_bibliography_index.py
赫伯特·西蒙著作索引 V1.0
基于《赫伯特_西蒙著作研究_满意解理论与合伙人决策业务的学术根基》

功能:
- 西蒙关键著作与核心概念索引（Administrative Behavior / Sciences of the Artificial / Models of Bounded Rationality）
- 满意解（Satisficing）与有限理性（Bounded Rationality）在合伙人决策中的应用映射
- 生成西蒙学术根基报告
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

from defense_base_components import BaseComponent


class SimonBibliographyIndex(BaseComponent):
    """赫伯特·西蒙著作索引"""

    WORKS = {
        "Administrative Behavior (1947)": {
            "核心贡献": "提出'有限理性'概念，批判完全理性经济人假设",
            "合伙人决策映射": "组织决策中信息不完备、时间受限是常态，需用满意解替代最优解",
        },
        "Sciences of the Artificial (1969)": {
            "核心贡献": "建立设计科学与人工智能的理论基础",
            "合伙人决策映射": "合伙人匹配系统可视为'人工系统'，需在约束条件下找到足够好的解",
        },
        "Models of Bounded Rationality (1982)": {
            "核心贡献": "系统阐述有限理性的数学与行为模型",
            "合伙人决策映射": "合伙人评估中的 aspiration level（抱负水平）动态调整机制",
        },
    }

    CORE_CONCEPTS = {
        "Bounded Rationality (有限理性)": "决策者的认知能力、信息获取能力和时间都是有限的，无法追求最优解",
        "Satisficing (满意解)": "设定一个可接受的抱负水平（aspiration level），选择第一个达到或超过该水平的方案",
        "Aspiration Level (抱负水平)": "决策者对'足够好'的阈值定义，随经验和情境动态调整",
        "Heuristic Search (启发式搜索)": "在庞大解空间中使用经验法则快速缩小搜索范围",
    }

    def __init__(self):
        super().__init__("simon_bibliography_index")

    def query(self, concept: str = None) -> Dict[str, Any]:
        if concept:
            return {"著作": self.WORKS.get(concept, {}), "概念": self.CORE_CONCEPTS.get(concept, {})}
        return {"著作": self.WORKS, "概念": self.CORE_CONCEPTS}

    def generate_report(self) -> str:
        lines = [
            "# 赫伯特·西蒙学术根基报告",
            f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
            "## 关键著作",
            "```json",
            json.dumps(self.WORKS, ensure_ascii=False, indent=2),
            "```",
            "",
            "## 核心概念",
            "```json",
            json.dumps(self.CORE_CONCEPTS, ensure_ascii=False, indent=2),
            "```",
            "",
            "## 满意解研究所的方法论宣言",
            "> '我们不求最优，但求最适；结果为本，满意为尺。'",
        ]
        report_path = Path(self.workspace) / "memory" / f"simon-bibliography-{datetime.now().strftime('%Y%m%d-%H%M')}.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return str(report_path)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="赫伯特·西蒙著作索引")
    parser.add_argument("--report", action="store_true", help="生成学术根基报告")
    args = parser.parse_args()

    index = SimonBibliographyIndex()
    path = index.generate_report()
    print(f"西蒙学术根基报告已生成: {path}")


if __name__ == "__main__":
    main()
