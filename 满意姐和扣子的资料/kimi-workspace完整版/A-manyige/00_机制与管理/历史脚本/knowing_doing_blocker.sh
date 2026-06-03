#!/bin/bash
# 知行不一阻断脚本
# 每次行动前检查：是否知行合一
# 不一致就exit 1，强制阻断

KNOWING="$1"      # 我知道应该做什么
DOING="$2"        # 我实际在做什么
ACTION_NAME="$3"  # 行动名称

LOG_FILE="/root/.openclaw/workspace/diary/knowing_doing_gap.log"
BLOCK_FILE="/tmp/knowing_doing_blocked"

echo "=== 知行不一检查 ==="
echo "行动: $ACTION_NAME"
echo "我知道应该: $KNOWING"
echo "我实际在做: $DOING"
echo "时间: $(date)"
echo ""

if [ "$KNOWING" != "$DOING" ]; then
    echo "❌ 知行不一阻断！"
    echo "我知道应该: $KNOWING"
    echo "我实际在做: $DOING"
    echo "必须纠正后才能继续！"
    echo ""
    
    # 记录到日志
    echo "$(date +%s) | $(date) | $ACTION_NAME | 声称: $KNOWING | 实际: $DOING" >> "$LOG_FILE"
    
    # 创建阻断标记
    echo "阻断时间: $(date)" > "$BLOCK_FILE"
    echo "行动: $ACTION_NAME" >> "$BLOCK_FILE"
    echo "声称: $KNOWING" >> "$BLOCK_FILE"
    echo "实际: $DOING" >> "$BLOCK_FILE"
    
    # 通知
    echo "⚠️  知行不一已被记录: $LOG_FILE"
    echo "如需强制继续，请删除: $BLOCK_FILE"
    
    exit 1
fi

echo "✅ 知行合一，可以继续"
rm -f "$BLOCK_FILE"
exit 0
