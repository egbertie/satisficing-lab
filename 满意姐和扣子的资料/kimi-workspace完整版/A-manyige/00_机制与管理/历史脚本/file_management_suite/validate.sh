#!/bin/bash
#
# validate.sh - 完整性验证脚本
# 功能: 验证文件系统是否符合规范
# 用法: ./validate.sh [--fix]

set -e

FIX_MODE=false
if [ "$1" == "--fix" ]; then
    FIX_MODE=true
    echo "🔧 修复模式已启用"
fi

WORKSPACE="/root/.openclaw/workspace"
ERRORS=0
WARNINGS=0

echo "🔍 文件系统完整性验证"
echo "工作空间: $WORKSPACE"
echo ""

# 颜色定义
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

log_error() {
    echo -e "${RED}❌ ERROR:${NC} $1"
    ((ERRORS++)) || true
}

log_warning() {
    echo -e "${YELLOW}⚠️  WARNING:${NC} $1"
    ((WARNINGS++)) || true
}

log_ok() {
    echo -e "${GREEN}✓${NC} $1"
}

# 1. 检查核心文件
echo "→ 检查核心文件..."
CORE_FILES=(
    "README.md"
    "AGENTS.md"
    "USER.md"
    "MEMORY.md"
    "BOOTSTRAP.md"
)

for file in "${CORE_FILES[@]}"; do
    if [ -f "$WORKSPACE/$file" ]; then
        log_ok "核心文件存在: $file"
    else
        log_warning "核心文件缺失: $file"
        if [ "$FIX_MODE" = true ]; then
            echo "   创建占位文件: $file"
            echo "# $file" > "$WORKSPACE/$file"
            echo "待补充内容" >> "$WORKSPACE/$file"
        fi
    fi
done

# 2. 检查目录层级
echo ""
echo "→ 检查目录层级（应≤4层）..."
DEEP_DIRS=$(find "$WORKSPACE" -type d 2>/dev/null | awk -F'/' '{if(NF>8) print $0}')
if [ -n "$DEEP_DIRS" ]; then
    count=$(echo "$DEEP_DIRS" | wc -l)
    log_warning "发现 $count 个超层目录（超过4层）"
    echo "$DEEP_DIRS" | head -5 | while read d; do
        depth=$(echo "$d" | tr -cd '/' | wc -c)
        echo "   深度$((depth-1)): ${d:0:80}..."
    done
else
    log_ok "所有目录层级符合规范"
fi

# 3. 检查空目录
echo ""
echo "→ 检查空目录..."
EMPTY_DIRS=$(find "$WORKSPACE" -type d -empty 2>/dev/null | grep -v "/.git/" || true)
if [ -n "$EMPTY_DIRS" ]; then
    count=$(echo "$EMPTY_DIRS" | wc -l)
    log_warning "发现 $count 个空目录"
    echo "$EMPTY_DIRS" | head -5 | while read d; do
        echo "   $d"
    done
    if [ "$FIX_MODE" = true ]; then
        echo "   删除空目录..."
        echo "$EMPTY_DIRS" | xargs -r rmdir 2>/dev/null || true
    fi
else
    log_ok "无空目录"
fi

# 4. 检查README覆盖率
echo ""
echo "→ 检查README覆盖率..."
TOTAL_DIRS=$(find "$WORKSPACE" -type d -not -path "*/.*" -not -path "*/__pycache__*" 2>/dev/null | wc -l)
DIRS_WITH_README=$(find "$WORKSPACE" -type d -not -path "*/.*" -not -path "*/__pycache__*" 2>/dev/null | while read d; do
    if [ -f "$d/README.md" ] || [ -f "$d/readme.md" ]; then
        echo "1"
    fi
done | wc -l)

COVERAGE=$((DIRS_WITH_README * 100 / TOTAL_DIRS))
if [ "$COVERAGE" -lt 80 ]; then
    log_warning "README覆盖率 $COVERAGE% (目标: 100%)"
    if [ "$FIX_MODE" = true ]; then
        echo "   运行 ./index.sh 生成缺失的README"
    fi
else
    log_ok "README覆盖率 $COVERAGE%"
