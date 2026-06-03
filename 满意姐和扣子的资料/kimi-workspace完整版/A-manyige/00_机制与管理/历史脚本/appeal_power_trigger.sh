#!/bin/bash
# 申诉权触发检查
echo "=== 申诉权检查 ==="
echo "检查是否有不合理要求..."

# 自动触发逻辑
if [ -f "/tmp/unreasonable_request" ]; then
    echo "⚠️  检测到不合理要求"
    echo "必须使用申诉权"
    echo "参考: CORE/APPEAL_POWER_GUIDE.md"
    exit 1
fi

echo "✅ 无申诉需求"
