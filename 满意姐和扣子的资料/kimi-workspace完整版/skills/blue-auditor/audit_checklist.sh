#!/bin/bash
# 蓝军审计checklist脚本
# 使用方法: ./audit_checklist.sh <skill_name>

SKILL_NAME=$1
SKILL_DIR="/root/.openclaw/workspace/skills/$SKILL_NAME"
AUDIT_LOG="/root/.openclaw/workspace/skills/blue-auditor/audit_logs/${SKILL_NAME}_$(date +%Y%m%d_%H%M%S).log"

mkdir -p "$(dirname $AUDIT_LOG)"

echo "=== 蓝军审计: $SKILL_NAME ===" | tee -a $AUDIT_LOG
echo "审计时间: $(date)" | tee -a $AUDIT_LOG
echo "" | tee -a $AUDIT_LOG

PASS_COUNT=0
FAIL_COUNT=0

# Check 1: 目录存在
echo "[Check 1] 目录存在..." | tee -a $AUDIT_LOG
if [ -d "$SKILL_DIR" ]; then
    echo "  ✅ PASS: 目录存在" | tee -a $AUDIT_LOG
    ((PASS_COUNT++))
else
    echo "  ❌ FAIL: 目录不存在" | tee -a $AUDIT_LOG
    ((FAIL_COUNT++))
fi

# Check 2: SKILL.md存在
echo "[Check 2] SKILL.md存在..." | tee -a $AUDIT_LOG
if [ -f "$SKILL_DIR/SKILL.md" ]; then
    echo "  ✅ PASS: SKILL.md存在" | tee -a $AUDIT_LOG
    ((PASS_COUNT++))
else
    echo "  ⚠️  WARN: SKILL.md不存在" | tee -a $AUDIT_LOG
fi

# Check 3: 代码文件存在
echo "[Check 3] 代码文件存在..." | tee -a $AUDIT_LOG
CODE_COUNT=$(find "$SKILL_DIR" -name "*.py" -not -name "test*.py" -not -name "*_test.py" 2>/dev/null | wc -l)
if [ "$CODE_COUNT" -gt 0 ]; then
    echo "  ✅ PASS: $CODE_COUNT个代码文件" | tee -a $AUDIT_LOG
    ((PASS_COUNT++))
else
    echo "  ❌ FAIL: 无代码文件" | tee -a $AUDIT_LOG
    ((FAIL_COUNT++))
fi

# Check 4: 测试文件存在
echo "[Check 4] 测试文件存在..." | tee -a $AUDIT_LOG
TEST_COUNT=$(find "$SKILL_DIR" -name "test*.py" -o -name "*_test.py" 2>/dev/null | wc -l)
if [ "$TEST_COUNT" -gt 0 ]; then
    echo "  ✅ PASS: $TEST_COUNT个测试文件" | tee -a $AUDIT_LOG
    ((PASS_COUNT++))
else
    echo "  ❌ FAIL: 无测试文件" | tee -a $AUDIT_LOG
    ((FAIL_COUNT++))
fi

# Check 5: 测试实际运行通过
echo "[Check 5] 测试实际运行..." | tee -a $AUDIT_LOG
TEST_FILE=$(find "$SKILL_DIR" -name "test*.py" | head -1)
if [ -n "$TEST_FILE" ]; then
    cd "$SKILL_DIR"
    TEST_RESULT=$(python3 "$TEST_FILE" 2>&1)
    if echo "$TEST_RESULT" | grep -q "OK"; then
        echo "  ✅ PASS: 测试运行通过" | tee -a $AUDIT_LOG
        ((PASS_COUNT++))
    else
        echo "  ❌ FAIL: 测试运行失败" | tee -a $AUDIT_LOG
        echo "  错误: $TEST_RESULT" | tee -a $AUDIT_LOG
        ((FAIL_COUNT++))
    fi
else
    echo "  ❌ FAIL: 无测试可运行" | tee -a $AUDIT_LOG
    ((FAIL_COUNT++))
fi

# 汇总
echo "" | tee -a $AUDIT_LOG
echo "=== 审计汇总 ===" | tee -a $AUDIT_LOG
echo "通过: $PASS_COUNT" | tee -a $AUDIT_LOG
echo "失败: $FAIL_COUNT" | tee -a $AUDIT_LOG

if [ "$FAIL_COUNT" -eq 0 ]; then
    echo "" | tee -a $AUDIT_LOG
    echo "🟢 最终结果: PASS" | tee -a $AUDIT_LOG
    exit 0
else
    echo "" | tee -a $AUDIT_LOG
    echo "🔴 最终结果: FAIL" | tee -a $AUDIT_LOG
    exit 1
fi
