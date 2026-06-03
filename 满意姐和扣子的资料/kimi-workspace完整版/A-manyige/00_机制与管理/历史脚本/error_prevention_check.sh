#!/bin/bash
# 错误预防检查脚本 - 物理化执行
ERRORS=0
echo "=== 错误预防检查 ==="
echo "时间: $(date)"

# 检查1: 单向沟通
if [ ! -f "/tmp/confirmation_received" ]; then
    echo "❌ 未确认双向确认"
    ERRORS=$((ERRORS + 1))
else
    echo "✅ 双向确认已确认"
fi

# 检查2: 原则坚持  
if [ ! -f "/root/.openclaw/workspace/diary/category6_completed" ]; then
    echo "⚠️  第6类未完成（进行中）"
fi

if [ $ERRORS -gt 0 ]; then
    echo "❌ 发现 $ERRORS 个错误"
    exit 1
else
    echo "✅ 检查通过"
    exit 0
fi
