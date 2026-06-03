#!/bin/bash
# Sentinel Guard - 哨兵守卫系统主监控
# 全维度系统监控与自动响应
# 运行频率: 每5分钟

SCRIPT_DIR="/root/.openclaw/workspace/scripts"
LOG_DIR="/var/log/sentinel"
CONFIG_FILE="/root/.openclaw/workspace/config/sentinel-guard.conf"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# 确保日志目录存在
mkdir -p "$LOG_DIR"

# 加载配置（如果不存在则使用默认值）
load_config() {
    DISK_THRESHOLD=${DISK_THRESHOLD:-80}
    DISK_CRITICAL=${DISK_CRITICAL:-90}
    CPU_THRESHOLD=${CPU_THRESHOLD:-70}
    CPU_CRITICAL=${CPU_CRITICAL:-85}
    MEM_THRESHOLD=${MEM_THRESHOLD:-80}
    MEM_CRITICAL=${MEM_CRITICAL:-90}
    ZOMBIE_THRESHOLD=${ZOMBIE_THRESHOLD:-1}
    ZOMBIE_CRITICAL=${ZOMBIE_CRITICAL:-5}
    WORKSPACE_MAX_MB=${WORKSPACE_MAX_MB:-20480}
}
load_config

# 日志函数
log() {
    local level=$1
    local metric=$2
    local value=$3
    local details=${4:-""}
    echo "[$TIMESTAMP] $level $metric $value $details" | tee -a "$LOG_DIR/sentinel.log"
}

# ===== 存储监控 =====
check_storage() {
    # 磁盘使用率
    local disk_usage=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
    if [ "$disk_usage" -ge "$DISK_CRITICAL" ]; then
        log "CRIT" "disk_usage_percent" "$disk_usage" "超过临界值${DISK_CRITICAL}%"
        # 自动触发清理
        "$SCRIPT_DIR/disk-monitor.sh" 2>/dev/null
    elif [ "$disk_usage" -ge "$DISK_THRESHOLD" ]; then
        log "ALERT" "disk_usage_percent" "$disk_usage" "超过阈值${DISK_THRESHOLD}%"
    else
        log "OK" "disk_usage_percent" "$disk_usage"
    fi
    
    # Workspace大小
    local workspace_mb=$(du -sm /root/.openclaw/workspace 2>/dev/null | cut -f1)
    if [ "$workspace_mb" -ge "$WORKSPACE_MAX_MB" ]; then
        log "ALERT" "workspace_size_mb" "$workspace_mb" "超过${WORKSPACE_MAX_MB}MB限制"
    else
        log "OK" "workspace_size_mb" "$workspace_mb"
    fi
    
    # 嵌套备份检测
    local nest_count=$(find /root/.openclaw/workspace -type d -name "shadow-clone" 2>/dev/null | wc -l)
    if [ "$nest_count" -gt 1 ]; then
        log "CRIT" "backup_nest_level" "$nest_count" "发现嵌套备份！"
        # 自动清理
        mv /root/.openclaw/workspace/shadow-clone "/tmp/trash-shadow-clone-$(date +%Y%m%d-%H%M%S)" 2>/dev/null
    else
        log "OK" "backup_nest_level" "$nest_count"
    fi
}

# ===== 计算监控 =====
check_compute() {
    # CPU使用率（5秒平均）
    local cpu_usage=$(top -bn2 -d5 | grep "Cpu(s)" | tail -1 | awk '{print $2}' | cut -d'%' -f1)
    cpu_usage=${cpu_usage%.*}  # 取整
    
    if [ -z "$cpu_usage" ]; then
        cpu_usage=$(cat /proc/stat | awk '/cpu / {print ($2+$4)*100/($2+$4+$5)}' | cut -d'.' -f1)
    fi
    
    if [ "$cpu_usage" -ge "$CPU_CRITICAL" ]; then
        log "ALERT" "cpu_usage_percent" "$cpu_usage" "CPU使用率高"
    else
        log "OK" "cpu_usage_percent" "$cpu_usage"
    fi
    
    # 负载检查
    local load_avg=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $2}' | sed 's/,//')
    if [ "$(echo "$load_avg > 4.0" | bc 2>/dev/null || echo "0")" -eq 1 ]; then
        log "ALERT" "load_average_5m" "$load_avg" "负载过高"
    else
        log "OK" "load_average_5m" "$load_avg"
    fi
}

# ===== 内存监控 =====
check_memory() {
    # 内存使用率
    local mem_info=$(free | grep Mem)
    local mem_total=$(echo $mem_info | awk '{print $2}')
    local mem_used=$(echo $mem_info | awk '{print $3}')
    local mem_usage=$((mem_used * 100 / mem_total))
    
    if [ "$mem_usage" -ge "$MEM_CRITICAL" ]; then
        log "CRIT" "memory_usage_percent" "$mem_usage" "内存严重不足"
    elif [ "$mem_usage" -ge "$MEM_THRESHOLD" ]; then
        log "ALERT" "memory_usage_percent" "$mem_usage" "内存使用率偏高"
    else
        log "OK" "memory_usage_percent" "$mem_usage"
    fi
    
    # 交换使用率
    local swap_info=$(free | grep Swap)
    local swap_total=$(echo $swap_info | awk '{print $2}')
    if [ "$swap_total" -gt 0 ]; then
        local swap_used=$(echo $swap_info | awk '{print $3}')
        local swap_usage=$((swap_used * 100 / swap_total))
        
        if [ "$swap_usage" -ge 80 ]; then
            log "ALERT" "swap_usage_percent" "$swap_usage" "交换空间使用高"
        else
            log "OK" "swap_usage_percent" "$swap_usage"
        fi
    fi
}

# ===== 进程监控 =====
check_process() {
    # 僵尸进程
    local zombie_count=$(ps aux | grep -w Z | wc -l)
    if [ "$zombie_count" -ge "$ZOMBIE_CRITICAL" ]; then
        log "ALERT" "zombie_process_count" "$zombie_count" "僵尸进程过多"
        # 自动清理
        "$SCRIPT_DIR/zombie-hunter.sh" 2>/dev/null
    elif [ "$zombie_count" -ge "$ZOMBIE_THRESHOLD" ]; then
        log "WARN" "zombie_process_count" "$zombie_count"
    else
        log "OK" "zombie_process_count" "$zombie_count"
    fi
    
    # 总进程数
    local proc_count=$(ps aux | wc -l)
    if [ "$proc_count" -gt 300 ]; then
        log "ALERT" "total_process_count" "$proc_count" "进程数过多"
    else
        log "OK" "total_process_count" "$proc_count"
    fi
}

# ===== 日志监控 =====
check_logs() {
    # 检查日志文件大小
    local large_logs=$(find /var/log -name "*.log" -size +100M 2>/dev/null)
    if [ -n "$large_logs" ]; then
        for log in $large_logs; do
            local size=$(du -sm "$log" 2>/dev/null | cut -f1)
            log "ALERT" "log_size_mb" "$size" "日志过大: $log"
        done
        # 触发日志轮转
        "$SCRIPT_DIR/log-rotator.sh" 2>/dev/null
    fi
    
    # 检查日志系统健康
    if systemctl is-active --quiet systemd-journald 2>/dev/null; then
        log "OK" "journald_status" "active"
    else
        log "WARN" "journald_status" "inactive" "日志服务异常"
    fi
}

# ===== 主执行 =====
main() {
    log "OK" "sentinel_check_start" "$(date +%s)"
    
    check_storage
    check_compute
    check_memory
    check_process
    check_logs
    
    log "OK" "sentinel_check_complete" "$(date +%s)"
}

main
exit 0
