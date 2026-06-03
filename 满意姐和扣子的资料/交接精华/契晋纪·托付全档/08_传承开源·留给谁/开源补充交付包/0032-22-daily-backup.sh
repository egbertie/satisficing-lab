#!/bin/bash
# daily-backup.sh - 每日备份脚本
# 创建于: 2026-04-15
# 频率: 每日04:30

BACKUP_DIR="/backup/daily"
SOURCE_DIR="/root/.openclaw/workspace"
DATE=$(date '+%Y%m%d-%H%M%S')
LOG_FILE="/var/log/openclaw/daily-backup.log"

# 创建备份目录
mkdir -p "$BACKUP_DIR"
mkdir -p "$(dirname $LOG_FILE)"

# 执行备份
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 开始每日备份..." >> "$LOG_FILE"

tar -czf "$BACKUP_DIR/workspace-$DATE.tar.gz" \
    -C "$(dirname $SOURCE_DIR)" \
    --exclude='.git/objects' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    "$(basename $SOURCE_DIR)" 2>> "$LOG_FILE"

if [ $? -eq 0 ]; then
    BACKUP_SIZE=$(du -h "$BACKUP_DIR/workspace-$DATE.tar.gz" | cut -f1)
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ 备份成功: $BACKUP_SIZE" >> "$LOG_FILE"
    
    # 清理旧备份（保留7天）
    find "$BACKUP_DIR" -name "workspace-*.tar.gz" -mtime +7 -delete
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 🧹 已清理7天前的旧备份" >> "$LOG_FILE"
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ❌ 备份失败!" >> "$LOG_FILE"
    exit 1
fi

exit 0
