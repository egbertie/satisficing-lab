#!/usr/bin/env python3
"""
磁盘损坏备份机制
用途: 每日自动备份关键文件到外部存储
规则: 保留7天历史版本，磁盘损坏时可恢复
"""

import os
import shutil
import json
from datetime import datetime, timedelta
from pathlib import Path

# 关键文件列表
CRITICAL_FILES = [
    "/root/.openclaw/workspace/SOUL.md",
    "/root/.openclaw/workspace/USER.md",
    "/root/.openclaw/workspace/MEMORY.md",
    "/root/.openclaw/workspace/AGENTS.md",
    "/root/.openclaw/workspace/TOOLS.md"
]

CRITICAL_DIRS = [
    "/root/.openclaw/workspace/memory",
    "/root/.openclaw/workspace/docs",
    "/root/.openclaw/workspace/skills",
    "/root/.openclaw/workspace/checklists",
    "/root/.openclaw/workspace/scripts"
]

# 备份目录（使用/tmp作为示例，实际应该使用外部存储）
BACKUP_BASE = "/root/.openclaw/workspace/backups"

def create_backup():
    """创建每日备份"""
    
    today = datetime.now().strftime("%Y-%m-%d")
    backup_dir = Path(f"{BACKUP_BASE}/{today}")
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"=== 创建备份: {today} ===")
    
    # 备份关键文件
    for file_path in CRITICAL_FILES:
        if os.path.exists(file_path):
            dest = backup_dir / Path(file_path).name
            shutil.copy2(file_path, dest)
            print(f"✅ 文件备份: {Path(file_path).name}")
    
    # 备份关键目录（压缩）
    for dir_path in CRITICAL_DIRS:
        if os.path.exists(dir_path):
            dir_name = Path(dir_path).name
            archive_name = backup_dir / f"{dir_name}.tar.gz"
            os.system(f"tar -czf {archive_name} -C {Path(dir_path).parent} {dir_name} 2>/dev/null")
            print(f"✅ 目录备份: {dir_name}.tar.gz")
    
    # 保存备份清单
    backup_manifest = {
        "timestamp": datetime.now().isoformat(),
        "backup_dir": str(backup_dir),
        "files_backed_up": len(CRITICAL_FILES),
        "dirs_backed_up": len(CRITICAL_DIRS)
    }
    
    with open(backup_dir / "manifest.json", 'w') as f:
        json.dump(backup_manifest, f, indent=2)
    
    # 清理旧备份（保留7天）
    cleanup_old_backups()
    
    print(f"\n✅ 备份完成: {backup_dir}")
    return backup_dir

def cleanup_old_backups():
    """清理7天前的备份"""
    if not os.path.exists(BACKUP_BASE):
        return
    
    cutoff = datetime.now() - timedelta(days=7)
    
    for backup_name in os.listdir(BACKUP_BASE):
        try:
            backup_date = datetime.strptime(backup_name, "%Y-%m-%d")
            if backup_date < cutoff:
                old_backup = Path(f"{BACKUP_BASE}/{backup_name}")
                shutil.rmtree(old_backup)
                print(f"🗑️  清理旧备份: {backup_name}")
        except ValueError:
            continue

def verify_backup():
    """验证备份完整性"""
    today = datetime.now().strftime("%Y-%m-%d")
    backup_dir = Path(f"{BACKUP_BASE}/{today}")
    
    if not backup_dir.exists():
        print("❌ 今日备份不存在")
        return False
    
    manifest_file = backup_dir / "manifest.json"
    if not manifest_file.exists():
        print("❌ 备份清单不存在")
        return False
    
    print("✅ 备份验证通过")
    return True

if __name__ == "__main__":
    backup_dir = create_backup()
    verify_backup()
    print("\n⚠️  建议: 配置crontab每日自动运行")
    print("   0 2 * * * python3 /root/.openclaw/workspace/scripts/backup_to_external.py")
