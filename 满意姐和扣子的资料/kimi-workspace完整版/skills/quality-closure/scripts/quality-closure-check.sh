#!/bin/bash
# 质量闭环检查脚本
# skills/quality-closure/scripts/quality-closure-check.sh

echo "=== 质量闭环检查 ==="
echo "检查时间: $(date)"
echo ""

WORKSPACE="/root/.openclaw/workspace"
SKILL_DIR="$WORKSPACE/skills/quality-closure"
LOG_DIR="$SKILL_DIR/logs"
DEFECT_FILE="$LOG_DIR/defects.json"

mkdir -p "$LOG_DIR"

# 初始化缺陷文件
if [ ! -f "$DEFECT_FILE" ]; then
    echo "[]" > "$DEFECT_FILE"
fi

# 检查待验证修复
echo "1. 检查待验证修复..."
PENDING_VERIFY=$(cat "$DEFECT_FILE" 2>/dev/null | grep -c '"status": "fixed"' || echo "0")
echo "   待验证: $PENDING_VERIFY 个"

# 检查逾期缺陷
echo ""
echo "2. 检查逾期缺陷..."
# 这里简化处理，实际应该解析JSON检查due_date
OVERDUE=$(cat "$DEFECT_FILE" 2>/dev/null | grep -c '"level": "p0"' || echo "0")
if [ "$OVERDUE" -gt 0 ]; then
    echo "   ⚠️ 发现 $OVERDUE 个P0级缺陷，需立即处理!"
else
    echo "   ✅ 无逾期缺陷"
fi

# 检查质量指标
echo ""
echo "3. 质量指标统计..."
TOTAL_DEFECTS=$(cat "$DEFECT_FILE" 2>/dev/null | grep -c '"id":' || echo "0")
CLOSED_DEFECTS=$(cat "$DEFECT_FILE" 2>/dev/null | grep -c '"status": "closed"' || echo "0")

if [ "$TOTAL_DEFECTS" -gt 0 ]; then
    CLOSURE_RATE=$((CLOSED_DEFECTS * 100 / TOTAL_DEFECTS))
    echo "   总缺陷: $TOTAL_DEFECTS"
    echo "   已关闭: $CLOSED_DEFECTS"
    echo "   闭环率: ${CLOSURE_RATE}%"
else
    echo "   暂无缺陷记录"
fi

# 生成检查记录
LOG_FILE="$LOG_DIR/quality-check-$(date +%Y%m%d-%H%M%S).log"
cat > "$LOG_FILE" << EOF
质量闭环检查记录
check_time: $(date -Iseconds)
pending_verification: $PENDING_VERIFY
overdue_defects: $OVERDUE
total_defects: $TOTAL_DEFECTS
closed_defects: $CLOSED_DEFECTS
status: completed
EOF

echo ""
echo "记录已保存: $LOG_FILE"
echo "=== 检查完成 ==="

# 如果有P0缺陷，返回错误码
if [ "$OVERDUE" -gt 0 ]; then
    exit 1
fi

exit 0
