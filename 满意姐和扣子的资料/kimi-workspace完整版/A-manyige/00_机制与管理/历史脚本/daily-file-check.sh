#!/bin/bash
# daily-file-check.sh - 每日文件系统检查脚本
# 用途: 自动化检查文件系统健康状态
# 执行频率: 每日 23:00 (通过Cron)

set -e

WORKSPACE="/root/.openclaw/workspace"
DOWNLOADS="/root/openclaw/kimi/downloads"
LOG_DIR="$WORKSPACE/logs"
REPORT="$LOG_DIR/file-check-$(date +%Y%m%d).md"

echo "开始每日文件检查..."

# 确保日志目录存在
mkdir -p "$LOG_DIR"

# 创建报告头
cat > "$REPORT" << EOF
# 每日文件检查报告

**检查时间**: $(date '+%Y-%m-%d %H:%M:%S')

---

## 1. 空文件夹检查

EOF

# 检查空文件夹（排除.git和备份目录）
EMPTY_FOLDERS=$(find "$WORKSPACE" -type d -empty 2>/dev/null | grep -v ".git" | grep -v "backup" | grep -v "BACKUP" || true)
EMPTY_COUNT=$(echo "$EMPTY_FOLDERS" | grep -v "^$" | wc -l)

echo "**空文件夹数量**: $EMPTY_COUNT" >> "$REPORT"

if [ $EMPTY_COUNT -gt 0 ]; then
    echo "" >> "$REPORT"
    echo "### 空文件夹列表" >> "$REPORT"
    echo "" >> "$REPORT"
    echo "\`\`\`" >> "$REPORT"
    echo "$EMPTY_FOLDERS" >> "$REPORT"
    echo "\`\`\`" >> "$REPORT"
    echo "" >> "$REPORT"
    
    if [ $EMPTY_COUNT -gt 10 ]; then
        echo "⚠️ **警告**: 空文件夹数量超过10个，建议清理" >> "$REPORT"
    fi
else
    echo "✅ 未发现空文件夹" >> "$REPORT"
fi

# 检查downloads目录
cat >> "$REPORT" << EOF

---

## 2. Downloads目录检查

EOF

DOWNLOADS_COUNT=$(ls "$DOWNLOADS" 2>/dev/null | wc -l)
DOWNLOADS_SIZE=$(du -sh "$DOWNLOADS" 2>/dev/null | cut -f1)

echo "**文件数量**: $DOWNLOADS_COUNT" >> "$REPORT"
echo "**占用空间**: $DOWNLOADS_SIZE" >> "$REPORT"
echo "" >> "$REPORT"

if [ $DOWNLOADS_COUNT -gt 1000 ]; then
    echo "🔴 **严重**: Downloads目录文件数超过1000，需要立即处理" >> "$REPORT"
elif [ $DOWNLOADS_COUNT -gt 500 ]; then
    echo "🟠 **警告**: Downloads目录文件数超过500，建议本周处理" >> "$REPORT"
else
    echo "✅ **正常**: Downloads目录文件数在合理范围内" >> "$REPORT"
fi

# 检查重复文件名
cat >> "$REPORT" << EOF

---

## 3. 重复文件名检查 (Top 10)

EOF

DUPLICATES=$(find "$WORKSPACE" -type f -name "*.md" 2>/dev/null | sed 's|.*/||' | sort | uniq -c | sort -rn | grep -v "^ *1 " | head -10)

if [ -n "$DUPLICATES" ]; then
    echo "\`\`\`" >> "$REPORT"
    echo "$DUPLICATES" >> "$REPORT"
    echo "\`\`\`" >> "$REPORT"
else
    echo "✅ 未发现重复文件名" >> "$REPORT"
fi

# 检查命名规范
cat >> "$REPORT" << EOF

---

## 4. 命名规范检查

EOF

# 检查emoji
EMOJI_FILES=$(find "$WORKSPACE/A满意哥专属_folder" -name "*[📄📑🔥✅📋📚🔴🎨🔄🔧📦👥🧠💡📊🖼️📈🧭💻🚀📝]*" 2>/dev/null | head -10)
EMOJI_COUNT=$(echo "$EMOJI_FILES" | grep -v "^$" | wc -l)

echo "**包含emoji的文件/文件夹**: $EMOJI_COUNT 个" >> "$REPORT"

if [ $EMOJI_COUNT -gt 0 ]; then
    echo "" >> "$REPORT"
    echo "### 示例（需整改）" >> "$REPORT"
    echo "\`\`\`" >> "$REPORT"
    echo "$EMOJI_FILES" >> "$REPORT"
    echo "\`\`\`" >> "$REPORT"
fi

# 检查大文件
cat >> "$REPORT" << EOF

---

## 5. 大文件检查 (>10MB)

EOF

LARGE_FILES=$(find "$WORKSPACE" -type f -size +10M 2>/dev/null | head -10)
LARGE_COUNT=$(echo "$LARGE_FILES" | grep -v "^$" | wc -l)

echo "**超过10MB的文件**: $LARGE_COUNT 个" >> "$REPORT"

if [ $LARGE_COUNT -gt 0 ]; then
    echo "" >> "$REPORT"
    echo "\`\`\`" >> "$REPORT"
    ls -lh $LARGE_FILES 2>/dev/null >> "$REPORT" || true
    echo "\`\`\`" >> "$REPORT"
fi

# 报告结尾
cat >> "$REPORT" << EOF

---

## 6. 检查摘要

| 检查项 | 状态 | 数值 |
|--------|------|------|
| 空文件夹 | $(if [ $EMPTY_COUNT -gt 10 ]; then echo "🔴"; elif [ $EMPTY_COUNT -gt 0 ]; then echo "🟠"; else echo "✅"; fi) | $EMPTY_COUNT |
| Downloads文件数 | $(if [ $DOWNLOADS_COUNT -gt 1000 ]; then echo "🔴"; elif [ $DOWNLOADS_COUNT -gt 500 ]; then echo "🟠"; else echo "✅"; fi) | $DOWNLOADS_COUNT |
| 大文件数 | $(if [ $LARGE_COUNT -gt 10 ]; then echo "🟠"; else echo "✅"; fi) | $LARGE_COUNT |

---

**检查完成**: $(date '+%Y-%m-%d %H:%M:%S')

*由 daily-file-check.sh 自动生成*
EOF

echo "✅ 每日检查完成: $REPORT"

# 如果发现问题，输出到控制台
if [ $EMPTY_COUNT -gt 10 ] || [ $DOWNLOADS_COUNT -gt 500 ]; then
    echo ""
    echo "⚠️ 发现问题，请查看报告: $REPORT"
    exit 1
fi
