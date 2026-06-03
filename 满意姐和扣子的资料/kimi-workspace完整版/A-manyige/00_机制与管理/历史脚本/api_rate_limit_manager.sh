#!/bin/bash
# API调用节流管理器
# 防止触发rate limit

RATE_LIMIT_LOG="/root/.openclaw/workspace/diary/api_rate_limit_manager.log"
CALL_COUNT=0
MAX_CALLS_PER_MINUTE=30

echo "=== API调用节流管理器 ===" | tee -a "$RATE_LIMIT_LOG"
echo "启动时间: $(date)" | tee -a "$RATE_LIMIT_LOG"
echo "最大调用频率: $MAX_CALLS_PER_MINUTE 次/分钟" | tee -a "$RATE_LIMIT_LOG"
echo "" | tee -a "$RATE_LIMIT_LOG"

# 节流函数
throttle() {
    CALL_COUNT=$((CALL_COUNT + 1))
    
    if [ $CALL_COUNT -ge $MAX_CALLS_PER_MINUTE ]; then
        echo "达到频率限制，暂停5秒..." | tee -a "$RATE_LIMIT_LOG"
        sleep 5
        CALL_COUNT=0
    else
        # 每5次调用后小暂停
        if [ $((CALL_COUNT % 5)) -eq 0 ]; then
            sleep 1
        fi
    fi
}

# 导出函数供其他脚本使用
export -f throttle
export RATE_LIMIT_LOG

echo "节流管理器已启动" | tee -a "$RATE_LIMIT_LOG"
echo "使用: source scripts/api_rate_limit_manager.sh" | tee -a "$RATE_LIMIT_LOG"
