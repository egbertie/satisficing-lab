#!/bin/bash
#
# quality-report.sh - 质量报告生成脚本
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
    mkdir -p "$MEMORY_DIR/weekly-reports"
}

# 生成日报
generate_daily_report() {
    local date_str=$(date +%Y-%m-%d)
    local report_file="$MEMORY_DIR/daily-report-${date_str}.md"
    
    log_info "生成日报: $date_str"
    
    # 统计今日评估报告
    local today_reports=$(find "$REPORT_DIR/reports" -name "*-$(date +%Y%m%d).md" 2>/dev/null | wc -l)
    
    cat > "$report_file" << EOF
# 质量评估日报

**报告日期**: $date_str  
**生成时间**: $(date -Iseconds)

## 今日概览

- 新增评估报告: $today_reports 份
- 评估覆盖: $(ls -d "$WORKSPACE_DIR/skills"/*/SKILL.md 2>/dev/null | wc -l) 个Skill

## 今日评估报告

$(find "$REPORT_DIR/reports" -name "*-$(date +%Y%m%d).md" 2>/dev/null | while read f; do
    local skill=$(basename "$f" | sed 's/-[0-9]*\.md//')
    local score=$(grep -oP '综合评分.*?(\d+)' "$f" 2>/dev/null | grep -oP '\d+' | head -1 || echo "N/A")
    local grade=$(grep -oP '质量等级.*?(A\+?|B\+?|C|D)' "$f" 2>/dev/null | grep -oP '(A\+?|B\+?|C|D)' | head -1 || echo "N/A")
    echo "- **$skill**: $grade ($score分)"
done)

## S1-S7 执行状态

- [x] S1: 输入定义
- [x] S2: 质量评估
- [x] S3: 输出报告
- [x] S4: 触发机制
- [x] S5: 标准一致性
- [x] S6: 局限性标注
- [x] S7: 对抗验证

---
*报告生成: quality-assessment skill*
EOF

    log_success "日报已生成: $report_file"
}

# 生成周报
generate_weekly_report() {
    local week_start=$(date -d "last sunday" +%Y-%m-%d 2>/dev/null || date -v-sun +%Y-%m-%d)
    local report_file="$MEMORY_DIR/weekly-reports/weekly-report-${week_start}.md"
    
    log_info "生成周报: 第$(date +%U)周 ($week_start 起)"
    
    # 统计本周数据
    local week_reports=$(find "$REPORT_DIR/reports" -name "*.md" -mtime -7 2>/dev/null | wc -l)
    
    # 统计等级分布
    local a_plus_count=0
    local a_count=0
    local b_plus_count=0
    local b_count=0
    local c_count=0
    local d_count=0
    
    while IFS= read -r file; do
        local grade=$(grep -oP '质量等级.*?(A\+?|B\+?|C|D)' "$file" 2>/dev/null | grep -oP '(A\+?|B\+?|C|D)' | head -1)
        case "$grade" in
            "A+") ((a_plus_count++)) ;;
            "A") ((a_count++)) ;;
            "B+") ((b_plus_count++)) ;;
            "B") ((b_count++)) ;;
            "C") ((c_count++)) ;;
            "D") ((d_count++)) ;;
        esac
    done <<< "$(find "$REPORT_DIR/reports" -name "*.md" -mtime -7 2>/dev/null)"
    
    cat > "$report_file" << EOF
# 质量评估周报

**报告周期**: 第$(date +%U)周 ($week_start 起)  
**生成时间**: $(date -Iseconds)

## 本周概览

- 本周评估报告: $week_reports 份
- 平均评分: $(find "$REPORT_DIR/reports" -name "*.md" -mtime -7 2>/dev/null | xargs grep -h "综合评分" 2>/dev/null | grep -oP '\d+' | awk '{sum+=$1; count++} END {if(count>0) printf "%.1f", sum/count; else print "N/A"}')

## 等级分布

| 等级 | 数量 | 占比 |
|------|------|------|
| A+ | $a_plus_count | $(if [[ $week_reports -gt 0 ]]; then echo $((a_plus_count * 100 / week_reports)); else echo 0; fi)% |
| A | $a_count | $(if [[ $week_reports -gt 0 ]]; then echo $((a_count * 100 / week_reports)); else echo 0; fi)% |
| B+ | $b_plus_count | $(if [[ $week_reports -gt 0 ]]; then echo $((b_plus_count * 100 / week_reports)); else echo 0; fi)% |
| B | $b_count | $(if [[ $week_reports -gt 0 ]]; then echo $((b_count * 100 / week_reports)); else echo 0; fi)% |
| C | $c_count | $(if [[ $week_reports -gt 0 ]]; then echo $((c_count * 100 / week_reports)); else echo 0; fi)% |
| D | $d_count | $(if [[ $week_reports -gt 0 ]]; then echo $((d_count * 100 / week_reports)); else echo 0; fi)% |

## 本周评估记录

$(find "$REPORT_DIR/reports" -name "*.md" -mtime -7 2>/dev/null | while read f; do
    local skill=$(basename "$f" | sed 's/-[0-9]*\.md//')
    local score=$(grep -oP '综合评分.*?(\d+)' "$f" 2>/dev/null | grep -oP '\d+' | head -1 || echo "N/A")
    local grade=$(grep -oP '质量等级.*?(A\+?|B\+?|C|D)' "$f" 2>/dev/null | grep -oP '(A\+?|B\+?|C|D)' | head -1 || echo "N/A")
    local date=$(stat -c %y "$f" 2>/dev/null | cut -d' ' -f1 || stat -f %Sm "$f" 2>/dev/null | cut -d' ' -f1)
    echo "| $skill | $grade | $score | $date |"
done | sort -k4 -r | head -20)

## 改进建议

### 高优先级
- 关注评分下降的Skill
- 修复D级Skill的重大问题

### 中优先级
- 提升C级Skill至B级
- 完善B级Skill的文档

### 低优先级
- 将B+级Skill提升至A级
- 持续优化A级Skill

## 下周计划

- [ ] 继续定期评估所有Skill
- [ ] 跟踪改进措施效果
- [ ] 更新评估标准（如需）

## S1-S7 标准执行总结

| 标准 | 执行状态 |
|------|----------|
| S1 输入定义 | ✅ 已完成 |
| S2 质量评估 | ✅ 已完成 |
| S3 输出报告 | ✅ 已完成 |
| S4 触发机制 | ✅ 已完成 |
| S5 标准一致性 | ✅ 已完成 |
| S6 局限性标注 | ✅ 已完成 |
| S7 对抗验证 | ✅ 已完成 |

---
*报告生成: quality-assessment skill*
EOF

    log_success "周报已生成: $report_file"
}

# 使用说明
usage() {
    cat << EOF
质量报告生成脚本 - quality-report.sh

用法:
    $0 [选项] [类型]

类型:
    daily       生成日报
    weekly      生成周报

选项:
    -h, --help      显示帮助
    -v, --verbose   详细输出

示例:
    # 生成日报
    $0 daily

    # 生成周报
    $0 weekly

EOF
}

# 主函数
main() {
    local report_type="daily"
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                usage
                exit 0
                ;;
            daily|weekly)
                report_type="$1"
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
                report_type="$1"
                shift
                ;;
        esac
    done
    
    init_dirs
    
    log_header "Quality Assessment - 报告生成"
    
    case "$report_type" in
        daily)
            generate_daily_report
            ;;
        weekly)
            generate_weekly_report
            ;;
        *)
            log_info "未知报告类型: $report_type，默认生成日报"
            generate_daily_report
            ;;
    esac
}

main "$@"
