#!/bin/bash
# Log Rotator - 日志轮转与清理
# 运行频率: 每日

LOG_DIR="/var/log"
SENTINEL_LOG_DIR="/var/log/sentinel"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
RETENTION_DAYS=7
MAX_LOG_SIZE_MB=100

log() {
    echo "[$TIMESTAMP] $1" >> "$SENTINEL_LOG_DIR/log-rotator.log"
}

# 轮转大日志文件
rotate_large_logs() {
    log "INFO: 开始检查大日志文件"
    
    find "$LOG_DIR" -name "*.log" -size +${MAX_LOG_SIZE_MB}M 2>/dev/null | while read -r logfile; do
        local basename=$(basename "$logfile" .log)
        local rotated="${logfile}.${TIMESTAMP}.gz"
        
        # 压缩归档
        gzip -c "$logfile" > "$rotated"
        
        # 清空原文件
        > "$logfile"
        
        log "ROTATED: $logfile -> $rotated ($(du -sh "$rotated" | cut -f1))"
    done
}

# 清理旧归档
cleanup_old_archives() {
    log "INFO: 清理${RETENTION_DAYS}天前的日志归档"
    
    find "$LOG_DIR" -name "*.gz" -mtime +$RETENTION_DAYS -delete 2>/dev/null
    find "$SENTINEL_LOG_DIR" -name "*.gz" -mtime +$RETENTION_DAYS -delete 2>/dev/null
    
    log "INFO: 旧归档清理完成"
}

# 清理特定日志
cleanup_specific_logs() {
    # 清理shadow-clone.log（如果超过50MB）
    if [ -f "$LOG_DIR/shadow-clone.log" ]; then
        local size=$(du -sm "$LOG_DIR/shadow-clone.log" 2>/dev/null | cut -f1)
        if [ "$size" -gt 50 ]; then
            > "$LOG_DIR/shadow-clone.log"
            log "CLEARED: shadow-clone.log (${size}MB)"
        fi
    fi
    
    # 清理cloud-monitor-agent.log（如果超过10MB）
    if [ -f "$LOG_DIR/iaas_monitor/cloud-monitor-agent.log" ]; then
        local size=$(du -sm "$LOG_DIR/iaas_monitor/cloud-monitor-agent.log" 2>/dev/null | cut -f1)
        if [ "$size" -gt 10 ]; then
            > "$LOG_DIR/iaas_monitor/cloud-monitor-agent.log"
            log "CLEARED: cloud-monitor-agent.log (${size}MB)"
        fi
    fi
}

# 修复日志系统
repair_journald() {
    log "INFO: 检查journald状态"
    
    # 检查磁盘空间
    local avail=$(df /var/log/journal 2>/dev/null | tail -1 | awk '{print $4}' || echo "0")
    if [ "$avail" -lt 102400 ]; then  # 100MB
        log "WARN: journald分区空间不足，执行清理"
        journalctl --vacuum-time=3d 2>/dev/null || true
        journalctl --vacuum-size=500M 2>/dev/null || true
    fi
    
    # 重启journald（如果需要）
    if ! systemctl is-active --quiet systemd-journald 2>/dev/null; then
        log "ALERT: journald未运行，尝试重启"
        systemctl restart systemd-journald 2>/dev/null || log "ERROR: 无法重启journald"
    fi
}

# 主执行
main() {
    mkdir -p "$SENTINEL_LOG_DIR"
    log "INFO: === 日志轮转任务开始 ==="
    
    rotate_large_logs
    cleanup_old_archives
    cleanup_specific_logs
    repair_journald
    
    log "INFO: === 日志轮转任务完成 ==="
}

main
exit 0
