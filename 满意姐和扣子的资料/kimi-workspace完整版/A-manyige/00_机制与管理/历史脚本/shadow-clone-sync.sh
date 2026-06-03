#!/bin/bash
# Shadow Clone - 影子克隆同步脚本
# 每10分钟同步一次到备份目录

SOURCE_DIR="/root/.openclaw/workspace"
SHADOW_DIR="/root/.openclaw/workspace/shadow-clone"
LOG_FILE="/var/log/shadow-clone.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# 确保影子目录存在
mkdir -p "$SHADOW_DIR"

# 执行同步（排除日志、临时文件和备份目录本身）
rsync -avz --delete \
  --exclude='.git/objects' \
  --exclude='logs/' \
  --exclude='tmp/' \
  --exclude='*.log' \
  --exclude='shadow-clone/' \
  "$SOURCE_DIR/" "$SHADOW_DIR/" 2>/dev/null

# 记录同步状态
if [ $? -eq 0 ]; then
    echo "[$TIMESTAMP] SYNC_OK - Shadow clone updated" >> "$LOG_FILE"
    # 写入健康检查文件
    echo "$TIMESTAMP" > "$SHADOW_DIR/.last-sync"
else
    echo "[$TIMESTAMP] SYNC_FAIL - Check rsync" >> "$LOG_FILE"
fi
