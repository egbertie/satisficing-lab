#!/bin/bash
# 双向确认执行脚本 - 物理化机制
# 自动执行通知流程

TARGET="${1:-蓝军}"
TASK="${2:-任务}"
FILE="${3:-文件路径}"
LOG="/root/.openclaw/workspace/diary/bidirectional_confirmation.log"

log_msg() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG"
}

log_msg "=== 双向确认执行开始 ==="
log_msg "目标: $TARGET"
log_msg "任务: $TASK"
log_msg "文件: $FILE"

# 步骤1: 检查文件存在
if [ -f "$FILE" ]; then
    SIZE=$(stat -c%s "$FILE")
    log_msg "✅ 文件存在: $FILE ($SIZE 字节)"
else
    log_msg "❌ 文件不存在: $FILE"
    exit 1
fi

# 步骤2: 生成通知内容
echo ""
echo "========================================"
echo "通知内容（请复制发送给$TARGET）:"
echo "========================================"
echo ""
echo "$TARGET，$TASK 已完成。"
echo ""
echo "交付物: $FILE"
echo "大小: $SIZE 字节"
echo ""
echo "请确认收到，并开始审计。"
echo "审计完成后，请明确说'通过'或'需修正'。"
echo ""
echo "验证命令:"
echo "  ls -la $FILE"
echo "  cat $FILE"
echo ""
echo "========================================"
echo ""

log_msg "通知内容已生成"
log_msg "请手动发送给$TARGET"

# 步骤3: 开始计时
START_TIME=$(date +%s)
log_msg "计时开始: $(date)"
log_msg "1分钟后如无回应，再次通知"
log_msg "2分钟后如无回应，申请用户介入"

# 保存状态
STATE_FILE="/tmp/bidirectional_state_$(echo "$TASK" | tr ' ' '_').txt"
echo "$START_TIME" > "$STATE_FILE"
echo "$TARGET" >> "$STATE_FILE"
echo "$TASK" >> "$STATE_FILE"

log_msg "状态已保存: $STATE_FILE"
log_msg "=== 双向确认执行完成 ==="
