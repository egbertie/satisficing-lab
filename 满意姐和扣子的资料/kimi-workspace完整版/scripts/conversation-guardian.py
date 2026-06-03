#!/usr/bin/env python3
"""
conversation-guardian.py - 对话上下文守护
每30分钟保存当前对话状态快照
"""
import json
import os
from datetime import datetime
from pathlib import Path

def save_conversation_snapshot():
    """保存对话快照"""
    snapshot_dir = Path('/root/.openclaw/workspace/memory/conversation-snapshots')
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    
    # 记录快照元数据
    snapshot = {
        'timestamp': timestamp,
        'iso_time': datetime.now().isoformat(),
        'workspace_size': get_workspace_size(),
        'git_commits_today': get_today_commits(),
        'memory_files_count': count_memory_files()
    }
    
    snapshot_file = snapshot_dir / f'snapshot-{timestamp}.json'
    with open(snapshot_file, 'w', encoding='utf-8') as f:
        json.dump(snapshot, f, indent=2, ensure_ascii=False)
    
    # 清理旧快照（保留最近48小时）
    cleanup_old_snapshots(snapshot_dir)
    
    print(f"✅ 对话快照已保存: {snapshot_file.name}")
    return snapshot

def get_workspace_size():
    """获取工作区大小"""
    try:
        import subprocess
        result = subprocess.run(['du', '-sb', '/root/.openclaw/workspace'], 
                              capture_output=True, text=True)
        return int(result.stdout.split()[0])
    except:
        return 0

def get_today_commits():
    """获取今日git提交数"""
    try:
        import subprocess
        today = datetime.now().strftime('%Y-%m-%d')
        result = subprocess.run(
            ['git', '-C', '/root/.openclaw/workspace', 'log', 
             '--since', f'{today} 00:00:00', '--oneline'],
            capture_output=True, text=True
        )
        return len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
    except:
        return 0

def count_memory_files():
    """统计memory目录文件数"""
    try:
        memory_dir = Path('/root/.openclaw/workspace/memory')
        return len(list(memory_dir.glob('**/*'))) if memory_dir.exists() else 0
    except:
        return 0

def cleanup_old_snapshots(snapshot_dir):
    """清理48小时前的快照"""
    import time
    cutoff = time.time() - (48 * 3600)  # 48小时前
    
    for f in snapshot_dir.glob('snapshot-*.json'):
        if f.stat().st_mtime < cutoff:
            f.unlink()

if __name__ == '__main__':
    save_conversation_snapshot()
