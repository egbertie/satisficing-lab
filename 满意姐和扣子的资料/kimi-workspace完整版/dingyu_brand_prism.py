#!/usr/bin/env python3
"""
dingyu_brand_prism.py
鼎玉·晋·五路 品牌棱镜 V1.0
基于《21鼎玉_晋_五路_满意解研究所的文化根脉与创始人精神》

功能:
- 解析鼎（规则/风控）、玉（价值/灵活）、晋（向光而行）、五路（土火水金木）的品牌符号体系
- 生成品牌叙事、创始人口号、对外传播文案
- 根据受众类型（创业者/投资人/合作伙伴）输出定制化品牌表达
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

from defense_base_components import BaseComponent


class DingyuBrandPrism(BaseComponent):
    """鼎玉·晋·五路 品牌棱镜"""

    SYMBOLS = {
        "鼎": {
            "意象": "国之重器，契约之信",
            "创始人映射": "前11年大型商业银行：规则、风控、契约、严谨",
            "品牌承诺": "用规则守护合作，用条款界定边界",
            "关键词": ["契约", "风控", "退出机制", "厚重"],
        },
        "玉": {
            "意象": "光华内蕴，温润坚韧",
            "创始人映射": "后11年中小企业浸润：灵活、价值、体感、韧性",
            "品牌承诺": "内在价值比外在估值更值得守护",
            "关键词": ["温润", "成长", "价值守护", "韧性"],
        },
        "晋": {
            "意象": "向光而行，永不止步",
            "创始人映射": "双系统融合后的信念：满意解不是终点，而是向上的起点",
            "品牌承诺": "陪伴创业者从鼎玉之基走向晋阶之光",
            "关键词": ["向上", "进化", "陪伴", "向光而行"],
        },
        "五路": {
            "意象": "土火水金木，五维相生",
            "品牌映射": "满意解研究所的方法论核心",
            "品牌承诺": "让每一次合伙决策都有据可依、有光可向",
            "关键词": ["土/德", "火/顿悟", "水/观自在", "金/满意解", "木/仁"],
        },
    }

    def __init__(self):
        super().__init__("dingyu_brand_prism")

    def narrative(self, focus: str = "完整版") -> Dict[str, str]:
        if focus == "鼎玉":
            return {
                "主标题": "鼎玉相成",
                "副标题": "规则之内，价值为基；器重则立，德华则远",
                "正文": "鼎代表我们在大型机构中淬炼的风控与契约精神；玉代表我们在中小企业实战中磨砺的价值体感。鼎玉相济，方成晋。",
            }
        if focus == "晋":
            return {
                "主标题": "向光而行",
                "副标题": "满意解不是终点，而是向上的起点",
                "正文": "从鼎玉之基出发，穿越创业的风雨与迷雾，陪伴每一位创始人抵达晋阶之光。",
            }
        return {
            "主标题": "鼎玉·晋·五路",
            "副标题": "扎根三千年文明土壤，服务最前沿硬科技创业",
            "正文": "我们以鼎为契约之信，以玉为价值之华，以晋为向上之志，以五路为决策之法。让每一次合伙决策，都有据可依，有光可向，有晋可期。",
        }

    def audience_message(self, audience: str) -> str:
        messages = {
            "创业者": "我们懂你的合约焦虑，更懂你的价值执念。鼎玉相成，陪你向光而行。",
            "投资人": "硬科技投资的本质是投人。我们用五路图腾的系统方法，识别真正能走过十年的合伙人组合。",
            "合作伙伴": "以鼎立信，以玉寻价，以晋共行。期待与每一位志同道合者，共建硬科技创业的决策基础设施。",
            "内部团队": "鼎是我们的风控底线，玉是我们的价值体感，晋是我们的共同信念，五路是我们每天都在用的方法论。",
        }
        return messages.get(audience, messages["创业者"])

    def generate_report(self) -> str:
        lines = [
            "# 鼎玉·晋·五路 品牌棱镜报告",
            f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
            "## 符号体系",
            "```json",
            json.dumps(self.SYMBOLS, ensure_ascii=False, indent=2),
            "```",
            "",
            "## 品牌叙事（完整版）",
            self.narrative("完整版")["正文"],
            "",
            "## 受众定制话术",
            "- **创业者**：" + self.audience_message("创业者"),
            "- **投资人**：" + self.audience_message("投资人"),
            "- **合作伙伴**：" + self.audience_message("合作伙伴"),
            "- **内部团队**：" + self.audience_message("内部团队"),
            "",
            "## 主金句",
            "> 让每一次合伙决策，都有据可依，有光可向，有晋可期。",
        ]
        report_path = Path(self.workspace) / "memory" / f"dingyu-brand-prism-{datetime.now().strftime('%Y%m%d-%H%M')}.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return str(report_path)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="鼎玉·晋·五路 品牌棱镜")
    parser.add_argument("--report", action="store_true", help="生成品牌棱镜报告")
    args = parser.parse_args()

    prism = DingyuBrandPrism()
    path = prism.generate_report()
    print(f"品牌棱镜报告已生成: {path}")


if __name__ == "__main__":
    main()
