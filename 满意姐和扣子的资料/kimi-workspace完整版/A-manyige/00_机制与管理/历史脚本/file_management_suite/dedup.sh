#!/bin/bash
#
# dedup.sh - 重复文件检测与处理
# 功能: 扫描重复文件，生成处理建议
# 用法: ./dedup.sh [--action=report|link|delete]

set -e

ACTION="${1:-report}"  # report, link, delete
WORKSPACE="/root/.openclaw/workspace"
MIN_SIZE="1k"  # 最小文件大小

echo "🔍 重复文件检测"
echo "模式: $ACTION"
echo "扫描路径: $WORKSPACE"
echo ""

# 创建临时文件
TMP_DIR=$(mktemp -d)
HASH_FILE="$TMP_DIR/hashes.txt"
DUP_FILE="$TMP_DIR/duplicates.txt"
REPORT_FILE="$WORKSPACE/docs/DUPLICATE_REPORT_$(date +%Y%m%d_%H%M%S).md"

trap "rm -rf $TMP_DIR" EXIT

echo "→ 正在计算文件哈希..."
find "$WORKSPACE" -type f -size +$MIN_SIZE \
    -not -path "*/.git/*" \
    -not -path "*/__pycache__/*" \
    -not -path "*/node_modules/*" \
    -exec md5sum {} \; 2>/dev/null | sort > "$HASH_FILE"

echo "→ 分析重复文件..."
# 找出重复的哈希
awk '{print $1}' "$HASH_FILE" | uniq -d > "$DUP_FILE"

DUP_COUNT=$(wc -l < "$DUP_FILE")
echo "发现 $(($DUP_COUNT)) 组重复文件"
echo ""

if [ "$DUP_COUNT" -eq 0 ]; then
    echo "✅ 没有发现重复文件"
    exit 0
fi

# 生成报告
cat > "$REPORT_FILE" << EOF
# 重复文件检测报告

**检测时间**: $(date)  
**检测路径**: $WORKSPACE  
**最小文件大小**: $MIN_SIZE

---

## 重复文件列表

| MD5 | 大小 | 文件数量 | 文件路径 |
|-----|------|---------|---------|
EOF

while read hash; do
    files=$(grep "^$hash" "$HASH_FILE" | cut -d' ' -f3-)
    file_count=$(echo "$files" | wc -l)
    first_file=$(echo "$files" | head -1)
    file_size=$(du -h "$first_file" 2>/dev/null | cut -f1)
    
    echo "| ${hash:0:8}... | $file_size | $file_count | $(echo "$files" | head -1 | xargs basename) |" >> "$REPORT_FILE"
    
    echo "### 组: ${hash:0:16}..." >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    echo "\`\`\`" >> "$REPORT_FILE"
    echo "$files" >> "$REPORT_FILE"
    echo "\`\`\`" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
done < "$DUP_FILE"

echo "📄 报告已生成: $REPORT_FILE"

# 根据action执行不同操作
case "$ACTION" in
    report)
        echo ""
        echo "重复文件预览（前5组）:"
        echo "========================"
        head -5 "$DUP_FILE" | while read hash; do
            echo ""
            echo "MD5: ${hash:0:16}..."
            grep "^$hash" "$HASH_FILE" | cut -d' ' -f3- | head -3 | nl
            count=$(grep "^$hash" "$HASH_FILE" | wc -l)
            if [ "$count" -gt 3 ]; then
                echo "  ... 还有 $((count - 3)) 个重复文件"
            fi
        done
        echo ""
        echo "💡 提示: 使用 ./dedup.sh link 创建硬链接，或 ./dedup.sh delete 删除重复文件"
        ;;
        
    link)
        echo "→ 正在创建硬链接..."
        while read hash; do
            files=$(grep "^$hash" "$HASH_FILE" | cut -d' ' -f3-)
            first_file=$(echo "$files" | head -1)
            
            echo "$files" | tail -n +2 | while read dup_file; do
                if [ -f "$dup_file" ]; then
                    backup="${dup_file}.backup"
                    mv "$dup_file" "$backup"
                    ln "$first_file" "$dup_file" && rm "$backup"
                    echo "  ✓ 已链接: $(basename "$dup_file") → $(basename "$first_file")"
                fi
            done
        done < "$DUP_FILE"
        echo "✅ 硬链接创建完成"
        ;;
        
    delete)
        echo "⚠️ 警告: 将删除重复文件（保留第一个）"
        read -p "确认删除? (yes/no): " confirm
        if [ "$confirm" == "yes" ]; then
            while read hash; do
                files=$(grep "^$hash" "$HASH_FILE" | cut -d' ' -f3-)
                echo "$files" | tail -n +2 | while read dup_file; do
                    if [ -f "$dup_file" ]; then
                        rm "$dup_file"
                        echo "  ✓ 已删除: $dup_file"
                    fi
                done
            done < "$DUP_FILE"
            echo "✅ 重复文件删除完成"
        else
            echo "已取消"
        fi
        ;;
        
    *)
        echo "未知动作: $ACTION"
        echo "用法: ./dedup.sh [report|link|delete]"
        exit 1
        ;;
esac
