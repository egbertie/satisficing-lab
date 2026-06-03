#!/bin/bash
#
# trend-analysis.sh - 质量趋势分析脚本
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
WORKSPACE_DIR="$(dirname "$(dirname "$SKILL_DIR")")"
REPORT_DIR="$WORKSPACE_DIR/reports/assessment"
MEMORY_DIR="$WORKSPACE_DIR/memory/quality"

# 颜色定义
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_header() { echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"; echo -e "${CYAN}$1${NC}"; echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"; }

# 创建目录
init_dirs() {
    mkdir -p "$REPORT_DIR"
    mkdir -p "$MEMORY_DIR"
}

# 收集历史数据
collect_history() {
    local skill_name="$1"
    local history_file="$MEMORY_DIR/trends.json"
    
    # 查找该Skill的历史报告
    local reports=$(ls -t "$REPORT_DIR/reports/${skill_name}"-*.json 2>/dev/null | head -10)
    
    local history=""
    for report in $reports; do
        if [[ -f "$report" ]]; then
            local date=$(basename "$report" | sed "s/${skill_name}-//; s/\.json//")
            local score=$(grep -o '"overall_score":[0-9]*' "$report" | cut -d: -f2 || echo "0")
            local grade=$(grep -o '"overall_grade":"[^"]*"' "$report" | cut -d'"' -f4 || echo "N/A")
            
            if [[ -n "$history" ]]; then history="${history},"; fi
            history="${history}{\"date\":\"$date\",\"score\":$score,\"grade\":\"$grade\"}"
        fi
    done
    
    echo "[$history]"
}

# 分析趋势
analyze_trend() {
    local history_json="$1"
    
    # 使用Python进行趋势分析
    python3 << EOF
import json
import sys

try:
    data = json.loads('$history_json')
    if len(data) < 2:
        print("数据点不足，无法分析趋势")
        sys.exit(0)
    
    scores = [d['score'] for d in data]
    dates = [d['date'] for d in data]
    
    # 计算趋势
    first_score = scores[-1]  # 最早的
    last_score = scores[0]    # 最新的
    
    trend = "stable"
    if last_score > first_score + 5:
        trend = "upward"
    elif last_score < first_score - 5:
        trend = "downward"
    
    # 计算平均值
    avg_score = sum(scores) / len(scores)
    
    # 计算波动
    variance = sum((s - avg_score) ** 2 for s in scores) / len(scores)
    std_dev = variance ** 0.5
    
    print(f"趋势: {trend}")
    print(f"最新得分: {last_score}")
    print(f"起始得分: {first_score}")
    print(f"变化: {last_score - first_score:+d}")
    print(f"平均分: {avg_score:.1f}")
    print(f"标准差: {std_dev:.1f}")
except Exception as e:
    print(f"分析错误: {e}")
EOF
}

# 生成趋势报告
generate_trend_report() {
    local skill_name="$1"
    local history=$(collect_history "$skill_name")
    local trend_info=$(analyze_trend "$history")
    
    local timestamp=$(date -Iseconds)
    local report_file="$MEMORY_DIR/trend-${skill_name}-$(date +%Y%m%d).md"
    
    cat > "$report_file" << EOF
# 质量趋势分析报告: $skill_name

**分析时间**: $timestamp

## 趋势概览

$trend_info

## 历史数据

| 日期 | 得分 | 等级 |
|------|------|------|
$(echo "$history" | python3 -c "import sys,json; d=json.load(sys.stdin); print('\n'.join([f'| {x[\"date\"]} | {x[\"score\"]} | {x[\"grade\"]} |' for x in d]))" 2>/dev/null || echo "| - | - | - |")

## 趋势分析

$(echo "$trend_info" | grep "趋势:" | sed 's/趋势:/- 质量趋势:/')
$(echo "$trend_info" | grep "变化:" | sed 's/变化:/- 得分变化:/')
$(echo "$trend_info" | grep "标准差:" | sed 's/标准差:/- 稳定性:/')

## 建议

$(if echo "$trend_info" | grep -q "upward"; then
    echo "✅ 质量呈上升趋势，继续保持"
elif echo "$trend_info" | grep -q "downward"; then
    echo "⚠️ 质量呈下降趋势，建议分析原因并改进"
else
    echo "📊 质量保持稳定，关注细节优化"
fi)

---
*报告生成: quality-assessment skill*
EOF

    log_success "趋势报告已生成: $report_file"
}

