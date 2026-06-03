#!/bin/bash
# 工作流锁定检查脚本
# 防止并发冲突和状态不一致

LOCK_FILE="/root/.openclaw/workspace/.workflow_lock"
LOCK_TIMEOUT=300

echo "=== 工作流锁定检查 ==="
echo "时间: $(date)"
echo ""

if [ -f "$LOCK_FILE" ]; then
    LOCK_PID=$(cat "$LOCK_FILE" 2>/dev/null || echo "")
    LOCK_TIME=$(stat -c %Y "$LOCK_FILE" 2>/dev/null || echo "0")
    CURRENT_TIME=$(date +%s)
    LOCK_AGE=$((CURRENT_TIME - LOCK_TIME))
    
    echo "发现活跃锁:"
    echo "  PID: $LOCK_PID"
    echo "  年龄: ${LOCK_AGE}秒"
    
    if [ -n "$LOCK_PID" ] && kill -0 "$LOCK_PID" 2>/dev/null; then
        if [ $LOCK_AGE -gt $LOCK_TIMEOUT ]; then
            echo "  ⚠️ 超时(${LOCK_AGE}秒)"
            exit 1
        else
            echo "  正常锁定中"
            exit 1
        fi
    else
        echo "  僵尸锁，自动清理..."
        rm -f "$LOCK_FILE"
        echo "  ✅ 已清理"
    fi
else
    echo "✅ 无活跃锁，工作流可用"
fi
