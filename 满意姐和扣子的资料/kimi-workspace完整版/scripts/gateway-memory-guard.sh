#!/bin/bash
# Gateway Memory Guard - 自动监控与重启止血脚本
# 版本: 1.1
# 创建于: 2026-04-12
# 阈值: RSS >= 800MB 时自动重启
# 2026-04-12 修正: 每次检测追加结构化 JSON 到 memory/gateway-memory-series.json

PID=$(pgrep -f "openclaw-gateway" | head -1)
THRESHOLD_MB=800
LOG_FILE="/root/.openclaw/logs/gateway-memory-guard.log"
SERIES_FILE="/root/.openclaw/workspace/memory/gateway-memory-series.json"
NOW=$(date '+%Y-%m-%d %H:%M:%S')
NOW_ISO=$(date -Iseconds)

if [ -z "$PID" ]; then
    echo "${NOW} - Gateway not running, starting..." >> "$LOG_FILE"
    systemctl restart openclaw-gateway 2>/dev/null || /usr/local/bin/openclaw gateway restart 2>/dev/null
    # 追加 JSON 记录
    echo "{\"time\":\"${NOW_ISO}\",\"rss_mb\":0,\"threshold_mb\":${THRESHOLD_MB},\"action\":\"start\",\"status\":\"not_running\"}" >> "$SERIES_FILE"
    exit 0
fi

RSS_KB=$(cat /proc/$PID/status | grep VmRSS | awk '{print $2}')
RSS_MB=$((RSS_KB / 1024))

if [ "$RSS_MB" -ge "$THRESHOLD_MB" ]; then
    echo "${NOW} - Gateway RSS=${RSS_MB}MB >= ${THRESHOLD_MB}MB, restarting..." >> "$LOG_FILE"
    # 强制终止确保重启生效，然后启动新进程
    kill -TERM "$PID" 2>/dev/null
    sleep 2
    kill -KILL "$PID" 2>/dev/null
    sleep 1
    # 在重启前清理过期的 cron session，降低启动基线内存
    if [ -x "/root/.openclaw/workspace/scripts/gateway-session-bloat-cleaner.sh" ]; then
        /root/.openclaw/workspace/scripts/gateway-session-bloat-cleaner.sh >> "$LOG_FILE" 2>&1
    fi
    systemctl restart openclaw-gateway 2>/dev/null || /usr/local/bin/openclaw gateway restart 2>/dev/null
    NEW_PID=$(pgrep -f "openclaw-gateway" | head -1)
    echo "${NOW} - Gateway restarted. Old PID=${PID}, New PID=${NEW_PID:-unknown}" >> "$LOG_FILE"
    ACTION="restart"
    STATUS="threshold_exceeded"
else
    echo "${NOW} - Gateway RSS=${RSS_MB}MB, OK." >> "$LOG_FILE"
    ACTION="none"
    STATUS="ok"
fi

# 追加结构化 JSON 记录
echo "{\"time\":\"${NOW_ISO}\",\"pid\":${PID},\"rss_mb\":${RSS_MB},\"threshold_mb\":${THRESHOLD_MB},\"action\":\"${ACTION}\",\"status\":\"${STATUS}\"}" >> "$SERIES_FILE"
