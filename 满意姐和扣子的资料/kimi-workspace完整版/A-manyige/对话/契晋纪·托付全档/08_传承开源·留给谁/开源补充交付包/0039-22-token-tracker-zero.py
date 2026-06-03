#!/usr/bin/env python3
"""
Token Tracker Zero - 零Token消耗会话监控器
版本: 1.2
日期: 2026-04-12
核心原则: 监控本身不消耗Token，纯本地文件计算

新增 (v1.2):
- 波动性监控: 周内日消耗标准差与变异系数(CV)
- 日内分布: 今日各小时消耗分布
- 用尽策略(endgame): 周期末尾主动降级避免额度浪费
- 双向联动: token异常时自动触发 hibernation-control.py auto-check

数据源:
- /root/.openclaw/agents/main/sessions/*.jsonl (真实 usage 数据)
- /root/.openclaw/workspace/memory/token-weekly-monitor.json (用户校准)
- /root/.openclaw/workspace/memory/token-daily-ledger.jsonl (历史波动)

输出:
- /root/.openclaw/workspace/memory/token-zero-tracker.json
- /root/.openclaw/workspace/memory/token-daily-ledger.jsonl
"""

import json
import math
import subprocess
from pathlib import Path
from datetime import datetime, timedelta

WORKSPACE = Path("/root/.openclaw/workspace")
MEMORY_DIR = WORKSPACE / "memory"
SESSIONS_DIR = Path("/root/.openclaw/agents/main/sessions")
TRACKER_FILE = MEMORY_DIR / "token-zero-tracker.json"
HIBERNATION_STATE_FILE = MEMORY_DIR / "hibernation-state.json"
HIBERNATION_CONTROL = WORKSPACE / "skills/hibernation-protocol/hibernation-control.py"

CHARS_PER_TOKEN = 3.8
TOOL_CALL_TOKENS = 400


def parse_session(filepath):
    """解析单个 session JSONL，返回 (actual, estimated, tool_calls, date, is_user_session, today_actual, today_estimated, hourly_actual)"""
    actual = estimated = tool_calls = msg_chars = 0
    date = None
    is_user_session = False
    today_str = datetime.now().strftime("%Y-%m-%d")
    today_actual = today_estimated = 0
    hourly_actual = {}

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue

                msg = entry.get("message", {})
                entry_type = entry.get("type")

                msg_ts = entry.get("timestamp", "")
                msg_date = msg_ts[:10] if len(msg_ts) >= 10 else ""
                msg_hour = msg_ts[:13] if len(msg_ts) >= 13 else ""
                if date is None and msg_date:
                    date = msg_date

                if entry_type != "message":
                    continue

                role = msg.get("role")
                content = msg.get("content", [])

                if role == "assistant":
                    usage = msg.get("usage", {})
                    total = usage.get("totalTokens")
                    if total:
                        actual += total
                        if msg_date == today_str:
                            today_actual += total
                            if msg_hour:
                                hourly_actual[msg_hour] = hourly_actual.get(msg_hour, 0) + total
                    else:
                        text_len = sum(len(item.get("text", "")) for item in content if isinstance(item, dict) and item.get("type") == "text")
                        est = int(text_len / CHARS_PER_TOKEN)
                        estimated += est
                        if msg_date == today_str:
                            today_estimated += est

                    for item in content:
                        if isinstance(item, dict) and item.get("type") == "toolCall":
                            tool_calls += 1

                elif role == "user":
                    for item in content:
                        if isinstance(item, dict) and item.get("type") == "text":
                            text = item.get("text", "")
                            msg_chars += len(text)
                            if "User Message From Kimi" in text:
                                is_user_session = True

    except Exception:
        return 0, 0, 0, None, False, 0, 0, {}

    estimated += tool_calls * TOOL_CALL_TOKENS + int(msg_chars / CHARS_PER_TOKEN)
    today_estimated += tool_calls * TOOL_CALL_TOKENS + int(msg_chars / CHARS_PER_TOKEN)
    return actual, estimated, tool_calls, date, is_user_session, today_actual, today_estimated, hourly_actual


def week_boundaries(reference=None):
    """以每周三 12:00 为周期起点"""
    if reference is None:
        reference = datetime.now()
    days_since_wed = (reference.weekday() - 2) % 7
    start = reference - timedelta(days=days_since_wed)
    start = start.replace(hour=12, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=7)
    return start, end


