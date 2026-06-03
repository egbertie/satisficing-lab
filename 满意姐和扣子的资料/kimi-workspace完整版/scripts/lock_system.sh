#!/bin/bash
# 文件: /root/.openclaw/workspace/scripts/lock_system.sh
# 功能: 物理锁控制机制 - 蓝军监督锁定系统
# 作者: Skeptor-7 (蓝军)
# 创建时间: 2026-04-04

LOCK_FILE="/root/.openclaw/workspace/.blue_team_lock"
WORK_LOG="/root/.openclaw/workspace/.work_log"
SUPERVISOR_PID="/root/.openclaw/workspace/.supervisor_pid"
CIRCUIT_BREAKER="/root/.openclaw/workspace/.circuit_breaker"

# 蓝军启动时调用：建立锁定
blue_team_start() {
    echo $$ > "$SUPERVISOR_PID"
    echo "$(date '+%Y-%m-%d %H:%M:%S') BLUE_START" >> "$WORK_LOG"
    
    cat > "$LOCK_FILE" << EOF
{
    "status": "SUPERVISING",
    "pid": $$,
    "start_time": "$(date '+%Y-%m-%d %H:%M:%S')",
    "checksum": "$(date +%s | sha256sum | cut -d' ' -f1)"
}
EOF
    echo "✅ 蓝军监督启动，满意姐工作权限已解锁"
    return 0
}

# 蓝军休息时调用：释放锁定
blue_team_rest() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') BLUE_REST" >> "$WORK_LOG"
    
    cat > "$LOCK_FILE" << EOF
{
    "status": "RESTING",
    "pid": $(cat "$SUPERVISOR_PID" 2>/dev/null || echo "0"),
    "rest_time": "$(date '+%Y-%m-%d %H:%M:%S')",
    "checksum": "$(date +%s | sha256sum | cut -d' ' -f1)",
    "lock_expiry": "$(date -d '+30 minutes' '+%Y-%m-%d %H:%M:%S' 2>/dev/null || echo 'N/A')"
}
EOF
    echo "🔒 蓝军休息，满意姐工作权限已锁定（30分钟内无法操作）"
    return 0
}

# 满意姐工作前必须调用：检查锁状态
check_work_permission() {
    if [ ! -f "$LOCK_FILE" ]; then
        echo "❌ 严重违规：锁文件不存在！蓝军未启动或系统被篡改"
        echo "$(date '+%Y-%m-%d %H:%M:%S') VIOLATION_LOCK_MISSING" >> "$WORK_LOG"
        return 1
    fi
    
    STATUS=$(grep -o '"status": "[^"]*"' "$LOCK_FILE" 2>/dev/null | cut -d'"' -f4)
    
    if [ "$STATUS" != "SUPERVISING" ]; then
        REST_TIME=$(grep -o '"rest_time": "[^"]*"' "$LOCK_FILE" 2>/dev/null | cut -d'"' -f4)
        echo "❌ 工作被拒绝：蓝军处于休息状态（从 ${REST_TIME:-unknown} 开始）"
        echo "$(date '+%Y-%m-%d %H:%M:%S') VIOLATION_WORK_WHEN_REST" >> "$WORK_LOG"
        trigger_circuit_breaker "WORK_WHEN_BLUE_REST"
        return 1
    fi
    
    echo "✅ 工作权限验证通过"
    return 0
}

# 熔断机制
trigger_circuit_breaker() {
    local reason=$1
    
    cat > "$CIRCUIT_BREAKER" << EOF
{
    "triggered_at": "$(date '+%Y-%m-%d %H:%M:%S')",
    "reason": "$reason",
    "severity": "CRITICAL",
    "action": "STOP_ALL_WORK",
    "manual_reset_required": true
}
EOF
    echo "🚨 熔断器已触发！原因：$reason"
    echo "所有工作必须立即停止，等待用户手动解除"
}

# 主入口
case "$1" in
    start)
        blue_team_start
        ;;
    rest)
        blue_team_rest
        ;;
    check)
        check_work_permission
        ;;
    status)
        if [ -f "$LOCK_FILE" ]; then
            cat "$LOCK_FILE"
        else
            echo "锁文件不存在"
        fi
        ;;
    *)
        echo "用法: $0 {start|rest|check|status}"
        exit 1
        ;;
esac
