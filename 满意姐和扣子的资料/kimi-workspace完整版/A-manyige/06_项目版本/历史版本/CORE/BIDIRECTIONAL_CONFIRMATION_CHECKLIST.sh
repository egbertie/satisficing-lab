#!/bin/bash
# BIDIRECTIONAL_CONFIRMATION_CHECKLIST机制执行脚本
echo "=== BIDIRECTIONAL_CONFIRMATION_CHECKLIST机制检查 ==="
echo "时间: $(date)"
if [ -f "/root/.openclaw/workspace/CORE/BIDIRECTIONAL_CONFIRMATION_CHECKLIST.md" ]; then
    echo "✅ BIDIRECTIONAL_CONFIRMATION_CHECKLIST.md 存在"
else
    echo "❌ BIDIRECTIONAL_CONFIRMATION_CHECKLIST.md 不存在"
    exit 1
fi
echo "检查完成"
