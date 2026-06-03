#!/bin/bash
# 搜索计数器脚本
# 确保搜索执行足够次数，防止偷工减料

COUNTER_FILE="/root/.openclaw/workspace/.search_counter"
REQUIRED_COUNT=5

echo "=== 搜索执行计数器 ==="
echo "时间: $(date)"
echo ""

CURRENT_COUNT=0
if [ -f "$COUNTER_FILE" ]; then
    CURRENT_COUNT=$(cat "$COUNTER_FILE" 2>/dev/null || echo "0")
fi

echo "当前计数: $CURRENT_COUNT"
echo "要求次数: $REQUIRED_COUNT"
echo ""

if [ "$CURRENT_COUNT" -ge "$REQUIRED_COUNT" ]; then
    echo "✅ 次数达标 ($CURRENT_COUNT >= $REQUIRED_COUNT)"
    exit 0
else
    echo "❌ 次数不足，还差 $((REQUIRED_COUNT - CURRENT_COUNT)) 次"
    exit 1
fi
