#!/bin/bash
# SOP强制执行守卫

RULE_NAME="$1"
PLAN_FILE="$2"

echo "=== SOP强制执行检查 ==="
echo "规则: $RULE_NAME"

if [ -z "$RULE_NAME" ] || [ -z "$PLAN_FILE" ] || [ ! -f "$PLAN_FILE" ]; then
    echo "❌ 错误: 必须提供规则名称和.plan文件"
    exit 1
fi

echo "【检查】韧性检查清单..."
for item in 重启 超时 并发 权限 依赖 资源; do
    if ! grep -q "$item" "$PLAN_FILE"; then
        echo "  ❌ 缺少: $item"
        exit 1
    fi
    echo "  ✅ $item"
done

echo "【检查】5层思考..."
for step in "Step 1" "Step 2" "Step 3" "Step 4"; do
    if ! grep -q "$step" "$PLAN_FILE"; then
        echo "  ❌ 缺少: $step"
        exit 1
    fi
    echo "  ✅ $step"
done

echo "【检查】五维度..."
for dim in 时间维度 空间维度 深度维度 关联维度 演进维度; do
    if ! grep -q "$dim" "$PLAN_FILE"; then
        echo "  ❌ 缺少: $dim"
        exit 1
    fi
    echo "  ✅ $dim"
done

echo "【检查】蓝军预审计..."
if ! grep -q "蓝军预审计通过" "$PLAN_FILE"; then
    echo "  ❌ 缺少蓝军预审计"
    exit 1
fi
echo "  ✅ 蓝军预审计通过"

echo ""
echo "✅ 所有检查通过！"
exit 0
