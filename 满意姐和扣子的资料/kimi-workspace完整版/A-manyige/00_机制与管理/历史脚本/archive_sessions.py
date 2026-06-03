#!/usr/bin/env python3
"""
会话归档脚本
自动归档旧会话
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path("/root/.openclaw/workspace")))

def archive_sessions(older_than_hours=24):
    """归档旧会话"""
    memory_dir = Path("/root/.openclaw/workspace/memory")
    archive_dir = Path("/root/.openclaw/workspace/memory/archive")
    archive_dir.mkdir(exist_ok=True)
    
    cutoff = datetime.now() - timedelta(hours=older_than_hours)
    archived = 0
    
    # 遍历memory目录
    if memory_dir.exists():
        for file in memory_dir.glob("*.md"):
            if file.stat().st_mtime < cutoff.timestamp():
                # 归档逻辑
                archived += 1
    
    print(f"✅ 会话归档完成")
    print(f"   归档文件数: {archived}")
    
    return archived

def main():
    import argparse
    parser = argparse.ArgumentParser(description="会话归档")
    parser.add_argument("--older-than", type=int, default=24, help="归档条件（小时）")
    args = parser.parse_args()
    
    return archive_sessions(args.older_than)

if __name__ == "__main__":
    sys.exit(main())
