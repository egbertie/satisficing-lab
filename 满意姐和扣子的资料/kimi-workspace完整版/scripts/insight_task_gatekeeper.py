#!/usr/bin/env python3
"""
insight_task_gatekeeper.py
Daily check if yesterday's memory file has insights not reflected in TASK_MASTER.md within 24h.
血液化规则：洞察必须在24小时内任务化。
"""
import os
import re
import datetime

WORKSPACE = "/root/.openclaw/workspace"
MEMORY_DIR = os.path.join(WORKSPACE, "memory")
TASK_MASTER = os.path.join(WORKSPACE, "docs", "TASK_MASTER.md")
REPORT_DIR = os.path.join(WORKSPACE, "A-manyige", "审计")
QUEUE_FILE = os.path.join(WORKSPACE, "memory", "insight_task_queue.json")

KEYWORDS = ["洞察", "启发", "机制", "建议", "任务化", "血液化", "闭环", "固定规则", "必须", "下一步"]


def get_yesterday_memory():
    d = datetime.date.today() - datetime.timedelta(days=1)
    return os.path.join(MEMORY_DIR, f"{d}.md")


def extract_blocks(text):
    blocks = []
    for para in re.split(r"\n{2,}", text):
        para = para.strip()
        if 30 <= len(para) <= 600:
            score = sum(1 for kw in KEYWORDS if kw in para)
            if score >= 2:
                blocks.append(para.replace("\n", " "))
    return blocks


def load_taskmaster():
    if not os.path.exists(TASK_MASTER):
        return ""
    with open(TASK_MASTER, "r", encoding="utf-8") as f:
        return f.read()


def write_report(missing):
    os.makedirs(REPORT_DIR, exist_ok=True)
    today = datetime.date.today().isoformat()
    path = os.path.join(REPORT_DIR, f"insight_gatekeeper_report_{today}.md")
    lines = [
        f"# 洞察任务门神报告 ({today})",
        f"\n未闭环洞察数量: **{len(missing)}**",
        "\n## 昨日 memory 中未在 TASK_MASTER.md 体现的洞察/启发\n"
    ]
    for i, b in enumerate(missing, 1):
        lines.append(f"{i}. {b}\n")
    lines.append("---\n**Action**: 立即将上述内容转化为 TASK_MASTER.md 中的具体任务项。")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return path


def main():
    mem_path = get_yesterday_memory()
    if not os.path.exists(mem_path):
        print(f"SKIP: {mem_path} not found")
        return
    with open(mem_path, "r", encoding="utf-8") as f:
        blocks = extract_blocks(f.read())
    if not blocks:
        print("No insight blocks found")
        return
    tm = load_taskmaster()
    missing = [b for b in blocks if b[:40] not in tm]
    if missing:
        path = write_report(missing)
        print(f"ALERT: {len(missing)} untasked insights -> {path}")
    else:
        print("OK: insights covered")


if __name__ == "__main__":
    main()
