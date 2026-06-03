#!/bin/bash
# MEMORY机制执行脚本
echo "=== MEMORY机制检查 ==="
echo "时间: $(date)"
if [ -f "/root/.openclaw/workspace/CORE/MEMORY.md" ]; then
    echo "✅ MEMORY.md 存在"
else
    echo "❌ MEMORY.md 不存在"
    exit 1
fi
echo "检查完成"
