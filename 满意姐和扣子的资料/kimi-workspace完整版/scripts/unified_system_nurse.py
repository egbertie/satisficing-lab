#!/usr/bin/env python3
"""
unified_system_nurse.py - 统一系统护士
覆盖: 磁盘 / Gateway内存 / Token / Skills / Cron
每日 06:17 运行 + 条件触发清理
"""
import json, os, shutil, subprocess, sys
from pathlib import Path
from datetime import datetime, timedelta

WS = Path("/root/.openclaw/workspace")
MEM = WS / "memory"
REPORT = MEM / f"unified-nurse-report-{datetime.now():%Y%m%d}.json"
THRESH = {"disk_warn":75,"disk_danger":85,"mem_warn":900*1024,"mem_danger":1200*1024,"skills_max":150,"cron_max":15}

# Token S-curve upper limits by day (7-day cycle)
TOKEN_PACE = [0.08, 0.18, 0.32, 0.50, 0.68, 0.85, 1.00]

def log(m): print(f"[{datetime.now():%H:%M:%S}] {m}")

def disk_pct():
    u = shutil.disk_usage("/")
    return round(u.used/u.total*100,1)

def gateway_mem():
    try:
        for line in subprocess.run(["ps","aux"],capture_output=True,text=True,timeout=5).stdout.splitlines():
            if "openclaw-gateway" in line and "grep" not in line:
                return int(line.split()[5])
    except Exception:
        pass
    return 0

def token_state():
    """Returns (actual_pct, time_progress, pace_ratio, day_index) or zeros on failure."""
    try:
        data = json.loads((MEM/"token-zero-tracker.json").read_text())
        display = data.get("display", {})
        actual = display.get("display_percentage") or display.get("week_percent") or data.get("week_percent", 0)
        cycle = data.get("cycle", {})
        start = cycle.get("week_start", "")
        end = cycle.get("week_end", "")
        if start and end:
            start_dt = datetime.fromisoformat(start)
            end_dt = datetime.fromisoformat(end)
            now = datetime.now()
            total = (end_dt - start_dt).total_seconds()
            elapsed = (now - start_dt).total_seconds()
            time_prog = max(0.0, min(1.0, elapsed / total)) if total > 0 else 0.0
        else:
            time_prog = cycle.get("time_progress_pct", 0) / 100.0
        day_idx = min(6, max(0, int(time_prog * 7)))
        expected_upper = TOKEN_PACE[day_idx]
        pace = (actual / 100.0) / expected_upper if expected_upper > 0 else 0.0
        return actual, time_prog, pace, day_idx
    except Exception as e:
        log(f"读取token状态失败: {e}")
        return 0, 0, 0, 0

def skills_count():
    return sum(1 for d in (WS/"skills").iterdir() if d.is_dir())

def cron_count():
    try:
        out = subprocess.run(["crontab","-l"],capture_output=True,text=True,timeout=5).stdout
        return sum(1 for line in out.splitlines() if line.strip() and not line.strip().startswith("#"))
    except:
        return 0

def cleanup_browser():
    p = Path.home()/".openclaw"/"browser"/"openclaw"/"user-data"
    if p.exists():
        shutil.rmtree(p,ignore_errors=True); p.mkdir(parents=True,exist_ok=True)
        return True
    return False

def cleanup_tmp():
    ttl = 3*24*3600; cnt=0; now=datetime.now().timestamp()
    for base in [Path("/tmp"),WS/"tmp",Path.home()/".openclaw"/"tmp"]:
        if not base.exists(): continue
        for f in base.iterdir():
            try:
                if f.is_file() and f.stat().st_mtime < now-ttl:
                    f.unlink(); cnt+=1
            except: pass
    return cnt

def main():
    log("启动")
    # 2026-04-12 修正：先刷新 Token 追踪器，确保读取最新数据（使用 --force-refresh bypass 休眠节流）
    try:
        subprocess.run([sys.executable, str(WS/"scripts/token-tracker-zero.py"), "--force-refresh"], capture_output=True, timeout=60)
    except Exception as e:
        log(f"刷新token追踪器失败: {e}")
    dsk=disk_pct(); mem=gateway_mem()
    tok, time_prog, pace, day_idx = token_state()
    skl=skills_count(); crn=cron_count()
    report={
        "time":datetime.now().isoformat(),
        "checks":{"disk_pct":dsk,"gateway_rss_mb":round(mem/1024,1),"token_pct":tok,"token_time_progress":round(time_prog*100,1),"token_pace_ratio":round(pace,2),"token_day":day_idx+1,"skills":skl,"crons":crn},
        "actions":[],"alerts":[]
    }

    if dsk>=THRESH["disk_warn"]:
        cnt=cleanup_tmp(); report["actions"].append(f"tmp_cleanup:{cnt}")
        log(f"磁盘{dsk}% 清理临时文件 {cnt} 个")
        if dsk>=THRESH["disk_danger"]:
            cleanup_browser(); report["actions"].append("browser_cleanup")
            log("磁盘危险区，browser清理")
            report["alerts"].append(f"🔴 磁盘危险:{dsk}%")
        else:
            report["alerts"].append(f"🟡 磁盘警告:{dsk}%")

    if mem>=THRESH["mem_warn"]:
        report["actions"].append("gateway_memory_alert")
        report["alerts"].append(f"🟡 Gateway内存:{round(mem/1024,1)}MB")
    if mem>=THRESH["mem_danger"]:
        subprocess.Popen(["systemctl","restart","openclaw-gateway"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        report["actions"].append("gateway_restart")
        log("Gateway内存危险，已重启")
        report["alerts"].append(f"🔴 Gateway内存危险:{round(mem/1024,1)}MB")

    # Token pacing logic with time-progress挂钩
    if pace > 1.60:
        report["alerts"].append(f"🔴 Token严重超支: 实际{tok}%, 时间进度{round(time_prog*100,1)}%, 倍率{round(pace,2)}")
    elif pace > 1.30:
        report["alerts"].append(f"🟡 Token消耗偏快: 实际{tok}%, 时间进度{round(time_prog*100,1)}%, 倍率{round(pace,2)}")
    elif time_prog > 0.80 and tok < 60:
        report["alerts"].append(f"🟡 Token可能浪费: 实际{tok}%, 时间进度{round(time_prog*100,1)}%, 建议释放轻量任务")
    elif time_prog > 0.90 and tok < 75:
        report["alerts"].append(f"🔴 Token浪费风险: 实际{tok}%, 时间进度{round(time_prog*100,1)}%, 主动推进积压任务")

    if skl>THRESH["skills_max"]:
        report["alerts"].append(f"🟡 Skills溢出:{skl}")
    if crn>THRESH["cron_max"]:
        report["alerts"].append(f"🟡 Cron溢出:{crn}")

    report["status"] = "🟢 ALL_GREEN" if not report["alerts"] else f"🟡 {len(report['alerts'])}项告警"
    log(report["status"])
    REPORT.write_text(json.dumps(report,indent=2,ensure_ascii=False))
    log(f"报告:{REPORT}")
    return 1 if report["alerts"] else 0

if __name__.startswith("__main__"):
    raise SystemExit(main())
