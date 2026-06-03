#!/bin/bash
# HEARTBEAT机制执行脚本
echo "=== HEARTBEAT机制检查 ==="
echo "时间: $(date)"
if [ -f "/root/.openclaw/workspace/CORE/HEARTBEAT.md" ]; then
    echo "✅ HEARTBEAT.md 存在"
else
    echo "❌ HEARTBEAT.md 不存在"
    exit 1
fi
echo "检查完成"
