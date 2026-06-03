#!/bin/bash
# 直接克隆P0批次的skill

FIXED_DIR="/root/openclaw/kimi/downloads/fixed_skills"
REPORT_FILE="/root/.openclaw/workspace/reports/SKILL_429_FIX_REPORT.md"

P0_SKILLS=("brave-search" "automate-excel" "csvtoexcel" "copywriting" "duckdb-cli-ai-skills" "cron-scheduling" "markdown-converter" "markdown-exporter" "mermaid-diagrams")

echo "# Skill 429修复报告" > "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo "生成时间: $(date '+%Y-%m-%d %H:%M:%S')" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

echo "## P0批次 - 优先修复结果" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

success_count=0
failed_count=0

for slug in "${P0_SKILLS[@]}"; do
    echo "正在处理: $slug"
    target_dir="$FIXED_DIR/$slug"
    mkdir -p "$target_dir"
    
    # 尝试 clawhub
    echo "  尝试: https://github.com/clawhub/skills/$slug.git"
    if git clone --depth 1 "https://github.com/clawhub/skills/$slug.git" "$target_dir" 2>/dev/null; then
        echo "  ✅ 成功从 clawhub 克隆"
        echo "- ✅ **$slug**: 成功从 clawhub/skills 克隆" >> "$REPORT_FILE"
        ((success_count++))
        continue
    fi
    
    rm -rf "$target_dir"
    mkdir -p "$target_dir"
    
    # 尝试 openclaw
    echo "  尝试: https://github.com/openclaw/skills/$slug.git"
    if git clone --depth 1 "https://github.com/openclaw/skills/$slug.git" "$target_dir" 2>/dev/null; then
        echo "  ✅ 成功从 openclaw 克隆"
        echo "- ✅ **$slug**: 成功从 openclaw/skills 克隆" >> "$REPORT_FILE"
        ((success_count++))
        continue
    fi
    
    rm -rf "$target_dir"
    echo "  ❌ 克隆失败"
    echo "- ❌ **$slug**: 克隆失败（两个仓库均不可访问）" >> "$REPORT_FILE"
    ((failed_count++))
done

echo "" >> "$REPORT_FILE"
echo "## P0批次修复统计" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo "- 总数: 9" >> "$REPORT_FILE"
echo "- 成功: $success_count" >> "$REPORT_FILE"
echo "- 失败: $failed_count" >> "$REPORT_FILE"

echo ""
echo "P0批次修复完成: 成功 $success_count, 失败 $failed_count"
