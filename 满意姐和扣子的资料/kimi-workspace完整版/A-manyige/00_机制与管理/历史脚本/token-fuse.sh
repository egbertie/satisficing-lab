#!/bin/bash
# Token熔断脚本 - 蓝军修复版

LOG_FILE="/tmp/token-fuse.log"
DATE_STR=$(date '+%Y-%m-%d %H:%M:%S')

# Token阈值设置
CRITICAL_THRESHOLD=10
WARNING_THRESHOLD=30
CAUTION_THRESHOLD=50

# 模拟Token检查
TOKEN_REMAINING=75

echo "[$DATE_STR] 🔍 Token fuse check: ${TOKEN_REMAINING}% remaining" >> "$LOG_FILE"

if [ "$TOKEN_REMAINING" -le "$CRITICAL_THRESHOLD" ]; then
    echo "[$DATE_STR] 🚨 CRITICAL: Token ${TOKEN_REMAINING}% - Entering full hibernation" >> "$LOG_FILE"
    echo "hibernation" > /tmp/token-mode.txt
elif [ "$TOKEN_REMAINING" -le "$WARNING_THRESHOLD" ]; then
    echo "[$DATE_STR] ⚠️  WARNING: Token ${TOKEN_REMAINING}% - Reducing task frequency" >> "$LOG_FILE"
    echo "reduced" > /tmp/token-mode.txt
elif [ "$TOKEN_REMAINING" -le "$CAUTION_THRESHOLD" ]; then
    echo "[$DATE_STR] ⚡ CAUTION: Token ${TOKEN_REMAINING}% - Monitor closely" >> "$LOG_FILE"
    echo "caution" > /tmp/token-mode.txt
else
    echo "[$DATE_STR] ✅ NORMAL: Token ${TOKEN_REMAINING}% - Full operation" >> "$LOG_FILE"
    echo "normal" > /tmp/token-mode.txt
fi
