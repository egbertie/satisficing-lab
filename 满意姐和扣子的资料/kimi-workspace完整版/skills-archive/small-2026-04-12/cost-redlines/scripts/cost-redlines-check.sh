#!/bin/bash
# 成本红线检查脚本
# skills/cost-redlines/scripts/cost-redlines-check.sh

echo "=== 成本红线检查 ==="
echo "检查时间: $(date)"
echo ""

WORKSPACE="/root/.openclaw/workspace"
SKILL_DIR="$WORKSPACE/skills/cost-redlines"
LOG_DIR="$SKILL_DIR/logs"
BUDGET_FILE="$LOG_DIR/budgets.json"
COST_FILE="$LOG_DIR/costs.json"

mkdir -p "$LOG_DIR"

# 初始化文件
if [ ! -f "$BUDGET_FILE" ]; then
    echo "[]" > "$BUDGET_FILE"
fi
if [ ! -f "$COST_FILE" ]; then
    echo "[]" > "$COST_FILE"
fi

# 检查预算状态
echo "1. 检查预算状态..."
BUDGET_COUNT=$(cat "$BUDGET_FILE" 2>/dev/null | grep -c '"id":' || echo "0")
echo "   预算数量: $BUDGET_COUNT 个"

# 检查成本执行率
echo ""
echo "2. 检查成本执行率..."
# 简化计算，实际应解析JSON
TOTAL_BUDGET=10000
TOTAL_COST=$(cat "$COST_FILE" 2>/dev/null | grep -o '"amount": [0-9.]*' | awk '{sum+=$2} END {printf "%.2f", sum}')
TOTAL_COST=${TOTAL_COST:-0}

if (( $(echo "$TOTAL_BUDGET > 0" | bc -l 2>/dev/null || echo "0") )); then
    EXEC_RATE=$(echo "scale=2; $TOTAL_COST * 100 / $TOTAL_BUDGET" | bc 2>/dev/null || echo "0")
    echo "   总预算: $TOTAL_BUDGET"
    echo "   已支出: $TOTAL_COST"
    echo "   执行率: ${EXEC_RATE}%"
    
    # 红线判断
    if (( $(echo "$EXEC_RATE >= 100" | bc -l 2>/dev/null || echo "0") )); then
        echo "   🔴 已触发成本红线! 暂停非必要支出"
    elif (( $(echo "$EXEC_RATE >= 80" | bc -l 2>/dev/null || echo "0") )); then
        echo "   🟡 已触发成本黄线! 注意控制支出"
    elif (( $(echo "$EXEC_RATE >= 60" | bc -l 2>/dev/null || echo "0") )); then
        echo "   🔵 成本提醒: 已使用60%以上预算"
    else
        echo "   🟢 成本正常"
    fi
else
    echo "   暂无预算记录"
fi

# 生成检查记录
LOG_FILE="$LOG_DIR/cost-check-$(date +%Y%m%d-%H%M%S).log"
cat > "$LOG_FILE" << EOF
成本红线检查记录
check_time: $(date -Iseconds)
budget_count: $BUDGET_COUNT
total_budget: $TOTAL_BUDGET
total_cost: $TOTAL_COST
execution_rate: ${EXEC_RATE:-0}
status: completed
EOF

echo ""
echo "记录已保存: $LOG_FILE"
echo "=== 检查完成 ==="

# 如果触发红线，返回错误码
if (( $(echo "${EXEC_RATE:-0} >= 100" | bc -l 2>/dev/null || echo "0") )); then
    exit 1
fi

exit 0
