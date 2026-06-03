#!/bin/bash
echo "=== auto-git-commit.sh - 8步验证 ==="
SCRIPT="/root/.openclaw/workspace/scripts/auto-git-commit.sh"
test -f "$SCRIPT" && echo "Step1 ✅"
bash -n "$SCRIPT" 2>/dev/null && echo "Step2 ✅"
test -x "$SCRIPT" && echo "Step3 ✅"
echo "Step4-8: 待验证"
echo "状态: PENDING"
