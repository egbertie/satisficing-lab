#!/usr/bin/env python3
"""
bootstrap_guard.py - Bootstrap文件守卫
防止意外覆盖/编辑SOUL.md、USER.md、TOOLS.md、AGENTS.md等核心bootstrap文件
"""

import os
from pathlib import Path
from typing import Optional

# 绝对禁止编辑的bootstrap文件列表（小写文件名用于匹配）
BOOTSTRAP_FILES = {
    "soul.md", "user.md", "tools.md", "agents.md", "bootstrap.md",
    "identity.md", "heartbeat.md",
}

# 允许追加但不能覆盖的bootstrap关联文件
APPEND_ONLY_FILES = {
    "memory.md",
}


class BootstrapGuardError(PermissionError):
    """试图非法修改bootstrap文件时抛出"""
    pass


def _normalize_filename(filepath: str) -> str:
    """提取纯文件名并转为小写"""
    return Path(filepath).name.lower()


def is_bootstrap_file(filepath: str) -> bool:
    """判断目标文件是否为受保护的bootstrap文件"""
    return _normalize_filename(filepath) in BOOTSTRAP_FILES


def is_append_only_file(filepath: str) -> bool:
    """判断目标文件是否为仅允许追加的文件"""
    return _normalize_filename(filepath) in APPEND_ONLY_FILES


def guard(filepath: str, mode: str = "w"):
    """
    检查写入操作是否被允许。
    - 'w'/'x'/'w+' 等覆盖模式对bootstrap文件会触发异常
    - 'a'/'a+' 追加模式对bootstrap文件仍触发异常；对APPEND_ONLY文件允许
    """
    name = _normalize_filename(filepath)
    if name in BOOTSTRAP_FILES:
        raise BootstrapGuardError(
            f"🚨 红线触发：禁止编辑/覆盖bootstrap文件 `{filepath}`。"
            f"该文件为系统身份/记忆/工具定义的核心锚点，任何覆盖都会导致人格解离或记忆丢失。"
        )
    if name in APPEND_ONLY_FILES and "a" not in mode:
        raise BootstrapGuardError(
            f"🚨 红线触发：文件 `{filepath}` 只允许追加（append-only），"
            f"不支持覆盖或截断写入。请使用 'a'/'a+' 模式。"
        )


def safe_write(filepath: str, content: str, mode: str = "w"):
    """
    安全写入文件。会先经过guard检查。
    适用于所有由AI执行的文件写操作。
    """
    guard(filepath, mode)
    with open(filepath, mode, encoding="utf-8") as f:
        f.write(content)


def safe_edit(file_path: str, old_text: str, new_text: str):
    """
    安全编辑文件（替换文本）。
    禁止对bootstrap文件执行任何edit操作。
    """
    guard(file_path, mode="w")
    p = Path(file_path)
    if not p.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")
    original = p.read_text(encoding="utf-8")
    if old_text not in original:
        raise ValueError("old_text在文件中未找到，无法替换")
    updated = original.replace(old_text, new_text, 1)
    p.write_text(updated, encoding="utf-8")
