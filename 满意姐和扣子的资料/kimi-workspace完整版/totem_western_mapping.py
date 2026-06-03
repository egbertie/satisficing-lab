#!/usr/bin/env python3
"""
totem_western_mapping.py
五路图腾 — 西方管理学概念映射器 V1.0
基于《35东方决策智慧的科学化批判研究》的功能对等性矩阵

功能:
- 查询五路图腾与西方管理学核心概念的功能对等性评分
- 输出可直译、需意译、不可译的概念分类
- 提供应用场景建议（高优势情境 vs 有效性边界）
- 生成概念映射报告
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

from defense_base_components import BaseComponent


class TotemWesternMapping(BaseComponent):
    """五路图腾 — 西方管理学概念映射器"""

    MAPPINGS = {
        "土_刘禹锡_德": {
            "西方对应概念": "Organizational Culture / Virtue Ethics",
            "功能对等性": 0.65,
            "翻译分类": "需意译",
            "核心张力": "原典中的反商业审美维度与创业语境存在概念断裂",
            "应用场景": "文化重塑、合伙人伦理筛选、组织身份认同构建",
            "有效性边界": "纯量化绩效评估、短期财务决策",
        },
        "火_六祖慧能_顿悟": {
            "西方对应概念": "Insight / Aha Moment / Creative Leap",
            "功能对等性": 0.55,
            "翻译分类": "不可译",
            "核心张力": "存在论维度的'见性'无法还原为心理学的insight",
            "应用场景": "战略迷茫期、危机谈判、技术路线转折点的直觉突破",
            "有效性边界": "日常运营优化、标准化流程决策",
        },
        "水_观自在": {
            "西方对应概念": "Mindfulness / Meta-Cognition / Emotional Intelligence",
            "功能对等性": 0.75,
            "翻译分类": "需意译",
            "核心张力": "观自在包含超越自我的解脱维度，EI侧重人际效能",
            "应用场景": "高压决策情境、合伙人冲突调解、创始人情绪管理",
            "有效性边界": "纯技术参数确定、合规审查",
        },
        "木_孔子_仁": {
            "西方对应概念": "Benevolence / Differential Mode of Association / Social Capital",
            "功能对等性": 0.70,
            "翻译分类": "不可译",
            "核心张力": "差序格局无法还原为西方普遍主义伦理",
            "应用场景": "合伙人信任构建、利益相关方管理、组织伦理基石",
            "有效性边界": "全球化跨国团队的统一规则制定",
        },
        "金_司马贺_满意解": {
            "西方对应概念": "Bounded Rationality / Satisficing",
            "功能对等性": 0.85,
            "翻译分类": "可直译",
            "核心张力": "几乎无张力，可直接对接决策科学"
            ,"应用场景": "所有信息不完备、时间受限的真实商业决策",
            "有效性边界": "算法可完全优化的纯计算场景",
        },
    }

    RISK_WARNINGS = {
        "顿悟依赖": "过度依赖直觉可能导致决策冲动，需与系统分析结合",
        "差序扩展失衡": "仁的差序格局若过度扩展可能损害公平性",
        "德之符号化": "'德'可能被工具化为表演性文化符号而非真实伦理",
    }

    def __init__(self):
        super().__init__("totem_western_mapping")

    def query(self, totem: str) -> Dict[str, Any]:
        return self.MAPPINGS.get(totem, {"错误": "未找到该图腾映射"})

    def list_all(self) -> Dict[str, Any]:
        return {
            "可直译": [k for k, v in self.MAPPINGS.items() if v["翻译分类"] == "可直译"],
            "需意译": [k for k, v in self.MAPPINGS.items() if v["翻译分类"] == "需意译"],
            "不可译": [k for k, v in self.MAPPINGS.items() if v["翻译分类"] == "不可译"],
        }

    def recommend_application(self, decision_context: str) -> List[str]:
        """根据决策情境推荐适用的图腾-西方混合框架"""
        recs = []
        if any(w in decision_context for w in ["合伙人", "冲突", "信任", "伦理"]):
            recs.append("木_孔子_仁 + Social Capital 理论")
        if any(w in decision_context for w in ["战略", "迷茫", "转折", "危机"]):
            recs.append("火_六祖慧能_顿悟 + Insight 研究（但保留不可译的存在论维度）")
        if any(w in decision_context for w in ["情绪", "压力", "调解", "自我调节"]):
            recs.append("水_观自在 + Emotional Intelligence 量表")
        if any(w in decision_context for w in ["信息不完备", "时间紧迫", "多目标", "权衡"]):
            recs.append("金_司马贺_满意解 + Bounded Rationality / DDM")
        if any(w in decision_context for w in ["文化", "价值观", "组织认同", "长期承诺"]):
            recs.append("土_刘禹锡_德 + Organizational Culture 研究")
        return recs

    def generate_report(self, decision_context: str = "合伙人选择与冲突管理") -> str:
        lines = [
            "# 五路图腾 — 西方管理学概念映射报告",
            f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
            "## 完整映射矩阵",
            "```json",
            json.dumps(self.MAPPINGS, ensure_ascii=False, indent=2),
            "```",
            "",
            "## 翻译分类汇总",
            "```json",
            json.dumps(self.list_all(), ensure_ascii=False, indent=2),
            "```",
            "",
            f"## 针对情境 '{decision_context}' 的应用建议",
            "- " + "\n- ".join(self.recommend_application(decision_context)),
            "",
            "## 风险警示",
            "- " + "\n- ".join([f"{k}：{v}" for k, v in self.RISK_WARNINGS.items()]),
        ]
        report_path = Path(self.workspace) / "memory" / f"totem-western-mapping-{datetime.now().strftime('%Y%m%d-%H%M')}.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return str(report_path)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="五路图腾 — 西方管理学概念映射器")
    parser.add_argument("--context", default="合伙人选择与冲突管理", help="决策情境")
    parser.add_argument("--report", action="store_true", help="生成映射报告")
    args = parser.parse_args()

    mapper = TotemWesternMapping()
    path = mapper.generate_report(decision_context=args.context)
    print(f"概念映射报告已生成: {path}")


if __name__ == "__main__":
    main()
