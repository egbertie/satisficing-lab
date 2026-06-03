#!/bin/bash
# gateway-session-bloat-cleaner.sh
# 清理 OpenClaw Gateway sessions.json 中过期的一次性 cron session，降低启动内存基线
# 版本: 1.0
# 作者: 蓝军 Skeptor-7 | 2026-04-13

set -euo pipefail

SESSIONS_FILE="/root/.openclaw/agents/main/sessions/sessions.json"
BACKUP_DIR="/root/.openclaw/agents/main/sessions/backups"
KEEP_CRON_HOURS=48
DRY_RUN=""

usage() {
    echo "Usage: $0 [--dry-run]"
    echo "  --dry-run    只计算并报告可清理的 session，不实际删除"
    exit 1
}

if [ $# -gt 0 ]; then
    if [ "$1" == "--dry-run" ]; then
        DRY_RUN="yes"
    else
        usage
    fi
fi

if [ ! -f "$SESSIONS_FILE" ]; then
    echo "❌ sessions.json 不存在: $SESSIONS_FILE"
    exit 1
fi

mkdir -p "$BACKUP_DIR"

python3 -c "
import json, sys, os, time

sessions_file = '$SESSIONS_FILE'
keep_hours = int('$KEEP_CRON_HOURS')
dry_run = bool('$DRY_RUN')

with open(sessions_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Find max updatedAt among all entries to establish our 'now' baseline
max_ts = 0
for v in data.values():
    ts = v.get('updatedAt', 0)
    if isinstance(ts, (int, float)) and ts > max_ts:
        max_ts = ts

threshold = max_ts - (keep_hours * 3600 * 1000)

to_delete = []
cron_kept = 0
cron_removed = 0
other_kept = 0
bytes_before = len(json.dumps(data))

for k, v in data.items():
    if ':cron:' in k:
        ts = v.get('updatedAt', 0)
        if isinstance(ts, (int, float)) and ts < threshold:
            to_delete.append(k)
            cron_removed += 1
        else:
            cron_kept += 1
    else:
        other_kept += 1

bytes_freed = sum(len(json.dumps(data[k])) for k in to_delete)

print(f'━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
print(f' Gateway Session Bloat Cleaner Report')
print(f'━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
print(f' 当前总条目数      : {len(data)}')
print(f' Cron 保留数量     : {cron_kept}')
print(f' Cron 拟删除数量   : {cron_removed}')
print(f' 非 Cron 保留数量  : {other_kept}')
print(f' 阈值 (updatedAt <): {threshold} ({keep_hours}h 前)')
print(f' 预估释放 JSON 大小: {bytes_freed / 1024 / 1024:.2f} MB')
print(f' 原 sessions.json   : {bytes_before / 1024 / 1024:.2f} MB')
print(f'━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')

if dry_run:
    print(' [DRY-RUN] 未执行删除。')
    if to_delete:
        print(' 拟删除 keys (前 5 个):')
        for k in to_delete[:5]:
            print(f'   - {k}')
    sys.exit(0)

# Actual cleanup
if not to_delete:
    print(' 无需清理。')
    sys.exit(0)

# Backup
backup_path = os.path.join('$BACKUP_DIR', f'sessions-{int(time.time())}.json')
with open(backup_path, 'w', encoding='utf-8') as f:
    json.dump(data, f)
print(f' 已备份到: {backup_path}')

for k in to_delete:
    del data[k]

with open(sessions_file, 'w', encoding='utf-8') as f:
    json.dump(data, f)

bytes_after = len(json.dumps(data))
print(f' 清理完成。')
print(f' 新 sessions.json   : {bytes_after / 1024 / 1024:.2f} MB')
print(f' 实际释放           : {(bytes_before - bytes_after) / 1024 / 1024:.2f} MB')
"
