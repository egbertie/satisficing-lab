#!/bin/bash
# 磁盘空间监控与自动清理
# 当磁盘使用超过80%时自动清理临时文件

DISK_USAGE=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
LOG_FILE="/var/log/disk-monitor.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

if [ "$DISK_USAGE" -gt 80 ]; then
    echo "[$TIMESTAMP] ALERT: 磁盘使用率 ${DISK_USAGE}%，开始自动清理..." | tee -a "$LOG_FILE"
    
    # 清理1: 临时文件
    find /tmp -type f -mtime +1 -delete 2>/dev/null
    
    # 清理2: 回收站（shadow-clone 嵌套）
    find /tmp -name "trash-shadow-clone-*" -type d -mtime +1 -exec rm -rf {} + 2>/dev/null
    
    # 清理3: 日志文件（保留最近7天）
    find /var/log -name "*.log.*" -mtime +7 -delete 2>/dev/null
    find /var/log -name "*.gz" -mtime +7 -delete 2>/dev/null
    
    # 清理后检查
    DISK_AFTER=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
    echo "[$TIMESTAMP] CLEAN_DONE: 使用率从 ${DISK_USAGE}% 降至 ${DISK_AFTER}%" | tee -a "$LOG_FILE"
    
    if [ "$DISK_AFTER" -gt 85 ]; then
        echo "[$TIMESTAMP] CRITICAL: 清理后仍超过85%，需要人工介入！" | tee -a "$LOG_FILE"
        exit 1
    fi
else
    echo "[$TIMESTAMP] OK: 磁盘使用率 ${DISK_USAGE}%" >> "$LOG_FILE"
fi

exit 0
