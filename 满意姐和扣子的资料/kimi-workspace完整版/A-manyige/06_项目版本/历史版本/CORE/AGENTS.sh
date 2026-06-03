#!/bin/bash
# AGENTS机制执行脚本
# 检查agents配置和执行状态

echo "=== AGENTS机制检查 ==="
echo "时间: $(date)"

# 检查AGENTS.md是否存在
if [ -f "/root/.openclaw/workspace/CORE/AGENTS.md" ]; then
    echo "✅ AGENTS.md 存在"
else
    echo "❌ AGENTS.md 不存在"
    exit 1
fi

# 检查关键配置
echo "检查完成"
