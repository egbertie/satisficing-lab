#!/usr/bin/env python3
"""
confucian_hardtech_case_index.py
儒商哲学硬科技案例索引 V1.0
基于《09硬科技儒商哲学》《企业儒学理论建构与实践验证_黎红雷_2.0版》《黎红雷教授深度研究报告1.0》

功能:
- 硬科技企业儒商管理案例索引（方太、海底捞、华为、黑芝麻、地平线、大疆等）
- 黎红雷企业儒学「十大观」与「十六字方针」结构化查询
- 证据置信度标注（高/中/低）
- 生成儒商管理应用报告
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

from defense_base_components import BaseComponent


class ConfucianHardtechCaseIndex(BaseComponent):
    """儒商哲学硬科技案例索引"""

    CASES = {
        "方太集团": {
            "核心制度": ["孔子堂", "身股制", "五常考核", "全员践行儒家文化"],
            "关键数据": {
                "2023年营收": "176.29亿元（高置信度，来自茅忠群致辞+多源交叉）",
                "员工敬业度": "87分（高置信度，怡安翰威特评估）",
            },
            "儒商映射": "中学明道，西学优术，中西合璧，以道御术",
            "置信度": "高",
        },
        "海底捞": {
            "核心制度": ["家文化", "师徒制", "接班人培养机制"],
            "关键数据": {
                "门店数": "全球超1300家",
                "员工流失率": "显著低于行业平均",
            },
            "儒商映射": "仁（家文化）+ 礼（服务标准）+ 信（顾客信任）",
            "置信度": "高",
        },
        "华为": {
            "核心制度": ["以奋斗者为本", "虚拟受限股", "轮值董事长"],
            "关键数据": {
                "研发投入占比": "长期超20%",
                "股权激励覆盖": "超12万员工",
            },
            "儒商映射": "自强不息（奋斗者）+ 共同体意识（股权共享）",
            "置信度": "高",
        },
        "黑芝麻智能": {
            "合伙人结构": "单记章（芯片）+ 刘卫红（汽车）",
            "核心经验": "30年同学关系+产业互补+股权慷慨",
            "儒商映射": "强关系（信）+ 产业互补（和）",
            "置信度": "中",
        },
        "地平线": {
            "合伙人结构": "余凯+黄畅+陶斐雯",
            "核心经验": "A类股10倍投票权保证控制权56%",
            "儒商映射": "和而不同（团队稳定）+ 礼（治理结构）",
            "置信度": "中",
        },
    }

    LI_HONGLEI_FRAMEWORK = {
        "十六字方针": "中学明道，西学优术，中西合璧，以道御术",
        "核心命题": [
            "西方管理理论如何与中国实际相结合",
            "儒家思想是否可以赋能现代企业",
        ],
        "十大观": [
            "以人为本的管理观",
            "修己安人的领导观",
            "义利合一的经营观",
            "信用至上的交易观",
            "和谐共生的组织观",
            "创新求变的的发展观",
            "勤俭敬业的劳动观",
            "经世济民的社会责任观",
            "天人合一的生态观",
            "知行合一的教育观",
        ],
        "代表著作": [
            "《儒家管理哲学》（1991）",
            "《儒家商道智慧》（2017）",
            "《企业儒学》（2017）",
            "《儒商文化通论》（2025）",
        ],
    }

    def __init__(self):
        super().__init__("confucian_hardtech_case_index")

    def query_case(self, company: str) -> Dict[str, Any]:
        return self.CASES.get(company, {"错误": "未找到该公司案例"})

    def query_framework(self) -> Dict[str, Any]:
        return self.LI_HONGLEI_FRAMEWORK

    def generate_report(self, focus_company: str = None) -> str:
        case_data = self.query_case(focus_company) if focus_company else self.CASES
        lines = [
            f"# 儒商哲学硬科技案例索引报告{f' — {focus_company}' if focus_company else ''}",
            f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
            "## 企业案例",
            "```json",
            json.dumps(case_data, ensure_ascii=False, indent=2),
            "```",
            "",
            "## 黎红雷企业儒学框架",
            "```json",
            json.dumps(self.LI_HONGLEI_FRAMEWORK, ensure_ascii=False, indent=2),
            "```",
        ]
        report_path = Path(self.workspace) / "memory" / f"confucian-case-index-{datetime.now().strftime('%Y%m%d-%H%M')}.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return str(report_path)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="儒商哲学硬科技案例索引")
    parser.add_argument("--company", default="", help="聚焦企业名称")
    parser.add_argument("--report", action="store_true", help="生成案例索引报告")
    args = parser.parse_args()

    index = ConfucianHardtechCaseIndex()
    path = index.generate_report(focus_company=args.company or None)
    print(f"儒商案例索引报告已生成: {path}")


if __name__ == "__main__":
    main()
