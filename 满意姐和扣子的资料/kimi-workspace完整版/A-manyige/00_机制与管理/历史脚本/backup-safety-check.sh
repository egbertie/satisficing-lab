#!/bin/bash
# 循环备份检测器 - 定期扫描防止嵌套
# 建议每30分钟运行一次

WORKSPACE="/root/.openclaw/workspace"
LOG_FILE="/var/log/backup-safety-check.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# 检测嵌套深度
deep_dirs=$(find "$WORKSPACE" -type d -name "shadow-clone" 2>/dev/null)
count=$(echo "$deep_dirs" | grep -c "shadow-clone" 2>/dev/null || echo "0")
count=$(echo "$count" | tr -d '\n')

if [ "$count" -gt 1 ]; then
    echo "[$TIMESTAMP] ALERT: 检测到 $count 层嵌套备份！" | tee -a "$LOG_FILE"
    echo "$deep_dirs" | tee -a "$LOG_FILE"
    
    # 发送通知（如果有配置）
    if command -v notify-send > /dev/null 2>&1; then
        notify-send "⚠️ 循环备份警告" "发现 ${count} 层嵌套，请立即检查"
    fi
    
    exit 1
fi

# 检查备份目录大小
total_size=$(du -sm "$WORKSPACE" 2>/dev/null | cut -f1)
if [ "$total_size" -gt 20480 ]; then  # 20GB上限
    echo "[$TIMESTAMP] WARN: workspace 总大小 ${total_size}MB，接近20GB红线" | tee -a "$LOG_FILE"
fi

echo "[$TIMESTAMP] CHECK_OK - 嵌套层数: $count, 总大小: ${total_size}MB" >> "$LOG_FILE"
exit 0