def load_monitor_calibration():
    try:
        with open(MEMORY_DIR / "token-weekly-monitor.json", 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("currentStatus", {}).get("percentage")
    except Exception:
        return None


def compute_weekly_volatility(week_start, week_end):
    """从 ledger 计算本周日消耗的波动率"""
    ledger_file = MEMORY_DIR / "token-daily-ledger.jsonl"
    daily_values = []
    if ledger_file.exists():
        try:
            with open(ledger_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                    except Exception:
                        continue
                    ts = entry.get("timestamp", "")
                    dt = datetime.fromisoformat(ts)
                    if week_start.date() <= dt.date() < week_end.date():
                        daily_values.append(entry.get("today_actual", 0))
        except Exception:
            pass

    if len(daily_values) < 2:
        return {"daily_mean": daily_values[0] if daily_values else 0, "daily_std": 0, "cv": 0.0}

    mean = sum(daily_values) / len(daily_values)
    variance = sum((x - mean) ** 2 for x in daily_values) / len(daily_values)
    std = math.sqrt(variance)
    cv = std / mean if mean > 0 else 0.0
    return {"daily_mean": int(mean), "daily_std": round(std, 1), "cv": round(cv, 2)}


def get_current_hibernation_level():
    try:
        with open(HIBERNATION_STATE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f).get("status", "normal")
    except Exception:
        return "normal"


def get_previous_tracker_level():
    try:
        with open(TRACKER_FILE, 'r', encoding='utf-8') as f:
            return json.load(f).get("display", {}).get("level", "unknown")
    except Exception:
        return "unknown"


def trigger_hibernation_sync(new_level, reason):
    """当 token 档位建议发生显著变化时，触发休眠控制器同步"""
    current_hibernation = get_current_hibernation_level()
    # 映射 tracker 推荐级别到 hibernation 级别
    target_map = {
        "L4-emergency": "deep-silent",
        "L2-warning": "silent",
        "L1-waste-risk": "normal",
        "L1-endgame": "normal",
        "L0-sprint": "turbo",
        "L1-available": "normal",
        "L0-normal": "normal",
    }
    target = target_map.get(new_level)
    if not target:
        return

    # 只在以下情况触发：
    # 1. 当前休眠级别与目标不匹配
    # 2. 且不是用户手动强制设置的（紧急 L4 除外）
    if current_hibernation == target:
        return

    user_forced = False
    try:
        with open(HIBERNATION_STATE_FILE, 'r', encoding='utf-8') as f:
            hstate = json.load(f)
        hreason = hstate.get("reason", "")
        if hreason in ("manual", "user_command") and new_level != "L4-emergency":
            user_forced = True
    except Exception:
        pass

    if user_forced:
        print(f"  [双向联动] 用户手动强制 {current_hibernation}，跳过自动调整")
        return

    try:
        result = subprocess.run(
            ["python3", str(HIBERNATION_CONTROL), target, "--reason", reason],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            print(f"  [双向联动] 已触发休眠调整: {current_hibernation} -> {target} ({reason})")
        else:
            print(f"  [双向联动] 触发失败: {result.stderr.strip()}")
    except Exception as e:
        print(f"  [双向联动] 异常: {e}")


import sys

def main():
    force_refresh = "--force-refresh" in sys.argv
    # === 休眠级别节流 ===
    last_tracker_run_file = MEMORY_DIR / "token-zero-tracker-last-run.json"
    if not force_refresh and HIBERNATION_STATE_FILE.exists():
        try:
            with open(HIBERNATION_STATE_FILE, 'r', encoding='utf-8') as f:
                hstate = json.load(f)
            level = hstate.get("status", "normal")
            # 2026-04-12 修正：任何模式下最多 60 分钟强制刷新，防止 deep-silent 下自瞎
            heartbeat_min = {"normal": 30, "turbo": 30, "hibernating": 30, "silent": 60, "deep-silent": 60}.get(level, 30)
            if last_tracker_run_file.exists():
                with open(last_tracker_run_file, 'r', encoding='utf-8') as f:
                    last_run = datetime.fromisoformat(json.load(f).get("timestamp", ""))
                minutes_since = (datetime.now() - last_run).total_seconds() / 60
                if minutes_since < heartbeat_min:
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {level} 模式节流中，上次运行 {minutes_since:.1f} 分钟前，间隔 {heartbeat_min} 分钟，跳过")
                    return
        except Exception:
            pass

    files = sorted(SESSIONS_DIR.glob("*.jsonl"), key=lambda p: p.stat().st_mtime)
    week_start, week_end = week_boundaries()
    today = datetime.now().strftime("%Y-%m-%d")

    total_actual = total_estimated = 0
    week_actual = week_estimated = 0
    today_actual = today_estimated = 0
    user_week_actual = user_week_estimated = 0
    today_hourly = {}

    for filepath in files:
        actual, estimated, tool_calls, date, is_user, sess_today_actual, sess_today_estimated, hourly = parse_session(filepath)
        if date is None:
            date = today

        total_actual += actual
        total_estimated += estimated
        today_actual += sess_today_actual
        today_estimated += sess_today_estimated
        for h, v in hourly.items():
            today_hourly[h] = today_hourly.get(h, 0) + v

        try:
            dt = datetime.strptime(date, "%Y-%m-%d")
            if week_start.date() <= dt.date() < week_end.date():
                week_actual += actual
                week_estimated += estimated
                if is_user:
                    user_week_actual += actual
                    user_week_estimated += estimated
        except ValueError:
            continue

    # 校准值
    calibrated_pct = load_monitor_calibration()

    # 时间进度
    now = datetime.now()
    time_progress = min(100.0, max(0.0, ((now - week_start).total_seconds() / (week_end - week_start).total_seconds()) * 100))

    # 移除 WEEK_BUDGET=50000 的失真百分比指标
    backend_frontend_ratio = round(week_actual / user_week_actual, 2) if user_week_actual > 0 else None

    # 显示百分比：有校准用校准，否则保留 None
    display_pct = calibrated_pct
    delta = round(display_pct - time_progress, 1) if display_pct is not None else None

    # === 波动性指标 ===
    volatility = compute_weekly_volatility(week_start, week_end)
    burn_rate = (display_pct / time_progress) if time_progress > 0 and display_pct is not None else 0.0

    # === 时间进度挂钩的 S-曲线模型 ===
    TOKEN_PACE = [0.08, 0.18, 0.32, 0.50, 0.68, 0.85, 1.00]
    day_idx = min(6, max(0, int((time_progress / 100.0) * 7)))
    expected_upper = TOKEN_PACE[day_idx] * 100.0
    pace_ratio = (display_pct / expected_upper) if expected_upper > 0 and display_pct is not None else 0.0

    # 按当前日均推算周期末预计消耗百分比（简化：假设日均不变）
    days_elapsed = max(0.1, day_idx + (time_progress % (100/7)) / (100/7))
    remaining_days = max(0.1, 7 - days_elapsed)
    daily_mean = volatility.get("daily_mean", 0)
    # 无校准值时跳过 projection
    if display_pct is not None and daily_mean > 0 and calibrated_pct is not None:
        # 将日均 token 映射为百分点增长：假设全周均匀，则用 pace_ratio 推算更稳
        projected_end_pct = min(100.0, display_pct + (display_pct / max(0.1, days_elapsed)) * remaining_days)
    else:
        projected_end_pct = None

    # === 基于倍率的档位推荐 + 用尽策略 ===
    if display_pct is None:
        level = "unknown"
        pace_status = "unknown"
    elif time_progress > 95 and display_pct < 95:
        # 周期末冲刺：鼓励用完额度
        level = "L0-sprint"
        pace_status = "endgame-sprint"
    elif time_progress > 85 and display_pct < 85:
        # 周期末尾可用额度较多，建议提升活跃度
        level = "L1-endgame"
        pace_status = "endgame-available"
    elif time_progress > 85 and display_pct < 60:
        level = "L1-waste-risk"
        pace_status = "under-spending"
    elif pace_ratio > 1.60:
        level = "L4-emergency"
        pace_status = "severe-over"
    elif pace_ratio > 1.30:
        level = "L2-warning"
        pace_status = "fast"
    elif pace_ratio < 0.70 and time_progress > 50:
        level = "L1-available"
        pace_status = "slow"
    else:
        level = "L0-normal"
        pace_status = "on-track"

    # === 异常波动附加标记 ===
    volatility_alert = None
    if volatility["cv"] > 1.0:
        volatility_alert = "high_cv"
    elif volatility["cv"] > 0.5:
        volatility_alert = "moderate_cv"

    tracker = {
        "version": "1.2-zero",
        "principle": "零Token监控",
        "last_updated": now.isoformat(),
        "cycle": {
            "week_start": week_start.isoformat(),
            "week_end": week_end.isoformat(),
            "time_progress_pct": round(time_progress, 1)
        },
        "budget": None,
        "summary": {
            "today_actual": today_actual,
            "today_estimated": today_estimated,
            "week_actual": week_actual,
            "week_estimated": week_estimated,
            "user_week_actual": user_week_actual,
            "user_week_estimated": user_week_estimated,
            "all_time_actual": total_actual,
            "all_time_estimated": total_estimated
        },
        "volatility": {
            "daily_mean": volatility["daily_mean"],
            "daily_std": volatility["daily_std"],
            "cv": volatility["cv"],
            "burn_rate": round(burn_rate, 2),
            "projected_end_pct": round(projected_end_pct, 1) if projected_end_pct is not None else None,
            "volatility_alert": volatility_alert,
            "today_hourly_peaks": len([v for v in today_hourly.values() if v > volatility["daily_mean"] * 0.3]) if volatility["daily_mean"] > 0 else 0
        },
        "display": {
            "calibrated_percentage": display_pct,
            "backend_frontend_ratio": backend_frontend_ratio,
            "display_percentage": display_pct,
            "time_progress_pct": round(time_progress, 1),
            "token_day": day_idx + 1,
            "expected_upper_pct": round(expected_upper, 1),
            "pace_ratio": round(pace_ratio, 2),
            "pace_status": pace_status,
            "delta": delta,
            "level": level
        }
    }

    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    with open(TRACKER_FILE, 'w', encoding='utf-8') as f:
        json.dump(tracker, f, indent=2, ensure_ascii=False)

    # === 每日 ledger 追加 ===
    ledger_file = MEMORY_DIR / "token-daily-ledger.jsonl"
    ledger_entry = {
        "timestamp": now.isoformat(),
        "date": today,
        "today_actual": today_actual,
        "today_estimated": today_estimated,
        "week_actual": week_actual,
        "week_estimated": week_estimated,
        "user_week_actual": user_week_actual,
        "user_week_estimated": user_week_estimated,
        "backend_frontend_ratio": backend_frontend_ratio,
        "pace_ratio": round(pace_ratio, 2),
        "display_percentage": display_pct,
        "level": level
    }
    with open(ledger_file, 'a', encoding='utf-8') as f:
        f.write(json.dumps(ledger_entry, ensure_ascii=False) + "\n")

    with open(last_tracker_run_file, 'w', encoding='utf-8') as f:
        json.dump({"timestamp": now.isoformat()}, f, indent=2, ensure_ascii=False)

    # === 双向联动：token 档位与休眠级别同步（必须在覆盖 tracker 文件前读取旧状态）===
    previous_level = get_previous_tracker_level()

    # 中文终端输出
    print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] Token Tracker Zero 更新完成")
    print(f"  今日实际消耗: {today_actual:,} tokens")
    print(f"  本周实际消耗(全量): {week_actual:,} tokens")
    print(f"  本周实际消耗(用户会话): {user_week_actual:,} tokens")
    print(f"  前后台消耗比(B/F): {backend_frontend_ratio}")
    print(f"  用户校准值: {calibrated_pct}%")
    print(f"  时间进度: {round(time_progress, 1)}%")
    print(f"  S-曲线预期上限(Day {day_idx+1}): {round(expected_upper, 1)}%")
    print(f"  Pace Ratio: {round(pace_ratio, 2)}")
    print(f"  Pace Status: {pace_status}")
    print(f"  Burn Rate: {round(burn_rate, 2)}")
    print(f"  日均波动(CV): {volatility['cv']}")
    print(f"  周期末预计: {round(projected_end_pct, 1) if projected_end_pct is not None else 'N/A'}%")
    print(f"  波动预警: {volatility_alert or '无'}")
    print(f"  Delta: {delta}")
    print(f"  当前档位: {level}")
    print(f"  Ledger 已追加: {MEMORY_DIR / 'token-daily-ledger.jsonl'}")

    if previous_level != level:
        trigger_hibernation_sync(level, f"token_auto_{pace_status}_{level}")


if __name__ == "__main__":
    main()
