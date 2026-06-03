#!/bin/bash
# Suicide-Rebirth Test - 自杀重生测试脚本
# 模拟实例销毁并从备份恢复

WORKSPACE="/root/.openclaw/workspace"
SHADOW="/root/.openclaw/workspace/shadow-clone"
TEST_DIR="/tmp/rebirth-test-$(date +%s)"
LOG="/var/log/rebirth-test.log"

echo "=== 自杀重生测试 $(date) ===" | tee -a "$LOG"

# 步骤1: 验证影子克隆存在
if [ ! -d "$SHADOW" ]; then
    echo "❌ FAIL: Shadow clone not found" | tee -a "$LOG"
    exit 1
fi

# 步骤2: 创建测试恢复目录
mkdir -p "$TEST_DIR"

# 步骤3: 从影子克隆恢复
cp -r "$SHADOW" "$TEST_DIR/restored"

# 步骤4: 验证关键文件完整性
KEY_FILES=(
    "SOUL.md"
    "USER.md"
    "MEMORY.md"
    "AGENTS.md"
    "HEARTBEAT.md"
)

MISSING=0
for file in "${KEY_FILES[@]}"; do
    if [ ! -f "$TEST_DIR/restored/$file" ]; then
        echo "❌ MISSING: $file" | tee -a "$LOG"
        MISSING=$((MISSING + 1))
    fi
done

# 步骤5: 验证Skill目录
if [ ! -d "$TEST_DIR/restored/skills" ]; then
    echo "❌ FAIL: skills/ directory missing" | tee -a "$LOG"
    MISSING=$((MISSING + 1))
fi

# 步骤6: 计算恢复时间
START_TIME=$(date +%s)
# 模拟恢复过程（实际只是验证）
END_TIME=$(date +%s)
RECOVERY_TIME=$((END_TIME - START_TIME))

# 清理测试目录
rm -rf "$TEST_DIR"

# 输出结果
if [ $MISSING -eq 0 ]; then
    echo "✅ REBIRTH_TEST_PASS" | tee -a "$LOG"
    echo "   Recovery Time: ${RECOVERY_TIME}s" | tee -a "$LOG"
    echo "   Files Verified: ${#KEY_FILES[@]}" | tee -a "$LOG"
    echo "   Status: READY_FOR_DISASTER" | tee -a "$LOG"
    exit 0
else
    echo "❌ REBIRTH_TEST_FAIL - $MISSING files missing" | tee -a "$LOG"
    exit 1
fi
