#!/bin/bash
################################################################################
# Token智能时段控制器 - 自动切换对话模式
# 用途: 根据时间段自动优化Token消耗策略
################################################################################

set -euo pipefail

CONFIG_FILE="/root/.openclaw/workspace/config/token_mode_config.json"
STATE_FILE="/tmp/token_mode_state.json"
LOG_FILE="/tmp/token_mode_controller.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# 获取当前小时（北京时间）
get_current_hour() {
    date -d '+8 hours' +%H | sed 's/^0//'
}

# 判断当前时段模式
get_mode_for_hour() {
    local hour=$1
    if [[ $hour -ge 0 && $hour -lt 8 ]]; then
        echo "hibernate"  # 00:00-08:00 休眠模式
    elif [[ $hour -ge 9 && $hour -lt 18 ]]; then
        echo "core"        # 09:00-18:00 核心工作模式
    else
        echo "light"       # 18:00-24:00 轻度模式
    fi
}

# 获取模式配置
get_mode_config() {
    local mode=$1
    case $mode in
        "hibernate")
            echo '{"token_limit":500,"response_style":"minimal","context_depth":"surface","enabled":true}'
            ;;
        "core")
            echo '{"token_limit":8000,"response_style":"full","context_depth":"deep","enabled":true}'
            ;;
        "light")
            echo '{"token_limit":3000,"response_style":"balanced","context_depth":"medium","enabled":true}'
            ;;
        *)
            echo '{"token_limit":5000,"response_style":"balanced","context_depth":"medium","enabled":true}'
            ;;
    esac
}

# 主逻辑
main() {
    local hour=$(get_current_hour)
    local mode=$(get_mode_for_hour $hour)
    local config=$(get_mode_config $mode)
    
    # 检查状态变化
    local last_mode=""
    if [[ -f "$STATE_FILE" ]]; then
        last_mode=$(cat "$STATE_FILE" | grep -o '"mode":"[^"]*"' | cut -d'"' -f4)
    fi
    
    if [[ "$mode" != "$last_mode" ]]; then
        log "模式切换: ${last_mode:-none} → $mode (小时: $hour)"
        echo "{\"mode\":\"$mode\",\"hour\":$hour,\"config\":$config,\"updated\":$(date +%s)}" > "$STATE_FILE"
        
        # 发送模式变更通知（可选）
        # echo "Token模式已切换至: $mode" | wall 2>/dev/null || true
    fi
    
    echo "$config"
}

main "$@"
