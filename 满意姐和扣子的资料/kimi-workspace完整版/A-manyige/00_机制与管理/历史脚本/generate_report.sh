#!/bin/bash
# 完整的skill检查和报告生成脚本

DOWNLOAD_DIR="/root/openclaw/kimi/downloads"
FIXED_DIR="/root/openclaw/kimi/downloads/fixed_skills"
REPORT_FILE="/root/.openclaw/workspace/reports/SKILL_429_FIX_REPORT.md"

# P0批次
P0_SKILLS=("brave-search" "automate-excel" "csvtoexcel" "copywriting" "duckdb-cli-ai-skills" "cron-scheduling" "markdown-converter" "markdown-exporter" "mermaid-diagrams")

# 初始化统计
p0_total=9
p0_success=0
p0_failed=0

all_slugs=()
incomplete_slugs=()

echo "# Skill 429修复报告" > "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo "生成时间: $(date '+%Y-%m-%d %H:%M:%S')" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# 提取所有slug
echo "正在分析所有skill..."
for meta_file in "$DOWNLOAD_DIR"/*_meta.json; do
    if [ -f "$meta_file" ]; then
        slug=$(jq -r '.slug // empty' "$meta_file" 2>/dev/null)
        if [ -n "$slug" ]; then
            all_slugs+=("$slug")
        fi
    fi
done

echo "找到 ${#all_slugs[@]} 个skill"

# 检查每个skill的完整度
echo "正在检查skill完整度..."
for slug in "${all_slugs[@]}"; do
    skill_dir="$DOWNLOAD_DIR/$slug"
    
    # 检查skill目录是否存在且有内容
    if [ ! -d "$skill_dir" ]; then
        incomplete_slugs+=("$slug")
    else
        # 检查是否有SKILL.md或skill.md
        has_skill_md=$(find "$skill_dir" -maxdepth 1 -iname "skill.md" 2>/dev/null | wc -l)
        file_count=$(find "$skill_dir" -type f 2>/dev/null | wc -l)
        
        # 如果少于2个文件或没有SKILL.md，认为不完整
        if [ "$file_count" -lt 2 ] || [ "$has_skill_md" -eq 0 ]; then
            incomplete_slugs+=("$slug")
        fi
    fi
done

echo "发现 ${#incomplete_slugs[@]} 个不完整的skill"

# P0批次修复结果
echo "## P0批次修复结果" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo "P0批次包含9个优先修复的skill:" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo "| Skill | 本地状态 | GitHub克隆 | 结果 |" >> "$REPORT_FILE"
echo "|-------|----------|------------|------|" >> "$REPORT_FILE"

for slug in "${P0_SKILLS[@]}"; do
    # 检查本地状态
    skill_dir="$DOWNLOAD_DIR/$slug"
    if [ -d "$skill_dir" ]; then
        file_count=$(find "$skill_dir" -type f 2>/dev/null | wc -l)
        if [ "$file_count" -gt 1 ]; then
            local_status="✅ 存在($file_count文件)"
        else
            local_status="⚠️ 不完整($file_count文件)"
        fi
    else
        local_status="❌ 缺失"
    fi
    
    # 尝试克隆（使用超时）
    target_dir="$FIXED_DIR/$slug"
    rm -rf "$target_dir"
    mkdir -p "$target_dir"
    
    clone_result="未尝试"
    if timeout 20 git clone --depth 1 "https://github.com/clawhub/skills/$slug.git" "$target_dir" 2>/dev/null; then
        if [ -f "$target_dir/SKILL.md" ] || [ -f "$target_dir/skill.md" ] || [ "$(ls -A "$target_dir" | grep -v .git | wc -l)" -gt 0 ]; then
            clone_result="✅ clawhub成功"
            ((p0_success++))
        else
            clone_result="⚠️ 仓库空"
            ((p0_failed++))
        fi
    else
        rm -rf "$target_dir"
        mkdir -p "$target_dir"
        if timeout 20 git clone --depth 1 "https://github.com/openclaw/skills/$slug.git" "$target_dir" 2>/dev/null; then
            if [ -f "$target_dir/SKILL.md" ] || [ -f "$target_dir/skill.md" ] || [ "$(ls -A "$target_dir" | grep -v .git | wc -l)" -gt 0 ]; then
                clone_result="✅ openclaw成功"
                ((p0_success++))
            else
                clone_result="⚠️ 仓库空"
                ((p0_failed++))
            fi
        else
            rm -rf "$target_dir"
            clone_result="❌ 失败"
            ((p0_failed++))
        fi
    fi
    
    echo "| $slug | $local_status | 已尝试 | $clone_result |" >> "$REPORT_FILE"
done

echo "" >> "$REPORT_FILE"
echo "### P0批次统计" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo "- 总数: $p0_total" >> "$REPORT_FILE"
echo "- 成功: $p0_success" >> "$REPORT_FILE"
echo "- 失败: $p0_failed" >> "$REPORT_FILE"

# 所有不完整的skill列表
echo "" >> "$REPORT_FILE"
echo "## 所有不完整的Skill (${#incomplete_slugs[@]}个)" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo "```" >> "$REPORT_FILE"
for slug in "${incomplete_slugs[@]}"; do
    echo "$slug" >> "$REPORT_FILE"
done
echo "```" >> "$REPORT_FILE"

# 已修复的skill清单
echo "" >> "$REPORT_FILE"
echo "## 已修复Skill清单" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
if [ -d "$FIXED_DIR" ]; then
    for skill_dir in "$FIXED_DIR"/*; do
        if [ -d "$skill_dir" ]; then
            slug=$(basename "$skill_dir")
            file_count=$(find "$skill_dir" -type f 2>/dev/null | wc -l)
            echo "- **$slug**: $file_count 个文件" >> "$REPORT_FILE"
        fi
    done
else
    echo "无" >> "$REPORT_FILE"
fi

# 建议的替代方案
echo "" >> "$REPORT_FILE"
echo "## 建议的替代方案" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo "对于从GitHub克隆失败的skill，建议以下替代方案:" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo "1. **检查仓库名称**" >> "$REPORT_FILE"
echo "   - 可能使用复数形式（如 `cron-scheduling` → `cron-schedulings`）" >> "$REPORT_FILE"
echo "   - 可能使用连字符不同（如 `duckdb-cli-ai-skills` → `duckdb-cli-ai-skill`）" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo "2. **搜索GitHub**" >> "$REPORT_FILE"
echo "   - 使用搜索关键词: `site:github.com [skill-name] openclaw`" >> "$REPORT_FILE"
echo "   - 检查组织: `clawhub`, `openclaw`" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo "3. **联系原始来源**" >> "$REPORT_FILE"
echo "   - 从_meta.json中的 `ownerId` 可能追踪到原始发布者" >> "$REPORT_FILE"
echo "   - 检查是否有其他分发渠道" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo "4. **手动重建**" >> "$REPORT_FILE"
echo "   - 基于skill名称和描述重建基本结构" >> "$REPORT_FILE"
echo "   - 创建基本的SKILL.md文件" >> "$REPORT_FILE"

echo "报告已生成: $REPORT_FILE"
cat "$REPORT_FILE"
