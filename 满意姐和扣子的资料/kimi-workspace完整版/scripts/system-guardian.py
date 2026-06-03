#!/usr/bin/env python3
"""
System Guardian V1.0 - 系统健康统一守护中枢
生效日期: 2026-04-10
蓝军规划执行 | 满意姐监督

整合范围：
- 磁盘监控与清理（原 disk-guardian.py）
- 内存监控与告警
- Token 经济监控（读取 token-zero-tracker.json）
- 双经济守门（原 dual-economy-guard.py）
- 休眠级别监控（原 hibernation-control.py 状态）
- 基线错误率监控
- 全盘清理指令支持

使用方式:
  python3 system-guardian.py auto           # 自动巡检，发现超标自动清理
  python3 system-guardian.py scan           # 全盘扫描，输出健康报告
  python3 system-guardian.py full-clean     # 主动触发"全盘清理"
  python3 system-guardian.py disk           # 仅清理磁盘
  python3 system-guardian.py gate --job-id ID --job-name NAME   # 双经济守门
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import glob
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = Path("/root/.openclaw/workspace")
MEMORY_DIR = WORKSPACE / "memory"
REPORTS_DIR = WORKSPACE / "skills/baseline-checker/reports"

# ======== 红线阈值 ========
THRESHOLDS = {
    "disk_warning": 75.0,    # %
    "disk_danger": 85.0,     # %
    "disk_critical": 93.0,   # %
    "memory_warning": 900.0, # MB
    "memory_danger": 1200.0, # MB
    "token_warning": 70.0,   # %
    "token_danger": 90.0,    # %
}

# ======== 通用工具 ========
def now():
    return datetime.now().isoformat()


def log(level, msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] [{level}] {msg}")


def safe_remove(path):
    try:
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)
        return True
    except Exception as e:
        log("WARN", f"删除失败 {path}: {e}")
        return False


# ======== 状态读取 ========
def get_disk_state():
    usage = shutil.disk_usage("/")
    pct = usage.used / usage.total * 100
    return {
        "percent": round(pct, 1),
        "used_gb": round(usage.used / (1024**3), 1),
        "free_gb": round(usage.free / (1024**3), 1),
        "total_gb": round(usage.total / (1024**3), 1),
        "status": "PASS" if pct < THRESHOLDS["disk_warning"] else "WARNING" if pct < THRESHOLDS["disk_danger"] else "VIOLATION",
    }


def get_memory_state():
    gateway_mem_mb = None
    try:
        import psutil
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'memory_info']):
            name = proc.info['name'] or ''
            cmdline = ' '.join(proc.info['cmdline'] or [])
            if name == 'openclaw-gateway' or 'openclaw-gateway' in cmdline or (name == 'node' and 'openclaw' in cmdline):
                gateway_mem_mb = proc.info['memory_info'].rss / 1024 / 1024
                break
    except Exception:
        pass
    if gateway_mem_mb is None:
        # fallback: 当前进程
        try:
            import psutil
            gateway_mem_mb = psutil.Process().memory_info().rss / 1024 / 1024
        except Exception:
            gateway_mem_mb = 0.0
    return {
        "mb": round(gateway_mem_mb, 2),
        "status": "PASS" if gateway_mem_mb < THRESHOLDS["memory_warning"] else "WARNING" if gateway_mem_mb < THRESHOLDS["memory_danger"] else "VIOLATION",
    }


def get_token_state():
    tracker = MEMORY_DIR / "token-zero-tracker.json"
    if tracker.exists():
        try:
            with open(tracker, 'r') as f:
                data = json.load(f)
            display = data.get("display", {})
            pct = display.get("display_percentage", 0.0) or 0.0
            level = display.get("level", "L1") or "L1"
            pace = display.get("pace_ratio", 0.0) or 0.0
            time_prog = display.get("time_progress_pct", data.get("cycle", {}).get("time_progress_pct", 0.0)) or 0.0
            # Unified guardian uses absolute thresholds as safety net; pace logic lives in unified_system_nurse.py
            return {
                "percent": round(float(pct), 1),
                "level": level,
                "pace_ratio": round(float(pace), 2),
                "time_progress_pct": round(float(time_prog), 1),
                "status": "PASS" if float(pct) < THRESHOLDS["token_warning"] else "WARNING" if float(pct) < THRESHOLDS["token_danger"] else "VIOLATION",
            }
        except Exception as e:
            log("WARN", f"读取 token tracker 失败: {e}")
    return {"percent": 0.0, "level": "L1", "pace_ratio": 0.0, "time_progress_pct": 0.0, "status": "UNKNOWN"}


def get_hibernation_state():
    state_file = MEMORY_DIR / "hibernation-state.json"
    if state_file.exists():
        try:
            with open(state_file, 'r') as f:
                data = json.load(f)
            return {
                "level": data.get("status", "normal"),
                "reason": data.get("reason", "unknown"),
            }
        except Exception:
            pass
    return {"level": "normal", "reason": "default"}


def get_baseline_error_rate():
    # 读取最新的基线检查报告
    reports = sorted(REPORTS_DIR.glob("baseline-check-*.json"), reverse=True)
    if reports:
        try:
            with open(reports[0], 'r') as f:
                data = json.load(f)
            perf = data.get("categories", {}).get("performance", {})
            for ind in perf.get("indicators", []):
                if ind.get("name") == "error_rate_percent":
                    actual = ind.get("actual", 0)
                    status = ind.get("status", "PASS")
                    return {"percent": actual, "status": status}
        except Exception:
            pass
    return {"percent": None, "status": "UNKNOWN"}


# ======== 清理模块 ========
def clean_git_tmp_packs():
    freed = 0
    git_pack = WORKSPACE / ".git" / "objects" / "pack"
    for f in glob.glob(str(git_pack / "tmp_pack_*")):
        freed += os.path.getsize(f)
        safe_remove(f)
    return freed


def clean_tmp_backups():
    freed = 0
    patterns = [
        "/tmp/workspace-backup-*.tar.gz",
        "/tmp/workspace_*.tar.gz",
        str(WORKSPACE / "tmp/*.tar.gz"),
    ]
    for pattern in patterns:
        for path in glob.glob(pattern):
            age_days = (datetime.now() - datetime.fromtimestamp(os.path.getmtime(path))).days
            if age_days >= 1:
                freed += os.path.getsize(path)
                safe_remove(path)
    return freed


def clean_backup_parts():
    freed = 0
    backup_dir = WORKSPACE / "backups"
    for path in glob.glob(str(backup_dir / "*.part-*")):
        freed += os.path.getsize(path)
        safe_remove(path)
    return freed


def clean_kimi_downloads():
    freed = 0
    dl_dir = WORKSPACE / ".kimi/downloads"
    for ext in ["*.pdf", "*.docx", "*.png", "*.jpg"]:
        for path in glob.glob(str(dl_dir / ext)):
            age_days = (datetime.now() - datetime.fromtimestamp(os.path.getmtime(path))).days
            if age_days >= 1 or os.path.getsize(path) > 5 * 1024 * 1024:
                freed += os.path.getsize(path)
                safe_remove(path)
    return freed


def clean_old_backups():
    backup_dir = WORKSPACE / "backups"
    freed = 0
    if not backup_dir.exists():
        return freed
    files = glob.glob(str(backup_dir / "workspace-backup-*.tar.gz"))
    files.sort()
    to_keep = set(files[-3:]) if len(files) > 3 else set(files)
    for f in files:
        if f not in to_keep:
            freed += os.path.getsize(f)
            safe_remove(f)
    return freed


def compress_logs():
    try:
        subprocess.run("find /var/log/ -name '*.log.*' -type f ! -name '*.gz' -exec gzip -9 {} +", shell=True, timeout=30, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass


def run_git_gc_if_needed(disk_pct):
    if disk_pct >= THRESHOLDS["disk_danger"]:
        log("INFO", "磁盘超红线，触发 git gc...")
        try:
            subprocess.run(["git", "gc", "--prune=now"], cwd=WORKSPACE, timeout=180, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except Exception as e:
            log("WARN", f"git gc 失败: {e}")
    return False


def kill_zombie_sessions():
    """清理超时或死掉的子代理会话"""
    log("INFO", "检查僵尸会话...")
    try:
        result = subprocess.run(["openclaw", "sessions", "list", "--limit", "50"], capture_output=True, text=True, timeout=15)
        # 这里只做日志记录，实际清理交给子代理管理协议
        return 0
    except Exception:
        return 0


# ======== 核心动作 ========
def do_full_cleanup():
    log("INFO", "开始全盘清理...")
    freed = 0
    freed += clean_git_tmp_packs()
    freed += clean_tmp_backups()
    freed += clean_backup_parts()
    freed += clean_kimi_downloads()
    freed += clean_old_backups()
    compress_logs()
    kill_zombie_sessions()
    disk = get_disk_state()
    run_git_gc_if_needed(disk["percent"])
    disk_after = get_disk_state()
    freed_mb = freed / (1024**2)
    log("INFO", f"全盘清理完成。释放约 {freed_mb:.1f}MB。磁盘: {disk['percent']}% -> {disk_after['percent']}%")
    return freed_mb, disk_after


def do_disk_cleanup():
    log("INFO", "开始磁盘专项清理...")
    freed = 0
    freed += clean_git_tmp_packs()
    freed += clean_tmp_backups()
    freed += clean_backup_parts()
    freed += clean_kimi_downloads()
    freed += clean_old_backups()
    compress_logs()
    disk = get_disk_state()
    run_git_gc_if_needed(disk["percent"])
    disk_after = get_disk_state()
    freed_mb = freed / (1024**2)
    log("INFO", f"磁盘清理完成。释放约 {freed_mb:.1f}MB。磁盘: {disk['percent']}% -> {disk_after['percent']}%")
    return freed_mb, disk_after


def do_auto_check_and_cleanup():
    """自动模式：发现任何红线自动清理"""
    report = do_scan()
    actions_taken = []
    if report["disk"]["status"] in ("WARNING", "VIOLATION"):
        do_disk_cleanup()
        actions_taken.append("disk_cleanup")
    if report["memory"]["status"] in ("WARNING", "VIOLATION"):
        # Gateway 内存过高时主动重启（P0 机制化）
        log("WARN", f"Gateway 内存告警 ({report['memory']['mb']:.0f}MB)，启动自动重启...")
        subprocess.run(["openclaw", "gateway", "restart"], capture_output=True)
        actions_taken.append("gateway_restart")
    if report["token"]["status"] in ("WARNING", "VIOLATION"):
        actions_taken.append("token_alert")

    # 记录 guardian 日志
    log_file = MEMORY_DIR / "system-guardian-log.json"
    history = []
    if log_file.exists():
        try:
            with open(log_file, 'r') as f:
                history = json.load(f)
        except Exception:
            history = []
    history.append({
        "timestamp": now(),
        "mode": "auto",
        "actions": actions_taken,
        "report": report,
    })
    history = history[-200:]
    log_file.parent.mkdir(parents=True, exist_ok=True)
    with open(log_file, 'w') as f:
        json.dump(history, f, indent=2)

    log("INFO", f"自动巡检完成。动作: {actions_taken}")
    return report, actions_taken


# ======== 扫描 / 报告 ========
def do_scan():
    report = {
        "timestamp": now(),
        "disk": get_disk_state(),
        "memory": get_memory_state(),
        "token": get_token_state(),
        "hibernation": get_hibernation_state(),
        "error_rate": get_baseline_error_rate(),
    }
    return report


def print_scan_report(report):
    print("\n" + "=" * 60)
    print("🛡️  System Guardian 系统健康扫描报告")
    print("=" * 60)
    d = report["disk"]
    icon = "✅" if d["status"] == "PASS" else "🟡" if d["status"] == "WARNING" else "🔴"
    print(f"{icon} 磁盘: {d['percent']}% ({d['used_gb']}G / {d['total_gb']}G), 可用 {d['free_gb']}G")

    m = report["memory"]
    icon = "✅" if m["status"] == "PASS" else "🟡" if m["status"] == "WARNING" else "🔴"
    print(f"{icon} 内存: {m['mb']:.1f} MB")

    t = report["token"]
    icon = "✅" if t["status"] == "PASS" else "🟡" if t["status"] == "WARNING" else "🔴"
    print(f"{icon} Token: {t['percent']}% (level: {t['level']}, pace: {t['pace_ratio']}, time_prog: {t['time_progress_pct']}%)")

    h = report["hibernation"]
    print(f"💤 休眠级别: {h['level']} ({h['reason']})")

    e = report["error_rate"]
    icon = "✅" if e["status"] == "PASS" else "🟡" if e["status"] == "WARNING" else "🔴" if e["status"] == "VIOLATION" else "⚪"
    val = f"{e['percent']}%" if e["percent"] is not None else "N/A"
    print(f"{icon} 基线错误率: {val}")
    print("=" * 60)


# ======== 双经济守门（兼容 dual-economy-guard.py） ========
def do_gate(job_id, job_name, essential_override):
    hibernation = get_hibernation_state()
    level = hibernation.get("level", "normal")

    ESSENTIAL_JOBS = {
        "a9a9abbf-8848-451a-b00c-c2ee0bdf9c2e",  # daily-backup
        "49811b9f-82cb-4a85-a17d-315e7de0fe52",  # weekly-essential-snapshot
        "9c44bc69-b6d0-4f9f-b15b-cd87e24f54fe",  # weekly-check
        "3cf8e9f2-08c1-4438-b6bc-22eafd20513b",  # weekly-cloud-backup
        "8631dfb5-ebbf-4baa-84de-674b9cd26768",  # hibernation-check
        "61cfb1fc-c308-4b0e-a005-aec9f82ef4f3",  # disk-guardian / system-guardian
    }
    EXPENSIVE_JOBS = {
        "a8f9fecf-a825-40d0-bab3-5e5165ea20a4": "daily-asset-activation",
        "6828c851-dc8f-4c04-b942-d6b8d267bc5c": "evening-totem",
        "ea4ef0ad-337b-4e5c-90be-dcb7f3db9f90": "token-optimizer",
    }

    job_name = job_name or EXPENSIVE_JOBS.get(job_id, "unknown")
    is_essential = essential_override or job_id in ESSENTIAL_JOBS
    is_expensive = job_id in EXPENSIVE_JOBS

    LEVEL_POLICIES = {
        "normal": {"gate": "allow_all"},
        "turbo": {"gate": "turbo_focus"},
        "hibernating": {"gate": "block_expensive"},
        "silent": {"gate": "block_nonessential"},
        "deep-silent": {"gate": "essential_only"},
    }

    policy = LEVEL_POLICIES.get(level, LEVEL_POLICIES["normal"])
    gate = policy["gate"]

    # 保活任务直接放行
    if is_essential:
        print(f"✅ {job_name} 为保活任务，直接放行")
        sys.exit(0)

    if gate == "allow_all" or (gate == "turbo_focus" and is_expensive):
        print(f"✅ {job_name} 放行（{level} 模式）")
        sys.exit(0)
    elif gate == "block_expensive" and is_expensive:
        print(f"🌙 系统处于休眠模式，{job_name} 被拦截")
        sys.exit(1)
    elif gate == "block_nonessential":
        print(f"🤫 系统处于静默模式，{job_name} 被拦截")
        sys.exit(1)
    elif gate == "essential_only":
        print(f"🪦 系统处于深度静默模式，{job_name} 被拦截")
        sys.exit(1)

    print(f"✅ {job_name} 放行（{level} 模式）")
    sys.exit(0)


# ======== CLI ========
def main():
    parser = argparse.ArgumentParser(description="System Guardian V1.0 系统健康守护中枢")
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    subparsers.add_parser("scan", help="全盘健康扫描")
    subparsers.add_parser("full-clean", help="主动全盘清理")
    subparsers.add_parser("disk", help="磁盘专项清理")
    subparsers.add_parser("auto", help="自动巡检并按需清理")

    gate_parser = subparsers.add_parser("gate", help="双经济守门检查")
    gate_parser.add_argument("--job-id", default="")
    gate_parser.add_argument("--job-name", default="")
    gate_parser.add_argument("--essential", action="store_true")

    args = parser.parse_args()

    if args.command == "scan":
        report = do_scan()
        print_scan_report(report)
        return 0

    elif args.command == "full-clean":
        freed_mb, disk_after = do_full_cleanup()
        print(f"\n全盘清理完成。释放约 {freed_mb:.1f}MB。当前磁盘: {disk_after['percent']}%")
        return 0

    elif args.command == "disk":
        freed_mb, disk_after = do_disk_cleanup()
        print(f"\n磁盘清理完成。释放约 {freed_mb:.1f}MB。当前磁盘: {disk_after['percent']}%")
        return 0

    elif args.command == "auto":
        report, actions = do_auto_check_and_cleanup()
        print_scan_report(report)
        if actions:
            print(f"自动执行动作: {actions}")
        else:
            print("无需自动清理")
        # 如有严重违规返回非0
        severe = any(report[k]["status"] == "VIOLATION" for k in ("disk", "memory", "token"))
        return 2 if severe else 0

    elif args.command == "gate":
        do_gate(args.job_id, args.job_name, args.essential)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
