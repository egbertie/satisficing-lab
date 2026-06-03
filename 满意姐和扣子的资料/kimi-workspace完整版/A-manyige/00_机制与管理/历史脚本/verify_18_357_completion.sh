#!/bin/bash
# 18+357 完成验证脚本

echo "=== 18+357 执行完成验证 ==="
echo "时间: $(date)"
echo ""

echo "【18个CORE脚本】"
CORE_COUNT=$(ls /root/.openclaw/workspace/CORE/*.sh 2>/dev/null | wc -l)
echo "已完成: $CORE_COUNT 个脚本"
echo ""

echo "【357个技能验证】"
SKILL_COUNT=$(find /root/.openclaw/workspace/skills/ -name "verified" -type f 2>/dev/null | wc -l)
echo "已完成: $SKILL_COUNT 个技能验证"
echo ""

echo "【总体进度】"
if [ $CORE_COUNT -ge 18 ] && [ $SKILL_COUNT -ge 357 ]; then
    echo "✅ 18+357 全部完成"
    echo "状态: COMPLETED"
    echo "$(date): 18+357 全部完成" > /tmp/18_357_COMPLETED
else
    echo "⚠️  部分完成"
    echo "脚本: $CORE_COUNT/18"
    echo "技能: $SKILL_COUNT/357"
fi
