#!/usr/bin/env python3
"""
disk-guardian.py - 兼容层
已整合到 system-guardian.py，本文件保留以确保下游调用不中断
"""
import subprocess
import sys
from pathlib import Path

SYSTEM_GUARDIAN = Path(__file__).parent / "system-guardian.py"

def main():
    cmd = ["python3", str(SYSTEM_GUARDIAN), "disk"]
    result = subprocess.run(cmd)
    sys.exit(result.returncode)

if __name__ == "__main__":
    main()
