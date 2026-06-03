#!/bin/bash
# 定期回归测试机制
# 每小时运行一次，验证所有9个核心skill

SKILLS=(
    "strict-write-manager"
    "token-budget-guard"
    "knowledge-curator"
    "ethics-checker"
    "neuroscience-baseline"
    "case-analyzer"
    "effectiveness-validator"
    "extension-evaluator"
    "memory-indexer"
)

PASS=0
FAIL=0

LOG_FILE="/root/.openclaw/workspace/logs/regression-test-$(date +%Y%m%d-%H%M).log"
mkdir -p /root/.openclaw/workspace/logs

echo "===============================================" | tee -a $LOG_FILE
echo "回归测试 - $(date)" | tee -a $LOG_FILE
echo "===============================================" | tee -a $LOG_FILE

for skill in "${SKILLS[@]}"; do
    echo "" | tee -a $LOG_FILE
    echo "Testing: $skill" | tee -a $LOG_FILE
    cd "/root/.openclaw/workspace/skills/$skill" 2>/dev/null || continue
    
    if [ -f "test_runner.py" ]; then
        if python3 test_runner.py --test 2>&1 | grep -q "100.0%"; then
            echo "  ✅ PASS" | tee -a $LOG_FILE
            ((PASS++))
        else
            echo "  ❌ FAIL" | tee -a $LOG_FILE
            ((FAIL++))
        fi
    elif [ -f "*.py" ]; then
        # Try main file with --test
        main_file=$(ls *.py | grep -v test | head -1)
        if python3 $main_file --test 2>&1 | grep -q "100.0%"; then
            echo "  ✅ PASS" | tee -a $LOG_FILE
            ((PASS++))
        else
            echo "  ❌ FAIL" | tee -a $LOG_FILE
            ((FAIL++))
        fi
    fi
done

echo "" | tee -a $LOG_FILE
echo "===============================================" | tee -a $LOG_FILE
echo "结果: $PASS PASS / $FAIL FAIL" | tee -a $LOG_FILE
echo "===============================================" | tee -a $LOG_FILE

# 如果有失败，发送通知
if [ $FAIL -gt 0 ]; then
    echo "⚠️  $FAIL 个skill测试失败，需要关注！" | tee -a $LOG_FILE
fi

exit $FAIL
