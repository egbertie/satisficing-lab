#!/bin/bash
# 外部监督Cron任务8步验证
# 任务: @reboot外部监督

echo "=== 外部监督Cron任务 (@reboot) - 8步验证 ==="
echo ""

SCRIPT_PATH="/root/.openclaw/workspace/scripts/external_supervision.sh"

STEP1=false; STEP2=false; STEP3=false; STEP4=false

# Step 1
echo "Step 1: 配置写入验证"
if crontab -l | grep -q "@reboot.*external_supervision"; then
    echo "  ✅ 已写入crontab (@reboot)"
    STEP1=true
fi

# Step 2
echo "Step 2: 语法检查"
if bash -n "$SCRIPT_PATH" 2>/dev/null; then
    echo "  ✅ Shell语法正确"
    STEP2=true
fi

# Step 3
echo "Step 3: 权限验证"
if test -x "$SCRIPT_PATH"; then
    echo "  ✅ 可执行"
    STEP3=true
fi

# Step 4
echo "Step 4: 依赖检查"
echo "  ⚠️  需重启后验证supervise功能"
STEP4=true

echo "Step 5-8: 需重启后验证/记录"

echo ""
echo "状态: PENDING (需下次重启后完全验证)"
echo "验证时间: $(date -Iseconds)"
