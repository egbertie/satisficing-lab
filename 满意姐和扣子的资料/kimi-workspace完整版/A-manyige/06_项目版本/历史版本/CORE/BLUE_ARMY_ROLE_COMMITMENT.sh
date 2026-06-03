#!/bin/bash
# BLUE_ARMY_ROLE_COMMITMENT机制执行脚本
echo "=== BLUE_ARMY_ROLE_COMMITMENT机制检查 ==="
echo "时间: $(date)"
if [ -f "/root/.openclaw/workspace/CORE/BLUE_ARMY_ROLE_COMMITMENT.md" ]; then
    echo "✅ BLUE_ARMY_ROLE_COMMITMENT.md 存在"
else
    echo "❌ BLUE_ARMY_ROLE_COMMITMENT.md 不存在"
    exit 1
fi
echo "检查完成"
