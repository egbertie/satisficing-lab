#!/usr/bin/env python3
"""
weekly_status_rollup.py
读取 TASK_MASTER.md 与近 7 天 memory 文件，自动生成周报汇总。
输出到 A-manyige/汇报/日报/周报-YYYY-MM-DD.md
返回码: 0
"""
import datetime
import subprocess
from pathlib import Path

TASK_MASTER = Path("/root/.openclaw/workspace/docs/TASK_MASTER.md")
MEMORY_DIR = Path("/root/.openclaw/workspace/memory")
OUTPUT_DIR = Path("/root/.openclaw/workspace/A-manyige/汇报/日报")


def parse_task_master(path: Path):
    total = fin = pending = 0
    lines = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
    for line in lines:
        if "|" not in line:
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 4:
            continue
        status_field = parts[2] if len(parts) > 2 else ""
        if any(s in status_field for s in ("FIN", "✅", "🔄", "待执行", "进行中")):
            total += 1
            if any(s in status_field for s in ("FIN", "✅")):
                fin += 1
            else:
                pending += 1
    return total, fin, pending


def main():
    today = datetime.date.today()
    total, fin, pending = parse_task_master(TASK_MASTER)

    mem_count = 0
    for mem in sorted(MEMORY_DIR.glob("2026-04-*.md")):
        d = mem.stem
        try:
            if (today - datetime.date.fromisoformat(d)).days <= 7:
                mem_count += 1
        except ValueError:
            pass

    report = f"""# 周报汇总 ({today})

## 任务大盘点
- 总任务数: {total}
- 已完成 (FIN): {fin}
- 待执行/进行中: {pending}
- 完成率: {round(fin/total*100, 1) if total else 0}%

## 近期记忆活跃度
- 近 7 天 memory 文件数: {mem_count}

## 系统健康速览
"""

    guardian = Path("/root/.openclaw/workspace/scripts/system-guardian.py")
    if guardian.exists():
        try:
            out = subprocess.run(
                [guardian, "scan"],
                capture_output=True, text=True, timeout=30
            )
            report += f"\n```\n{out.stdout[:1500]}\n```\n"
        except Exception as e:
            report += f"\n系统扫描异常: {e}\n"
    else:
        report += "\n`scripts/system-guardian.py` 未找到，跳过系统扫描。\n"

    report += """
----
*本报告由 weekly_status_rollup.py 自动生成*
"""

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / f"周报-{today}.md"
    out_path.write_text(report, encoding="utf-8")
    print(f"周报已生成: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
