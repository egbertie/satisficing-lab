#!/usr/bin/env python3
"""
Backup Manager - 满意解决策引擎灾备管理脚本
版本: 3.0
更新日期: 2026-03-18
核心规则: 全量灾备必须包含全部完整资料，时间错开整点
"""

import os
import sys
import json
import shutil
import hashlib
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

# 强制规则配置
BACKUP_RULES = {
    "version": "3.0",
    "last_updated": "2026-03-18",
    "critical_paths": [
        "/root/.openclaw/workspace/A满意哥专属文件夹",  # 全部子目录必须包含
        "/root/.openclaw/workspace/SOUL.md",
        "/root/.openclaw/workspace/USER.md",
        "/root/.openclaw/workspace/MEMORY.md",
        "/root/.openclaw/workspace/memory",
        "/root/.openclaw/workspace/skills",
        "/root/.openclaw/workspace/docs",
        "/root/.openclaw/extensions",
    ],
    "timing_rules": {
        "daily_backup": "01:53",      # 错开整点
        "weekly_backup": "02:47",     # 周日
        "cleanup": "03:42",           # 清理任务
        "offset_strategy": "±13分钟偏移，避开整点和半整点",
    },
    "retention_policy": {
        "daily": 30,   # 日备保留30天
        "weekly": 90,  # 周备保留90天
        "monthly": 365, # 月备保留365天
    },
    "integrity_check": {
        "required": True,
        "methods": ["file_count", "size_checksum", "manifest_verification"],
        "failure_action": "abort_and_alert",
    },
    "mandatory_note": "全量灾备必须包含A满意哥专属文件夹全部资料，不得遗漏任何子目录。这是安全底线。",
}

def verify_critical_paths():
    """验证关键路径完整性"""
    missing = []
    for path in BACKUP_RULES["critical_paths"]:
        if not os.path.exists(path):
            missing.append(path)
    return missing

def generate_manifest(backup_dir):
    """生成备份清单"""
    manifest = {
        "timestamp": datetime.now().isoformat(),
        "version": BACKUP_RULES["version"],
        "paths_backed_up": [],
        "file_count": 0,
        "total_size": 0,
    }
    
    for root, dirs, files in os.walk(backup_dir):
        for file in files:
            filepath = os.path.join(root, file)
            manifest["file_count"] += 1
            manifest["total_size"] += os.path.getsize(filepath)
    
    # 保存清单
    manifest_path = os.path.join(backup_dir, "BACKUP_MANIFEST.json")
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    return manifest

def verify_backup_integrity(backup_dir):
    """验证备份完整性"""
    manifest_path = os.path.join(backup_dir, "BACKUP_MANIFEST.json")
    
    if not os.path.exists(manifest_path):
        return False, "清单文件不存在"
    
    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)
    
    # 验证文件数量
    actual_count = 0
    for root, dirs, files in os.walk(backup_dir):
        actual_count += len(files)
    
    # 排除清单文件本身
    actual_count -= 1
    
    if actual_count != manifest["file_count"]:
        return False, f"文件数量不匹配: 期望{manifest['file_count']}, 实际{actual_count}"
    
    return True, "完整性验证通过"

def backup_daily():
    """执行每日备份"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"/data/backups/daily/backup_{timestamp}"
    
    os.makedirs(backup_dir, exist_ok=True)
    
    # 验证关键路径
    missing = verify_critical_paths()
    if missing:
        raise Exception(f"关键路径缺失: {missing}")
    
    # 执行备份
    for path in BACKUP_RULES["critical_paths"]:
        dest = os.path.join(backup_dir, os.path.basename(path))
        if os.path.isdir(path):
            shutil.copytree(path, dest, dirs_exist_ok=True)
        else:
            shutil.copy2(path, dest)
    
    # 生成清单
    manifest = generate_manifest(backup_dir)
    
    # 验证完整性
    ok, msg = verify_backup_integrity(backup_dir)
    if not ok:
        raise Exception(f"备份完整性验证失败: {msg}")
    
    return {
        "status": "success",
        "backup_dir": backup_dir,
        "file_count": manifest["file_count"],
        "total_size_mb": round(manifest["total_size"] / (1024 * 1024), 2),
    }

def cleanup_old_backups():
    """清理过期备份"""
    now = datetime.now()
    deleted = []
    
    # 清理日备
    daily_dir = "/data/backups/daily"
    if os.path.exists(daily_dir):
        for item in os.listdir(daily_dir):
            item_path = os.path.join(daily_dir, item)
            mtime = datetime.fromtimestamp(os.path.getmtime(item_path))
            if (now - mtime).days > BACKUP_RULES["retention_policy"]["daily"]:
                shutil.rmtree(item_path)
                deleted.append(item)
    
    return {"deleted": deleted, "count": len(deleted)}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: backup_manager.py [backup|cleanup|verify]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "backup":
        result = backup_daily()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif command == "cleanup":
        result = cleanup_old_backups()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif command == "verify":
        # 验证最近一次备份
        daily_dir = "/data/backups/daily"
        if os.path.exists(daily_dir):
            backups = sorted(os.listdir(daily_dir))
            if backups:
                latest = os.path.join(daily_dir, backups[-1])
                ok, msg = verify_backup_integrity(latest)
                print(json.dumps({"verified": ok, "message": msg}, ensure_ascii=False))
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
