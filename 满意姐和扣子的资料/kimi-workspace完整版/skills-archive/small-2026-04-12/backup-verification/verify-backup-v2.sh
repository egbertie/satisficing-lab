#!/bin/bash
################################################################################
# Backup Verification System V2.0 - Shell Wrapper
# 备份验证系统 V2.0 - 5标准完整实现
#
# S1: 全局考虑 - 评估灾备影响
# S2: 系统闭环 - 检测→验证→修复→验证
# S3: 可观测输出 - 结构化报告
# S4: 自动化集成 - 定时验证+自动修复
# S5: 自我验证 - 验证机制自检
# S6: 认知谦逊 - 明确标注局限
# S7: 对抗测试 - 模拟损坏场景
################################################################################

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="/root/.openclaw/workspace"
PYTHON_SCRIPT="${SCRIPT_DIR}/backup_verification_v2.py"
REPORT_FILE="/tmp/backup_verification_latest.json"
LOG_FILE="/tmp/backup_verification.log"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印彩色输出
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 显示帮助
show_help() {
    cat << EOF
Backup Verification System V2.0 - 5标准完整实现

用法: $(basename "$0") [选项]

选项:
    --quick, -q         快速验证模式（默认）
    --deep, -d          深度验证模式（全量hash+恢复测试）
    --no-repair, -n     禁用自动修复
    --adversarial, -a   运行对抗测试
    --json, -j          输出JSON格式报告
    --status, -s        显示上次验证状态
    --repair-only, -r   仅执行修复（不验证）
    --cron              定时模式（静默输出）
    --help, -h          显示此帮助

5标准实现:
    S1: 全局考虑 - 评估备份失败对灾备的影响
    S2: 系统闭环 - 检测→验证→告警→修复→再验证
    S3: 可观测输出 - 健康分数、分层报告、修复记录
    S4: 自动化集成 - 支持Cron定时执行
    S5: 自我验证 - 环境自检、算法验证
    S6: 认知谦逊 - 明确标注验证局限
    S7: 对抗测试 - 模拟损坏场景验证检测能力

示例:
    $(basename "$0")                    # 快速验证
    $(basename "$0") --deep             # 深度验证
    $(basename "$0") --deep --no-repair # 深度验证但不修复
    $(basename "$0") --adversarial      # 运行对抗测试
    $(basename "$0") --status           # 查看状态

EOF
}

# 检查依赖
check_dependencies() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python3 未安装"
        exit 1
    fi
    
    if [[ ! -f "$PYTHON_SCRIPT" ]]; then
        print_error "验证脚本未找到: $PYTHON_SCRIPT"
        exit 1
    fi
}

# 执行验证
run_verification() {
    local args="$1"
    
    print_info "启动备份验证系统 V2.0..."
    print_info "时间: $(date '+%Y-%m-%d %H:%M:%S')"
    print_info "工作目录: $WORKSPACE"
    
    if ! python3 "$PYTHON_SCRIPT" $args; then
        print_error "验证发现问题，请查看报告"
        return 1
    fi
    
    return 0
}

# 显示状态
show_status() {
    if [[ -f "$REPORT_FILE" ]]; then
        print_info "上次验证报告:"
        if command -v jq &> /dev/null; then
            jq -r '
                "时间: " + .timestamp,
                "状态: " + .overall_status,
                "健康度: " + (.health_score | tostring) + "%",
                if .repair_summary.attempted then 
                    "修复尝试: " + (.repair_summary.attempted_repairs | tostring) +
                    " (成功: " + (.repair_summary.successful_repairs | tostring) + ")"
                else "修复: 未启用" end
            ' "$REPORT_FILE"
        else
            cat "$REPORT_FILE"
        fi
    else
        print_warning "未找到验证报告，请先运行验证"
    fi
}

