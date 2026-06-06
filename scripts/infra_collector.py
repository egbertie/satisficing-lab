#!/usr/bin/env python3
"""
满意解研究所 · 基础设施状态采集 v1.0
=====================================
在 Mac 本地和腾讯云 CVM 上运行，生成统一格式的 infra_state.json
Cron: 每5分钟运行一次

Mac:   python3 infra_collector.py --role=mac
CVM:   python3 infra_collector.py --role=cvm
"""

import subprocess, json, os, sys, argparse
from datetime import datetime

def run(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout.strip()

def collect_mac():
    """采集 Mac 本地数据"""
    data = {
        "host": {
            "role": "mac",
            "name": run("hostname"),
            "os": run("sw_vers -productName 2>/dev/null || uname -s").strip() + " " + run("sw_vers -productVersion 2>/dev/null || uname -r").strip(),
            "cpu": run("sysctl -n machdep.cpu.brand_string"),
            "cores": int(run("sysctl -n hw.ncpu") or "0"),
            "memory_total_gb": round(int(run("sysctl -n hw.memsize") or "0") / 1024**3, 1),
        },
        "disk": {},
        "services": {
            "openclaw": len([l for l in os.popen("ps aux").readlines() if "openclaw" in l and "grep" not in l]),
            "chrome": len([l for l in os.popen("ps aux").readlines() if "[G]oogle Chrome" in l or "Google Chrome" in l and "grep" not in l]),
        },
        "repo": {
            "commits": int(run("cd /Users/egbertielau/.openclaw/workspace/satisficing-lab && git rev-list --count HEAD") or "0"),
            "last_commit": run("cd /Users/egbertielau/.openclaw/workspace/satisficing-lab && git log -1 --format='%ar'"),
            "remote_main": run("cd /Users/egbertielau/.openclaw/workspace/satisficing-lab && git remote get-url tencent 2>/dev/null || echo 'not set'"),
        },
        "load": {
            "uptime": run("uptime"),
            "load_1m": 0.0, "load_5m": 0.0, "load_15m": 0.0
        },
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    # 磁盘
    for line in run("df -h / /Users").split("\n")[1:]:
        parts = line.split()
        if len(parts) >= 5:
            data["disk"][parts[-1]] = {
                "total": parts[1], "used": parts[2], "avail": parts[3],
                "used_pct": int(parts[4].replace("%","")), "mount": parts[-1]
            }

    # 负载
    upt = run("uptime")
    if "load" in upt:
        loads = upt.split("load averages:")[-1].strip().split()
        if len(loads) >= 3:
            data["load"]["load_1m"] = float(loads[0])
            data["load"]["load_5m"] = float(loads[1])
            data["load"]["load_15m"] = float(loads[2])

    return data

def collect_cvm():
    """采集腾讯云 CVM 数据"""
    data = {
        "host": {
            "role": "cvm",
            "name": run("hostname"),
            "os": run("cat /etc/os-release 2>/dev/null | grep PRETTY_NAME | cut -d= -f2 | tr -d '\"'"),
            "cpu": run("lscpu | grep 'Model name' | sed 's/.*: *//'"),
            "cores": int(run("nproc") or "0"),
            "memory_total_gb": round(float(run("free -h | grep Mem | awk '{print $2}' | sed 's/Gi//'") or "0"), 1),
            "ip_public": "101.33.219.144",
            "ip_private": "172.16.16.3",
            "region": "ap-guangzhou",
            "instance_id": "ins-h3yc7m0w",
        },
        "disk": {},
        "services": {},
        "backups": {},
        "iptables": {},
        "cron": {},
        "feishu": {
            "webhook": False,
            "token": False,
            "bitable": False,
        },
        "load": run("uptime"),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    # 磁盘
    for mp in ["/", "/mnt/datadisk0"]:
        try:
            out = run(f"df -h {mp}").split("\n")[1]
            parts = out.split()
            if len(parts) >= 5:
                data["disk"][mp] = {
                    "total": parts[1], "used": parts[2], "avail": parts[3],
                    "used_pct": int(parts[4].replace("%","")), "mount": mp
                }
        except: pass

    # 服务
    for svc in ["nginx", "sri-api", "sshd"]:
        try:
            active = "active" in run(f"systemctl is-active {svc}")
        except:
            active = False
        data["services"][svc] = active

    # 备份
    try:
        backups_dir = "/mnt/datadisk0/backups"
        files = sorted([f for f in os.listdir(backups_dir) if f.endswith(".tar.gz")])
        if files:
            latest = files[-1]
            size = run(f"ls -lh {backups_dir}/{latest} | awk '{{print $5}}'")
            data["backups"] = {
                "latest_file": latest,
                "latest_size": size,
                "count": len(files),
                "last_backup": run(f"stat -c '%y' {backups_dir}/{latest} | cut -d. -f1")
            }
    except: pass

    # iptables
    try:
        rules_count = run("iptables -L INPUT -n | wc -l")
        policy = run("iptables -L INPUT -n | head -1 | awk '{print $4}'")
        data["iptables"] = {"rules_count": int(rules_count) - 5 if rules_count.isdigit() else 0, "policy": policy}
    except: pass

    # Cron
    try:
        cron_count = run("ls /etc/cron.d/sriserver* | wc -l")
        data["cron"]["count"] = int(cron_count)
    except: pass

    # 飞书
    try:
        env_file = "/etc/sriserver/env"
        if os.path.exists(env_file):
            with open(env_file) as f:
                env_content = f.read()
            data["feishu"]["webhook"] = "FEISHU_WEBHOOK=https://" in env_content
    except: pass

    return data

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--role", choices=["mac", "cvm"], required=True)
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    if args.role == "mac":
        data = collect_mac()
        output = args.output or "/Users/egbertielau/.openclaw/workspace/memory/_data/infra_state_mac.json"
    else:
        data = collect_cvm()
        output = args.output or "/mnt/datadisk0/satisficing-lab/infra_state_cvm.json"

    os.makedirs(os.path.dirname(output), exist_ok=True)
    with open(output, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ {args.role} state → {output}")
