#!/bin/bash
# ORGANIZATION机制执行脚本
echo "=== ORGANIZATION机制检查 ==="
echo "时间: $(date)"
if [ -f "/root/.openclaw/workspace/CORE/ORGANIZATION.md" ]; then
    echo "✅ ORGANIZATION.md 存在"
else
    echo "❌ ORGANIZATION.md 不存在"
    exit 1
fi
echo "检查完成"
