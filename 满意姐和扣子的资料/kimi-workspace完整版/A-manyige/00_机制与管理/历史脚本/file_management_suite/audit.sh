#!/bin/bash
#
# audit.sh - 全面审计脚本
# 功能: 扫描文件系统，生成审计报告
# 用法: ./audit.sh [workspace_path]

set -e

WORKSPACE="${1:-/root/.openclaw/workspace}"
DOWNLOADS="/root/openclaw/kimi/downloads"
REPORT_DIR="$WORKSPACE/docs"
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
REPORT_FILE="$REPORT_DIR/AUDIT_REPORT_$TIMESTAMP.md"

echo "🔍 开始全面文件审计..."
echo "工作空间: $WORKSPACE"
echo "报告文件: $REPORT_FILE"

# 创建报告
mkdir -p "$REPORT_DIR"

cat > "$REPORT_FILE" << EOF
# 文件系统审计报告

**审计时间**: $(date '+%Y-%m-%d %H:%M:%S')  
**审计路径**: $WORKSPACE  
**审计脚本**: audit.sh

---

## 1. 基础统计

### 1.1 文件数量统计
EOF

# 统计文件数
echo "正在统计文件..."
TOTAL_FILES=$(find "$WORKSPACE" -type f 2>/dev/null | wc -l)
TOTAL_DIRS=$(find "$WORKSPACE" -type d 2>/dev/null | wc -l)
DOWNLOAD_FILES=$(find "$DOWNLOADS" -type f 2>/dev/null | wc -l)

cat >> "$REPORT_FILE" << EOF
| 项目 | 数量 |
|------|------|
| 工作空间文件 | $TOTAL_FILES |
| 工作空间目录 | $TOTAL_DIRS |
| 下载目录文件 | $DOWNLOAD_FILES |

### 1.2 文件类型分布

| 类型 | 数量 | 占比 |
|------|------|------|
EOF

find "$WORKSPACE" -type f 2>/dev/null | sed 's/.*\.//' | sort | uniq -c | sort -rn | head -20 | while read count ext; do
    pct=$(echo "scale=1; $count * 100 / $TOTAL_FILES" | bc 2>/dev/null || echo "N/A")
    echo "| .$ext | $count | ${pct}% |" >> "$REPORT_FILE"
done

# 空目录检测
echo "" >> "$REPORT_FILE"
echo "## 2. 问题检测" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo "### 2.1 空目录列表" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo "\`\`\`" >> "$REPORT_FILE"
find "$WORKSPACE" -type d -empty 2>/dev/null | head -30 >> "$REPORT_FILE" || echo "无" >> "$REPORT_FILE"
echo "\`\`\`" >> "$REPORT_FILE"

# 目录层级检测
echo "" >> "$REPORT_FILE"
echo "### 2.2 超层目录（超过4层）" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo "| 深度 | 路径 |" >> "$REPORT_FILE"
echo "|------|------|" >> "$REPORT_FILE"
find "$WORKSPACE" -type d 2>/dev/null | awk -F'/' '{if(NF>8) print NF-1"|"$0}' | sort -rn | head -20 | while IFS='|' read depth path; do
    echo "| $depth | $path |" >> "$REPORT_FILE"
done

# 大文件检测
echo "" >> "$REPORT_FILE"
echo "### 2.3 大文件（>5MB）" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo "| 大小 | 路径 |" >> "$REPORT_FILE"
echo "|------|------|" >> "$REPORT_FILE"
find "$WORKSPACE" "$DOWNLOADS" -type f -size +5M 2>/dev/null | while read f; do
    size=$(du -h "$f" 2>/dev/null | cut -f1)
    echo "| $size | $f |" >> "$REPORT_FILE"
done

# 重复文件检测
echo "" >> "$REPORT_FILE"
echo "### 2.4 潜在重复文件（MD5前32位相同）" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo "| MD5 | 文件1 | 文件2 |" >> "$REPORT_FILE"
echo "|-----|-------|-------|" >> "$REPORT_FILE"

# 使用tmpfile避免管道问题
TMP_DUP=$(mktemp)
find "$WORKSPACE" -type f -size +100c 2>/dev/null | head -200 | while read f; do
    md5sum "$f" 2>/dev/null
done | sort | uniq -d -w32 | head -10 > "$TMP_DUP"

while read md5 file; do
    # 找到所有匹配的文件
    matches=$(find "$WORKSPACE" -type f -size +100c 2>/dev/null | xargs md5sum 2>/dev/null | grep "^$md5" | cut -d' ' -f3-)
    file1=$(echo "$matches" | head -1)
    file2=$(echo "$matches" | tail -1)
    if [ "$file1" != "$file2" ]; then
        echo "| ${md5:0:8}... | $(basename "$file1") | $(basename "$file2") |" >> "$REPORT_FILE"
    fi
done < "$TMP_DUP"
rm -f "$TMP_DUP"

# README缺失检测
echo "" >> "$REPORT_FILE"
echo "### 2.5 缺少README的目录（前30个）" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo "\`\`\`" >> "$REPORT_FILE"
find "$WORKSPACE" -type d -not -path "*/.*" -not -path "*/__pycache__*" 2>/dev/null | while read dir; do
    if [ ! -f "$dir/README.md" ] && [ ! -f "$dir/readme.md" ]; then
        echo "$dir"
    fi
done | head -30 >> "$REPORT_FILE"
echo "\`\`\`" >> "$REPORT_FILE"

# 结尾
cat >> "$REPORT_FILE" << EOF

---

## 3. 建议操作

1. **立即处理**: 删除空目录
2. **本周处理**: 处理超层目录，创建README
3. **本月处理**: 清理重复文件

*报告生成时间: $(date)*
EOF

echo "✅ 审计完成！"
echo "📄 报告位置: $REPORT_FILE"
