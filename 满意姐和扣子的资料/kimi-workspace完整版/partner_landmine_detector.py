#!/usr/bin/env python3
"""
partner_landmine_detector.py
合伙人踩雷检测器 V1.0
基于《16合伙人踩雷检测》产品设计方案

功能:
- 15分钟快速合伙人风险检测
- 五路图腾五维评估（土/金/水/木/火）
- 普通版（15题）与进阶版风险报告
- 输出踩雷风险指数与预警信号
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

from defense_base_components import BaseComponent


class PartnerLandmineDetector(BaseComponent):
    """合伙人踩雷检测器"""

    DIMENSIONS = {
        "土_价值观契合度": {
            "描述": "你们看重的东西，是不是一回事？",
            "高风险": "价值观冲突、利益导向不同",
            "权重": 1.0,
        },
        "金_决策风格兼容": {
            "描述": "信息不全时，你们能不能一起拍板？",
            "高风险": "决策风格冲突、互相推诿",
            "权重": 1.0,
        },
        "水_压力情绪韧性": {
            "描述": "压力来了，你们扛得住吗？",
            "高风险": "情绪失控、互相指责",
            "权重": 1.0,
        },
        "木_伦理底线一致": {
            "描述": "钱和原则之间，你们会怎么选？",
            "高风险": "利益至上、伦理底线模糊",
            "权重": 1.0,
        },
        "火_直觉信任程度": {
            "描述": "关键时刻，你们敢不敢信直觉？",
            "高风险": "过度分析、不相信彼此判断",
            "权重": 1.0,
        },
    }

    def __init__(self, team_name: str = ""):
        super().__init__("partner_landmine_detector")
        self.team_name = team_name

    def assess(self, scores: Dict[str, float]) -> Dict[str, Any]:
        """scores: 每个维度的平均分（1-5分）"""
        risk_scores = {}
        for dim, info in self.DIMENSIONS.items():
            score = scores.get(dim, 3.0)
            # 分数越低风险越高
            risk_level = "低风险" if score >= 4 else "中风险" if score >= 3 else "高风险"
            risk_scores[dim] = {
                "得分": round(score, 2),
                "风险等级": risk_level,
                "核心问题": info["描述"],
            }

        avg_score = sum(s["得分"] for s in risk_scores.values()) / len(risk_scores)
        overall_risk = "绿灯（低风险）" if avg_score >= 4 else "黄灯（中风险）" if avg_score >= 3 else "红灯（高风险）"
        high_risk_dims = [k for k, v in risk_scores.items() if v["风险等级"] == "高风险"]

        return {
            "团队": self.team_name or "未命名",
            "五维风险": risk_scores,
            "综合得分": round(avg_score, 2),
            "整体风险": overall_risk,
            "高风险维度": high_risk_dims,
            "建议": "建议立即引入第三方深度评估" if high_risk_dims else "合伙人关系健康，继续保持",
        }

    def generate_report(self, scores: Dict[str, float]) -> str:
        result = self.assess(scores)
        lines = [
            f"# 合伙人踩雷检测报告 — {self.team_name or '未命名团队'}",
            f"**检测时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"**综合得分**: {result['综合得分']} | **整体风险**: {result['整体风险']}",
            "",
            "## 五维风险评估",
            "```json",
            json.dumps(result["五维风险"], ensure_ascii=False, indent=2),
            "```",
            "",
            f"## 高风险维度\n- " + "\n- ".join(result["高风险维度"]) if result["高风险维度"] else "## 高风险维度\n（无）",
            "",
            f"## 建议\n\n{result['建议']}",
        ]
        report_path = Path(self.workspace) / "memory" / f"landmine-detector-{self.team_name or 'draft'}-{datetime.now().strftime('%Y%m%d-%H%M')}.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return str(report_path)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="合伙人踩雷检测器")
    parser.add_argument("--team", default="", help="团队名称")
    parser.add_argument("--report", action="store_true", help="生成踩雷检测报告")
    args = parser.parse_args()

    detector = PartnerLandmineDetector(team_name=args.team)
    # 示例数据
    scores = {
        "土_价值观契合度": 3.5,
        "金_决策风格兼容": 4.0,
        "水_压力情绪韧性": 2.5,
        "木_伦理底线一致": 4.5,
        "火_直觉信任程度": 3.0,
    }
    path = detector.generate_report(scores)
    print(f"踩雷检测报告已生成: {path}")


if __name__ == "__main__":
    main()
