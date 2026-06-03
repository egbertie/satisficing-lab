#!/usr/bin/env python3
"""
轻量级管理规则检查脚本 - Token优化版
预计Token消耗: ~50-100/次

使用方法:
    python3 check_management_rules_light.py
"""

import os
import sys
import json
import time
import hashlib
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = Path("/root/.openclaw/workspace")
CACHE_FILE = WORKSPACE / ".cache" / "check_cache.json"

def get_file_mtime(filepath):
    """获取文件修改时间（轻量）"""
    try:
        return os.path.getmtime(filepath)
    except:
        return 0

def get_file_hash(filepath):
    """获取文件指纹（MD5前8位）"""
    try:
        with open(filepath, 'rb') as f:
            return hashlib.md5(f.read(1024)).hexdigest()[:8]
    except:
        return "0"

def load_cache():
    """加载检查缓存"""
    if CACHE_FILE.exists():
        try:
            return json.loads(CACHE_FILE.read_text())
        except:
            pass
    return {}

def save_cache(cache):
    """保存检查缓存"""
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(json.dumps(cache, indent=2))

def check_truth_redline():
    """实事求是红线检查（轻量）"""
    # 只检查错误档案中是否有未纠正的
    errors_dir = WORKSPACE / "diary" / "errors"
    if errors_dir.exists():
        for ef in errors_dir.glob("error_*.md"):
            content = ef.read_text()
            if "- [ ]" in content and "纠正措施" in content:
                return False, f"有未纠正错误: {ef.name}"
    return True, None

def check_task_deadline():
    """任务截止检查（轻量）"""
    # 只检查文件修改时间，不解析内容
    task_master = WORKSPACE / "TASK_MASTER.md"
    if task_master.exists():
        mtime = get_file_mtime(task_master)
        # 如果超过24小时未更新，提醒检查
        if time.time() - mtime > 86400:
            return False, "TASK_MASTER.md超过24小时未更新"
    return True, None

def check_memory_update():
    """记忆更新检查（轻量）"""
    memory_file = WORKSPACE / "MEMORY.md"
    if memory_file.exists():
        mtime = get_file_mtime(memory_file)
        if time.time() - mtime > 86400:
            return False, "MEMORY.md超过24小时未更新"
    return True, None

def run_light_check():
    """执行轻量检查"""
    cache = load_cache()
    current_time = time.time()
    
    # 如果距离上次检查不到1小时，使用缓存
    if cache.get("last_check", 0) > current_time - 3600:
        return cache.get("last_issues", [])
    
    issues = []
    
    # 轻量检查（只检查时间戳，不读全文）
    checks = [
        ("实事求是红线", check_truth_redline),
        ("任务截止", check_task_deadline),
        ("记忆更新", check_memory_update),
    ]
    
    for check_name, check_func in checks:
        passed, error = check_func()
        if not passed:
            issues.append({"check": check_name, "error": error})
    
    # 更新缓存
    cache["last_check"] = current_time
    cache["last_issues"] = issues
    save_cache(cache)
    
    return issues

def format_report(issues):
    """格式化问题报告（极简）"""
    if not issues:
        return None
    
    lines = ["⚠️ 检查发现问题:"]
    for i, issue in enumerate(issues, 1):
        lines.append(f"{i}. [{issue['check']}] {issue['error']}")
    return "\n".join(lines)

if __name__ == "__main__":
    issues = run_light_check()
    report = format_report(issues)
    
    if report:
        print(report)
        sys.exit(1)
    else:
        print("OK")
        sys.exit(0)