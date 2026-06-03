#!/bin/bash
# 提取所有skill的slug并检查完整度

DOWNLOAD_DIR="/root/openclaw/kimi/downloads"
REPORT_FILE="/root/.openclaw/workspace/reports/SKILL_429_FIX_REPORT.md"

# 清空报告
echo "# Skill 429修复报告" > "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo "生成时间: $(date)" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# 提取所有slug
echo "## 提取的Skill Slug列表" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

for meta_file in "$DOWNLOAD_DIR"/*_meta.json; do
    if [ -f "$meta_file" ]; then
        slug=$(jq -r '.slug' "$meta_file" 2>/dev/null)
        if [ -n "$slug" ] && [ "$slug" != "null" ]; then
            echo "- $slug" >> "$REPORT_FILE"
        fi
    fi
done

echo "" >> "$REPORT_FILE"
echo "总计: $(find "$DOWNLOAD_DIR" -name '*_meta.json' | wc -l) 个skill" >> "$REPORT_FILE"

cat "$REPORT_FILE"
