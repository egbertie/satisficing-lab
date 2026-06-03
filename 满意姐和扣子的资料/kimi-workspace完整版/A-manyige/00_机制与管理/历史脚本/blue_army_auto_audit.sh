#!/bin/bash
# 蓝军审计自动化Cron脚本
# 每小时自动审计所有Skill

cd /root/.openclaw/workspace

echo "═══════════════════════════════════════════════════════════"
echo "              蓝军自动审计 - $(date '+%Y-%m-%d %H:%M:%S')"
echo "═══════════════════════════════════════════════════════════"
echo ""

# 需要审计的Skill列表
SKILLS=(
    "checkpoint-manager"
    "blackboard-manager"
    "worker-orchestrator"
    "blue-army-auditor"
    "secret-manager"
    "disaster-recovery-auditor"
)

PASS_COUNT=0
FAIL_COUNT=0

for skill in "${SKILLS[@]}"; do
    echo "🔍 审计: $skill"
    
    if python3 skills/blue-army-auditor/blue_army_auditor.py "$skill" --save > /dev/null 2>&1; then
        echo "   ✅ PASS"
        ((PASS_COUNT++))
    else
        echo "   ❌ FAIL"
        ((FAIL_COUNT++))
    fi
done

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "审计汇总: $PASS_COUNT PASS, $FAIL_COUNT FAIL"
echo "═══════════════════════════════════════════════════════════"

# 记录到日志
LOG_FILE="diary/blue-army/auto-audit-$(date +%Y%m%d-%H).log"
mkdir -p diary/blue-army
echo "$(date '+%Y-%m-%d %H:%M:%S') | $PASS_COUNT PASS | $FAIL_COUNT FAIL" >> "$LOG_FILE"

exit 0
