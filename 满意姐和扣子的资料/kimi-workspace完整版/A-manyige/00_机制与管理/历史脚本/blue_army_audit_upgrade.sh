#!/bin/bash
# 蓝军审计升级机制脚本
# 实现"抽查→扩大→全量"的强制升级

WORKSPACE="/root/.openclaw/workspace"
AUDIT_UPGRADE_LOG="$WORKSPACE/diary/blue-army-audit-upgrade.log"

echo "=== 蓝军审计升级机制 ===" | tee -a "$AUDIT_UPGRADE_LOG"
echo "执行时间: $(date)" | tee -a "$AUDIT_UPGRADE_LOG"
echo "" | tee -a "$AUDIT_UPGRADE_LOG"

# 参数检查
if [ $# -lt 2 ]; then
    echo "用法: $0 <总数> <已抽查数> <发现问题数>" | tee -a "$AUDIT_UPGRADE_LOG"
    echo "示例: $0 94 10 3" | tee -a "$AUDIT_UPGRADE_LOG"
    exit 1
fi

TOTAL=$1
SAMPLED=$2
ISSUES=${3:-0}

echo "总数: $TOTAL" | tee -a "$AUDIT_UPGRADE_LOG"
echo "已抽查: $SAMPLED" | tee -a "$AUDIT_UPGRADE_LOG"
echo "发现问题: $ISSUES" | tee -a "$AUDIT_UPGRADE_LOG"
echo "" | tee -a "$AUDIT_UPGRADE_LOG"

# 计算问题率
if [ $SAMPLED -gt 0 ]; then
    ISSUE_RATE=$(( ISSUES * 100 / SAMPLED ))
else
    ISSUE_RATE=0
fi

echo "问题率: ${ISSUE_RATE}%" | tee -a "$AUDIT_UPGRADE_LOG"

# 升级决策
if [ $ISSUES -gt 0 ]; then
    echo "" | tee -a "$AUDIT_UPGRADE_LOG"
    echo "⚠️  发现问题，必须升级抽查范围！" | tee -a "$AUDIT_UPGRADE_LOG"
    
    if [ $SAMPLED -lt $(( TOTAL * 10 / 100 )) ]; then
        # 第一阶段：抽查不足10%，扩大到10%
        TARGET=$(( TOTAL * 10 / 100 ))
        echo "→ 当前抽查不足10%，要求扩大到: $TARGET 个" | tee -a "$AUDIT_UPGRADE_LOG"
        
    elif [ $SAMPLED -lt $(( TOTAL * 50 / 100 )) ]; then
        # 第二阶段：抽查不足50%，扩大到50%
        TARGET=$(( TOTAL * 50 / 100 ))
        echo "→ 问题率${ISSUE_RATE}%，要求扩大到: $TARGET 个" | tee -a "$AUDIT_UPGRADE_LOG"
        
    elif [ $ISSUE_RATE -gt 20 ]; then
        # 第三阶段：问题率>20%，全量验证
        echo "→ 问题率${ISSUE_RATE}% > 20%，要求全量验证: $TOTAL 个" | tee -a "$AUDIT_UPGRADE_LOG"
        TARGET=$TOTAL
    else
        echo "→ 问题率${ISSUE_RATE}% <= 20%，当前抽查范围可接受" | tee -a "$AUDIT_UPGRADE_LOG"
        TARGET=$SAMPLED
    fi
    
    echo "" | tee -a "$AUDIT_UPGRADE_LOG"
    echo "蓝军必须执行: 从 $SAMPLED 扩大到 $TARGET" | tee -a "$AUDIT_UPGRADE_LOG"
    echo "如不执行，向用户申请介入" | tee -a "$AUDIT_UPGRADE_LOG"
    
else
    echo "" | tee -a "$AUDIT_UPGRADE_LOG"
    echo "✅ 未发现新问题，当前抽查范围可接受" | tee -a "$AUDIT_UPGRADE_LOG"
fi

echo "" | tee -a "$AUDIT_UPGRADE_LOG"
echo "升级日志: $AUDIT_UPGRADE_LOG" | tee -a "$AUDIT_UPGRADE_LOG"
