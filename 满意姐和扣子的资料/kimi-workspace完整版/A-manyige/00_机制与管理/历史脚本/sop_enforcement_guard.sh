#!/bin/bash
# SOP强制执行守卫脚本
# 任何新规则创建前，必须通过此脚本检查
# 不通过则阻止创建

set -e

RULE_NAME="$1"
PLAN_FILE="$2"

echo "=== SOP强制执行检查 ==="
echo "规则名称: $RULE_NAME"
echo "检查时间: $(date)"
echo ""

if [ -z "$RULE_NAME" ]; then
    echo "❌ 错误: 必须提供规则名称"
    echo "用法: $0 <规则名称> <.plan文件路径>"
    exit 1
fi

if [ -z "$PLAN_FILE" ] || [ ! -f "$PLAN_FILE" ]; then
    echo "❌ 错误: 必须提供.plan文件，且文件必须存在"
    echo ".plan文件必须包含完整的SOP思考过程"
    exit 1
fi

echo "【检查1】.plan文件存在 ✅"
echo ""

# 检查韧性检查清单（6类意外因素）
echo "【检查2】韧性检查清单..."
REQUIRED_RESILIENCE=("重启" "超时" "并发" "权限" "依赖" "资源")
MISSING_RESILIENCE=()

for item in "${REQUIRED_RESILIENCE[@]}"; do
    if grep -q "$item" "$PLAN_FILE"; then
        echo "  ✅ $item - 已考虑"
    else
        echo "  ❌ $item - 未考虑"
        MISSING_RESILIENCE+=("$item")
    fi
done

if [ ${#MISSING_RESILIENCE[@]} -gt 0 ]; then
    echo ""
    echo "❌ 韧性检查未通过，缺少: ${MISSING_RESILIENCE[*]}"
    exit 1
fi

echo ""
echo "【检查3】5层思考过程（Step 1-4）..."
REQUIRED_STEPS=("Step 1" "Step 2" "Step 3" "Step 4")
MISSING_STEPS=()

for step in "${REQUIRED_STEPS[@]}"; do
    if grep -q "$step" "$PLAN_FILE"; then
        echo "  ✅ $step - 已包含"
    else
        echo "  ❌ $step - 未包含"
        MISSING_STEPS+=("$step")
    fi
done

if [ ${#MISSING_STEPS[@]} -gt 0 ]; then
    echo ""
    echo "❌ 5层思考未通过，缺少: ${MISSING_STEPS[*]}"
    exit 1
fi

echo ""
echo "【检查4】五维度检查..."
REQUIRED_DIMENSIONS=("时间维度" "空间维度" "深度维度" "关联维度" "演进维度")
MISSING_DIMENSIONS=()

for dim in "${REQUIRED_DIMENSIONS[@]}"; do
    if grep -q "$dim" "$PLAN_FILE"; then
        echo "  ✅ $dim - 已评估"
    else
        echo "  ❌ $dim - 未评估"
        MISSING_DIMENSIONS+=("$dim")
    fi
done

if [ ${#MISSING_DIMENSIONS[@]} -gt 0 ]; then
    echo ""
    echo "❌ 五维度检查未通过，缺少: ${MISSING_DIMENSIONS[*]}"
    exit 1
fi

echo ""
echo "【检查5】蓝军预审计标记..."
if grep -q "蓝军预审计通过" "$PLAN_FILE"; then
    echo "  ✅ 蓝军预审计通过"
else
    echo "  ❌ 缺少蓝军预审计标记"
    echo "  必须先通过蓝军预审计才能创建"
    exit 1
fi

echo ""
echo "========================================"
echo "✅ 所有SOP检查通过！"
echo "可以创建规则: $RULE_NAME"
echo "========================================"
exit 0
