#!/bin/bash
# 智能检查点脚本 - Token优化版

set -e

WORKSPACE="/root/.openclaw/workspace"
VAULT_PATH="/root/.openclaw/immortal-state/checkpoints"
LOG_FILE="/tmp/checkpoint.log"
INDEX_FILE="$VAULT_PATH/index.json"

mkdir -p "$VAULT_PATH"

# 获取当前时间
TIMESTAMP=$(date '+%Y%m%d-%H%M%S')
DATE_STR=$(date '+%Y-%m-%d %H:%M:%S')

# ===== 智能跳过逻辑 =====
# 1. 检查上次检查点时间
LAST_CHECKPOINT=0
if [ -f "$INDEX_FILE" ]; then
    LAST_CHECKPOINT=$(stat -c %Y "$INDEX_FILE" 2>/dev/null || echo 0)
fi
CURRENT_TIME=$(date +%s)
TIME_DIFF=$((CURRENT_TIME - LAST_CHECKPOINT))

# 如果距离上次检查点<25分钟，跳过（防止Cron重复执行）
if [ $TIME_DIFF -lt 1500 ]; then
    echo "[$DATE_STR] ⏭️  Skip: Last checkpoint was ${TIME_DIFF}s ago" >> "$LOG_FILE"
    exit 0
fi

# 2. 检查文件变更
RECENT_FILES=$(find "$WORKSPACE" -type f -mtime -0.02 2>/dev/null | wc -l)
if [ "$RECENT_FILES" -eq 0 ]; then
    echo "[$DATE_STR] ⏭️  Skip: No file changes in last 30 minutes" >> "$LOG_FILE"
    exit 0
fi

# 3. 检查Token状态（模拟，实际需读取真实Token）
BACKUP_TYPE="full"

# ===== 执行检查点 =====
if [ "$BACKUP_TYPE" = "full" ]; then
    # 完整备份
    tar czf "$VAULT_PATH/cpt-main-${TIMESTAMP}.tar.gz" -C "$WORKSPACE" . 2>/dev/null || true
    SIZE=$(stat -c %s "$VAULT_PATH/cpt-main-${TIMESTAMP}.tar.gz" 2>/dev/null || echo 0)
    echo "[$DATE_STR] ✅ Checkpoint: cpt-main-${TIMESTAMP} (${SIZE} bytes, ${RECENT_FILES} files changed)" >> "$LOG_FILE"
else
    # 轻量备份（仅关键文件）
    tar czf "$VAULT_PATH/cpt-minimal-${TIMESTAMP}.tar.gz" -C "$WORKSPACE" docs/ memory/ config/ 2>/dev/null || true
    echo "[$DATE_STR] ⚡ Minimal checkpoint (low token mode)" >> "$LOG_FILE"
fi

# 更新索引
echo '{"last_checkpoint": "'"$TIMESTAMP"'", "files_changed": '$RECENT_FILES'}' > "$INDEX_FILE"

# 清理旧检查点（保留最近20个）
ls -t "$VAULT_PATH"/cpt-*.tar.gz 2>/dev/null | tail -n +21 | xargs -r rm -f

echo "[$DATE_STR] ✅ Checkpoint completed" >> "$LOG_FILE"
