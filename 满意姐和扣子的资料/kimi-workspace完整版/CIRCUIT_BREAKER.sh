#!/bin/bash
# CIRCUIT_BREAKER.sh - 熔断机制
# 功能: 实时检测异常，自动熔断防止问题扩大
# 创建时间: 2026-04-04
# 版本: 1.0

set -euo pipefail

# 配置
CIRCUIT_STATE="/root/.openclaw/workspace/.circuit_state"
CIRCUIT_LOG="/root/.openclaw/workspace/.circuit_log"
METRICS_DIR="/root/.openclaw/workspace/.circuit_metrics"

# 熔断阈值
THRESHOLD_ERROR_RATE=20       # 错误率20%触发熔断
THRESHOLD_RESPONSE_TIME=30000 # 30秒响应时间触发熔断
THRESHOLD_REPEAT_ERROR=3      # 连续3次同类错误触发熔断

# 初始化
init() {
    mkdir -p "$METRICS_DIR"
    
    if [[ ! -f "$CIRCUIT_STATE" ]]; then
        cat > "$CIRCUIT_STATE" << EOF
{
    "state": "CLOSED",
    "last_check": "$(date '+%Y-%m-%d %H:%M:%S')",
    "error_count": 0,
    "success_count": 0,
    "trip_count": 0
}
EOF
    fi
}

# 日志
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$CIRCUIT_LOG"
}

# 获取当前状态
get_state() {
    grep -o '"state": "[^"]*"' "$CIRCUIT_STATE" | cut -d'"' -f4
}

# 更新状态
set_state() {
    local new_state="$1"
    local reason="${2:-""}"
    
    cat > "$CIRCUIT_STATE" << EOF
{
    "state": "$new_state",
    "last_change": "$(date '+%Y-%m-%d %H:%M:%S')",
    "previous_state": "$(get_state)",
    "reason": "$reason",
    "trip_count": $(($(grep -o '"trip_count": [0-9]*' "$CIRCUIT_STATE" | awk '{print $2}') + 1))
}
EOF
    
    log "STATE_CHANGE: $new_state - $reason"
}

# 记录指标
record_metric() {
    local metric_type="$1"
    local value="$2"
    local timestamp
    timestamp=$(date '+%Y%m%d_%H%M%S')
    
    echo "{\"time\": \"$timestamp\", \"type\": \"$metric_type\", \"value\": $value}" \
        >> "$METRICS_DIR/${metric_type}_${timestamp}.json"
}

# 检查是否允许执行
check_allow() {
    local state
    state=$(get_state)
    
    case "$state" in
        CLOSED)
            # 正常状态，允许执行
            return 0
            ;;
        OPEN)
            # 熔断状态，阻止执行
            log "CIRCUIT_OPEN: 熔断器打开，阻止执行"
            echo "🔴 系统处于熔断状态，请检查问题后手动重置"
            return 1
            ;;
        HALF_OPEN)
            # 半开状态，允许试探性执行
            log "CIRCUIT_HALF_OPEN: 半开状态，允许试探执行"
            return 0
            ;;
    esac
}

# 检测错误并可能触发熔断
detect_error() {
    local error_type="$1"
    local error_detail="${2:-""}"
    
    log "ERROR_DETECTED: $error_type - $error_detail"
    record_metric "error" 1
    
    # 检查连续错误
    local recent_errors
    recent_errors=$(find "$METRICS_DIR" -name "error_*.json" -mmin -5 | wc -l)
    
    if [[ $recent_errors -ge $THRESHOLD_REPEAT_ERROR ]]; then
        log "TRIP_DECISION: 连续错误 $recent_errors 次，触发熔断"
        set_state "OPEN" "连续 $recent_errors 次错误: $error_type"
        
        # 通知锁系统
        if [[ -x ./LOCK_SYSTEM.sh ]]; then
            ./LOCK_SYSTEM.sh lockdown "Circuit breaker tripped: $error_type"
        fi
        
        return 1
    fi
    
    return 0
}

# 记录成功
record_success() {
    record_metric "success" 1
    
    local state
    state=$(get_state)
    
    # 半开状态下连续成功，关闭熔断器
    if [[ "$state" == "HALF_OPEN" ]]; then
        local recent_success
        recent_success=$(find "$METRICS_DIR" -name "success_*.json" -mmin -5 | wc -l)
        
        if [[ $recent_success -ge 3 ]]; then
            set_state "CLOSED" "半开状态连续成功，恢复正常"
        fi
    fi
}

# 手动重置熔断器
reset_circuit() {
    log "MANUAL_RESET: 手动重置熔断器"
    set_state "HALF_OPEN" "Manual reset by operator"
    
    # 清理旧指标
    find "$METRICS_DIR" -name "*.json" -mmin +60 -delete
    
    echo "✅ 熔断器已重置为半开状态，系统将试探性恢复"
}

# 自动检查（定时任务调用）
auto_check() {
    # 检查是否需要半开→关闭转换
    local state
    state=$(get_state)
    
    if [[ "$state" == "OPEN" ]]; then
        local last_change
        last_change=$(grep -o '"last_change": "[^"]*"' "$CIRCUIT_STATE" | cut -d'"' -f4)
        local last_ts
        last_ts=$(date -d "$last_change" +%s 2>/dev/null || echo 0)
        local now_ts
        now_ts=$(date +%s)
        local elapsed=$((now_ts - last_ts))
        
        # 5分钟后自动尝试半开
        if [[ $elapsed -gt 300 ]]; then
            set_state "HALF_OPEN" "Auto recovery after ${elapsed}s"
        fi
    fi
}

# 主入口
init

case "${1:-status}" in
    check)
        check_allow
        ;;
    error)
        detect_error "${2:-Unknown}" "${3:-}"
        ;;
    success)
        record_success
        ;;
    reset)
        reset_circuit
        ;;
    auto)
        auto_check
        ;;
    status)
        echo "熔断器状态: $(get_state)"
        cat "$CIRCUIT_STATE"
        ;;
    *)
        echo "用法: $0 {check|error [类型] [详情]|success|reset|status|auto}"
        ;;
esac
