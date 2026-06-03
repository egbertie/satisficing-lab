#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
todo_ghost_hunter.py
待办幽灵猎人 V1.0

机制用途：在每次汇报待办清单前，自动交叉验证待办项是否真的还未完成。
验证维度：
  1. 代码存在性 —— 目标文件是否存在且非占位/stub状态
  2. 测试状态 —— 对应 pytest 是否已通过
  3. Git 足迹 —— 近期 commit 是否已包含该任务的完成标记

蓝军宪章：没有验证的待办汇报，就是幻觉。
"""

import os
import re
import subprocess
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

WORKSPACE = "/root/.openclaw/workspace"


@dataclass
class TodoItem:
    text: str
    file_hint: Optional[str] = None
    test_hint: Optional[str] = None
    keyword_hint: Optional[str] = None


class TodoGhostHunter:
    """待办幽灵猎人 —— 交叉验证待办项真实性"""

    COMMON_FILE_PATTERNS = [
        r"([a-zA-Z_][a-zA-Z0-9_]*\.py)",
        r"`([a-zA-Z_][a-zA-Z0-9_\-\.]+)`",
    ]

    def __init__(self, workspace: str = WORKSPACE):
        self.workspace = workspace

    def extract_file_hints(self, todo_text: str) -> List[str]:
        hits = []
        for pat in self.COMMON_FILE_PATTERNS:
            hits += re.findall(pat, todo_text)
        # 去重，过滤明显不是文件的
        return list({h for h in hits if "." in h or "_" in h})

    def check_file_existence(self, filename: str) -> Tuple[bool, str]:
        path = os.path.join(self.workspace, filename)
        if not os.path.exists(path):
            return False, f"文件不存在: {filename}"
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        if len(content.strip()) < 100:
            return False, f"文件过短/可能是占位: {filename}"
        # 检查 stub/CONDITIONAL_PASS 标记
        stub_ratio = content.lower().count("stub") / max(len(content), 1)
        if "CONDITIONAL_PASS" in content:
            return False, f"文件仍标记 CONDITIONAL_PASS: {filename}"
        if stub_ratio > 0.005:  # stub 出现频率异常高
            return False, f"文件含大量 stub 标记: {filename}"
        return True, f"文件存在且内容完整: {filename}"

    def check_test_status(self, filename: str) -> Tuple[bool, str]:
        # 推断测试文件名
        base = filename.replace(".py", "")
        test_file = f"test_{base}.py"
        test_path = os.path.join(self.workspace, test_file)
        if not os.path.exists(test_path):
            # 尝试复数或通用测试文件
            alt = f"test_{base.replace('_', '_')}.py"
            if not os.path.exists(os.path.join(self.workspace, alt)):
                return True, f"无对应测试文件: {test_file}（跳过）"
        try:
            result = subprocess.run(
                ["python3", "-m", "pytest", test_path, "-q"],
                cwd=self.workspace,
                capture_output=True,
                text=True,
                timeout=60,
            )
            passed = result.returncode == 0
            return passed, f"pytest {test_file}: {'通过' if passed else '失败'}"
        except Exception as e:
            return False, f"pytest 执行异常: {e}"

    def check_git_footprint(self, keyword: str) -> Tuple[bool, str]:
        try:
            result = subprocess.run(
                ["git", "log", "--oneline", "-10", f"--grep={keyword}"],
                cwd=self.workspace,
                capture_output=True,
                text=True,
                timeout=10,
            )
            hits = [l for l in result.stdout.strip().split("\n") if l.strip()]
            if hits:
                return True, f"Git 近期 commit 含 '{keyword}': {len(hits)} 条"
            # 若 grep 未命中，尝试宽松搜索 diff
            result2 = subprocess.run(
                ["git", "log", "--oneline", "-10", "--all", f"-S{keyword}"],
                cwd=self.workspace,
                capture_output=True,
                text=True,
                timeout=10,
            )
            hits2 = [l for l in result2.stdout.strip().split("\n") if l.strip()]
            found = len(hits2) > 0
            return found, f"Git 代码足迹含 '{keyword}': {'是' if found else '否'}"
        except Exception as e:
            return False, f"Git 查询异常: {e}"

    def hunt(self, todos: List[str]) -> Dict[str, any]:
        """主入口：输入待办文本列表，返回幽灵检测报告"""
        ghosts = []
        real = []
        uncertain = []

        for todo in todos:
            todo = todo.strip()
            if not todo:
                continue

            files = self.extract_file_hints(todo)
            keywords = [re.sub(r"[^\u4e00-\u9fa5a-zA-Z0-9_\-]", "", todo)[:20]]

            evidences = []
            is_ghost = False
            is_real = False

            # 文件存在性检查
            for f in files:
                ok, msg = self.check_file_existence(f)
                evidences.append(msg)
                if ok:
                    is_ghost = True  # 文件都好了，任务可能是幽灵
                else:
                    is_real = True   # 文件确实有问题

                # 测试检查
                test_ok, test_msg = self.check_test_status(f)
                evidences.append(test_msg)
                if test_ok and not msg.startswith("无对应测试文件"):
                    is_ghost = True
                elif not test_ok and not msg.startswith("无对应测试文件"):
                    is_real = True

            # Git 足迹检查
            for kw in keywords:
                git_ok, git_msg = self.check_git_footprint(kw)
                evidences.append(git_msg)
                if git_ok:
                    is_ghost = True

            # 判定逻辑
            if is_ghost and not is_real:
                ghosts.append({"todo": todo, "evidences": evidences})
            elif is_real:
                real.append({"todo": todo, "evidences": evidences})
            else:
                uncertain.append({"todo": todo, "evidences": evidences})

        return {
            "total": len(todos),
            "ghosts": ghosts,
            "real": real,
            "uncertain": uncertain,
            "ghost_count": len(ghosts),
            "real_count": len(real),
            "uncertain_count": len(uncertain),
            "verdict": "存在幽灵任务" if ghosts else "未发现明显幽灵任务",
        }

    def report(self, todos: List[str]) -> str:
        result = self.hunt(todos)
        lines = [
            "# 待办幽灵猎人检测报告",
            "",
            f"**待办总数**: {result['total']}",
            f"**幽灵任务**: {result['ghost_count']}",
            f"**真实待办**: {result['real_count']}",
            f"**不确定**: {result['uncertain_count']}",
            f"**结论**: {result['verdict']}",
            "",
        ]
        if result["ghosts"]:
            lines.append("## 🔴 幽灵任务（建议立即从待办中移除）")
            for g in result["ghosts"]:
                lines.append(f"- **{g['todo']}**")
                for ev in g["evidences"]:
                    lines.append(f"  - {ev}")
            lines.append("")
        if result["real"]:
            lines.append("## 🟢 真实待办（确实未完成）")
            for r in result["real"]:
                lines.append(f"- **{r['todo']}**")
                for ev in r["evidences"]:
                    lines.append(f"  - {ev}")
            lines.append("")
        if result["uncertain"]:
            lines.append("## 🟡 不确定项（需要人工复核）")
            for u in result["uncertain"]:
                lines.append(f"- **{u['todo']}**")
                for ev in u["evidences"]:
                    lines.append(f"  - {ev}")
            lines.append("")
        lines.append("---")
        lines.append("*报告由 todo_ghost_hunter.py 自动生成*")
        return "\n".join(lines)


def demo():
    # 示例：用之前出现的问题任务做演示
    sample_todos = [
        "补齐企业儒学十大观念中缺失的第4（身正令行的领导观）、5（举贤使能的用人观）、8（兼善天下的责任观）项",
        "运行代码资产 confucian_business_wisdom.py 完成功能验证",
        "生成 confucian_business_wisdom.py 闭环报告",
        "将 confucian_business_wisdom.py 登记到 daily_asset_runner.py",
    ]
    hunter = TodoGhostHunter()
    print(hunter.report(sample_todos))


if __name__ == "__main__":
    demo()
