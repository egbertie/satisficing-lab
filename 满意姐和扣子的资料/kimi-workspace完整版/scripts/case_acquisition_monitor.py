#!/usr/bin/env python3
"""
case_acquisition_monitor.py
Check if the case repository has grown in the last 7 days.
If not, generate a reminder/report.
首年目标：30个案例库。血液化监督。
"""
import os
import json
import datetime

WORKSPACE = "/root/.openclaw/workspace"
CASE_DIRS = [
    os.path.join(WORKSPACE, "A-manyige", "项目版本", "V1.6", "案例库", "真实案例"),
    os.path.join(WORKSPACE, "A-manyige", "项目版本", "V1.6", "案例库", "模拟案例"),
]
TRACKER = os.path.join(WORKSPACE, "memory", "case_acquisition_tracker.json")
REPORT_DIR = os.path.join(WORKSPACE, "A-manyige", "审计")


def count_cases():
    total = 0
    for d in CASE_DIRS:
        if os.path.isdir(d):
            # Count directories that look like cases (TypeNN_ or have .md files)
            for entry in os.scandir(d):
                if entry.is_dir():
                    total += 1
                elif entry.is_file() and entry.name.endswith(".md"):
                    total += 1
    return total


def load_tracker():
    if not os.path.exists(TRACKER):
        return {"history": []}
    with open(TRACKER, "r", encoding="utf-8") as f:
        return json.load(f)


def save_tracker(data):
    with open(TRACKER, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def write_report(current, last_week_count):
    os.makedirs(REPORT_DIR, exist_ok=True)
    today = datetime.date.today().isoformat()
    path = os.path.join(REPORT_DIR, f"case_acquisition_alert_{today}.md")
    lines = [
        f"# 案例获取监督报告 ({today})",
        f"\n⚠️ **案例库已 {last_week_count} 天未增长。**",
        f"\n当前案例总量: {current}",
        "\n首年目标: 30 个案例库。",
        "\n---",
        "**Action**: 立即启动案例获取动作（访谈、公开资料、模拟生成）。",
        "\n建议来源:",
        "- 科创板 IPO 问询函",
        "- 硬科技创业者访谈",
        "- 新闻报道中的合伙人冲突事件"
    ]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return path


def main():
    current = count_cases()
    data = load_tracker()
    today = datetime.date.today().isoformat()
    data["history"].append({"date": today, "count": current})
    data["history"] = data["history"][-30:]
    save_tracker(data)

    # Check if there's been growth in last 7 days
    last_week = None
    for h in reversed(data["history"][:-1]):
        # Find the entry closest to 7 days ago
        d = datetime.date.fromisoformat(h["date"])
        delta = (datetime.date.today() - d).days
        if delta >= 7:
            last_week = h
            break

    if last_week is None:
        print(f"OK: First run or not enough history. Current={current}")
        return

    if current <= last_week["count"]:
        path = write_report(current, (datetime.date.today() - datetime.date.fromisoformat(last_week["date"])).days)
        print(f"ALERT: No case growth in 7+ days -> {path}")
    else:
        print(f"OK: Cases grew from {last_week['count']} to {current}")


if __name__ == "__main__":
    main()
