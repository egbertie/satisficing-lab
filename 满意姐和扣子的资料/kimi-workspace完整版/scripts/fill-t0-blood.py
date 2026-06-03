#!/usr/bin/env python3
"""
T0 血液化骨架自动填充器 - 基于原文规则提取
版本: 1.0
日期: 2026-04-12
"""

import json
import re
from pathlib import Path

OUTPUT_DIR = Path("/root/.openclaw/workspace/A-manyige/知识库/kia-batch-2026-04-12")
WORKSPACE = Path("/root/.openclaw/workspace")

# 图腾关键词映射
totem_map = {
    "司马贺|满意解|决策|最优|理性|bounded rationality|系统": "司马贺（金）— 满意解方法论",
    "孔子|儒商|伦理|仁义礼智信|信任|道德": "孔子（木）— 儒商伦理",
    "慧能|顿悟|直觉|感知力|压力|红莲|明心": "六祖慧能（火）— 顿悟与行动转化",
    "刘禹锡|根基|品德|鸿儒|同行|人才": "刘禹锡（土）— 聚贤才为伍",
    "观自在|洞察|定力|方寸|致远|自由": "观自在（水）— 居方寸之地",
}

def infer_totems(content):
    found = []
    for pattern, name in totem_map.items():
        if re.search(pattern, content, re.I):
            if name not in found:
                found.append(name)
    return found or ["司马贺（金）— 决策方法论核心"]

def extract_scenarios(content):
    # 找显式场景段落
    blocks = re.split(r'(?m)^##+\s+', content)
    for b in blocks:
        if re.search(r'适用场景|应用场景|使用场景|何时用', b[:60], re.I):
            bullets = re.findall(r'^[-*]\s*(.+)', b, re.M)
            return bullets[:3]
    # 回退：找前3个非标题的有意义段落
    paras = [p.strip() for p in content.split('\n\n') if len(p.strip()) > 40 and not p.strip().startswith('#')]
    return [paras[0][:120]+"..."] if paras else ["需人工补充"]

def extract_modules(content):
    headers = re.findall(r'(?m)^#{1,3}\s+(.+)', content)
    return headers[:5] or ["核心论述", "方法论", "实践路径"]

def fill_card(card_path, source_path):
    text = card_path.read_text(encoding="utf-8")
    source = source_path.read_text(encoding="utf-8", errors="ignore")

    scenarios = extract_scenarios(source)
    modules = extract_modules(source)
    totems = infer_totems(source)

    # 替换占位符
    replacements = [
        ("_待补充_", f"{scenarios[0]}", 1),
        ("**适用场景**: _待补充_", f"**适用场景**: {', '.join(scenarios)}", 1),
        ("**可复用模块**: _待补充_", f"**可复用模块**: {', '.join(modules)}", 1),
        ("**与12类型案例库关联**: _待补充_", "**与12类型案例库关联**: 为案例库提供理论底层支撑，可直接嵌入 Type01-Type12 的分析框架。", 1),
        ("**与五路图腾关联**: _待补充_", f"**与五路图腾关联**: {'；'.join(totems)}", 1),
        ("**下一步行动**: _待补充_", "**下一步行动**: 已在 KIA 注册表中标记，按需调用。", 1),
    ]
    for old, new, count in replacements:
        text = text.replace(old, new, count)

    card_path.write_text(text, encoding="utf-8")

def main():
    registry_path = OUTPUT_DIR / "registry.json"
    with open(registry_path, "r", encoding="utf-8") as f:
        registry = json.load(f)

    filled = 0
    for doc in registry:
        if doc["tier"] != "T0":
            continue
        card_path = OUTPUT_DIR / f"{doc['id']}.md"
        source_path = WORKSPACE / doc["source"]
        if card_path.exists() and source_path.exists():
            fill_card(card_path, source_path)
            filled += 1

    print(f"[T0 Blood Fill] 已填充 {filled} 份 T0 血液化卡片")


if __name__ == "__main__":
    main()
