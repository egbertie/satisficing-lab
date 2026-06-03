#!/bin/bash
# 检查skill完整度并尝试从GitHub克隆

DOWNLOAD_DIR="/root/openclaw/kimi/downloads"
FIXED_DIR="/root/openclaw/kimi/downloads/fixed_skills"
REPORT_FILE="/root/.openclaw/workspace/reports/SKILL_429_FIX_REPORT.md"

# P0批次 - 优先修复
P0_SKILLS=("brave-search" "automate-excel" "csvtoexcel" "copywriting" "duckdb-cli-ai-skills" "cron-scheduling" "markdown-converter" "markdown-exporter" "mermaid-diagrams")

echo "# Skill 429修复报告" > "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo "生成时间: $(date '+%Y-%m-%d %H:%M:%S')" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# 统计函数
total_count=0
complete_count=0
incomplete_count=0
fixed_count=0
failed_count=0

# 检查skill完整度
check_skill_completeness() {
    local slug=$1
    local skill_dir="$DOWNLOAD_DIR/$slug"
    
    # 检查是否存在且包含关键文件
    if [ -d "$skill_dir" ]; then
        local has_skill_md=$(find "$skill_dir" -name "SKILL.md" -o -name "skill.md" | wc -l)
        local has_scripts=$(find "$skill_dir" -name "*.py" -o -name "*.js" -o -name "*.sh" 2>/dev/null | wc -l)
        local file_count=$(find "$skill_dir" -type f 2>/dev/null | wc -l)
        
        if [ "$has_skill_md" -gt 0 ] && [ "$file_count" -gt 1 ]; then
            echo "complete"
        else
            echo "incomplete"
        fi
    else
        echo "missing"
    fi
}

# 尝试从GitHub克隆
clone_from_github() {
    local slug=$1
    local target_dir="$FIXED_DIR/$slug"
    
    mkdir -p "$target_dir"
    
    # 优先尝试 clawhub
    if git clone --depth 1 "https://github.com/clawhub/skills/$slug.git" "$target_dir" 2>/dev/null; then
        echo "success_clawhub"
        return
    fi
    
    rm -rf "$target_dir"
    mkdir -p "$target_dir"
    
    # 备选尝试 openclaw
    if git clone --depth 1 "https://github.com/openclaw/skills/$slug.git" "$target_dir" 2>/dev/null; then
        echo "success_openclaw"
        return
    fi
    
    rm -rf "$target_dir"
    echo "failed"
}

echo "## P0批次 - 优先修复结果" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo "| Skill | 状态 | 修复结果 | 备注 |" >> "$REPORT_FILE"
echo "|-------|------|----------|------|" >> "$REPORT_FILE"

# 处理P0批次
for slug in "${P0_SKILLS[@]}"; do
    status=$(check_skill_completeness "$slug")
    
    if [ "$status" = "complete" ]; then
        echo "| $slug | ✅ 完整 | - | 已存在且完整 |" >> "$REPORT_FILE"
        ((complete_count++))
    else
        ((incomplete_count++))
        # 尝试克隆
        clone_result=$(clone_from_github "$slug")
        
        if [[ "$clone_result" == success_* ]]; then
            source=${clone_result#success_}
            echo "| $slug | ⚠️ $status | ✅ 成功 | 从 $source 克隆 |" >> "$REPORT_FILE"
            ((fixed_count++))
        else
            echo "| $slug | ⚠️ $status | ❌ 失败 | GitHub仓库不存在或无法访问 |" >> "$REPORT_FILE"
            ((failed_count++))
        fi
    fi
    ((total_count++))
done

echo "" >> "$REPORT_FILE"
echo "## 所有Skill状态汇总" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo "| Skill | 本地状态 |" >> "$REPORT_FILE"
echo "|-------|----------|" >> "$REPORT_FILE"

# 处理所有skill
for meta_file in "$DOWNLOAD_DIR"/*_meta.json; do
    if [ -f "$meta_file" ]; then
        slug=$(jq -r '.slug' "$meta_file" 2>/dev/null)
        if [ -n "$slug" ] && [ "$slug" != "null" ]; then
            # 跳过P0批次（已处理）
            if [[ ! " ${P0_SKILLS[@]} " =~ " $slug " ]]; then
                status=$(check_skill_completeness "$slug")
                status_icon="⚠️ 缺失"
                [ "$status" = "complete" ] && status_icon="✅ 完整"
                [ "$status" = "incomplete" ] && status_icon="⚠️ 不完整"
                echo "| $slug | $status_icon |" >> "$REPORT_FILE"
            fi
        fi
    fi
done

echo "" >> "$REPORT_FILE"
echo "## 统计摘要" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo "- 总计Skill数: 59" >> "$REPORT_FILE"
echo "- P0批次修复尝试: ${total_count}" >> "$REPORT_FILE"
echo "- 已完整存在: ${complete_count}" >> "$REPORT_FILE"
echo "- 成功修复: ${fixed_count}" >> "$REPORT_FILE"
echo "- 修复失败: ${failed_count}" >> "$REPORT_FILE"

echo "" >> "$REPORT_FILE"
echo "## 建议的替代方案" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo "对于从GitHub克隆失败的skill，建议:" >> "$REPORT_FILE"
echo "1. 检查仓库名称是否正确（可能是复数形式或不同命名）" >> "$REPORT_FILE"
echo "2. 搜索GitHub上的其他可能仓库地址" >> "$REPORT_FILE"
echo "3. 手动下载并放置到正确的目录" >> "$REPORT_FILE"
echo "4. 联系skill原作者获取最新版本" >> "$REPORT_FILE"

cat "$REPORT_FILE"
