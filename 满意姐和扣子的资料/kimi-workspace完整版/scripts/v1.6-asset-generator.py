#!/usr/bin/env python3
"""
v1.6-asset-generator.py
满意解研究所 V1.6 知识资产联动网络 · 生成器脚本
版本: 1.0
用法: python3 scripts/v1.6-asset-generator.py
说明: 读取 v1.6-knowledge-core.json，批量生成 4 份衍生材料。
核心原则: 只改 JSON，重新运行脚本即可联动更新所有产物。
"""

import json
import os
from datetime import datetime

CORE_PATH = "/root/.openclaw/workspace/A-manyige/项目版本/V1.6/知识资产网络/v1.6-knowledge-core.json"
OUTPUT_DIR = "/root/.openclaw/workspace/A-manyige/项目版本/V1.6/知识资产网络/产物"


def load_core():
    with open(CORE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def ensure_output_dir():
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def generate_flashcards(core):
    lines = [
        "# 满意解研究所 · 内部训练速记卡",
        "",
        f"> **版本**: {core['meta']['version']} 自动生成分支",
        f"> **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "> **用途**: 创始人/教练/助理日常背诵与快速回忆",
        "> **联动规则**: 修改 `v1.6-knowledge-core.json` 中的 `training_atoms`，重新运行生成器即可同步更新",
        "",
        "---",
        "",
    ]
    for idx, atom in enumerate(core["training_atoms"], 1):
        lines.append(f"## 卡片 {idx:02d}")
        lines.append("")
        lines.append(f"**问**: {atom['q']}")
        lines.append("")
        lines.append(f"> **答**: {atom['a']}")
        lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("*本文件由 `v1.6-asset-generator.py` 自动生成，请勿手动编辑。核心修改请走 `v1.6-knowledge-core.json`。*")
    return "\n".join(lines)


def generate_golden_quotes(core):
    lines = [
        "# 满意解研究所 · 金句弹药库",
        "",
        f"> **版本**: {core['meta']['version']} 自动生成分支",
        f"> **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "> **用途**: 演讲、公众号、客户面谈、PPT 封底",
        "> **联动规则**: 修改 `v1.6-knowledge-core.json` 中的 `golden_quotes`，重新运行生成器即可同步更新",
        "",
        "---",
        "",
    ]
    for q in core["golden_quotes"]:
        lines.append(f"## {q['source']}")
        lines.append("")
        lines.append(f"> **{q['text']}**")
        lines.append("")
        lines.append(f"💠 **适用场景**: {q['scenario']}")
        lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("*本文件由 `v1.6-asset-generator.py` 自动生成，请勿手动编辑。*")
    return "\n".join(lines)


def generate_client_assets(core):
    cs = core["client_scenarios"]
    lines = [
        "# 满意解研究所 · 客户场景话术包",
        "",
        f"> **版本**: {core['meta']['version']} 自动生成分支",
        f"> **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "> **用途**: 不同场合下的自我介绍/提案开场/投资人路演",
        "> **联动规则**: 修改 `v1.6-knowledge-core.json` 中的 `client_scenarios`，重新运行生成器即可同步更新",
        "",
        "---",
        "",
        "## 一、电梯演讲版（30 秒 / 60 字）",
        "",
        cs["elevator_pitch"],
        "",
        "---",
        "",
        "## 二、咖啡闲聊版（2 分钟 / 180 字）",
        "",
        cs["coffee_chat"],
        "",
        "---",
        "",
        "## 三、正式提案开场版（3 分钟 / 专业调性）",
        "",
        cs["formal_proposal_opening"],
        "",
        "---",
        "",
        "## 四、投资人路演版（强调 ROI 与风险对冲）",
        "",
        cs["investor_pitch"],
        "",
        "---",
        "",
        "*本文件由 `v1.6-asset-generator.py` 自动生成，请勿手动编辑。*",
    ]
    return "\n".join(lines)


def generate_training_textbook_outline(core):
    lines = [
        "# 满意解研究所 · 内部训练教材大纲",
        "",
        f"> **版本**: {core['meta']['version']} 自动生成分支",
        f"> **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "> **受众**: 内部教练、助理、合伙人",
        "> **联动规则**: 修改 `v1.6-knowledge-core.json` 后重新运行生成器即可同步更新本章节目录与核心知识点",
        "",
        "---",
        "",
        "## 第一章：品牌基因与身份定位",
        "",
        f"- 项目全称: {core['meta']['project_name']}",
        f"- 一句话定位: {core['meta']['tagline']}",
        f"- 灵魂信条: {core['meta']['soul_creed']}",
        f"- 愿景: {core['meta']['vision_short']}",
        f"- 方法论: {core['meta']['methodology']}",
        "",
        "## 第二章：五路图腾决策操作系统",
        "",
    ]
    for t in core["totems"]:
        lines.append(f"### {t['name']}（{t['element']}）— {t['role']}")
        lines.append(f"- **工整对仗**: {t['motto']}")
        lines.append(f"- **核心精髓**: {t['essence']}")
        lines.append(f"- **教练提示**: {t['training_hint']}")
        lines.append(f"- **客户钩子**: {t['client_hook']}")
        lines.append("")
    lines.append("## 第三章：核心概念词典")
    lines.append("")
    for c in core["core_concepts"]:
        lines.append(f"- **{c['term']}**: {c['definition']}")
    lines.append("")
    lines.append("## 第四章：产品 SKU 体系")
    lines.append("")
    for key, sku in core["skus"].items():
        lines.append(f"### {sku['name']}（{sku['positioning']}）")
        lines.append(f"- 一句话: {sku['one_liner']}")
        lines.append(f"- 价格定位: {sku['price_hint']}")
        lines.append("")
    lines.append("## 第五章：12 类型冲突案例导航")
    lines.append("")
    for ct in core["case_types"]:
        lines.append(f"- **{ct['code']} {ct['name']}**: {ct['conflict']}")
    lines.append("")
    lines.append("## 第六章：教练认证速记卡（Q&A）")
    lines.append("")
    lines.append("详见 `内部训练速记卡.md`（同目录产物）。")
    lines.append("")
    lines.append("## 第七章：金句与话术弹药")
    lines.append("")
    lines.append("详见 `金句弹药库.md` 与 `客户场景话术包.md`（同目录产物）。")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("*本文件由 `v1.6-asset-generator.py` 自动生成，请勿手动编辑。*")
    return "\n".join(lines)


def main():
    core = load_core()
    ensure_output_dir()

    products = {
        "内部训练速记卡.md": generate_flashcards,
        "金句弹药库.md": generate_golden_quotes,
        "客户场景话术包.md": generate_client_assets,
        "内部训练教材大纲.md": generate_training_textbook_outline,
    }

    for filename, generator in products.items():
        filepath = os.path.join(OUTPUT_DIR, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(generator(core))
        print(f"✅ 已生成: {filepath}")

    print("\n🎉 全部产物生成完毕。请记住：未来只要修改 JSON 核心并重新运行本脚本，所有产物将自动联动更新。")


if __name__ == "__main__":
    main()