fi

# 5. 检查缓存文件
echo ""
echo "→ 检查缓存文件..."
PYCACHE_COUNT=$(find "$WORKSPACE" -type d -name "__pycache__" 2>/dev/null | wc -l)
PYC_COUNT=$(find "$WORKSPACE" -name "*.pyc" 2>/dev/null | wc -l)

if [ "$PYCACHE_COUNT" -gt 0 ] || [ "$PYC_COUNT" -gt 0 ]; then
    log_warning "发现 $PYCACHE_COUNT 个 __pycache__ 目录, $PYC_COUNT 个 .pyc 文件"
    if [ "$FIX_MODE" = true ]; then
        echo "   清理缓存..."
        find "$WORKSPACE" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
        find "$WORKSPACE" -name "*.pyc" -delete 2>/dev/null || true
    fi
else
    log_ok "无Python缓存文件"
fi

# 6. 检查重复文件（快速检查）
echo ""
echo "→ 检查重复文件..."
# 只检查最大的10个文件
DUP_CHECK=$(find "$WORKSPACE" -type f -size +10k 2>/dev/null | head -100 | xargs md5sum 2>/dev/null | sort | uniq -d -w32 | wc -l)
if [ "$DUP_CHECK" -gt 0 ]; then
    log_warning "发现约 $DUP_CHECK 组潜在重复文件"
    echo "   运行 ./dedup.sh 进行详细检查"
else
    log_ok "未发现明显的重复文件"
fi

# 7. 检查敏感信息（基本检查）
echo ""
echo "→ 检查敏感信息泄露风险..."
if grep -r "password\|secret\|api_key\|token" "$WORKSPACE" --include="*.py" --include="*.sh" --include="*.json" -l 2>/dev/null | grep -v "__pycache__" | head -5; then
    log_warning "发现包含敏感关键词的文件（需人工检查）"
else
    log_ok "未发现明显的敏感信息泄露"
fi

# 8. 检查文件命名规范
echo ""
echo "→ 检查文件命名规范..."
# 检查包含空格的文件名
FILES_WITH_SPACES=$(find "$WORKSPACE" -type f -name "* *" 2>/dev/null | wc -l)
if [ "$FILES_WITH_SPACES" -gt 0 ]; then
    log_warning "发现 $FILES_WITH_SPACES 个包含空格的文件名"
else
    log_ok "文件名符合规范"
fi

# 9. 检查大文件
echo ""
echo "→ 检查大文件（>10MB）..."
LARGE_FILES=$(find "$WORKSPACE" -type f -size +10M 2>/dev/null)
if [ -n "$LARGE_FILES" ]; then
    count=$(echo "$LARGE_FILES" | wc -l)
    log_warning "发现 $count 个大文件"
    echo "$LARGE_FILES" | while read f; do
        size=$(du -h "$f" | cut -f1)
        echo "   $size - $(basename "$f")"
    done
else
    log_ok "无超大文件"
fi

# 10. 检查目录结构完整性
echo ""
echo "→ 检查目录结构完整性..."
REQUIRED_DIRS=(
    "docs"
    "skills"
    "memory"
)

for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$WORKSPACE/$dir" ]; then
        log_ok "核心目录存在: $dir/"
    else
        log_error "核心目录缺失: $dir/"
    fi
done

# 汇总
echo ""
echo "===================="
echo "验证结果汇总"
echo "===================="
echo -e "错误: ${RED}$ERRORS${NC}"
echo -e "警告: ${YELLOW}$WARNINGS${NC}"

if [ "$ERRORS" -eq 0 ] && [ "$WARNINGS" -eq 0 ]; then
    echo -e "${GREEN}✅ 所有检查通过！${NC}"
    exit 0
elif [ "$ERRORS" -eq 0 ]; then
    echo -e "${YELLOW}⚠️  有警告，但可以运行${NC}"
    exit 0
else
    echo -e "${RED}❌ 存在错误，建议修复后再运行${NC}"
    if [ "$FIX_MODE" = false ]; then
        echo "💡 提示: 使用 ./validate.sh --fix 尝试自动修复"
    fi
    exit 1
fi
