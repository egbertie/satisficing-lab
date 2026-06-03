#!/usr/bin/env python3
"""
daily_report_gatekeeper.py
检查 A-manyige/汇报/日报/ 是否在过去 7 天内缺失应生成的日报/资产激活报告/Token周报。
返回码: 0 = 无缺失, 1 = 存在缺失
"""
import os
import re
import datetime

REPORT_DIR = "/root/.openclaw/workspace/A-manyige/汇报/日报"
PATTERNS = [
    r"日报-(\d{{4}}-\d{{2}}-\d{{2}})",
    r"日常资产激活报告-(\d{{4}}-\d{{2}}-\d{{2}})",
    r"Token周报-(\d{{4}}-\d{{2}}-\d{{2}})",
    r"asset-activation-(\d{{4}}-\d{{2}}-\d{{2}})\.md",
]


def main():
    today = datetime.date.today()
    checked = []
    missing = []

    for i in range(1, 8):
        d = today - datetime.timedelta(days=i)
        d_str = d.strftime("%Y-%m-%d")
        checked.append(d_str)
        found = False
        if os.path.isdir(REPORT_DIR):
            for fname in os.listdir(REPORT_DIR):
                for pat in PATTERNS:
                    m = re.search(pat, fname)
                    if m and m.group(1) == d_str:
                        found = True
                        break
                if found:
                    break
        if not found:
            missing.append(d_str)

    print(f"# 日报守门员检查报告 ({today})\n")
    print(f"检查范围: 过去 7 天 {checked}\n")
    if missing:
        print("## 🔴 缺失报告日期")
        print("")
        for d in missing:
            print(f"- `{d}`")
        print("\n**建议**: 立即补录当日日报或资产激活报告。")
    else:
        print("## 🟢 全部命中")
        print("")
        print("过去 7 天每日均有报告落盘。")

    file_count = len(os.listdir(REPORT_DIR)) if os.path.isdir(REPORT_DIR) else 0
    print(f"\n----\n扫描目录内文件总数: {file_count}")
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
