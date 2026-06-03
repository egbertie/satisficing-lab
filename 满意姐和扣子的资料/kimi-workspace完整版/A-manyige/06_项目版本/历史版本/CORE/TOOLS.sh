#!/bin/bash
# TOOLS机制执行脚本
echo "=== TOOLS机制检查 ==="
echo "时间: $(date)"
if [ -f "/root/.openclaw/workspace/CORE/TOOLS.md" ]; then
    echo "✅ TOOLS.md 存在"
else
    echo "❌ TOOLS.md 不存在"
    exit 1
fi
echo "检查完成"
