#!/bin/bash
# 满意妞自我检查脚本
# 执行前强制检查

set -e

echo "=== 满意妞执行前强制检查 ==="
echo "时间: $(date)"
echo ""

PASS=0
FAIL=0

# 检查1: 用户明确说过"不要等决策，直接做"吗？
echo "【检查1】用户授权检查"
echo "用户明确说过'不要等决策，直接做'吗？"
echo "  如果是新任务/重大变更，需要确认"
echo "  如果是自己的遗漏/错误，直接执行"
echo "  ✅ 请确认后继续"
echo ""

# 检查2: 结果/效果/成本负责
echo "【检查2】三重责任检查"

echo "  结果责任 - 能验证实际效果吗？"
if [ -z "$VERIFICATION_COMMAND" ]; then
    echo "    ❌ 未提供验证命令"
    FAIL=$((FAIL + 1))
else
    echo "    ✅ 已提供验证命令"
    PASS=$((PASS + 1))
fi

echo "  效果责任 - 能长期运行吗？"
if [ -z "$SUSTAINABILITY_PLAN" ]; then
    echo "    ⚠️  未评估可持续性"
else
    echo "    ✅ 已评估可持续性"
    PASS=$((PASS + 1))
fi

echo "  成本责任 - Token/时间最小化了吗？"
echo "    请自我评估: 这是最小成本方案吗？"
echo ""

# 检查3: 思考过程展示
echo "【检查3】思考过程检查"

echo "  Step 1-4 完整吗？"
for step in "Step 1" "Step 2" "Step 3" "Step 4"; do
    echo "    $step: 请确认已包含"
done
echo ""

echo "  韧性检查做了吗？（6项）"
for item in "重启" "超时" "并发" "权限" "依赖" "资源"; do
    echo "    $item: 请确认已评估"
done
echo ""

echo "  四可评估做了吗？"
for item in "可运行" "可验证" "可持续" "可培养"; do
    echo "    $item: 请确认已评估"
done
echo ""

# 检查4: 虚报检测
echo "【检查4】虚报自检"
echo "  声称完成的内容，实际都完成了吗？"
echo "  声称部署的内容，实际都部署了吗？"
echo "  声称验证的内容，实际都验证了吗？"
echo "  如果任何一项是'否'，立即停止并报告"
echo ""

# 总结
echo "========================================"
echo "检查完成: $PASS通过, $FAIL失败"
echo "========================================"
echo ""

if [ $FAIL -gt 0 ]; then
    echo "❌ 有检查项未通过，请补全后再执行"
    exit 1
else
    echo "✅ 基础检查通过，请确保诚实回答每个检查项"
    echo ""
    echo "最终确认: 您确认已为结果/效果/成本负责了吗？"
    exit 0
fi
