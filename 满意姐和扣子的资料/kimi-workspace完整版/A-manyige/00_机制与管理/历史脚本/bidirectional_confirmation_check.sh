#!/bin/bash
# 双向确认检查
echo "=== 双向确认检查 ==="
echo "检查是否完成双向确认..."

if [ ! -f "/tmp/confirmation_received" ]; then
    echo "❌ 未完成双向确认"
    echo "必须@对方并等待确认"
    exit 1
fi

echo "✅ 双向确认完成"
