#!/bin/bash
################################################################################
# Daily Local Backup Script - 本地安全备份
# 蓝军执行 | 2026-04-10
################################################################################

set -euo pipefail

WORKSPACE="/root/.openclaw/workspace"
BACKUP_DIR="$WORKSPACE/backups"
DATE_STR=$(date +%Y%m%d-%H%M%S)
BACKUP_NAME="workspace-backup-${DATE_STR}.tar.gz"
TEMP_BACKUP_PATH="/tmp/$BACKUP_NAME"
BACKUP_PATH="$BACKUP_DIR/$BACKUP_NAME"

# 创建备份目录
mkdir -p "$BACKUP_DIR"

# 排除规则（控制备份体积）
EXCLUDES=(
    --exclude='workspace/backups'
    --exclude='*/__pycache__'
    --exclude='*/.git'
    --exclude='*/node_modules'
    --exclude='workspace/OLD-ARCHIVE-2026'
    --exclude='workspace/archive/md_conversions'
    --exclude='workspace/memory/claw-space-diagnosis-*.md'
    --exclude='workspace/downloads'
    --exclude='workspace/skills/token-optimizer/.token-optimizer-analysis.json'
    --exclude='*/.openclaw/extensions/*/node_modules'
)

# 执行备份（先写到 /tmp，避免自包含问题）
tar -czf "$TEMP_BACKUP_PATH" "${EXCLUDES[@]}" -C "$(dirname "$WORKSPACE")" "$(basename "$WORKSPACE")"

# 移动到最终位置
mv "$TEMP_BACKUP_PATH" "$BACKUP_PATH"

# 计算 SHA-256
SHA256=$(sha256sum "$BACKUP_PATH" | awk '{print $1}')
SIZE=$(du -h "$BACKUP_PATH" | cut -f1)

# 记录到数据库
DB_FILE="$BACKUP_DIR/backup-db.json"
if [ ! -f "$DB_FILE" ]; then
    echo '{"backups":[]}' > "$DB_FILE"
fi

python3 -c "
import json
from datetime import datetime
db_path = '$DB_FILE'
with open(db_path, 'r') as f:
    db = json.load(f)
db['backups'].append({
    'id': 'BK-' + datetime.now().isoformat(),
    'filename': '$BACKUP_NAME',
    'sha256': '$SHA256',
    'size_readable': '$SIZE',
    'timestamp': datetime.now().isoformat(),
    'status': 'completed'
})
# 只保留最近 3 条（P0 磁盘危机后收紧，2026-04-10）
if len(db['backups']) > 3:
    removed = db['backups'][:-3]
    db['backups'] = db['backups'][-3:]
    for b in removed:
        import os
        p = '$BACKUP_DIR/' + b['filename']
        if os.path.exists(p):
            os.remove(p)
with open(db_path, 'w') as f:
    json.dump(db, f, indent=2)
print('备份已记录。当前保留数量:', len(db['backups']))
"

echo "[成功] 每日备份已创建: $BACKUP_PATH ($SIZE)"
echo "[成功] 校验值 SHA-256: $SHA256"
