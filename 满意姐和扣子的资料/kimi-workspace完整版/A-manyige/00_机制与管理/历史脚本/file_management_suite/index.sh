#!/bin/bash
#
# index.sh - 索引生成脚本
# 功能: 为每个目录生成README索引
# 用法: ./index.sh [--all] [target_dir]

set -e

GENERATE_ALL=false
TARGET_DIR="${1:-/root/.openclaw/workspace}"

if [ "$1" == "--all" ]; then
    GENERATE_ALL=true
    TARGET_DIR="${2:-/root/.openclaw/workspace}"
fi

echo "📑 索引生成工具"
echo "目标目录: $TARGET_DIR"
echo ""

# 生成目录的README内容
generate_readme() {
    local dir="$1"
    local dirname=$(basename "$dir")
    local parent=$(dirname "$dir")
    
    # 统计信息
    local file_count=$(find "$dir" -maxdepth 1 -type f | wc -l)
    local dir_count=$(find "$dir" -maxdepth 1 -type d | grep -v "^$dir$" | wc -l)
    local subdirs=$(find "$dir" -maxdepth 1 -type d | grep -v "^$dir$")
    local files=$(find "$dir" -maxdepth 1 -type f -not -name "README.md" | sort)
    
    cat << EOF
# $dirname

**自动生成索引** | $(date '+%Y-%m-%d %H:%M:%S')

## 目录信息

- 📁 子目录: $dir_count 个
- 📄 文件: $file_count 个

## 子目录

EOF

    if [ -n "$subdirs" ]; then
        echo "$subdirs" | while read subdir; do
            local subname=$(basename "$subdir")
            local subcount=$(find "$subdir" -maxdepth 1 -type f 2>/dev/null | wc -l)
            echo "- [$subname](./$subname/) ($subcount 文件)"
        done
    else
        echo "_无子目录_"
    fi

    cat << EOF

## 文件列表

EOF

    if [ -n "$files" ]; then
        echo "$files" | while read f; do
            local fname=$(basename "$f")
            local fsize=$(du -h "$f" 2>/dev/null | cut -f1)
            local fdate=$(stat -c %y "$f" 2>/dev/null | cut -d' ' -f1 || stat -f %Sm "$f" 2>/dev/null || echo "N/A")
            echo "- [$fname](./$fname) - $fsize - $fdate"
        done
    else
        echo "_无文件_"
    fi

    cat << EOF

---

*由 index.sh 自动生成*
EOF
}

# 检查是否应该跳过该目录
should_skip() {
    local dir="$1"
    local name=$(basename "$dir")
    
    # 跳过隐藏目录
    if [[ "$name" == .* ]]; then
        return 0
    fi
    
    # 跳过特殊目录
    case "$name" in
        __pycache__|node_modules|vendor|.git|.svn)
            return 0
            ;;
    esac
    
    return 1
}

# 主逻辑
echo "→ 扫描目录结构..."

if [ "$GENERATE_ALL" = true ]; then
    # 为所有目录生成README
    find "$TARGET_DIR" -type d | while read dir; do
        if should_skip "$dir"; then
            continue
        fi
        
        readme_path="$dir/README.md"
        
        # 如果README已存在且不是自动生成的，询问是否覆盖
        if [ -f "$readme_path" ]; then
            if ! grep -q "由 index.sh 自动生成" "$readme_path" 2>/dev/null; then
                echo "  跳过 (手动创建的README): $dir"
                continue
            fi
        fi
        
        echo "  生成: $dir/README.md"
        generate_readme "$dir" > "$readme_path"
    done
else
    # 只为缺少README的目录生成
    find "$TARGET_DIR" -type d | while read dir; do
        if should_skip "$dir"; then
            continue
        fi
        
        readme_path="$dir/README.md"
        
        if [ ! -f "$readme_path" ]; then
            echo "  生成: $dir/README.md"
            generate_readme "$dir" > "$readme_path"
        fi
    done
fi

echo ""
echo "✅ 索引生成完成！"
echo ""
echo "💡 提示:"
echo "   ./index.sh --all    # 为所有目录重新生成（覆盖自动生成的）"
echo "   ./index.sh /path    # 为指定目录生成"
