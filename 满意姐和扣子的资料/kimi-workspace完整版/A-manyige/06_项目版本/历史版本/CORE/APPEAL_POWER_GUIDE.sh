#!/bin/bash
# APPEAL_POWER_GUIDE机制执行脚本
echo "=== APPEAL_POWER_GUIDE机制检查 ==="
echo "时间: $(date)"
if [ -f "/root/.openclaw/workspace/CORE/APPEAL_POWER_GUIDE.md" ]; then
    echo "✅ APPEAL_POWER_GUIDE.md 存在"
else
    echo "❌ APPEAL_POWER_GUIDE.md 不存在"
    exit 1
fi
echo "检查完成"
