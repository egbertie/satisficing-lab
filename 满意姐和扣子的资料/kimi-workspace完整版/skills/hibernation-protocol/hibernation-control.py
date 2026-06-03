#!/usr/bin/env python3
"""
休眠协议控制器 V2.1 - 五级运行模式完整版
生效日期: 2026-04-10
蓝军彻底重写版

五级光谱:
  L0 normal      - 正常模式（默认）
  L1 turbo       - 高耗能模式（全力输出）
  L2 hibernating - 休眠模式（无交互10分钟后）
  L3 silent      - 静默模式（无交互30分钟后或Token 10-20%）
  L4 deep-silent - 深度静默模式（用户指令或Token<10%或2小时无交互）

核心改进:
1. 从二级(awake/hibernating)升级到五级完整光谱
2. 每级对应明确的 gate 策略、cron 策略、用户唤醒规则
3. auto-check 自动根据交互时间和Token档位升降级
4. 支持手动强制进入任意级别（turbo/deep-silent用于用户主动控制）
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = Path("/root/.openclaw/workspace")
MEMORY_DIR = WORKSPACE / "memory"
HIBERNATION_LOG = MEMORY_DIR / "hibernation-log.json"
HIBERNATION_STATE = MEMORY_DIR / "hibernation-state.json"
LAST_INTERACTION = MEMORY_DIR / "last-interaction.json"
LAST_AUTO_CHECK = MEMORY_DIR / "hibernation-last-auto-check.json"
TOKEN_TRACKER = MEMORY_DIR / "token-zero-tracker.json"

# 阈值配置
THRESHOLDS = {
    "normal_to_hibernating_minutes": 10,
    "hibernating_to_silent_minutes": 30,
    "silent_to_deep_minutes": 120,
    "turbo_auto_downgrade_minutes": 10,
}

# 保活任务（任何模式下都运行）
ESSENTIAL_JOBS = {
    "a9a9abbf-8848-451a-b00c-c2ee0bdf9c2e",  # daily-backup
    "49811b9f-82cb-4a85-a17d-315e7de0fe52",  # weekly-essential-snapshot
    "9c44bc69-b6d0-4f9f-b15b-cd87e24f54fe",  # weekly-check
    "3cf8e9f2-08c1-4438-b6bc-22eafd20513b",  # weekly-cloud-backup
    "8631dfb5-ebbf-4baa-84de-674b9cd26768",  # hibernation-check itself
    "61cfb1fc-c308-4b0e-a005-aec9f82ef4f3",  # disk-guardian
    "fb03a552-3e4c-4376-98eb-a951013517d9",  # system-guardian
}

# 高消耗任务
EXPENSIVE_JOBS = {
    "a8f9fecf-a825-40d0-bab3-5e5165ea20a4",  # daily-asset-activation
    "6828c851-dc8f-4c04-b942-d6b8d267bc5c",  # evening-totem
    "ea4ef0ad-337b-4e5c-90be-dcb7f3db9f90",  # token-optimizer
}

# 五级状态定义
LEVELS = {
    "normal": {
        "name": "正常模式",
        "emoji": "🌅",
        "gate_policy": "allow_all",
        "cron_policy": "all_scheduled",
        "subagent_policy": "allow",
        "heartbeat_interval_minutes": 30,
        "compression": "normal",
    },
    "turbo": {
        "name": "高耗能模式",
        "emoji": "🚀",
        "gate_policy": "turbo_focus",
        "cron_policy": "essential_only_during_turbo",
        "subagent_policy": "allow_priority",
        "heartbeat_interval_minutes": 60,
        "compression": "disabled",
    },
    "hibernating": {
        "name": "休眠模式",
        "emoji": "🌙",
        "gate_policy": "block_expensive",
        "cron_policy": "essential_only",
        "subagent_policy": "block",
        "heartbeat_interval_minutes": 30,
        "compression": "normal",
    },
    "silent": {
        "name": "静默模式",
        "emoji": "🤫",
        "gate_policy": "block_nonessential",
        "cron_policy": "essential_only",
        "subagent_policy": "block",
        "heartbeat_interval_minutes": 120,
        "compression": "aggressive",
    },
    "deep-silent": {
        "name": "深度静默模式",
        "emoji": "🪦",
        "gate_policy": "essential_only",
        "cron_policy": "survival_only",
        "subagent_policy": "block",
        "heartbeat_interval_minutes": 720,
        "compression": "maximum",
    },
}

# cron 动态节流配置
HIBERNATION_CHECK_JOB_ID = "8631dfb5-ebbf-4baa-84de-674b9cd26768"
LEVEL_CRON_EXPR = {
    "normal": "*/30 * * * *",
    "turbo": "*/30 * * * *",
    "hibernating": "0 */2 * * *",
    "silent": "0 */4 * * *",
    "deep-silent": "0 */12 * * *",
}

def adjust_hibernation_cron(level):
    """根据级别调整休眠状态检查的 cron 间隔，减少 agentTurn 式后台消耗"""
    expr = LEVEL_CRON_EXPR.get(level)
    if not expr:
        return False
    try:
        result = subprocess.run(
            ["openclaw", "cron", "edit", HIBERNATION_CHECK_JOB_ID, "--cron", expr],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0:
            log_message("INFO", f"已调整休眠检查 cron 为 {expr} ({level})")
            return True
        else:
            log_message("WARN", f"调整 cron 失败: {result.stderr}")
            return False
    except Exception as e:
        log_message("WARN", f"调整 cron 异常: {e}")
        return False


def log_message(level, message):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] [{level}] {message}", flush=True)


def get_hibernation_state():
    if HIBERNATION_STATE.exists():
        try:
            with open(HIBERNATION_STATE, "r") as f:
                state = json.load(f)
            # 兼容 V2.0 旧状态名
            state["status"] = normalize_old_status(state.get("status", "normal"))
            return state
        except Exception as e:
            log_message("ERROR", f"读取休眠状态失败: {e}")
    return {
        "status": "normal",
        "level_id": None,
        "start_time": None,
        "mode": None,
        "reason": None,
    }


def set_hibernation_state(state):
    HIBERNATION_STATE.parent.mkdir(parents=True, exist_ok=True)
    with open(HIBERNATION_STATE, "w") as f:
        json.dump(state, f, indent=2)


def normalize_old_status(status):
    """兼容 V2.0 及更早的状态名称"""
    if status == "awake":
        return "normal"
    if status == "hibernating":
        return "hibernating"
    return status


def _naive_dt(dt_or_str):
    """将 datetime 或 ISO 字符串转为 offset-naive datetime"""
    if isinstance(dt_or_str, str):
        dt = datetime.fromisoformat(dt_or_str)
    else:
        dt = dt_or_str
    if dt.tzinfo:
        return dt.replace(tzinfo=None)
    return dt


def append_hibernation_log(entry):
    HIBERNATION_LOG.parent.mkdir(parents=True, exist_ok=True)
    log_data = []
    if HIBERNATION_LOG.exists():
        try:
            with open(HIBERNATION_LOG, "r") as f:
                log_data = json.load(f)
        except Exception:
            log_data = []
    entry["timestamp"] = datetime.now().isoformat()
    log_data.append(entry)
    log_data = log_data[-500:]
    with open(HIBERNATION_LOG, "w") as f:
        json.dump(log_data, f, indent=2)


def get_last_interaction():
    """返回最后交互时间戳和来源。优先信任 last-interaction.json，系统文件修改不视为用户交互。"""
    candidates = []

    if LAST_INTERACTION.exists():
        try:
            with open(LAST_INTERACTION, "r") as f:
                data = json.load(f)
            ts = _naive_dt(data.get("timestamp", "1970-01-01T00:00:00"))
            source = data.get("source", "unknown")
            candidates.append((ts, source, "last-interaction.json"))
        except Exception:
            pass

    today_str = datetime.now().strftime("%Y-%m-%d")
    mem_file = MEMORY_DIR / f"{today_str}.md"
    if mem_file.exists():
        try:
            mtime = datetime.fromtimestamp(mem_file.stat().st_mtime)
            candidates.append((mtime, "file_modified", f"memory/{today_str}.md"))
        except Exception:
            pass

    sessions_dir = Path("/root/.openclaw/agents/main/sessions")
    if sessions_dir.exists():
        try:
            files = sorted(sessions_dir.glob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)
            if files:
                mtime = datetime.fromtimestamp(files[0].stat().st_mtime)
                candidates.append((mtime, "file_modified", f"session/{files[0].name}"))
        except Exception:
            pass

    if not candidates:
        return None, None
    best = max(candidates, key=lambda x: x[0])
    return best[0], best[1]


def update_last_interaction(source="manual"):
    LAST_INTERACTION.parent.mkdir(parents=True, exist_ok=True)
    with open(LAST_INTERACTION, "w") as f:
        json.dump(
            {"timestamp": datetime.now().isoformat(), "source": source},
            f,
            indent=2,
        )
    log_message("INFO", f"交互时间已更新（来源: {source}）")


def get_token_level():
    if TOKEN_TRACKER.exists():
        try:
            with open(TOKEN_TRACKER, "r") as f:
                data = json.load(f)
            display = data.get("display", {})
            level = display.get("level")
            if level:
                return level
            # fallback: legacy dynamic tracker format
            snapshots = data.get("snapshots", [])
            if snapshots:
                return snapshots[-1].get("level", "L1")
            return data.get("current_level", "L1")
        except Exception:
            pass
    return "L1"


def get_token_pct():
    if TOKEN_TRACKER.exists():
        try:
            with open(TOKEN_TRACKER, "r") as f:
                data = json.load(f)
            display = data.get("display", {})
            pct = display.get("display_percentage")
            if pct is not None:
                return float(pct)
            # fallback: legacy dynamic tracker format
            snapshots = data.get("snapshots", [])
            if snapshots:
                return float(snapshots[-1].get("token_consumed_pct", 0.0))
            return float(data.get("token_consumed_pct", 0.0))
        except Exception:
            pass
    return 0.0


def get_token_pace_ratio():
    if TOKEN_TRACKER.exists():
        try:
            with open(TOKEN_TRACKER, "r") as f:
                data = json.load(f)
            display = data.get("display", {})
            return display.get("pace_ratio", 0.0)
        except Exception:
            pass
    return 0.0


def pre_hibernation_checklist():
    report = {
        "C1_session_log": False,
        "C2_memory_ptr": False,
        "C3_task_status": False,
        "C4_code_existence": False,
        "C5_git_snapshot": False,
        "C6_recovery_verify": False,
        "details": [],
    }
    today = datetime.now().strftime("%Y-%m-%d")
    session_log = MEMORY_DIR / f"{today}.md"

    if session_log.exists():
        content = session_log.read_text(encoding="utf-8", errors="ignore")
        report["C1_session_log"] = today in content

    memory_md = WORKSPACE / "MEMORY.md"
    report["C2_memory_ptr"] = memory_md.exists() and memory_md.stat().st_size > 0

    task_master = WORKSPACE / "docs" / "TASK_MASTER.md"
    if not task_master.exists():
        task_master = WORKSPACE / "TASK_MASTER.md"
    report["C3_task_status"] = task_master.exists() and task_master.stat().st_size > 0

    py_files = list(WORKSPACE.glob("*.py"))
    report["C4_code_existence"] = len(py_files) > 0

    try:
        import subprocess
        git_result = subprocess.run(
            ["git", "status", "--short"], cwd=WORKSPACE, capture_output=True, text=True
        )
        report["C5_git_snapshot"] = git_result.returncode == 0
        if git_result.stdout.strip():
            report["details"].append(f"Git 未追踪/未提交: {len(git_result.stdout.strip().splitlines())} 个")
    except Exception as e:
        report["details"].append(f"Git 检查失败: {e}")
        report["C5_git_snapshot"] = False

    try:
        report["C6_recovery_verify"] = session_log.exists() and task_master.exists()
    except Exception as e:
        report["details"].append(f"恢复验证失败: {e}")
        report["C6_recovery_verify"] = False

    all_passed = all(report[k] for k in report if k.startswith("C"))
    return all_passed, report


def resolve_level(elapsed_minutes, token_level, token_pct, pace_ratio, current_level):
    """
    根据交互时间和Token状态，解析当前应该处于哪一级
    规则（从高到低优先级）:
    1. 用户手动强制 turbo -> turbo
    2. 用户手动强制 deep-silent -> deep-silent
    3. Token >= 90% 或 L4 -> deep-silent（绝对阈值，自动生存模式）
    4. Token 70-90% 或 L3 -> silent（绝对阈值，自动低耗模式）
    5. pace_ratio > 1.60 -> deep-silent（相对超支严重）
    6. pace_ratio > 1.30 -> silent（相对超支较快）
    7. 无交互 > 120 分钟 -> deep-silent（自动）
    8. 无交互 > 30 分钟 -> silent
    9. 无交互 > 10 分钟 -> hibernating
    10. 默认 -> normal
    11. turbo 模式下如果超过 turbo_auto_downgrade_minutes 无交互 -> 降级
    """
    forced_reason = None

    # 手动 turbo 只要还在活跃期内就维持
    if current_level == "turbo":
        if elapsed_minutes < THRESHOLDS["turbo_auto_downgrade_minutes"]:
            return "turbo", "manual_turbo_active"
        else:
            return "normal", "turbo_auto_expired"

    # 手动 deep-silent 保持
    if current_level == "deep-silent":
        # 只有检测到交互后才应该唤醒（由 wake 函数处理）
        pass

    # 绝对阈值：作为休眠控制的安全网（不受时间进度影响）
    if token_pct >= 90 or token_level == "L4":
        return "deep-silent", f"token_critical_{token_level}_{token_pct:.1f}%"

    if (token_pct >= 70 and token_pct < 90) or token_level == "L3":
        return "silent", f"token_low_{token_level}_{token_pct:.1f}%"

    # S-曲线 pace_ratio 驱动（与时间进度挂钩）
    if pace_ratio > 1.60:
        return "deep-silent", f"token_pace_severe_{pace_ratio:.2f}"

    if pace_ratio > 1.30:
        return "silent", f"token_pace_fast_{pace_ratio:.2f}"

    if elapsed_minutes > THRESHOLDS["silent_to_deep_minutes"]:
        return "deep-silent", f"inactivity_extended_{elapsed_minutes:.0f}min"

    if elapsed_minutes > THRESHOLDS["hibernating_to_silent_minutes"]:
        return "silent", f"inactivity_silent_{elapsed_minutes:.0f}min"

    if elapsed_minutes > THRESHOLDS["normal_to_hibernating_minutes"]:
        return "hibernating", f"inactivity_hibernating_{elapsed_minutes:.0f}min"

    return "normal", "active"


def level_gate(level, job_id=None, job_name="unknown"):
    """
    五级 gate 策略
    返回值: (allowed: bool, mode: str, reason: str)
    mode: allow | block | minimal | turbo_focus
    """
    policy = LEVELS[level]["gate_policy"]

    is_essential = (
        job_id in ESSENTIAL_JOBS
        or job_name in {"daily-backup", "weekly-essential-snapshot", "weekly-check", "weekly-cloud-backup", "hibernation-check"}
    )
    is_expensive = (
        job_id in EXPENSIVE_JOBS
        or job_name in {"daily-asset-activation", "evening-totem", "token-optimizer"}
    )

    if policy == "allow_all":
        return True, "allow", "normal_mode_allow_all"

    if policy == "turbo_focus":
        # turbo 模式：放行主线高耗任务，但阻断非必要/分散注意力的任务
        if is_essential:
            return True, "allow", "turbo_essential"
        if is_expensive:
            # 高消耗任务在 turbo 下允许，但标记为 turbo_focus
            return True, "turbo_focus", "turbo_mainline_allowed"
        return True, "allow", "turbo_default"

    if policy == "block_expensive":
        if is_essential:
            return True, "allow", "hibernating_essential"
        if is_expensive:
            return False, "block", "hibernating_expensive_blocked"
        return True, "allow", "hibernating_other_allowed"

    if policy == "block_nonessential":
        if is_essential:
            return True, "allow", "silent_essential"
        return False, "block", "silent_nonessential_blocked"

    if policy == "essential_only":
        if is_essential:
            return True, "allow", "deep_silent_essential"
        return False, "block", "deep_silent_blocked"

    return True, "allow", "fallback"


def hibernation_gate(job_id=None, job_name="unknown"):
    """
    兼容旧接口的 gate 命令，返回 exit code:
      0 = 允许执行
      1 = 禁止执行
      2 = 允许但建议极简模式
      3 = turbo_focus（turbo 模式下允许高消耗主线任务）
    """
    state = get_hibernation_state()
    level = state.get("status", "normal")
    allowed, mode, reason = level_gate(level, job_id=job_id, job_name=job_name)

    if allowed:
        if mode == "turbo_focus":
            log_message("INFO", f"Turbo 模式，{job_name} 作为主线任务允许执行")
            return 3
        if mode == "minimal":
            log_message("WARN", f"{job_name} 允许执行但建议极简: {reason}")
            return 2
        log_message("INFO", f"{level} 模式，{job_name} 允许执行: {reason}")
        return 0
    else:
        log_message("INFO", f"{level} 模式，{job_name} 被拦截: {reason}")
        return 1


CRON_JOBS_FILE = Path("/root/.openclaw/cron/jobs.json")
DISABLED_JOBS_REGISTRY = MEMORY_DIR / "hibernation-disabled-jobs-l4.json"


def _load_cron_jobs():
    if not CRON_JOBS_FILE.exists():
        return None
    try:
        with open(CRON_JOBS_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        log_message("WARN", f"读取 cron jobs 失败: {e}")
        return None


def _save_cron_jobs(data):
    try:
        with open(CRON_JOBS_FILE, "w") as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        log_message("WARN", f"写入 cron jobs 失败: {e}")
        return False


def apply_cron_policy(level):
    """根据级别实施 cron 策略：非保活任务在静默期间禁用"""
    if level in ("normal", "turbo"):
        return

    jobs_data = _load_cron_jobs()
    if jobs_data is None:
        return

    disabled_ids = []
    jobs = jobs_data.get("jobs", [])

    for job in jobs:
        jid = job.get("id", "")
        jname = job.get("name", "")
        is_essential = jid in ESSENTIAL_JOBS or jname in {"daily-backup", "weekly-essential-snapshot", "weekly-check", "weekly-cloud-backup", "hibernation-check"}
        is_expensive = jid in EXPENSIVE_JOBS or jname in {"daily-asset-activation", "evening-totem", "token-optimizer"}

        if level == "hibernating":
            if is_expensive and job.get("enabled", True):
                job["enabled"] = False
                disabled_ids.append(jid)
        elif level in ("silent", "deep-silent"):
            if not is_essential and job.get("enabled", True):
                job["enabled"] = False
                disabled_ids.append(jid)

    if disabled_ids:
        existing = []
        if DISABLED_JOBS_REGISTRY.exists():
            try:
                with open(DISABLED_JOBS_REGISTRY, "r") as f:
                    existing = json.load(f)
            except Exception:
                pass
        # 合并去重
        merged = list(set(existing + disabled_ids))
        with open(DISABLED_JOBS_REGISTRY, "w") as f:
            json.dump(merged, f, indent=2)
        _save_cron_jobs(jobs_data)
        log_message("INFO", f"{level} 模式：已禁用 {len(disabled_ids)} 个非保活 cron")


def restore_crons():
    """唤醒时恢复所有被静默禁用的 cron"""
    if not DISABLED_JOBS_REGISTRY.exists():
        return

    try:
        with open(DISABLED_JOBS_REGISTRY, "r") as f:
            to_restore = json.load(f)
    except Exception:
        return

    if not to_restore:
        return

    jobs_data = _load_cron_jobs()
    if jobs_data is None:
        return

    restored_count = 0
    for job in jobs_data.get("jobs", []):
        if job.get("id") in to_restore and not job.get("enabled", True):
            job["enabled"] = True
            restored_count += 1

    if restored_count:
        _save_cron_jobs(jobs_data)
        log_message("INFO", f"已恢复 {restored_count} 个 cron 任务")

    # 清空注册表
    DISABLED_JOBS_REGISTRY.unlink()


def enter_level(level, reason="auto"):
    """进入指定级别，并记录日志"""
    if level not in LEVELS:
        log_message("ERROR", f"未知级别: {level}")
        return None

    old_state = get_hibernation_state()
    old_level = old_state.get("status", "normal")

    if old_level == level:
        log_message("INFO", f"已经在 {level} 模式，无需切换")
        return old_state.get("level_id")

    # 进入静默/深度静默前执行 C1-C6
    if level in ("hibernating", "silent", "deep-silent"):
        ready, report = pre_hibernation_checklist()
        if not ready:
            if not report["C6_recovery_verify"]:
                log_message("ERROR", "C6 失败，阻断静默进入")
                return None
            log_message("WARN", f"前置条件部分未通过: {report['details']}")

        ready_file = MEMORY_DIR / ".silent_mode_ready"
        with open(ready_file, "w") as f:
            json.dump({
                "ready": ready,
                "timestamp": datetime.now().isoformat(),
                "mode": level,
                "reason": reason,
            }, f, indent=2)

    level_id = f"LVL-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    state = {
        "status": level,
        "level_id": level_id,
        "start_time": datetime.now().isoformat(),
        "reason": reason,
        "old_level": old_level,
        "kept_jobs": list(ESSENTIAL_JOBS),
        "paused_jobs": list(EXPENSIVE_JOBS),
    }
    set_hibernation_state(state)
    adjust_hibernation_cron(level)
    apply_cron_policy(level)

    append_hibernation_log({
        "event": "level_change",
        "level_id": level_id,
        "new_level": level,
        "old_level": old_level,
        "reason": reason,
    })

    log_message("INFO", f"已进入 {LEVELS[level]['name']}: {level_id}")
    print(f"\n{LEVELS[level]['emoji']} {LEVELS[level]['name']} 已启动")
    print(f"级别ID: {level_id}")
    print(f"原因: {reason}")
    print(f"策略: {LEVELS[level]['gate_policy']}")
    print(f"心跳间隔: {LEVELS[level]['heartbeat_interval_minutes']} 分钟")
    if old_level != "normal":
        print(f"上一级别: {LEVELS.get(old_level, {}).get('name', old_level)}")
    print()
    return level_id


def wake(source="manual"):
    """从任何静默/休眠/深度静默中唤醒到 normal"""
    state = get_hibernation_state()
    old_level = state.get("status", "normal")

    if old_level == "normal":
        log_message("WARN", "当前已经在 normal 模式，无需唤醒")
        return False

    start_time = state.get("start_time")
    duration_minutes = 0.0
    if start_time:
        duration_minutes = (datetime.now() - _naive_dt(start_time)).total_seconds() / 60

    state["status"] = "normal"
    state["end_time"] = datetime.now().isoformat()
    state["duration_minutes"] = duration_minutes
    state["wake_source"] = source
    state["old_level"] = old_level
    set_hibernation_state(state)
    adjust_hibernation_cron("normal")
    restore_crons()

    append_hibernation_log({
        "event": "wake",
        "level_id": state.get("level_id"),
        "old_level": old_level,
        "duration_minutes": duration_minutes,
        "wake_source": source,
    })

    ready_file = MEMORY_DIR / ".silent_mode_ready"
    if ready_file.exists():
        ready_file.unlink()

    log_message("INFO", f"已从 {old_level} 唤醒，时长: {duration_minutes:.1f}分钟")
    print(f"\n🌅 已唤醒")
    print(f"上一模式: {LEVELS.get(old_level, {}).get('name', old_level)}")
    print(f"时长: {duration_minutes:.1f} 分钟")
    print(f"来源: {source}\n")
    return True


def status():
    state = get_hibernation_state()
    level = state.get("status", "normal")
    info = LEVELS.get(level, LEVELS["normal"])

    print(f"\n{info['emoji']} 五级运行状态 V2.1")
    print("=" * 40)
    print(f"当前级别: {info['name']} ({level})")
    print(f"Token 档位: {get_token_level()}")
    print(f"Token 消耗: {get_token_pct():.1f}%")

    if state.get("level_id"):
        print(f"级别ID: {state['level_id']}")
    if state.get("start_time"):
        start = _naive_dt(state["start_time"])
        duration = datetime.now() - start
        print(f"已持续: {duration.total_seconds()/60:.1f} 分钟")
    if state.get("reason"):
        print(f"原因: {state['reason']}")

    print(f"Gate 策略: {info['gate_policy']}")
    print(f"Cron 策略: {info['cron_policy']}")
    print(f"子代理策略: {info['subagent_policy']}")
    print(f"心跳间隔: {info['heartbeat_interval_minutes']} 分钟")

    last_interaction, last_source = get_last_interaction()
    if last_interaction:
        elapsed = datetime.now() - last_interaction
        print(f"最后交互: {elapsed.total_seconds()/60:.1f} 分钟前 (来源: {last_source})")
    else:
        print("最后交互: 未检测到")
    print("=" * 40)
    print()


def auto_check():
    log_message("INFO", "执行五级自动检测...")

    last_time, last_source = get_last_interaction()
    if last_time is None:
        log_message("WARN", "无法检测最后交互时间，保守处理为维持当前状态")
        return

    elapsed_minutes = (datetime.now() - last_time).total_seconds() / 60
    state = get_hibernation_state()
    current_level = state.get("status", "normal")
    current_reason = state.get("reason", "")
    token_level = get_token_level()
    token_pct = get_token_pct()
    pace_ratio = get_token_pace_ratio()

    log_message("INFO", f"级别={current_level}, 无交互={elapsed_minutes:.1f}min, Token={token_pct:.1f}% ({token_level}), pace={pace_ratio:.2f}, 交互来源={last_source}")

    # === 频率节流：静默模式下按对应心跳间隔 throttle ===
    heartbeat_min = LEVELS[current_level]["heartbeat_interval_minutes"]
    last_check_time = None
    if LAST_AUTO_CHECK.exists():
        try:
            with open(LAST_AUTO_CHECK, "r") as f:
                last_check_time = datetime.fromisoformat(json.load(f).get("timestamp", ""))
        except Exception:
            pass
    if last_check_time:
        if last_check_time.tzinfo:
            last_check_time = last_check_time.replace(tzinfo=None)
        minutes_since_last_check = (datetime.now() - last_check_time).total_seconds() / 60
        if minutes_since_last_check < heartbeat_min:
            log_message("INFO", f"{current_level} 模式节流中，上次检查 {minutes_since_last_check:.1f} 分钟前，心跳间隔 {heartbeat_min} 分钟，本次跳过")
            return

    # turbo 模式下检测到交互应该维持 turbo（直到超时或用户手动退出）
    if current_level == "turbo":
        if elapsed_minutes < THRESHOLDS["turbo_auto_downgrade_minutes"]:
            log_message("INFO", "Turbo 模式活跃期内，维持")
            return
        else:
            log_message("INFO", "Turbo 超时，降级到 normal")
            enter_level("normal", "turbo_auto_expired")
            return

    # 深度静默/静默/休眠：如果检测到真实用户交互，直接唤醒到 normal
    # 关键修复：系统自己的文件修改、agent_turn、cron 运行不算用户交互
    USER_SOURCES = {"user_message", "manual", "user_command", "wake"}
    is_user_triggered = last_source in USER_SOURCES

    if current_level in ("hibernating", "silent", "deep-silent"):
        if elapsed_minutes < THRESHOLDS["normal_to_hibernating_minutes"] and is_user_triggered:
            log_message("INFO", "静默/休眠中检测到近期用户交互，自动唤醒")
            wake(source="auto_interaction_detected")
            return
        else:
            # 如果用户手动进入 deep-silent，auto-check 保持用户意图（不因为系统动作唤醒）
            if current_level == "deep-silent" and current_reason in ("user_command", "manual"):
                # 只在 token 超危险时才强制调整；否则保持 deep-silent
                if token_pct >= 90 or token_level == "L4":
                    log_message("INFO", "Token 临界，保持 deep-silent")
                else:
                    log_message("INFO", "user_command 导致的 deep-silent，无真实用户交互，维持")
                return

            resolved, reason = resolve_level(elapsed_minutes, token_level, token_pct, pace_ratio, current_level)
            if resolved != current_level:
                log_message("INFO", f"静默深度升级: {current_level} -> {resolved} ({reason})")
                enter_level(resolved, reason)
            else:
                log_message("INFO", f"维持 {current_level}")
            return

    # normal 状态：判断是否需要降级
    if current_level == "normal":
        resolved, reason = resolve_level(elapsed_minutes, token_level, token_pct, pace_ratio, current_level)
        if resolved != current_level:
            log_message("INFO", f"自动降级: {current_level} -> {resolved} ({reason})")
            enter_level(resolved, reason)
        else:
            log_message("INFO", "维持 normal 模式")
        return

    # 记录本次执行时间
    LAST_AUTO_CHECK.parent.mkdir(parents=True, exist_ok=True)
    with open(LAST_AUTO_CHECK, "w") as f:
        json.dump({"timestamp": datetime.now().isoformat(), "level": current_level}, f, indent=2)


def main():
    if len(sys.argv) < 2:
        print("Usage: hibernation-control.py [normal|turbo|hibernating|silent|deep-silent|wake|status|auto-check|touch|gate|gate-for]")
        print("       turbo/hibernating/silent/deep-silent [--reason REASON]")
        print("       touch [--source SOURCE]")
        print("       gate --job-id ID --job-name NAME")
        sys.exit(1)

    command = sys.argv[1]

    if command in ("normal", "turbo", "hibernating", "silent", "deep-silent"):
        reason = "manual"
        if "--reason" in sys.argv:
            idx = sys.argv.index("--reason") + 1
            if idx < len(sys.argv):
                reason = sys.argv[idx]
        enter_level(command, reason)

    elif command == "wake":
        source = sys.argv[2] if len(sys.argv) > 2 else "manual"
        wake(source=source)

    elif command == "status":
        status()

    elif command == "auto-check":
        auto_check()

    elif command == "touch":
        source = "manual"
        if "--source" in sys.argv:
            idx = sys.argv.index("--source") + 1
            if idx < len(sys.argv):
                source = sys.argv[idx]
        update_last_interaction(source=source)

    elif command == "gate":
        job_id = None
        job_name = "unknown"
        if "--job-id" in sys.argv:
            idx = sys.argv.index("--job-id") + 1
            if idx < len(sys.argv):
                job_id = sys.argv[idx]
        if "--job-name" in sys.argv:
            idx = sys.argv.index("--job-name") + 1
            if idx < len(sys.argv):
                job_name = sys.argv[idx]
        code = hibernation_gate(job_id=job_id, job_name=job_name)
        sys.exit(code)

    elif command == "gate-for":
        if len(sys.argv) < 3:
            print("Usage: hibernation-control.py gate-for <job_id_or_name>")
            sys.exit(1)
        target = sys.argv[2]
        job_id = target if len(target) > 20 or target.startswith(("a", "e", "i", "o", "u", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9")) else None
        job_name = target if job_id is None else None
        code = hibernation_gate(job_id=job_id, job_name=job_name)
        sys.exit(code)

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
