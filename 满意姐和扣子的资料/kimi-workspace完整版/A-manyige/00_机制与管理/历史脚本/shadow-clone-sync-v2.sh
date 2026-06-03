#!/bin/bash
# Shadow Clone - 安全版本 V2.0
# 防止循环备份的关键防护措施

SOURCE_DIR="/root/.openclaw/workspace"
SHADOW_DIR="/root/.openclaw/workspace/shadow-clone"
LOG_FILE="/var/log/shadow-clone.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# ===== 安全红线检查 =====

# 红线1: 检查是否已存在 shadow-clone（防止嵌套）
if [ -d "$SHADOW_DIR/shadow-clone" ]; then
    echo "[$TIMESTAMP] FATAL: 检测到嵌套备份！立即停止！" | tee -a "$LOG_FILE"
    echo "[$TIMESTAMP] 请手动清理: rm -rf $SHADOW_DIR" | tee -a "$LOG_FILE"
    exit 1
fi

# 红线2: 检查备份目录大小
if [ -d "$SHADOW_DIR" ]; then
    SIZE=$(du -sm "$SHADOW_DIR" 2>/dev/null | cut -f1)
    if [ "$SIZE" -gt 2048 ]; then  # 2GB上限
        echo "[$TIMESTAMP] WARN: 备份目录超过2GB (${SIZE}MB)，跳过本次同步" | tee -a "$LOG_FILE"
        exit 0
    fi
fi

# 红线3: 检查磁盘空间
DISK_AVAIL=$(df -m "$SOURCE_DIR" | tail -1 | awk '{print $4}')
if [ "$DISK_AVAIL" -lt 5120 ]; then  # 5GB剩余空间警戒
    echo "[$TIMESTAMP] WARN: 磁盘空间不足 (${DISK_AVAIL}MB 可用)，跳过同步" | tee -a "$LOG_FILE"
    exit 0
fi

# ===== 执行同步（安全模式）=====
mkdir -p "$SHADOW_DIR"

rsync -avz --delete \
  --exclude='.git/objects' \
  --exclude='logs/' \
  --exclude='tmp/' \
  --exclude='*.log' \
  --exclude='shadow-clone/' \
  --exclude='.openclaw/immortal-state/' \
  "$SOURCE_DIR/" "$SHADOW_DIR/" 2>/dev/null

if [ $? -eq 0 ]; then
    echo "[$TIMESTAMP] SYNC_OK - $(du -sh "$SHADOW_DIR" 2>/dev/null | cut -f1)" >> "$LOG_FILE"
    echo "$TIMESTAMP" > "$SHADOW_DIR/.last-sync"
else
    echo "[$TIMESTAMP] SYNC_FAIL" >> "$LOG_FILE"
fi
