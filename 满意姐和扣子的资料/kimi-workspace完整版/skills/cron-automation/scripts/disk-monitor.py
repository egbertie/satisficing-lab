#!/usr/bin/env python3
"""
磁盘监控任务
"""
from datetime import datetime
import shutil

print(f"[{datetime.now().isoformat()}] 磁盘监控任务")
disk = shutil.disk_usage('/')
usage_pct = (disk.used / disk.total) * 100
print(f"- 磁盘使用率: {usage_pct:.1f}%")
print(f"- 可用空间: {disk.free / (1024**3):.1f} GB")
if usage_pct > 85:
    print("⚠️ 警告: 磁盘使用率超过85%")
print("任务完成")
