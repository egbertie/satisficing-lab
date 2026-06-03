#!/usr/bin/env python3
"""
code_asset_auditor.py
遍历工作区所有 .py 文件，执行 python3 -m py_compile 验证。
排除已知非代码目录（.git、venv、__pycache__、stubs_pending 等）。
生成审计报告，标出所有无法通过语法编译的文件。
返回码: 0 = 全部通过, 1 = 存在失败
"""
import os
import subprocess
import sys
from pathlib import Path

WORKSPACE = Path("/root/.openclaw/workspace")
SKIP_DIRS = {
    ".git", "__pycache__", ".kimi", "venv", "env",
    "node_modules", "archive", "backups", ".openclaw",
    "tmp", "stubs_pending", "skills-archive"
}


def find_py_files():
    for root, dirs, files in os.walk(WORKSPACE):
        root_path = Path(root)
        rel_parts = root_path.relative_to(WORKSPACE).parts
        if any(part in SKIP_DIRS for part in rel_parts):
            dirs[:] = []
            continue
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            if f.endswith(".py"):
                yield root_path.relative_to(WORKSPACE) / f


def main():
    failures = []
    successes = []
    for rel in find_py_files():
        full = WORKSPACE / rel
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", str(full)],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            failures.append((str(rel), result.stderr.strip() or "py_compile failed"))
        else:
            successes.append(str(rel))

    print("# 代码资产审计报告\n")
    print(f"扫描文件总数: {len(successes) + len(failures)}")
    print(f"✅ 通过 py_compile: {len(successes)}")
    print(f"❌ 失败: {len(failures)}\n")

    if failures:
        print("## 编译失败列表（疑似空气代码或语法灾难）\n")
        for path, err in failures:
            print(f"- `{path}`")
            print(f"  错误: `{err}`")
        print("\n**指控**: 上述文件存在于仓库中但无法通过基础语法检查，属于半成品或僵尸代码。")
    else:
        print("## 🟢 全部通过")
        print("")
        print("所有扫描到的 .py 文件均通过 py_compile 基础验证。")

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
