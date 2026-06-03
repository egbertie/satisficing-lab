#!/usr/bin/env python3
"""
配置版本控制
用途: 对核心文件进行版本控制，每次修改前自动备份
规则: 保留最近10个版本，可回滚
"""

import os
import shutil
import json
from datetime import datetime
from pathlib import Path

# 需要版本控制的核心文件
VERSIONED_FILES = [
    "/root/.openclaw/workspace/SOUL.md",
    "/root/.openclaw/workspace/USER.md",
    "/root/.openclaw/workspace/MEMORY.md",
    "/root/.openclaw/workspace/HEARTBEAT.md"
]

# 版本控制目录
VERSION_DIR = "/root/.openclaw/workspace/.versions"
MAX_VERSIONS = 10

def create_version(file_path):
    """为文件创建新版本"""
    
    file_path = Path(file_path)
    if not file_path.exists():
        print(f"❌ 文件不存在: {file_path}")
        return None
    
    # 创建版本目录
    file_name = file_path.stem
    file_version_dir = Path(f"{VERSION_DIR}/{file_name}")
    file_version_dir.mkdir(parents=True, exist_ok=True)
    
    # 生成版本号
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    version_file = file_version_dir / f"{file_name}_{timestamp}.md"
    
    # 复制文件
    shutil.copy2(file_path, version_file)
    
    # 更新版本清单
    manifest_file = file_version_dir / "manifest.json"
    versions = []
    if manifest_file.exists():
        with open(manifest_file, 'r') as f:
            versions = json.load(f)
    
    versions.append({
        "timestamp": timestamp,
        "file": str(version_file),
        "size": os.path.getsize(file_path)
    })
    
    # 只保留最近10个版本
    if len(versions) > MAX_VERSIONS:
        old_version = versions.pop(0)
        if os.path.exists(old_version["file"]):
            os.remove(old_version["file"])
    
    with open(manifest_file, 'w') as f:
        json.dump(versions, f, indent=2)
    
    print(f"✅ 版本创建: {file_name}@{timestamp}")
    return version_file

def rollback(file_name, version_timestamp=None):
    """回滚到指定版本"""
    
    file_version_dir = Path(f"{VERSION_DIR}/{file_name}")
    manifest_file = file_version_dir / "manifest.json"
    
    if not manifest_file.exists():
        print(f"❌ 无版本历史: {file_name}")
        return False
    
    with open(manifest_file, 'r') as f:
        versions = json.load(f)
    
    if version_timestamp:
        # 回滚到指定版本
        target = next((v for v in versions if v["timestamp"] == version_timestamp), None)
    else:
        # 回滚到上一个版本
        target = versions[-2] if len(versions) >= 2 else None
    
    if not target:
        print("❌ 目标版本不存在")
        return False
    
    # 执行回滚
    original_file = Path(f"/root/.openclaw/workspace/{file_name}.md")
    shutil.copy2(target["file"], original_file)
    
    print(f"✅ 回滚完成: {file_name} -> {target['timestamp']}")
    return True

def list_versions(file_name):
    """列出文件的所有版本"""
    
    file_version_dir = Path(f"{VERSION_DIR}/{file_name}")
    manifest_file = file_version_dir / "manifest.json"
    
    if not manifest_file.exists():
        print(f"❌ 无版本历史: {file_name}")
        return
    
    with open(manifest_file, 'r') as f:
        versions = json.load(f)
    
    print(f"=== {file_name} 版本历史 ===")
    for i, v in enumerate(versions, 1):
        print(f"{i}. {v['timestamp']} ({v['size']} bytes)")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 config_version_control.py [backup|rollback|list] [file]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "backup":
        for file_path in VERSIONED_FILES:
            create_version(file_path)
    elif command == "list" and len(sys.argv) >= 3:
        list_versions(sys.argv[2])
    elif command == "rollback" and len(sys.argv) >= 3:
        version = sys.argv[3] if len(sys.argv) > 3 else None
        rollback(sys.argv[2], version)
    else:
        print("未知命令")
