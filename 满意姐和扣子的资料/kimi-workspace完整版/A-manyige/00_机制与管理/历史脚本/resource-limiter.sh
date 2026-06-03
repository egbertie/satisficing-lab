#!/bin/bash
# Resource Limiter - 资源限制与保护
# 运行频率: 每5分钟

SENTINEL_LOG_DIR="/var/log/sentinel"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# 资源限制阈值
CPU_PER_PROCESS_LIMIT=50   # 单进程CPU上限%
MEM_PER_PROCESS_LIMIT=20   # 单进程内存上限%
MAX_OPEN_FILES=10000       # 单进程文件句柄上限

log() {
    echo "[$TIMESTAMP] $1" >> "$SENTINEL_LOG_DIR/resource-limiter.log"
}

# CPU资源限制
check_cpu_abusers() {
    log "INFO: 检查高CPU进程"
    
    ps aux | awk -v limit="$CPU_PER_PROCESS_LIMIT" '$3 > limit && $11 !~ /^\[/ {print $2, $3, $11}' 2>/dev/null | while read -r pid cpu cmd; do
        log "ALERT: 高CPU进程 PID=$pid CPU=${cpu}% CMD=$cmd"
        
        # 如果是用户进程，尝试降低优先级
        if [[ "$cmd" =~ (python|node|npm) ]]; then
            renice +10 -p "$pid" 2>/dev/null
            log "ACTION: 降低进程优先级 PID=$pid"
        fi
        
        # 如果持续超过80%，记录详细信息
        if [ "${cpu%.*}" -gt 80 ]; then
            log "CRIT: 超高CPU进程，需关注 PID=$pid"
        fi
    done
}

# 内存资源限制
check_memory_abusers() {
    log "INFO: 检查高内存进程"
    
    ps aux | awk -v limit="$MEM_PER_PROCESS_LIMIT" '$4 > limit && $11 !~ /^\[/ {print $2, $4, $6, $11}' 2>/dev/null | while read -r pid mem rss cmd; do
        local rss_mb=$((rss / 1024))
        log "WARN: 高内存进程 PID=$pid MEM=${mem}% RSS=${rss_mb}MB CMD=$cmd"
        
        # 如果RSS超过1GB且不是关键服务，警告
        if [ "$rss_mb" -gt 1024 ] && [[ ! "$cmd" =~ (openclaw|systemd) ]]; then
            log "ALERT: 超高内存使用 PID=$pid RSS=${rss_mb}MB"
        fi
    done
}

# 文件句柄限制
check_file_handles() {
    log "INFO: 检查文件句柄使用"
    
    # 系统总句柄数
    local system_handles=$(cat /proc/sys/fs/file-nr 2>/dev/null | awk '{print $1}')
    local system_max=$(cat /proc/sys/fs/file-max 2>/dev/null)
    local usage_percent=$((system_handles * 100 / system_max))
    
    if [ "$usage_percent" -gt 80 ]; then
        log "ALERT: 系统文件句柄使用率 ${usage_percent}% ($system_handles/$system_max)"
    fi
    
    # 检查单个进程的句柄使用
    for pid in $(ls /proc | grep -E '^[0-9]+$' | head -50); do
        if [ -d "/proc/$pid/fd" ]; then
            local fd_count=$(ls /proc/$pid/fd 2>/dev/null | wc -l)
            if [ "$fd_count" -gt "$MAX_OPEN_FILES" ]; then
                local cmd=$(cat /proc/$pid/comm 2>/dev/null || echo "unknown")
                log "ALERT: 进程文件句柄过多 PID=$pid FD=$fd_count CMD=$cmd"
            fi
        fi
    done
}

# 网络连接限制
check_network_connections() {
    log "INFO: 检查网络连接"
    
    local established=$(netstat -an 2>/dev/null | grep ESTABLISHED | wc -l)
    local time_wait=$(netstat -an 2>/dev/null | grep TIME_WAIT | wc -l)
    
    if [ "$established" -gt 100 ]; then
        log "WARN: 大量ESTABLISHED连接: $established"
    fi
    
    if [ "$time_wait" -gt 200 ]; then
        log "WARN: 大量TIME_WAIT连接: $time_wait"
        # 尝试清理（谨慎）
        # echo 1 > /proc/sys/net/ipv4/tcp_tw_reuse 2>/dev/null || true
    fi
}

# I/O监控
check_io_pressure() {
    if [ -f /proc/pressure/io ]; then
        local io_wait=$(cat /proc/pressure/io 2>/dev/null | grep "some" | awk -F'=' '{print $2}' | awk -F',' '{print $1}')
        if [ -n "$io_wait" ] && [ "${io_wait%.*}" -gt 50 ]; then
            log "ALERT: IO等待时间高: ${io_wait}"
        fi
    fi
}

# 主执行
main() {
    mkdir -p "$SENTINEL_LOG_DIR"
    
    check_cpu_abusers
    check_memory_abusers
    check_file_handles
    check_network_connections
    check_io_pressure
}

main
exit 0
