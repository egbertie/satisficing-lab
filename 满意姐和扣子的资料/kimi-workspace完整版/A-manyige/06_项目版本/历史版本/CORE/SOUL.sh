#!/bin/bash
# SOUL机制执行脚本
echo "=== SOUL机制检查 ==="
echo "时间: $(date)"
if [ -f "/root/.openclaw/workspace/CORE/SOUL.md" ]; then
    echo "✅ SOUL.md 存在"
else
    echo "❌ SOUL.md 不存在"
    exit 1
fi
echo "检查完成"