# 批量趋势分析
batch_trend_analysis() {
    log_header "批量趋势分析"
    
    local skills_dir="$WORKSPACE_DIR/skills"
    local summary_file="$MEMORY_DIR/trend-summary-$(date +%Y%m%d).md"
    local trends_data=""
    
    for skill_dir in "$skills_dir"/*/; do
        if [[ -f "$skill_dir/SKILL.md" ]]; then
            local skill_name=$(basename "$skill_dir")
            log_info "分析趋势: $skill_name"
            
            local history=$(collect_history "$skill_name")
            local trend_info=$(analyze_trend "$history")
            
            local latest_score=$(echo "$trend_info" | grep "最新得分:" | cut -d: -f2 | tr -d ' ')
            local change=$(echo "$trend_info" | grep "变化:" | cut -d: -f2 | tr -d ' ')
            local trend=$(echo "$trend_info" | grep "趋势:" | cut -d: -f2 | tr -d ' ')
            
            local trend_icon="📊"
            [[ "$trend" == "upward" ]] && trend_icon="📈"
            [[ "$trend" == "downward" ]] && trend_icon="📉"
            
            trends_data="${trends_data}| $skill_name | ${latest_score:-N/A} | ${change:-N/A} | $trend_icon |\n"
            
            generate_trend_report "$skill_name" >/dev/null 2>&1 || true
        fi
    done
    
    # 生成汇总报告
    cat > "$summary_file" << EOF
# 质量趋势汇总报告

**分析时间**: $(date -Iseconds)

## 各Skill趋势概览

| Skill名称 | 最新得分 | 变化 | 趋势 |
|-----------|----------|------|------|
$(echo -e "$trends_data")

## 图例

- 📈 上升趋势 (得分提升 >5分)
- 📉 下降趋势 (得分下降 >5分)
- 📊 保持稳定 (变化 ≤5分)

## 建议关注的Skill

$(echo -e "$trends_data" | grep "📉" | sed 's/^/⚠️ /')

---
*报告生成: quality-assessment skill (趋势分析)*
EOF

    log_success "趋势汇总报告: $summary_file"
}

# 更新趋势数据文件
update_trends_json() {
    local trends_file="$MEMORY_DIR/trends.json"
    
    log_info "更新趋势数据文件..."
    
    cat > "$trends_file" << EOF
{
    "last_updated": "$(date -Iseconds)",
    "skills": [
$(find "$WORKSPACE_DIR/skills" -name "SKILL.md" -exec dirname {} \; | while read skill_dir; do
    local skill_name=$(basename "$skill_dir")
    local history=$(collect_history "$skill_name")
    echo "        {\"name\": \"$skill_name\", \"history\": $history},"
done | sed '$ s/,$//')
    ]
}
EOF

    log_success "趋势数据已更新: $trends_file"
}

# 使用说明
usage() {
    cat << EOF
质量趋势分析脚本 - trend-analysis.sh

用法:
    $0 [选项] [skill-name]

选项:
    -h, --help      显示帮助
    -b, --batch     批量分析所有Skill
    -u, --update    更新趋势数据文件
    -v, --verbose   详细输出

示例:
    # 分析单个Skill趋势
    $0 task-coordinator

    # 批量分析
    $0 --batch

    # 更新趋势数据
    $0 --update

EOF
}

# 主函数
main() {
    local batch_mode=false
    local update_mode=false
    local skill_name=""
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                usage
                exit 0
                ;;
            -b|--batch)
                batch_mode=true
                shift
                ;;
            -u|--update)
                update_mode=true
                shift
                ;;
            -v|--verbose)
                set -x
                shift
                ;;
            -*)
                echo "未知选项: $1"
                usage
                exit 1
                ;;
            *)
                skill_name="$1"
                shift
                ;;
        esac
    done
    
    init_dirs
    
    log_header "Quality Assessment - 趋势分析"
    
    if [[ "$update_mode" == "true" ]]; then
        update_trends_json
    elif [[ "$batch_mode" == "true" ]]; then
        batch_trend_analysis
    elif [[ -n "$skill_name" ]]; then
        generate_trend_report "$skill_name"
    else
        log_info "运行批量分析模式"
        batch_trend_analysis
    fi
}

main "$@"
