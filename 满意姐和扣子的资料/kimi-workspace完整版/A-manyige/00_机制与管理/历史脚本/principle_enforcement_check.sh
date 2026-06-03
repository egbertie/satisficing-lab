#!/bin/bash
# 原则强制执行检查
echo "=== 原则强制执行检查 ==="

# 原则1: 第6类优先
if [ ! -f "/root/.openclaw/workspace/diary/category6_completed" ]; then
    echo "⚠️  原则1: 第6类未完成（进行中）"
fi

echo "✅ 原则检查完成"
