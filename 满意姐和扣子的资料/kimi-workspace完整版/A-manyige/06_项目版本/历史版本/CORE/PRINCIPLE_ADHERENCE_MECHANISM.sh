#!/bin/bash
# PRINCIPLE_ADHERENCE_MECHANISM机制执行脚本
echo "=== PRINCIPLE_ADHERENCE_MECHANISM机制检查 ==="
echo "时间: $(date)"
if [ -f "/root/.openclaw/workspace/CORE/PRINCIPLE_ADHERENCE_MECHANISM.md" ]; then
    echo "✅ PRINCIPLE_ADHERENCE_MECHANISM.md 存在"
else
    echo "❌ PRINCIPLE_ADHERENCE_MECHANISM.md 不存在"
    exit 1
fi
echo "检查完成"
