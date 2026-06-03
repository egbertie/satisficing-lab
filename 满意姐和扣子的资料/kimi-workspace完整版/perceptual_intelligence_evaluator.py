#!/usr/bin/env python3
"""
perceptual_intelligence_evaluator.py
感知力指数（PIQ）评估器 V1.0
基于《36感知力决策的经济价值量化研究》和《37感知力决策经济价值研究2.0》

功能:
- 从五路图腾维度（土/火/水/金/木）评估创始人感知力
- 外部可验证指标（80%权重）+ 深度验证指标（20%权重）
- 计算综合 PIQ 得分和分维度雷达图数据
- 生成感知力评估报告
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

from defense_base_components import BaseComponent


class PerceptualIntelligenceEvaluator(BaseComponent):
    """感知力指数（PIQ）评估器"""

    DIMENSIONS = {
        "土_价值观清晰度": {
            "描述": "价值锚定与长期承诺",
            "外部指标": "股权保留比例、使命愿景关键词频率、独立董事/科学顾问设立",
            "深度指标": "施瓦茨价值观量表简版",
        },
        "火_顿悟能力": {
            "描述": "战略敏捷与关键洞察",
            "外部指标": "战略方向调整次数、关键决策瞬间媒体叙事频率",
            "深度指标": "决策风格问卷、顿悟经历访谈",
        },
        "水_状态稳定性": {
            "描述": "情绪调节与团队韧性",
            "外部指标": "AI语音分析语言流畅度、融资失败后团队留存率",
            "深度指标": "情绪智力量表（WLEIS）",
        },
        "金_方法严谨性": {
            "描述": "系统思维与财务纪律",
            "外部指标": "财务模型完整性、外部审计引入",
            "深度指标": "风险偏好与决策严谨性测试",
        },
        "木_伦理契合度": {
            "描述": "社会责任与利益相关方管理",
            "外部指标": "劳动仲裁/供应商纠纷记录、行业公益参与",
            "深度指标": "伦理困境情境判断测试",
        },
    }

    def __init__(self, founder_name: str = ""):
        super().__init__("perceptual_intelligence_evaluator")
        self.founder_name = founder_name

    def evaluate(self, external_scores: Dict[str, float], deep_scores: Dict[str, float]) -> Dict[str, Any]:
        """计算 PIQ 得分，外部指标80% + 深度指标20%"""
        dimension_scores = {}
        for dim in self.DIMENSIONS.keys():
            ext = external_scores.get(dim, 50.0) / 100.0
            dep = deep_scores.get(dim, 50.0) / 100.0
            composite = ext * 0.8 + dep * 0.2
            dimension_scores[dim] = round(composite, 3)

        piq_score = sum(dimension_scores.values()) / len(dimension_scores)
        return {
            "创始人": self.founder_name or "未命名",
            "PIQ综合得分": round(piq_score, 3),
            "维度得分": dimension_scores,
            "评级": "A_高感知力" if piq_score >= 0.75 else "B_中等感知力" if piq_score >= 0.55 else "C_感知力待提升",
            "优势维度": [k for k, v in dimension_scores.items() if v >= 0.75],
            "短板维度": [k for k, v in dimension_scores.items() if v < 0.55],
        }

    def generate_report(self, external_scores: Dict[str, float], deep_scores: Dict[str, float]) -> str:
        result = self.evaluate(external_scores, deep_scores)
        lines = [
            f"# 感知力指数（PIQ）评估报告 — {self.founder_name or '未命名创始人'}",
            f"**评估时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"**PIQ 综合得分**: {result['PIQ综合得分']} | **评级**: {result['评级']}",
            "",
            "## 五维得分",
            "```json",
            json.dumps(result['维度得分'], ensure_ascii=False, indent=2),
            "```",
            "",
            f"## 优势维度\n- " + "\n- ".join(result['优势维度']) if result['优势维度'] else "## 优势维度\n（暂无）",
            "",
            f"## 短板维度\n- " + "\n- ".join(result['短板维度']) if result['短板维度'] else "## 短板维度\n（暂无）",
        ]
        report_path = Path(self.workspace) / "memory" / f"piq-report-{self.founder_name or 'draft'}-{datetime.now().strftime('%Y%m%d-%H%M')}.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return str(report_path)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="感知力指数（PIQ）评估器")
    parser.add_argument("--founder", default="", help="创始人姓名")
    parser.add_argument("--report", action="store_true", help="生成评估报告")
    args = parser.parse_args()

    evaluator = PerceptualIntelligenceEvaluator(founder_name=args.founder)
    external = {
        "土_价值观清晰度": 70.0,
        "火_顿悟能力": 65.0,
        "水_状态稳定性": 80.0,
        "金_方法严谨性": 55.0,
        "木_伦理契合度": 75.0,
    }
    deep = {
        "土_价值观清晰度": 60.0,
        "火_顿悟能力": 70.0,
        "水_状态稳定性": 65.0,
        "金_方法严谨性": 50.0,
        "木_伦理契合度": 60.0,
    }
    path = evaluator.generate_report(external, deep)
    print(f"PIQ 评估报告已生成: {path}")


if __name__ == "__main__":
    main()
