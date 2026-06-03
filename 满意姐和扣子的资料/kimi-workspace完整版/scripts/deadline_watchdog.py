#!/usr/bin/env python3
"""
deadline_watchdog.py
读取 P0-P1-P2 任务决策清单与 TASK_MASTER.md，提取截止日期与状态。
若截止日期已过且状态非 ✅/FIN/完成，则标红告警。
返回码: 0 = 无超期, 1 = 存在超期任务
"""
import os
import re
import datetime

P0P2_PATH = "/root/.openclaw/workspace/A-manyige/汇报/专项报告/P0-P1-P2任务决策清单_V1.0-2026-04-11.md"
TASK_MASTER_PATH = "/root/.openclaw/workspace/docs/TASK_MASTER.md"


def extract_from_p0p2(path: str):
    alerts = []
    if not os.path.exists(path):
        return alerts
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            m = re.match(
                r"\|\s*\*\*([^|]+)\*\*\s*\|[^|]+\|[^|]+\|[^|]+\|(\d{4}-\d{2}-\d{2})\s*\|[^|]+\|\s*([^|]+)\|",
                line,
            )
            if not m:
                continue
            task_id, deadline, status = (
                m.group(1).strip(),
                m.group(2).strip(),
                m.group(3).strip(),
            )
            try:
                d = datetime.date.fromisoformat(deadline)
            except ValueError:
                continue
            if d < datetime.date.today() and not any(
                s in status for s in ("✅", "FIN", "完成")
            ):
                alerts.append((task_id, deadline, status))
    return alerts


def extract_from_task_master(path: str):
    """Minimal scan: look for ISO dates in备注 column that look like deadlines."""
    alerts = []
    if not os.path.exists(path):
        return alerts
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if "|" not in line:
                continue
            parts = [p.strip() for p in line.split("|")]
            if len(parts) < 5:
                continue
            status_field = parts[3] if len(parts) > 3 else ""
            if any(s in status_field for s in ("✅", "FIN", "完成", "⏸")):
                continue
            # Search ISO dates only in remarks/notes columns (parts[4+]) or after deadline marker
            notes_text = " ".join(parts[4:]) if len(parts) > 4 else ""
            # Prefer dates preceded by 截止 / deadline marker; fallback to any date in notes
            deadline_dates = re.findall(r"(?:截止|deadline)[:\s]*(\d{4}-\d{2}-\d{2})", notes_text)
            if not deadline_dates:
                deadline_dates = re.findall(r"\d{4}-\d{2}-\d{2}", notes_text)
            for d_str in deadline_dates:
                try:
                    d = datetime.date.fromisoformat(d_str)
                    if d < datetime.date.today():
                        task_name = parts[1] if parts[1] else "未知任务"
                        alerts.append((task_name, d_str, status_field))
                        break
                except ValueError:
                    continue
    return alerts


def main():
    today = datetime.date.today()
    alerts = extract_from_p0p2(P0P2_PATH)
    alerts += extract_from_task_master(TASK_MASTER_PATH)
    # Deduplicate by task identifier
    seen = set()
    deduped = []
    for t, d, s in alerts:
        key = (t, d)
        if key not in seen:
            seen.add(key)
            deduped.append((t, d, s))

    print(f"# Deadline Watchdog 报告 ({today})\n")
    if deduped:
        print("## 🔴 超期未闭环任务\n")
        for tid, dl, st in deduped:
            print(f"- **{tid}** 截止 `{dl}`  当前状态: `{st}`")
        print(
            "\n**指控**: 上述任务截止日期已过，但状态仍未标记为 FIN/完成。"
            "血液化要求 deadline 必须有自动化守门，而非仅靠人工记忆。"
        )
    else:
        print("## 🟢 无超期任务\n")
        print("所有带明确截止日期的任务均已闭环或尚未到期。")

    return 1 if deduped else 0


if __name__ == "__main__":
    raise SystemExit(main())
