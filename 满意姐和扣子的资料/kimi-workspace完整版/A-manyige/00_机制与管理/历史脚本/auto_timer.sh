#!/bin/bash
# 自动计时器
# 1分钟/2分钟自动提醒

TARGET="${1:-蓝军}"
LOG="/root/.openclaw/workspace/diary/auto_timer.log"

START=$(date +%s)
echo "[$TARGET] 计时开始: $(date '+%H:%M:%S')" | tee -a "$LOG"

while true; do
    NOW=$(date +%s)
    ELAPSED=$((NOW - START))
    
    # 1分钟
    if [ $ELAPSED -eq 60 ]; then
        echo "⚠️  [$TARGET] 1分钟到，无回应" | tee -a "$LOG"
        echo "请再次通知$TARGET"
    fi
    
    # 2分钟
    if [ $ELAPSED -eq 120 ]; then
        echo "❌  [$TARGET] 2分钟到，无回应" | tee -a "$LOG"
        echo "请申请用户介入"
        break
    fi
    
    sleep 1
done
