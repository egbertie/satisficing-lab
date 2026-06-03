#!/usr/bin/env python3
"""
file_processing_insight_enforcer.py
扫描近 14 天的 memory 文件，检测是否存在「文件处理闭环」记录。
若存在，但同日期未找到 L1-L5 深度洞察产出，则标红告警。
对应 AGENTS.md 文件处理标准 V2.0 阶段 8：强制 L1-L5 洞察。
返回码: 0 = 全部合规, 1 = 存在缺口
"""
import re
import datetime
from pathlib import Path

MEMORY_DIR = Path("/root/.openclaw/workspace/memory")
DIALOGUE_DIR = Path("/root/.openclaw/workspace/A-manyige/对话")

FP_KEYWORDS = ["文件处理完成", "闭环完成", "入库完成", "处理闭环", "已闭环", "全部完成"]
INSIGHT_KEYWORDS = ["L1-L5", "深度洞察", "五层洞察", "五轮深度洞察", "洞察报告", "内化完成"]


def has_keyword(content: str, keywords):
    return any(re.search(kw, content) for kw in keywords)


def main():
    today = datetime.date.today()
    issues = []

    for mem_path in sorted(MEMORY_DIR.glob("2026-04-*.md")):
        date_str = mem_path.stem
        try:
            d = datetime.date.fromisoformat(date_str)
        except ValueError:
            continue
        if (today - d).days > 14:
            continue

        content = mem_path.read_text(encoding="utf-8")
        if not has_keyword(content, FP_KEYWORDS):
            continue

        insight_found = has_keyword(content, INSIGHT_KEYWORDS)

        # Also check same-date dialogue folder
        if not insight_found:
            dia_dir = DIALOGUE_DIR / date_str
            if dia_dir.exists():
                for dia_file in dia_dir.glob("*.md"):
                    if has_keyword(dia_file.read_text(encoding="utf-8"), INSIGHT_KEYWORDS):
                        insight_found = True
                        break

        if not insight_found:
            issues.append(date_str)

    print(f"# 文件处理 L1-L5 洞察强制检查报告 ({today})\n")
    if issues:
        print("## 🔴 缺失深度洞察的日期\n")
        for d in issues:
            print(f"- `{d}` 检测到文件处理闭环，但未找到对应 L1-L5 深度洞察")
        print(
            "\n**指控**: AGENTS.md 文件处理标准 V2.0 阶段 8 规定："
            "'闭环后 10 分钟内生成 L1-L5 洞察，未生成则标红告警。'"
            "上述日期仅有处理动作记录，无洞察产出，构成血液化缺口。"
        )
    else:
        print("## 🟢 全部合规\n")
        print("近 14 天内所有文件处理任务均已生成或关联到 L1-L5 深度洞察。")

    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
