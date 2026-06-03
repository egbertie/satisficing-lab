#!/usr/bin/env python3
"""
partner_mcda_selector.py
合伙人匹配 MCDA 方法选择器 V1.0
基于《77合伙人深度研究》中的多准则决策分析方法论

功能:
- 根据决策情境特征推荐最适合的 MCDA 方法
- 提供 AHP / PROMETHEE / VIKOR / TOPSIS / ELECTRE / Fuzzy MCDA 的适用检查
- 生成方法选择理由和下一步操作建议
- Markdown 决策建议报告生成
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

from defense_base_components import BaseComponent


class PartnerMCDASelector(BaseComponent):
    """合伙人匹配 MCDA 方法选择器"""

    METHODS = {
        "AHP": {
            "适用情境": ["准则间可补偿", "需明确权衡", "决策者偏好清晰"],
            "优点": "成对比较直观，一致性检验可验证",
            "缺点": "方案数量过多时成对比较负担重",
            "复杂度": "中",
        },
        "MAUT": {
            "适用情境": ["准则间可补偿", "需要量化价值", "有充足数据"],
            "优点": "理论基础扎实，允许风险态度建模",
            "缺点": "效用函数构建需要大量专家输入",
            "复杂度": "高",
        },
        "TOPSIS": {
            "适用情境": ["大量方案", "需要快速排序"],
            "优点": "计算高效，易于理解和解释",
            "缺点": "对权重敏感，没有一致性检验",
            "复杂度": "低",
        },
        "ELECTRE": {
            "适用情境": ["非补偿性", "需尊重准则独立性", "存在明显劣势方案"],
            "优点": "方法稳健，对权重调整不敏感",
            "缺点": "可能产生不可比方案，计算较复杂",
            "复杂度": "高",
        },
        "PROMETHEE": {
            "适用情境": ["需要可视化交互", "准则间非补偿", "需要解释性强"],
            "优点": "图形化展示（GAIA），辅助沟通效果好",
            "缺点": "需要选择适当的偏好函数",
            "复杂度": "中",
        },
        "VIKOR": {
            "适用情境": ["存在冲突", "需要妥协解", "关注最弱势群体"],
            "优点": "同时最大化群体效用和最小化个体遗憾",
            "缺点": "需要归一化处理，对数据质量要求高",
            "复杂度": "中",
        },
        "Fuzzy_MCDA": {
            "适用情境": ["信息模糊", "语言变量为主", "不确定性高"],
            "优点": "能处理人类语言中的模糊性",
            "缺点": "计算过程复杂，解释性较弱",
            "复杂度": "高",
        },
    }

    def __init__(self, project_name: str = "合伙人匹配评估"):
        super().__init__("partner_mcda_selector")
        self.project_name = project_name

    def recommend(self, context: Dict[str, bool]) -> Dict[str, Any]:
        """基于情境特征推荐 MCDA 方法"""
        scores = {m: 0 for m in self.METHODS.keys()}
        for method, info in self.METHODS.items():
            for condition in info["适用情境"]:
                if context.get(condition, False):
                    scores[method] += 1

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        best_method = ranked[0][0]
        return {
            "项目": self.project_name,
            "输入情境": context,
            "推荐方法": best_method,
            "推荐理由": self.METHODS[best_method],
            "得分排名": ranked,
        }

    def quick_assess(self, num_candidates: int, data_quality: str, has_conflict: bool, preference_clarity: str) -> Dict[str, Any]:
        """快速评估接口"""
        context = {
            "准则间可补偿": preference_clarity in ["高", "中"] and not has_conflict,
            "非补偿性": has_conflict,
            "大量方案": num_candidates >= 5,
            "需要快速排序": num_candidates >= 5,
            "存在冲突": has_conflict,
            "需要妥协解": has_conflict,
            "信息模糊": data_quality == "模糊",
            "语言变量为主": data_quality == "模糊",
            "不确定性高": data_quality == "模糊",
            "需要可视化交互": True,
            "需尊重准则独立性": has_conflict,
            "有明显劣势方案": has_conflict,
            "决策者偏好清晰": preference_clarity == "高",
            "需要量化价值": preference_clarity == "高" and data_quality == "高",
            "有充足数据": data_quality == "高",
        }
        return self.recommend(context)

    def generate_report(self, num_candidates: int = 3, data_quality: str = "中", has_conflict: bool = True, preference_clarity: str = "中") -> str:
        result = self.quick_assess(num_candidates, data_quality, has_conflict, preference_clarity)
        lines = [
            f"# 合伙人匹配 MCDA 方法选择报告 — {self.project_name}",
            f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
            "## 输入情境",
            f"- 候选人数: {num_candidates}",
            f"- 数据质量: {data_quality}",
            f"- 是否存在明显冲突: {'是' if has_conflict else '否'}",
            f"- 决策者偏好清晰度: {preference_clarity}",
            "",
            "## 推荐方法",
            f"**{result['推荐方法']}**",
            "",
            "```json",
            json.dumps(result['推荐理由'], ensure_ascii=False, indent=2),
            "```",
            "",
            "## 全部方法得分排名",
            "```json",
            json.dumps(result['得分排名'], ensure_ascii=False, indent=2),
            "```",
        ]
        report_path = Path(self.workspace) / "memory" / f"partner-mcda-report-{datetime.now().strftime('%Y%m%d-%H%M')}.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return str(report_path)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="合伙人匹配 MCDA 方法选择器")
    parser.add_argument("--project", default="合伙人匹配评估", help="项目名称")
    parser.add_argument("--candidates", type=int, default=3, help="候选人数")
    parser.add_argument("--quality", default="中", choices=["高", "中", "模糊"], help="数据质量")
    parser.add_argument("--conflict", action="store_true", help="是否存在明显冲突")
    parser.add_argument("--clarity", default="中", choices=["高", "中", "低"], help="偏好清晰度")
    parser.add_argument("--report", action="store_true", help="生成选择报告")
    args = parser.parse_args()

    selector = PartnerMCDASelector(project_name=args.project)
    path = selector.generate_report(
        num_candidates=args.candidates,
        data_quality=args.quality,
        has_conflict=args.conflict,
        preference_clarity=args.clarity,
    )
    print(f"MCDA 方法选择报告已生成: {path}")


if __name__ == "__main__":
    main()
