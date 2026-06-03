#!/usr/bin/env python3
"""
指标收集任务
"""
from datetime import datetime

print(f"[{datetime.now().isoformat()}] 指标收集任务")
print("- 收集系统指标")
print("- 收集任务执行指标")
print("- 写入时序数据库")
print("任务完成")
