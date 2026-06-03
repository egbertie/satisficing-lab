#!/bin/bash
# IDENTITY机制执行脚本
echo "=== IDENTITY机制检查 ==="
echo "时间: $(date)"
if [ -f "/root/.openclaw/workspace/CORE/IDENTITY.md" ]; then
    echo "✅ IDENTITY.md 存在"
else
    echo "❌ IDENTITY.md 不存在"
    exit 1
fi
echo "检查完成"
