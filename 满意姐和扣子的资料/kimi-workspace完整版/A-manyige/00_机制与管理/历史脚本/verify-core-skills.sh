#!/bin/bash
# 6个核心治理Skill验收脚本

echo "=========================================="
echo "核心治理Skill 5标准验收"
echo "=========================================="
echo ""

SKILLS=(
    "role-federation"
    "worry-list-manager"
    "honesty-tagging-protocol"
    "token-budget-enforcer"
    "quality-gate-system"
    "management-rules"
)

PASS_COUNT=0
FAIL_COUNT=0

for skill in "${SKILLS[@]}"; do
    echo "--- 检验: $skill ---"
    RESULT=$(python3 /root/.openclaw/workspace/skills/five-standard-auditor/scripts/auditor.py audit "/root/.openclaw/workspace/skills/$skill/SKILL.md" 2>&1)
    
    SCORE=$(echo "$RESULT" | grep "综合得分" | grep -oP '\d+\.?\d*%')
    PASSED=$(echo "$RESULT" | grep -c "^✅.*SKILL.md")
    
    if [ "$PASSED" -eq 1 ]; then
        echo "✅ 通过 - $SCORE"
        ((PASS_COUNT++))
    else
        echo "❌ 未通过 - $SCORE"
        echo "$RESULT" | grep -E "(❌ S|综合得分)"
        ((FAIL_COUNT++))
    fi
    echo ""
done

echo "=========================================="
echo "验收结果: $PASS_COUNT/6 通过"
echo "=========================================="

if [ "$PASS_COUNT" -eq 6 ]; then
    echo "🎉 全部达标！系统已就绪。"
    exit 0
else
    echo "⚠️  $FAIL_COUNT 个Skill需要继续修复"
    exit 1
fi
