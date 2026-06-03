#!/bin/bash
echo "=== blue_army_monitor.sh - 8步验证 ==="
SCRIPT="/root/.openclaw/workspace/scripts/blue_army_monitor.sh"
test -f "$SCRIPT" && echo "Step1 ✅"
bash -n "$SCRIPT" 2>/dev/null && echo "Step2 ✅"
test -x "$SCRIPT" && echo "Step3 ✅"
echo "Step4-8: 待验证"
echo "状态: PENDING"
