#!/bin/bash
# USER机制执行脚本
echo "=== USER机制检查 ==="
echo "时间: $(date)"
if [ -f "/root/.openclaw/workspace/CORE/USER.md" ]; then
    echo "✅ USER.md 存在"
else
    echo "❌ USER.md 不存在"
    exit 1
fi
echo "检查完成"
