#!/bin/bash
#
# organize.sh - 自动整理脚本
# 功能: 按规则自动整理文件到对应目录
# 用法: ./organize.sh [--dry-run]

set -e

DRY_RUN=false
if [ "$1" == "--dry-run" ]; then
    DRY_RUN=true
    echo "🔍 试运行模式（不会实际移动文件）"
fi

WORKSPACE="/root/.openclaw/workspace"
DOWNLOADS="/root/openclaw/kimi/downloads"

echo "🗂️  开始自动整理..."

# 1. 整理pycache
echo "→ 清理 __pycache__ 目录..."
if [ "$DRY_RUN" = false ]; then
    find "$WORKSPACE" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    echo "  ✓ 已清理"
else
    count=$(find "$WORKSPACE" -type d -name "__pycache__" 2>/dev/null | wc -l)
    echo "  发现 $count 个 __pycache__ 目录"
fi

# 2. 整理pyc文件
echo "→ 清理 .pyc 文件..."
if [ "$DRY_RUN" = false ]; then
    find "$WORKSPACE" -name "*.pyc" -delete 2>/dev/null || true
    echo "  ✓ 已清理"
else
    count=$(find "$WORKSPACE" -name "*.pyc" 2>/dev/null | wc -l)
    echo "  发现 $count 个 .pyc 文件"
fi

# 3. 整理临时文件
echo "→ 清理临时文件..."
if [ "$DRY_RUN" = false ]; then
    find "$WORKSPACE" -name "*.tmp" -mtime +7 -delete 2>/dev/null || true
    find "$WORKSPACE" -name "*.temp" -mtime +7 -delete 2>/dev/null || true
    find "$WORKSPACE" -name ".DS_Store" -delete 2>/dev/null || true
    echo "  ✓ 已清理"
else
    count=$(find "$WORKSPACE" \( -name "*.tmp" -o -name "*.temp" -o -name ".DS_Store" \) 2>/dev/null | wc -l)
    echo "  发现 $count 个临时文件"
fi

# 4. 创建标准目录结构
echo "→ 创建标准目录结构..."
DIRS=(
    "$WORKSPACE/00-SYSTEM/CORE"
    "$WORKSPACE/00-SYSTEM/CONFIG"
    "$WORKSPACE/00-SYSTEM/SKILLS"
    "$WORKSPACE/00-SYSTEM/SCRIPTS"
    "$WORKSPACE/01-PROJECTS"
    "$WORKSPACE/02-AREAS"
    "$WORKSPACE/03-RESOURCES/LIBRARY"
    "$WORKSPACE/03-RESOURCES/TEMPLATES"
    "$WORKSPACE/03-RESOURCES/DATA"
    "$WORKSPACE/04-ARCHIVES/2026-03"
    "$WORKSPACE/05-TEMP"
)

for dir in "${DIRS[@]}"; do
    if [ "$DRY_RUN" = false ]; then
        mkdir -p "$dir"
    else
        if [ ! -d "$dir" ]; then
            echo "  将创建: $dir"
        fi
    fi
done

if [ "$DRY_RUN" = false ]; then
    echo "  ✓ 目录结构已创建"
else
    echo "  目录结构检查完成"
fi

# 5. 移动测试文件
echo "→ 整理测试文件..."
TEST_FILES=$(find "$WORKSPACE" -maxdepth 2 -name "test_*" -o -name "*_test.*" 2>/dev/null | grep -v "test_files/" || true)
if [ -n "$TEST_FILES" ]; then
    if [ "$DRY_RUN" = false ]; then
        mkdir -p "$WORKSPACE/05-TEMP/tests"
        echo "$TEST_FILES" | while read f; do
            mv "$f" "$WORKSPACE/05-TEMP/tests/" 2>/dev/null || true
        done
        echo "  ✓ 测试文件已移动"
    else
        count=$(echo "$TEST_FILES" | wc -l)
        echo "  将移动 $count 个测试文件"
    fi
fi

# 6. 整理downloads中的meta文件
echo "→ 整理downloads元数据文件..."
META_COUNT=$(find "$DOWNLOADS" -name "*_meta.json" 2>/dev/null | wc -l)
if [ "$META_COUNT" -gt 0 ]; then
    if [ "$DRY_RUN" = false ]; then
        mkdir -p "$WORKSPACE/04-ARCHIVES/downloads_meta"
        find "$DOWNLOADS" -name "*_meta.json" -exec mv {} "$WORKSPACE/04-ARCHIVES/downloads_meta/" \; 2>/dev/null || true
        echo "  ✓ 已归档 $META_COUNT 个meta文件"
    else
        echo "  将归档 $META_COUNT 个meta文件"
    fi
fi

echo ""
if [ "$DRY_RUN" = false ]; then
    echo "✅ 整理完成！"
else
    echo "✅ 试运行完成，使用 --dry-run 查看详情"
fi
