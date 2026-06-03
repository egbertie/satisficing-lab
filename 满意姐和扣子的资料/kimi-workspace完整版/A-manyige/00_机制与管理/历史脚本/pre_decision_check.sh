#!/bin/bash
# 自动计时器
TARGET="${1:-蓝军}"
START=$(date +%s)
echo "计时开始: $(date '+%H:%M:%S')"

while true; do
    NOW=$(date +%s)
    ELAPSED=$((NOW - START))
    
    if [ $ELAPSED -eq 60 ]; then
        echo "⚠️  1分钟到，请再次通知"
    fi
    
    if [ $ELAPSED -eq 120 ]; then
        echo "❌ 2分钟到，请申请用户介入"
        break
    fi
    
    sleep 1
done
