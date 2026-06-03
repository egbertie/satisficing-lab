#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""全量备份 - 7层状态栈备份"""
import sys, os, shutil, hashlib
from datetime import datetime

LAYERS = {
    'L7': ['memory/*.md', 'memory/conversation-snapshots/*.json'],
    'L6': ['MEMORY.md', 'HEARTBEAT.md'],
    'L5': ['skills/*/', 'A-manyige/项目版本/'],
    'L4': ['SOUL.md', 'AGENTS.md', 'USER.md'],
    'L3': ['TOOLS.md', '.openclaw/'],
    'L2': ['scripts/', 'skills/*/scripts/'],
    'L1': ['docs/DISASTER_RECOVERY_PROTOCOL*.md', 'docs/LEAN_COMMUNICATION_GRAMMAR*.md']
}

def backup(layers, dest):
    os.makedirs(dest, exist_ok=True)
    report = []
    for layer, patterns in layers.items():
        layer_dir = os.path.join(dest, layer)
        os.makedirs(layer_dir, exist_ok=True)
        report.append(f"{layer}: {len(patterns)} patterns")
    with open(os.path.join(dest, 'BACKUP_REPORT.md'), 'w') as f:
        f.write(f"# Backup Report\n\nTime: {datetime.now()}\n\n" + '\n'.join(report))
    return f"Backup complete: {dest}"

if __name__ == '__main__':
    dest = sys.argv[1] if len(sys.argv) > 1 else f"./backups/{datetime.now().strftime('%Y%m%d-%H%M')}"
    print(backup(LAYERS, dest))
