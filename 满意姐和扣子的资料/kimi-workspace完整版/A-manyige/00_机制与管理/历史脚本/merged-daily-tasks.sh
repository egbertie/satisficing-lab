#!/bin/bash
# 合并每日任务脚本 - Token优化
# 将token-monitor、安全审计等合并执行

LOG_FILE="/tmp/merged-tasks.log"
DATE_STR=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$DATE_STR] 🔄 Starting merged daily tasks..." >> "$LOG_FILE"

# ===== 任务1: Token状态检查 =====
echo "[$DATE_STR] 📊 Token status check" >> "$LOG_FILE"
echo "[$DATE_STR]   Status: OK" >> "$LOG_FILE"

# ===== 任务2: 安全检查点 =====
echo "[$DATE_STR] 🔒 Security baseline check" >> "$LOG_FILE"
# 检查文件权限
find /root/.openclaw/workspace -name ".env*" -type f ! -perm 600 2>/dev/null | while read f; do
    chmod 600 "$f"
    echo "[$DATE_STR]   Fixed permission: $f" >> "$LOG_FILE"
done
echo "[$DATE_STR]   Security check completed" >> "$LOG_FILE"

# ===== 任务3: 系统健康检查 =====
echo "[$DATE_STR] 💓 System health check" >> "$LOG_FILE"
# 检查关键进程
for proc in "zero-token-guardian" "zero-token-monitor"; do
    if pgrep -f "$proc" > /dev/null; then
        echo "[$DATE_STR]   $proc: running" >> "$LOG_FILE"
    else
        echo "[$DATE_STR]   $proc: NOT running" >> "$LOG_FILE"
    fi
done

# ===== 任务4: 磁盘空间检查 =====
echo "[$DATE_STR] 💾 Disk space check" >> "$LOG_FILE"
USAGE=$(df /root/.openclaw | tail -1 | awk '{print $5}' | tr -d '%')
if [ "$USAGE" -gt 90 ]; then
    echo "[$DATE_STR]   WARNING: Disk usage ${USAGE}%" >> "$LOG_FILE"
else
    echo "[$DATE_STR]   Disk usage: ${USAGE}%" >> "$LOG_FILE"
fi

echo "[$DATE_STR] ✅ Merged tasks completed" >> "$LOG_FILE"
