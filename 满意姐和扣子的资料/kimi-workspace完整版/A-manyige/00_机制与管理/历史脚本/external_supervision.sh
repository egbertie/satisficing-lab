#!/bin/bash
# 外部监督脚本
# 他律约束，不是自律
# 自动记录问题，自动扣分，自动通知

CHECK_TYPE="$1"     # supervision/check/punish
TARGET="${2:-满意妞}"
LOG_FILE="/root/.openclaw/workspace/diary/external_supervision.log"
SCORE_FILE="/root/.openclaw/workspace/diary/trust_score.log"

echo "=== 外部监督机制 ==="
echo "检查类型: $CHECK_TYPE"
echo "目标: $TARGET"
echo "时间: $(date)"
echo ""

log_msg() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# 初始化信任积分（如果不存在）
init_score() {
    if [ ! -f "$SCORE_FILE" ]; then
        echo "initial: 50" > "$SCORE_FILE"
        log_msg "初始化信任积分: 50"
    fi
}

# 扣分机制
punish() {
    local reason="$1"
    local points="${2:-5}"
    
    init_score
    
    # 读取当前分数
    CURRENT=$(grep "^current:" "$SCORE_FILE" | awk '{print $2}' || echo "50")
    NEW=$((CURRENT - points))
    
    # 记录扣分
    echo "$(date +%s) | $(date) | 扣分 | -$points | 原因: $reason | 当前: $NEW" >> "$SCORE_FILE"
    echo "current: $NEW" >> "$SCORE_FILE"
    
    log_msg "⚠️  $TARGET 被扣分: -$points (原因: $reason)，当前积分: $NEW"
    
    # 如果积分过低，发出警告
    if [ $NEW -lt 30 ]; then
        log_msg "❌ 警告: $TARGET 信任积分过低 ($NEW)，需要立即整改"
    fi
}

# 检查机制
check() {
    log_msg "开始检查 $TARGET..."
    
    ISSUES=0
    
    # 检查1: 是否有知行不一记录
    if [ -f "/root/.openclaw/workspace/diary/knowing_doing_gap.log" ]; then
        RECENT=$(tail -5 /root/.openclaw/workspace/diary/knowing_doing_gap.log 2>/dev/null | wc -l)
        if [ $RECENT -gt 0 ]; then
            log_msg "发现 $RECENT 条知行不一记录"
            ISSUES=$((ISSUES + RECENT))
        fi
    fi
    
    # 检查2: 是否有未完成的任务
    PENDING=$(find /root/.openclaw/workspace/diary/ -name "*_pending" 2>/dev/null | wc -l)
    if [ $PENDING -gt 0 ]; then
        log_msg "发现 $PENDING 个待完成任务"
        ISSUES=$((ISSUES + PENDING))
    fi
    
    # 检查3: 是否有逾期的任务
    OVERDUE=$(find /root/.openclaw/workspace/diary/ -name "*_overdue" 2>/dev/null | wc -l)
    if [ $OVERDUE -gt 0 ]; then
        log_msg "发现 $OVERDUE 个逾期任务"
        ISSUES=$((ISSUES + OVERDUE * 2))
    fi
    
    if [ $ISSUES -eq 0 ]; then
        log_msg "✅ $TARGET 检查通过，无问题"
    else
        log_msg "❌ $TARGET 发现 $ISSUES 个问题"
        punish "检查发现 $ISSUES 个问题" $((ISSUES * 5))
    fi
}

# 监督模式（定期运行）
supervise() {
    log_msg "启动持续监督模式"
    
    while true; do
        check
        
        # 每30分钟检查一次
        log_msg "下次检查: 30分钟后"
        sleep 1800
    done
}

# 主逻辑
case "$CHECK_TYPE" in
    check)
        check
        ;;
    supervise)
        supervise
        ;;
    punish)
        punish "${3:-未指定原因}" "${4:-5}"
        ;;
    *)
        echo "用法: $0 {check|supervise|punish} [目标] [原因] [扣分]"
        echo "  check     - 单次检查"
        echo "  supervise - 持续监督（每30分钟检查一次）"
        echo "  punish    - 扣分"
        exit 1
        ;;
esac
