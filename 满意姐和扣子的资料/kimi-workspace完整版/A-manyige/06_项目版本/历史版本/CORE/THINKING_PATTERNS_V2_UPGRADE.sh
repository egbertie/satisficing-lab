#!/bin/bash
# THINKING_PATTERNS_V2_UPGRADE机制执行脚本
echo "=== THINKING_PATTERNS_V2_UPGRADE机制检查 ==="
echo "时间: $(date)"
if [ -f "/root/.openclaw/workspace/CORE/THINKING_PATTERNS_V2_UPGRADE.md" ]; then
    echo "✅ THINKING_PATTERNS_V2_UPGRADE.md 存在"
else
    echo "❌ THINKING_PATTERNS_V2_UPGRADE.md 不存在"
    exit 1
fi
echo "检查完成"
