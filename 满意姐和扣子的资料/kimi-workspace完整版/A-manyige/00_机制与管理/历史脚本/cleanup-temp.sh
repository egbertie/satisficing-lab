#!/bin/bash
# cleanup-temp.sh - 清理临时文件脚本
# 用途: 清理各类临时文件和空文件夹
# 执行频率: 按需或每日

set -e

WORKSPACE="/root/.openclaw/workspace"

echo "开始清理临时文件..."

# 1. 清理临时文件
TEMP_COUNT=0
for pattern in "*.tmp" "*.temp" "*~" "*.swp" "*.swo"; do
    COUNT=$(find "$WORKSPACE" -name "$pattern" -type f 2>/dev/null | wc -l)
    TEMP_COUNT=$((TEMP_COUNT + COUNT))
    find "$WORKSPACE" -name "$pattern" -type f -delete 2>/dev/null || true
done
echo "✅ 清理临时文件: $TEMP_COUNT 个"

# 2. 清理空文件夹（排除.git、backup、隐藏目录）
EMPTY_BEFORE=$(find "$WORKSPACE" -type d -empty 2>/dev/null | grep -v ".git" | grep -v "backup" | grep -v "BACKUP" | wc -l)

find "$WORKSPACE" -type d -empty 2>/dev/null | \
    grep -v ".git" | \
    grep -v "backup" | \
    grep -v "BACKUP" | \
    grep -v "/\." | \
    xargs -r rmdir -p 2>/dev/null || true

EMPTY_AFTER=$(find "$WORKSPACE" -type d -empty 2>/dev/null | grep -v ".git" | grep -v "backup" | grep -v "BACKUP" | wc -l)

EMPTY_CLEANED=$((EMPTY_BEFORE - EMPTY_AFTER))
echo "✅ 清理空文件夹: $EMPTY_CLEANED 个 (剩余: $EMPTY_AFTER)"

# 3. 清理staging/temp目录
if [ -d "$WORKSPACE/staging/temp" ]; then
    STAGING_TEMP=$(ls "$WORKSPACE/staging/temp" 2>/dev/null | wc -l)
    rm -rf "$WORKSPACE/staging/temp/"* 2>/dev/null || true
    echo "✅ 清理staging/temp: $STAGING_TEMP 个文件"
fi

# 4. 记录日志
LOG_ENTRY="[$(date '+%Y-%m-%d %H:%M:%S')] 清理完成: 临时文件=$TEMP_COUNT, 空文件夹=$EMPTY_CLEANED"
echo "$LOG_ENTRY" >> "$WORKSPACE/logs/cleanup.log"

echo ""
echo "🎉 清理完成"
