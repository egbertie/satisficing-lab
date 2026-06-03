#!/bin/bash
# BOOTSTRAP机制执行脚本
echo "=== BOOTSTRAP机制检查 ==="
echo "时间: $(date)"
if [ -f "/root/.openclaw/workspace/CORE/BOOTSTRAP.md" ]; then
    echo "✅ BOOTSTRAP.md 存在"
else
    echo "❌ BOOTSTRAP.md 不存在"
    exit 1
fi
echo "检查完成"
