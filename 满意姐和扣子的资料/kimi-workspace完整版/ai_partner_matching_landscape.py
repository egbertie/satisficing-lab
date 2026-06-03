#!/usr/bin/env python3
"""
ai_partner_matching_landscape.py
AI 合伙人匹配服务竞争格局扫描器 V1.0
基于《26AI决策教练合伙人匹配服务竞争格局研究报告》

功能:
- AI决策支持市场格局分析（工具辅助→智慧共创）
- 主要竞品对比：传统相亲式匹配/算法推荐/专家咨询/感知力决策
- 差异化定位评分
- 生成竞争格局评估报告
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

from defense_base_components import BaseComponent


class AIPartnerMatchingLandscape(BaseComponent):
    """AI 合伙人匹配服务竞争格局扫描器"""

    COMPETITORS = {
        "工具辅助型匹配": {
            "代表": ["爱合伙", "缘创派", "找合伙"],
            "核心逻辑": "标签化技能互补匹配",
            "优势": "效率快、门槛低、覆盖广",
            "劣势": "只看技能，不看价值观与长期兼容性",
            "感知力决策得分": 20,
        },
        "算法推荐型平台": {
            "代表": ["合伙人算法推荐"],
            "核心逻辑": "大数据+MBTI/人格算法推荐",
            "优势": "有一定科学依据，可规模化",
            "劣势": "忽视情境、压力反应、伦理契合",
            "感知力决策得分": 40,
        },
        "专家咨询型服务": {
            "代表": ["传统猎头+管理咨询", "高管教练"],
            "核心逻辑": "资深专家经验判断",
            "优势": "深度访谈、行业洞察",
            "劣势": "成本高、不可规模化、主观偏差大",
            "感知力决策得分": 60,
        },
        "感知力决策模式": {
            "代表": ["满意解研究所"],
            "核心逻辑": "左脑风控+右脑直觉，五维感知力评估",
            "优势": "技术-人文融合，理性+直觉双系统",
            "劣势": "需要客户深度参与，周期较长",
            "感知力决策得分": 85,
        },
    }

    POSITIONING_MESSAGES = [
        "感知力决策——AI算力与东方智慧的共生新范式",
        "左脑风控，右脑直觉，决策的艺术与科学在此融合",
        "不是AI替代人类，而是智慧赋能决策——感知力决策，让每一次选择都有据、有悟、有温度",
    ]

    def __init__(self):
        super().__init__("ai_partner_matching_landscape")

    def compare(self) -> Dict[str, Any]:
        return {
            name: {
                "代表": info["代表"],
                "核心逻辑": info["核心逻辑"],
                "优势": info["优势"],
                "劣势": info["劣势"],
                "感知力决策对标得分": info["感知力决策得分"],
            }
            for name, info in self.COMPETITORS.items()
        }

    def recommend_positioning(self, target_segment: str) -> List[str]:
        recs = []
        if "硬科技" in target_segment:
            recs.append("强调技术-商业互补的长期兼容性，而非短期技能匹配")
        if "创始人" in target_segment:
            recs.append("突出'能一起走十年'的人文陪伴型定位")
        if "vc" in target_segment.lower() or "投资" in target_segment:
            recs.append("用DID-PSM因果推断和案例数据证明感知力决策的投资回报")
        if "企业" in target_segment:
            recs.append("提供合伙人治理的周期性陪跑方案")
        if not recs:
            recs.append("通用定位：双系统验证，降低认知盲区")
        return recs

    def generate_report(self, target_segment: str = "硬科技创始人") -> str:
        lines = [
            "# AI 合伙人匹配服务竞争格局评估报告",
            f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"**目标客群**: {target_segment}",
            "",
            "## 竞争格局对比",
            "```json",
            json.dumps(self.compare(), ensure_ascii=False, indent=2),
            "```",
            "",
            "## 定位建议",
            "- " + "\n- ".join(self.recommend_positioning(target_segment)),
            "",
            "## 品类定义金句备选",
            "- " + "\n- ".join(self.POSITIONING_MESSAGES),
        ]
        report_path = Path(self.workspace) / "memory" / f"ai-landscape-report-{datetime.now().strftime('%Y%m%d-%H%M')}.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return str(report_path)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="AI 合伙人匹配服务竞争格局扫描器")
    parser.add_argument("--segment", default="硬科技创始人", help="目标客群")
    parser.add_argument("--report", action="store_true", help="生成竞争格局报告")
    args = parser.parse_args()

    scanner = AIPartnerMatchingLandscape()
    path = scanner.generate_report(target_segment=args.segment)
    print(f"竞争格局报告已生成: {path}")


if __name__ == "__main__":
    main()
