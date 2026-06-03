#!/bin/bash
#
# cleanup.sh - 清理脚本
# 功能: 清理临时文件、空目录、过期文件
# 用法: ./cleanup.sh [--dry-run] [--all]

set -e

DRY_RUN=false
CLEAN_ALL=false

# 解析参数
for arg in "$@"; do
    case $arg in
        --dry-run)
            DRY_RUN=true
            ;;
        --all)
            CLEAN_ALL=true
            ;;
    esac
done

WORKSPACE="/root/.openclaw/workspace"
LOG_FILE="$WORKSPACE/logs/cleanup_$(date +%Y%m%d_%H%M%S).log"

mkdir -p "$WORKSPACE/logs"

log() {
    echo "$1"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

if [ "$DRY_RUN" = true ]; then
    log "🔍 试运行模式（不会实际删除文件）"
else
    log "🧹 开始清理..."
fi

TOTAL_FREED=0

# 1. 清理pycache
log "→ 清理 Python 缓存..."
if [ "$DRY_RUN" = true ]; then
    count=$(find "$WORKSPACE" -type d -name "__pycache__" 2>/dev/null | wc -l)
    size=$(find "$WORKSPACE" -type d -name "__pycache__" -exec du -sb {} + 2>/dev/null | awk '{sum+=$1} END {print sum}')
    size_mb=$(echo "scale=2; $size/1024/1024" | bc 2>/dev/null || echo "0")
    log "  将删除 $count 个 __pycache__ 目录，释放约 ${size_mb}MB"
    TOTAL_FREED=$((TOTAL_FREED + size))
else
    find "$WORKSPACE" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    log "  ✓ Python 缓存已清理"
fi

# 2. 清理pyc文件
log "→ 清理 .pyc 文件..."
if [ "$DRY_RUN" = true ]; then
    count=$(find "$WORKSPACE" -name "*.pyc" 2>/dev/null | wc -l)
    log "  将删除 $count 个 .pyc 文件"
else
    find "$WORKSPACE" -name "*.pyc" -delete 2>/dev/null || true
    log "  ✓ .pyc 文件已清理"
fi

# 3. 清理临时文件
log "→ 清理临时文件..."
TEMP_PATTERNS=("*.tmp" "*.temp" "*.swp" "*.swo" "*~" ".DS_Store" "Thumbs.db")
for pattern in "${TEMP_PATTERNS[@]}"; do
    if [ "$DRY_RUN" = true ]; then
        count=$(find "$WORKSPACE" -name "$pattern" 2>/dev/null | wc -l)
        if [ "$count" -gt 0 ]; then
            log "  发现 $count 个 $pattern 文件"
        fi
    else
        find "$WORKSPACE" -name "$pattern" -delete 2>/dev/null || true
    fi
done
if [ "$DRY_RUN" = false ]; then
    log "  ✓ 临时文件已清理"
fi

# 4. 清理空目录
log "→ 清理空目录..."
if [ "$DRY_RUN" = true ]; then
    count=$(find "$WORKSPACE" -type d -empty 2>/dev/null | wc -l)
    log "  将删除 $count 个空目录"
else
    # 循环删除直到没有空目录（处理嵌套空目录）
    while true; do
        count=$(find "$WORKSPACE" -type d -empty 2>/dev/null | wc -l)
        if [ "$count" -eq 0 ]; then
            break
        fi
        find "$WORKSPACE" -type d -empty -delete 2>/dev/null || true
    done
    log "  ✓ 空目录已清理"
fi

# 5. 清理旧日志（如果--all）
if [ "$CLEAN_ALL" = true ]; then
    log "→ 清理旧日志文件（30天前）..."
    if [ "$DRY_RUN" = true ]; then
        count=$(find "$WORKSPACE/logs" -name "*.log" -mtime +30 2>/dev/null | wc -l)
        log "  将归档/删除 $count 个旧日志文件"
    else
        # 压缩旧日志
        find "$WORKSPACE/logs" -name "*.log" -mtime +30 -exec gzip {} \; 2>/dev/null || true
        # 删除超过90天的压缩日志
        find "$WORKSPACE/logs" -name "*.gz" -mtime +90 -delete 2>/dev/null || true
        log "  ✓ 旧日志已处理"
    fi
fi

# 6. 清理workspace_optimization备份（如果--all）
if [ "$CLEAN_ALL" = true ]; then
    log "→ 检查备份冗余..."
    BACKUP_DIR="$WORKSPACE/.workspace_optimization/backup_critical"
    if [ -d "$BACKUP_DIR" ]; then
        backup_size=$(du -sb "$BACKUP_DIR" 2>/dev/null | cut -f1)
        backup_size_mb=$(echo "scale=2; $backup_size/1024/1024" | bc 2>/dev/null || echo "0")
        if [ "$DRY_RUN" = true ]; then
            log "  发现备份目录: ${backup_size_mb}MB"
            log "  建议: 将备份移动到 /04-ARCHIVES/ 或使用硬链接"
        else
            # 移动到归档
            ARCHIVE_DIR="$WORKSPACE/04-ARCHIVES/backup_$(date +%Y%m%d)"
            mkdir -p "$ARCHIVE_DIR"
            mv "$BACKUP_DIR" "$ARCHIVE_DIR/" 2>/dev/null || true
            log "  ✓ 备份已归档到 $ARCHIVE_DIR"
        fi
    fi
fi

# 7. 清理downloads中的旧文件（如果--all）
if [ "$CLEAN_ALL" = true ]; then
    log "→ 检查 downloads 旧文件..."
    DOWNLOADS="/root/openclaw/kimi/downloads"
    if [ -d "$DOWNLOADS" ]; then
        old_count=$(find "$DOWNLOADS" -type f -mtime +90 2>/dev/null | wc -l)
        if [ "$old_count" -gt 0 ]; then
            if [ "$DRY_RUN" = true ]; then
                log "  发现 $old_count 个90天前的文件"
                log "  建议: 移动到归档目录"
            else
                ARCHIVE_DIR="$WORKSPACE/04-ARCHIVES/downloads_$(date +%Y%m%d)"
                mkdir -p "$ARCHIVE_DIR"
                find "$DOWNLOADS" -type f -mtime +90 -exec mv {} "$ARCHIVE_DIR/" \; 2>/dev/null || true
                log "  ✓ 旧文件已归档"
            fi
        fi
    fi
fi

# 汇总
log ""
if [ "$DRY_RUN" = true ]; then
    log "✅ 试运行完成。使用实际执行命令清理文件"
    log "💡 提示: 去掉 --dry-run 参数执行实际清理"
else
    log "✅ 清理完成！"
    log "📄 日志保存到: $LOG_FILE"
fi
