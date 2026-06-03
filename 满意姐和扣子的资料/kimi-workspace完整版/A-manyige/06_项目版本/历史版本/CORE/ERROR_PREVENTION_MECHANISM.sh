#!/bin/bash
# ERROR_PREVENTION_MECHANISM机制执行脚本
echo "=== ERROR_PREVENTION_MECHANISM机制检查 ==="
echo "时间: $(date)"
if [ -f "/root/.openclaw/workspace/CORE/ERROR_PREVENTION_MECHANISM.md" ]; then
    echo "✅ ERROR_PREVENTION_MECHANISM.md 存在"
else
    echo "❌ ERROR_PREVENTION_MECHANISM.md 不存在"
    exit 1
fi
echo "检查完成"
