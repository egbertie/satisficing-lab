#!/bin/bash
# 冗余文件清理脚本
# cleanup_redundant_files.sh
# 
# 功能: 清理临时文件、旧日志、备份文件
# 使用: ./cleanup_redundant_files.sh [--dry-run|--force]

set -e

WORKSPACE="/root/.openclaw/workspace"
DRY_RUN=false
FORCE=false
REPORT_FILE="$WORKSPACE/logs/cleanup_report_$(date +%Y%m%d_%H%M%S).log"

# 统计变量
DELETED_FILES=0
DELETED_SIZE=0
ARCHIVED_FILES=0
ARCHIVED_SIZE=0

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --force)
            FORCE=true
            shift
            ;;
        *)
            echo "未知参数: $1"
            echo "用法: $0 [--dry-run|--force]"
            exit 1
            ;;
    esac
done

echo "=========================================="
echo "🧹 冗余文件清理工具"
echo "=========================================="
echo "模式: $([ "$DRY_RUN" = true ] && echo '试运行' || echo '实际执行')"
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 创建日志目录
mkdir -p "$WORKSPACE/logs"

# 记录日志函数
log() {
    echo "$1" | tee -a "$REPORT_FILE"
}

# 安全删除函数
safe_delete() {
    local file="$1"
    local size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null || echo 0)
    
    if [ "$DRY_RUN" = true ]; then
        log "  [将删除] $file (${size} bytes)"
    else
        rm -f "$file"
        log "  [已删除] $file (${size} bytes)"
    fi
    
    DELETED_FILES=$((DELETED_FILES + 1))
    DELETED_SIZE=$((DELETED_SIZE + size))
}

# 安全归档函数
safe_archive() {
    local file="$1"
    local archive_dir="$WORKSPACE/archive/$(date +%Y%m)"
    local size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null || echo 0)
    
    mkdir -p "$archive_dir"
    
    if [ "$DRY_RUN" = true ]; then
        log "  [将归档] $file -> $archive_dir/"
    else
        mv "$file" "$archive_dir/"
        log "  [已归档] $file -> $archive_dir/"
    fi
    
    ARCHIVED_FILES=$((ARCHIVED_FILES + 1))
    ARCHIVED_SIZE=$((ARCHIVED_SIZE + size))
}

# ========== 清理1: 临时文件 ==========
log "📁 清理1: 临时文件 (*.tmp, *~)"
log "─────────────────────────────────────────"

TMP_PATTERNS=("*.tmp" "*~" "*.bak" "*.backup" ".DS_Store")
for pattern in "${TMP_PATTERNS[@]}"; do
    while IFS= read -r file; do
        [ -z "$file" ] && continue
        safe_delete "$file"
    done < <(find "$WORKSPACE" -name "$pattern" -type f 2>/dev/null)
done
log ""

# ========== 清理2: _meta.json.tmp 文件 ==========
log "📁 清理2: Skill临时元数据文件"
log "─────────────────────────────────────────"

find "$WORKSPACE/skills" -name "_meta.json.tmp" -type f 2>/dev/null | while read -r file; do
    safe_delete "$file"
done
log ""

# ========== 清理3: 旧日志文件 ==========
log "📁 清理3: 旧日志文件 (>30天)"
log "─────────────────────────────────────────"

# 保留最近30天的日志
find "$WORKSPACE/logs" -name "*.log" -type f -mtime +30 2>/dev/null | while read -r file; do
    safe_archive "$file"
done

# 清理 notion_sync 旧日志
find "$WORKSPACE/logs" -name "notion_sync_*.log" -type f -mtime +7 2>/dev/null | while read -r file; do
    safe_archive "$file"
done
log ""

# ========== 清理4: .pytest_cache ==========
log "📁 清理4: 测试缓存"
log "─────────────────────────────────────────"

find "$WORKSPACE" -type d -name ".pytest_cache" 2>/dev/null | while read -r dir; do
    if [ "$DRY_RUN" = true ]; then
        log "  [将清理] $dir/"
    else
        rm -rf "$dir"
        log "  [已清理] $dir/"
    fi
done
log ""

# ========== 清理5: .cache 过期文件 ==========
log "📁 清理5: 应用缓存"
log "─────────────────────────────────────────"

CACHE_DIR="$WORKSPACE/.cache"
if [ -d "$CACHE_DIR" ]; then
    find "$CACHE_DIR" -type f -mtime +7 2>/dev/null | while read -r file; do
        safe_delete "$file"
    done
fi
log ""

# ========== 清理6: 空目录 ==========
log "📁 清理6: 空目录"
log "─────────────────────────────────────────"

find "$WORKSPACE" -type d -empty 2>/dev/null | while read -r dir; do
    # 排除重要目录
    case "$dir" in
        */.git*) continue ;;
        */venv*) continue ;;
        */node_modules*) continue ;;
    esac
    
    if [ "$DRY_RUN" = true ]; then
        log "  [将删除] $dir/ (空目录)"
    else
        rmdir "$dir" 2>/dev/null && log "  [已删除] $dir/ (空目录)"
    fi
done
log ""

# ========== 汇总报告 ==========
log "=========================================="
log "📊 清理报告汇总"
log "=========================================="
log ""
log "删除文件数: $DELETED_FILES"
log "删除大小: $(numfmt --to=iec $DELETED_SIZE 2>/dev/null || echo "${DELETED_SIZE} bytes")"
log "归档文件数: $ARCHIVED_FILES"
log "归档大小: $(numfmt --to=iec $ARCHIVED_SIZE 2>/dev/null || echo "${ARCHIVED_SIZE} bytes")"
log ""

TOTAL_SAVED=$((DELETED_SIZE + ARCHIVED_SIZE))
log "总释放空间: $(numfmt --to=iec $TOTAL_SAVED 2>/dev/null || echo "${TOTAL_SAVED} bytes")"
log ""

if [ "$DRY_RUN" = true ]; then
    log "⚠️  这是试运行模式，实际未删除任何文件"
    log "   使用 --force 参数执行实际清理"
else
    log "✅ 清理完成"
fi

log ""
log "详细报告: $REPORT_FILE"
log ""

# 非dry-run模式，显示彩色输出
if [ "$DRY_RUN" = false ]; then
    echo -e "${GREEN}✅ 清理完成!${NC}"
    echo -e "释放空间: ${GREEN}$(numfmt --to=iec $TOTAL_SAVED 2>/dev/null || echo "${TOTAL_SAVED} bytes")${NC}"
else
    echo -e "${YELLOW}⚠️  试运行模式，未实际删除${NC}"
    echo -e "预计释放: ${YELLOW}$(numfmt --to=iec $TOTAL_SAVED 2>/dev/null || echo "${TOTAL_SAVED} bytes")${NC}"
fi
