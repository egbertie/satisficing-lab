#!/bin/bash
echo "=== daily-backup.sh - 8步验证 ==="
SCRIPT="/root/.openclaw/workspace/scripts/daily-backup.sh"
test -f "$SCRIPT" && echo "Step1 ✅"
bash -n "$SCRIPT" 2>/dev/null && echo "Step2 ✅"
test -x "$SCRIPT" && echo "Step3 ✅"
echo "Step4-8: 待验证"
echo "状态: PENDING"
