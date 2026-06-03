#!/usr/bin/env python3
from __future__ import annotations
"""
claw_space_manager.py
Kimi Claw 空间管理助手 V1.0
基于《03Kimi_Claw_空间不足》的简化可运行实现

功能:
- 分析 /root/.openclaw/workspace 磁盘使用情况
- 识别大文件、旧日志、缓存目录
- 生成清理建议清单
- 提供长期预防措施
- Markdown 空间诊断报告生成
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any

from defense_base_components import BaseComponent


class ClawSpaceManager(BaseComponent):
    """Kimi Claw 空间管理助手"""

    def __init__(self, workspace: str = "/root/.openclaw/workspace"):
        super().__init__("claw_space_manager")
        self.target_workspace = workspace

    def disk_usage(self) -> Dict[str, Any]:
        try:
            stat = os.statvfs(self.target_workspace)
            total = stat.f_blocks * stat.f_frsize
            free = stat.f_bavail * stat.f_frsize
            used = total - free
            return {
                "路径": self.target_workspace,
                "总空间_GB": round(total / (1024 ** 3), 2),
                "已用空间_GB": round(used / (1024 ** 3), 2),
                "可用空间_GB": round(free / (1024 ** 3), 2),
                "使用率_%": round(used / total * 100, 1),
                "健康状态": "健康" if used / total < 0.85 else "告警" if used / total < 0.95 else "危险",
            }
        except Exception as e:
            return {"错误": str(e)}

    def find_large_files(self, top_n: int = 20, min_size_mb: int = 10) -> List[Dict[str, Any]]:
        results = []
        workspace_path = Path(self.target_workspace)
        for path in workspace_path.rglob("*"):
            if path.is_file() and not any(p.startswith(".") for p in path.parts):
                try:
                    size_mb = path.stat().st_size / (1024 * 1024)
                    if size_mb >= min_size_mb:
                        results.append({
                            "文件": str(path.relative_to(workspace_path)),
                            "大小_MB": round(size_mb, 2),
                        })
                except (OSError, PermissionError):
                    continue
        results.sort(key=lambda x: x["大小_MB"], reverse=True)
        return results[:top_n]

    def find_old_logs(self, days: int = 30) -> List[str]:
        old_items = []
        cutoff = datetime.now() - timedelta(days=days)
        workspace_path = Path(self.target_workspace)
        for path in workspace_path.rglob("*"):
            if path.is_file():
                try:
                    if any(k in path.name.lower() for k in ["log", "cache", "tmp", "旧", "backup"]):
                        mtime = datetime.fromtimestamp(path.stat().st_mtime)
                        if mtime < cutoff:
                            old_items.append(str(path.relative_to(workspace_path)))
                except (OSError, PermissionError):
                    continue
        return old_items[:50]

    def cleanup_recommendations(self) -> Dict[str, Any]:
        return {
            "立即清理": [
                "删除 OLD-ARCHIVE-2026 中早于2026-03-01的超大临时文件",
                "清理 memory/ 目录中过期的日志和中间报告",
                "压缩或归档 cognitive_ecosystem/stubs_pending/ 中的未验证代码",
            ],
            "中期优化": [
                "将非活跃项目迁移到外部存储或 Git LFS",
                "设置自动清理脚本，每周删除超过60天的缓存",
            ],
            "长期预防": [
                "保持系统盘 ≥10% 可用空间",
                "每月审查一次大文件分布",
                "对 Kimi-Claw 下载目录设置自动过期策略",
            ],
        }

    def generate_diagnosis_report(self) -> str:
        report = {
            "disk_usage": self.disk_usage(),
            "top_large_files": self.find_large_files(),
            "old_logs": self.find_old_logs(),
            "recommendations": self.cleanup_recommendations(),
        }
        lines = [
            "# Kimi Claw 空间诊断报告",
            f"**诊断时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"**目标路径**: `{self.target_workspace}`",
            "",
            "## 一、磁盘使用情况",
            "```json",
            json.dumps(report["disk_usage"], ensure_ascii=False, indent=2),
            "```",
            "",
            "## 二、大文件 TOP 20",
            "```json",
            json.dumps(report["top_large_files"], ensure_ascii=False, indent=2),
            "```",
            "",
            "## 三、超过 30 天的旧日志/缓存",
            "```json",
            json.dumps(report["old_logs"], ensure_ascii=False, indent=2),
            "```",
            "",
            "## 四、清理建议",
            "```json",
            json.dumps(report["recommendations"], ensure_ascii=False, indent=2),
            "```",
        ]
        report_path = Path(self.target_workspace) / "memory" / f"claw-space-diagnosis-{datetime.now().strftime('%Y%m%d-%H%M')}.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return str(report_path)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Kimi Claw 空间管理助手")
    parser.add_argument("--workspace", default="/root/.openclaw/workspace", help="工作空间路径")
    parser.add_argument("--report", action="store_true", help="生成空间诊断报告")
    args = parser.parse_args()

    manager = ClawSpaceManager(workspace=args.workspace)
    path = manager.generate_diagnosis_report()
    print(f"空间诊断报告已生成: {path}")


if __name__ == "__main__":
    main()
