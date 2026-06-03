#!/bin/bash
# 自动审计触发脚本
# 当检测到任务完成标记时，自动启动审计

WATCH_DIR="/root/.openclaw/workspace/diary/"
PATTERN="*_completed"
LOG_FILE="/root/.openclaw/workspace/diary/auto_audit.log"

echo "=== 自动审计触发器启动 ==="
echo "监控目录: $WATCH_DIR"
echo "监控模式: $PATTERN"
echo "启动时间: $(date)"
echo ""

log_msg() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_msg "自动审计触发器已启动"

# 检查是否有audit脚本
AUDIT_SCRIPT="/root/.openclaw/workspace/scripts/blue_army_auto_audit.sh"
if [ ! -x "$AUDIT_SCRIPT" ]; then
    log_msg "❌ 审计脚本不存在或不可执行: $AUDIT_SCRIPT"
    exit 1
fi

while true; do
    # 检测新完成的任务标记（5分钟内创建或修改的）
    for file in $(find "$WATCH_DIR" -name "$PATTERN" -mmin -5 2>/dev/null); do
        if [ -f "$file" ]; then
            TASK=$(basename "$file" _completed)
            log_msg "检测到任务完成: $TASK"
            
            # 自动启动审计
            log_msg "自动启动审计: $TASK"
            bash "$AUDIT_SCRIPT" "$TASK" 2>&1 | tee -a "$LOG_FILE"
            AUDIT_RESULT=${PIPESTATUS[0]}
            
            if [ $AUDIT_RESULT -eq 0 ]; then
                log_msg "✅ 审计完成: $TASK - PASS"
                echo "PASS" > "/tmp/${TASK}_audit_result"
            else
                log_msg "❌ 审计完成: $TASK - FAIL"
                echo "FAIL" > "/tmp/${TASK}_audit_result"
            fi
            
            # 自动通知满意妞
            NOTIFICATION="/tmp/blue_army_notification_${TASK}"
            echo "蓝军已自动完成审计: $TASK" > "$NOTIFICATION"
            echo "结果: $(cat /tmp/${TASK}_audit_result 2>/dev/null || echo 'UNKNOWN')" >> "$NOTIFICATION"
            echo "时间: $(date)" >> "$NOTIFICATION"
            
            log_msg "已生成通知: $NOTIFICATION"
            
            # 移动已完成标记，避免重复审计
            mv "$file" "${file}.audited"
        fi
    done
    
    sleep 60  # 每分钟检查一次
done
