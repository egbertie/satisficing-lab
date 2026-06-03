#!/usr/bin/env python3
"""
双经济守门员 - 兼容层
已整合到 system-guardian.py，本文件保留以确保下游调用不中断
"""
import subprocess
import sys
from pathlib import Path

SYSTEM_GUARDIAN = Path(__file__).parent / "system-guardian.py"

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Dual Economy Cron Guard (compat layer)")
    parser.add_argument("--job-id", default="")
    parser.add_argument("--job-name", default="")
    parser.add_argument("--essential", action="store_true")
    args = parser.parse_args()

    cmd = [
        "python3", str(SYSTEM_GUARDIAN), "gate",
        "--job-id", args.job_id,
        "--job-name", args.job_name,
    ]
    if args.essential:
        cmd.append("--essential")

    result = subprocess.run(cmd)
    sys.exit(result.returncode)

if __name__ == "__main__":
    main()
