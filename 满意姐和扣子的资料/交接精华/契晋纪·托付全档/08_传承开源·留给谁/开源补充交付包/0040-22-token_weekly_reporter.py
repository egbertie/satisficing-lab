#!/usr/bin/env python3
"""
Token 周报条件触发器
原则：无洞察，不输出。取消固定准点，改为阈值触发。
"""

import json
import shutil
from pathlib import Path
from datetime import datetime

MEMORY_DIR = Path("/root/.openclaw/workspace/memory")
REPORT_DIR = Path("/root/.openclaw/workspace/A-manyige/汇报/日报")
TRACKER_FILE = MEMORY_DIR / "token-zero-tracker.json"
HISTORY_FILE = MEMORY_DIR / "token-weekly-history.json"

# 触发阈值
TRIGGER_DELTA_PCT = 15.0      # display_percentage 较上周同周期变化 >15%
TRIGGER_LEVEL_JUMP = True     # level 发生跳变（如 L2→L4）
TRIGGER_BUDGET_EXCEED = True  # 超出 100% 预算


def load_tracker():
    if not TRACKER_FILE.exists():
        return None
    with open(TRACKER_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_history():
    if not HISTORY_FILE.exists():
        return []
    with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_history(record):
    history = load_history()
    history.append(record)
    history = history[-12:]  # 保留最近 12 周
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2, ensure_ascii=False)


def should_generate(tracker, history):
    if not tracker:
        return False, "tracker 缺失"

    display_pct = tracker.get("display", {}).get("display_percentage")
    level = tracker.get("display", {}).get("level")
    week_est = tracker.get("summary", {}).get("week_estimated", 0)

    if not history:
        return True, "首次记录"

    last = history[-1]
    last_pct = last.get("display_percentage")
    last_level = last.get("level")

    # 预算超支
    if display_pct is not None and display_pct >= 100 and (last_pct is None or last_pct < 100):
        return True, f"预算突破 100%（上周 {last_pct}%）"

    # level 跳变（升或降）
    if TRIGGER_LEVEL_JUMP and level != last_level:
        return True, f"档位跳变 {last_level} → {level}"

    # 百分比显著变化
    if display_pct is not None and last_pct is not None:
        change = abs(display_pct - last_pct)
        if change >= TRIGGER_DELTA_PCT:
            return True, f"百分比变化 {change:.1f}%（{last_pct}% → {display_pct}%）"

    # 如果本周数据极少（或估算极低），但上周是高消耗，也触发（异常低）
    if display_pct is not None and last_pct is not None and last_pct > 50 and display_pct < 20:
        return True, f"消耗骤降（{last_pct}% → {display_pct}%）"

    return False, "无显著变化，静默跳过"


def generate_report(tracker, reason):
    display = tracker.get("display", {})
    summary = tracker.get("summary", {})
    cycle = tracker.get("cycle", {})
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")

    lines = [
        "# Token 周报",
        "",
        f"> 生成时间: {now_str}",
        f"> 触发原因: {reason}",
        "",
        "## 周期概况",
        "",
        f"- 周期起点: {cycle.get('week_start', 'N/A')}",
        f"- 时间进度: {display.get('time_progress_pct', 'N/A')}%",
        f"- 本周估算消耗: {summary.get('week_estimated', 0):,} tokens",
        f"- 用户会话消耗: {summary.get('user_week_estimated', 0):,} tokens",
        f"- 显示百分比: {display.get('display_percentage', 'N/A')}%",
        f"- Delta: {display.get('delta', 'N/A')}",
        f"- 当前档位: {display.get('level', 'N/A')}",
        "",
        "## 建议",
    ]

    level = display.get("level", "L1")
    delta = display.get("delta", 0)

    if level in ("L4", "L3"):
        lines.append("- 🔴 Token 进入紧缩区，建议立即启用 deep-silent 或减少高消耗任务")
    elif delta > 20:
        lines.append("- 🟡 消耗速度超过时间进度 20% 以上，需审查后台自动化任务")
    elif delta < -10:
        lines.append("- 🟢 消耗控制优于时间进度，当前策略可持续")
    else:
        lines.append("- 🟢 Token 使用节奏正常")

    if summary.get("week_estimated", 0) > summary.get("user_week_estimated", 0) * 1.5:
        lines.append("- 💡 后台自动化消耗占比过高，建议运行 `python3 scripts/system-guardian.py scan` 排查")

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("> 本报告由条件触发器生成：如无显著变化，不输出报告以节省精力。")

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d")
    report_path = REPORT_DIR / f"Token周报-{date_str}.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path


def main():
    tracker = load_tracker()
    history = load_history()

    should, reason = should_generate(tracker, history)

    record = {
        "timestamp": datetime.now().isoformat(),
        "display_percentage": tracker.get("display", {}).get("display_percentage") if tracker else None,
        "level": tracker.get("display", {}).get("level") if tracker else None,
        "week_estimated": tracker.get("summary", {}).get("week_estimated") if tracker else None,
        "triggered": should,
        "reason": reason,
    }
    save_history(record)

    if should:
        path = generate_report(tracker, reason)
        term_width = shutil.get_terminal_size().columns
        print(f"{'='*term_width}")
        print(f"[Token周报已触发] {reason}")
        print(f"报告已生成: {path}")
        print(f"{'='*term_width}")
    else:
        print(f"[Token周报跳过] {reason} — 无输出，节省精力")


if __name__ == "__main__":
    main()
