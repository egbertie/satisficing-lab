#!/bin/bash
# diary_archive.sh - diary目录自动归档脚本
# 用途: 将旧日志文件归档到备份目录
# 执行频率: 每周一次（通过Cron）
# 归档策略: 30天前的日志文件移动到archive目录

set -e

WORKSPACE="/root/.openclaw/workspace"
DIARY_DIR="$WORKSPACE/diary"
ARCHIVE_DIR="$DIARY_DIR/archive/$(date +%Y-%m)"
ARCHIVE_AGE_DAYS=30

echo "📦 开始归档diary目录..."
echo "   归档策略: ${ARCHIVE_AGE_DAYS}天前的文件"
echo "   归档目录: $ARCHIVE_DIR"
echo ""

# 创建归档目录
mkdir -p "$ARCHIVE_DIR"

# 统计归档前数量
BEFORE_COUNT=$(find "$DIARY_DIR" -maxdepth 1 -name "*.md" -type f 2>/dev/null | wc -l)
echo "   当前diary文件数: $BEFORE_COUNT"

# 查找并归档旧文件
ARCHIVED_COUNT=0
ARCHIVED_SIZE=0

while IFS= read -r file; do
    if [ -n "$file" ]; then
        # 计算文件大小
        FILE_SIZE=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null || echo 0)
        ARCHIVED_SIZE=$((ARCHIVED_SIZE + FILE_SIZE))
        
        # 移动文件
        mv "$file" "$ARCHIVE_DIR/"
        ARCHIVED_COUNT=$((ARCHIVED_COUNT + 1))
    fi
done < <(find "$DIARY_DIR" -maxdepth 1 -name "*.md" -type f -mtime +$ARCHIVE_AGE_DAYS 2>/dev/null)

# 压缩归档目录
if [ $ARCHIVED_COUNT -gt 0 ]; then
    echo "   压缩归档文件..."
    tar -czf "$ARCHIVE_DIR.tar.gz" -C "$DIARY_DIR/archive" "$(basename $ARCHIVE_DIR)" 2>/dev/null || true
    rm -rf "$ARCHIVE_DIR"
    echo "   ✅ 已压缩: $ARCHIVE_DIR.tar.gz"
fi

# 统计结果
AFTER_COUNT=$(find "$DIARY_DIR" -maxdepth 1 -name "*.md" -type f 2>/dev/null | wc -l)
ARCHIVE_SIZE_MB=$(echo "scale=2; $ARCHIVED_SIZE / 1024 / 1024" | bc 2>/dev/null || echo "0")

echo ""
echo "📊 归档统计:"
echo "   归档文件数: $ARCHIVED_COUNT"
echo "   归档大小: ${ARCHIVE_SIZE_MB}MB"
echo "   剩余文件数: $AFTER_COUNT"
echo ""

# 记录日志
LOG_FILE="$WORKSPACE/logs/diary_archive.log"
mkdir -p "$(dirname $LOG_FILE)"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 归档完成: 文件=$ARCHIVED_COUNT, 大小=${ARCHIVE_SIZE_MB}MB, 剩余=$AFTER_COUNT" >> "$LOG_FILE"

echo "🎉 归档完成"
