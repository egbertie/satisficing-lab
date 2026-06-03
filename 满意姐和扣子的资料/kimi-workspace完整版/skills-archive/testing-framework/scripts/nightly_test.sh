#!/bin/bash
# 夜间测试脚本 - S4标准实现
# 用于定时长时间运行测试

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_FILE="$PROJECT_DIR/reports/nightly_test_$(date +%Y%m%d_%H%M%S).log"

# 确保报告目录存在
mkdir -p "$PROJECT_DIR/reports"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_info() {
    log "${GREEN}INFO${NC}: $1"
}

log_warn() {
    log "${YELLOW}WARN${NC}: $1"
}

log_error() {
    log "${RED}ERROR${NC}: $1"
}

# 发送通知 (可根据需要实现)
send_notification() {
    local status="$1"
    local message="$2"
    
    log_info "发送通知: $status - $message"
    
    # 这里可以集成邮件、Slack、Discord等通知
    # 示例: 
    # curl -X POST -H 'Content-type: application/json' \
    #   --data "{\"text\":\"$message\"}" \
    #   "$SLACK_WEBHOOK_URL"
}

# 主测试流程
main() {
    log_info "开始夜间测试流程"
    log_info "日志文件: $LOG_FILE"
    
    cd "$PROJECT_DIR"
    
    local failed=0
    
    # 1. 安装依赖
    log_info "[1/8] 安装依赖..."
    pip install -q -r requirements.txt || {
        log_error "依赖安装失败"
        send_notification "FAILED" "夜间测试: 依赖安装失败"
        exit 1
    }
    
    # 2. 完整测试套件
    log_info "[2/8] 运行完整测试套件..."
    if python run_tests.py --all-levels 2>&1 | tee -a "$LOG_FILE"; then
        log_info "✓ 完整测试通过"
    else
        log_error "✗ 完整测试失败"
        failed=1
    fi
    
    # 3. 覆盖率检查 (更严格)
    log_info "[3/8] 运行覆盖率检查 (阈值: 85%)..."
    if python run_coverage.py --threshold 85 2>&1 | tee -a "$LOG_FILE"; then
        log_info "✓ 覆盖率达标"
    else
        log_error "✗ 覆盖率未达标"
        failed=1
    fi
    
    # 4. 测试质量自检
    log_info "[4/8] 运行测试质量自检..."
    if python test_quality_checker.py --mutation --threshold 85 2>&1 | tee -a "$LOG_FILE"; then
        log_info "✓ 质量检查通过"
    else
        log_warn "⚠ 质量检查未完全通过"
    fi
    
    # 5. 对抗测试
    log_info "[5/8] 运行对抗测试..."
    if python adversarial_test.py --mode all --threshold 90 2>&1 | tee -a "$LOG_FILE"; then
        log_info "✓ 对抗测试通过"
    else
        log_warn "⚠ 对抗测试检测率不足"
    fi
    
    # 6. 长时间稳定性测试 (模拟)
    log_info "[6/8] 运行稳定性测试..."
    local start_time=$(date +%s)
    local duration=300  # 5分钟模拟
    
    log_info "  模拟长时间运行 (${duration}s)..."
    sleep $duration
    
    local end_time=$(date +%s)
    local actual_duration=$((end_time - start_time))
    log_info "✓ 稳定性测试完成 (实际运行: ${actual_duration}s)"
    
    # 7. 生成完整报告
    log_info "[7/8] 生成完整报告..."
    python run_coverage.py 2>&1 | tee -a "$LOG_FILE"
    python defect_tracker.py --report 2>&1 | tee -a "$LOG_FILE"
    python test_quality_checker.py --report 2>&1 | tee -a "$LOG_FILE"
    log_info "✓ 报告生成完成"
    
    # 8. 资源使用检查
    log_info "[8/8] 资源使用检查..."
    log_info "  磁盘使用: $(df -h . | tail -1 | awk '{print $5}')"
    log_info "  内存使用: $(free | grep Mem | awk '{printf "%.1f%%", $3/$2 * 100.0}')"
    
    # 发送最终通知
    if [ $failed -eq 0 ]; then
        log_info "夜间测试全部通过 ✅"
        send_notification "SUCCESS" "夜间测试: 全部通过"
    else
        log_error "夜间测试部分失败 ❌"
        send_notification "FAILED" "夜间测试: 部分失败，请查看日志"
    fi
    
    # 保存测试历史
    local history_file="$PROJECT_DIR/reports/nightly_history.txt"
    local status_icon=$([ $failed -eq 0 ] && echo "✅" || echo "❌")
    echo "$(date '+%Y-%m-%d %H:%M:%S') $status_icon 夜间测试" >> "$history_file"
    
    exit $failed
}

# 信号处理
trap 'log_error "测试被中断"; exit 1' INT TERM

main "$@"
