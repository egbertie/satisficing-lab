#!/bin/bash
# Zombie Hunter - 僵尸进程清理
# 运行频率: 每15分钟

SENTINEL_LOG_DIR="/var/log/sentinel"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

log() {
    echo "[$TIMESTAMP] $1" >> "$SENTINEL_LOG_DIR/zombie-hunter.log"
}

# 查找并清理僵尸进程
hunt_zombies() {
    log "INFO: 开始僵尸进程扫描"
    
    # 获取僵尸进程列表
    local zombies=$(ps aux | awk '$8 ~ /^Z/ {print $2, $11}' 2>/dev/null)
    
    if [ -z "$zombies" ]; then
        log "OK: 未发现僵尸进程"
        return 0
    fi
    
    log "WARN: 发现僵尸进程:"
    echo "$zombies" | while read -r pid cmd; do
        log "ZOMBIE: PID=$pid CMD=$cmd"
        
        # 尝试找到父进程
        local ppid=$(ps -o ppid= -p "$pid" 2>/dev/null | tr -d ' ')
        if [ -n "$ppid" ] && [ "$ppid" -ne 1 ]; then
            log "ACTION: 尝试终止父进程 PPID=$ppid"
            kill -15 "$ppid" 2>/dev/null && sleep 1
            
            # 检查是否仍存在
            if ps -p "$pid" >/dev/null 2>&1; then
                kill -9 "$ppid" 2>/dev/null
                log "ACTION: 强制终止父进程 PPID=$ppid"
            fi
        fi
    done
    
    # 再次检查
    sleep 2
    local remaining=$(ps aux | grep -w Z | wc -l)
    if [ "$remaining" -gt 0 ]; then
        log "WARN: 清理后仍有 $remaining 个僵尸进程"
    else
        log "OK: 僵尸进程清理完成"
    fi
}

# 清理孤儿进程（可选，谨慎使用）
orphan_check() {
    # 只清理明显异常的孤儿进程（CPU/内存占用高的）
    ps aux | awk '$3 > 50 || $4 > 50 {print $2, $3, $4, $11}' 2>/dev/null | while read -r pid cpu mem cmd; do
        # 检查是否为孤儿（PPID=1且不是关键服务）
        local ppid=$(ps -o ppid= -p "$pid" 2>/dev/null | tr -d ' ')
        if [ "$ppid" = "1" ] && [[ ! "$cmd" =~ (systemd|sshd|cron|rsyslog) ]]; then
            log "ORPHAN: 高资源孤儿进程 PID=$pid CPU=$cpu% MEM=$mem% CMD=$cmd"
        fi
    done
}

# 主执行
main() {
    mkdir -p "$SENTINEL_LOG_DIR"
    hunt_zombies
    orphan_check
}

main
exit 0