# 执行修复
run_repair() {
    print_info "执行自动修复..."
    
    # 首先运行一次验证获取问题列表
    python3 "$PYTHON_SCRIPT" --json > /tmp/verify_temp.json
    
    local issues_count
    issues_count=$(jq '.layers | to_entries | map(.value.failed) | add' /tmp/verify_temp.json 2>/dev/null || echo "0")
    
    if [[ "$issues_count" -eq 0 ]]; then
        print_success "未发现需要修复的问题"
        return 0
    fi
    
    print_info "发现 $issues_count 个问题，尝试修复..."
    
    # 再次运行验证（启用修复）
    if python3 "$PYTHON_SCRIPT"; then
        print_success "修复完成"
    else
        print_warning "部分问题无法自动修复，需要人工介入"
    fi
    
    rm -f /tmp/verify_temp.json
}

# 显示报告摘要
show_report_summary() {
    if [[ -f "$REPORT_FILE" ]]; then
        echo ""
        echo "=========================================="
        echo "📊 备份验证报告摘要"
        echo "=========================================="
        
        local status health_score
        status=$(jq -r '.overall_status' "$REPORT_FILE" 2>/dev/null || echo "unknown")
        health_score=$(jq -r '.health_score' "$REPORT_FILE" 2>/dev/null || echo "0")
        
        case $status in
            "passed")
                echo -e "总体状态: ${GREEN}✅ 通过${NC}"
                ;;
            "partial")
                echo -e "总体状态: ${YELLOW}⚠️  部分通过${NC}"
                ;;
            "failed")
                echo -e "总体状态: ${RED}❌ 失败${NC}"
                ;;
            *)
                echo -e "总体状态: ${YELLOW}未知${NC}"
                ;;
        esac
        
        echo "健康分数: ${health_score}%"
        
        # 显示各层状态
        echo ""
        echo "分层验证详情:"
        jq -r '.layers | to_entries[] | 
            "  " + (if .value.failed == 0 then "✅" else "❌" end) + 
            " " + .key + ": " + 
            (.value.passed | tostring) + "/" + (.value.checked | tostring)' "$REPORT_FILE"
        
        # 显示修复摘要
        if jq -e '.repair_summary.attempted' "$REPORT_FILE" > /dev/null 2>&1; then
            echo ""
            echo "自动修复摘要:"
            jq -r '.repair_summary | 
                "  尝试修复: " + (.attempted_repairs | tostring),
                "  修复成功: " + (.successful_repairs | tostring),
                "  修复失败: " + (.failed_repairs | tostring),
                "  需要人工: " + (.manual_required | tostring),
                "  成功率: " + (.success_rate | tostring) + "%"' "$REPORT_FILE"
        fi
        
        echo "=========================================="
        
        # S6: 显示认知谦逊 - 局限说明
        echo ""
        echo "📋 验证局限说明 (S6: 认知谦逊)"
        echo "----------------------------------------"
        jq -r '.limitations[] | "  • " + .' "$REPORT_FILE"
    fi
}

# 主函数
main() {
    local mode="quick"
    local args=""
    local show_status_only=false
    local repair_only=false
    local cron_mode=false
    
    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            --quick|-q)
                mode="quick"
                shift
                ;;
            --deep|-d)
                mode="deep"
                args="$args --deep"
                shift
                ;;
            --no-repair|-n)
                args="$args --no-repair"
                shift
                ;;
            --adversarial|-a)
                args="$args --adversarial-test"
                shift
                ;;
            --json|-j)
                args="$args --json"
                shift
                ;;
            --status|-s)
                show_status_only=true
                shift
                ;;
            --repair-only|-r)
                repair_only=true
                shift
                ;;
            --cron)
                cron_mode=true
                shift
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
            *)
                print_error "未知选项: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    check_dependencies
    
    if $show_status_only; then
        show_status
        exit 0
    fi
    
    if $repair_only; then
        run_repair
        exit 0
    fi
    
    # 执行验证
    if $cron_mode; then
        # Cron模式：静默执行，仅记录日志
        python3 "$PYTHON_SCRIPT" $args > /dev/null 2>&1
        exit $?
    else
        if run_verification "$args"; then
            show_report_summary
            print_success "验证完成"
            exit 0
        else
            show_report_summary
            print_error "验证发现问题，已触发告警"
            exit 1
        fi
    fi
}

main "$@"
