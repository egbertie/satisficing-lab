#!/bin/bash
# 蓝军不作为监控脚本
# 满意妞用于监控蓝军审计是否及时的机制

WORKSPACE="/root/.openclaw/workspace"
BLUE_ARMY_AUDIT_DIR="$WORKSPACE/diary/blue-audit"
REPORT_FILE="$WORKSPACE/diary/blue-army-inactivity-alerts.md"

# 检查蓝军最近审计时间
LAST_AUDIT=$(ls -t "$BLUE_ARMY_AUDIT_DIR"/*.md 2>/dev/null | head -1)
LAST_AUDIT_TIME=$(stat -c %Y "$LAST_AUDIT" 2>/dev/null || echo "0")
NOW=$(date +%s)
HOURS_SINCE=$(( (NOW - LAST_AUDIT_TIME) / 3600 ))

# 如果超过2小时无审计，记录不作为
echo "=== 蓝军监控检查 ===" >> "$REPORT_FILE"
echo "检查时间: $(date)" >> "$REPORT_FILE"
echo "上次审计: $LAST_AUDIT" >> "$REPORT_FILE"
echo "距上次审计: ${HOURS_SINCE}小时" >> "$REPORT_FILE"

if [ "$HOURS_SINCE" -gt 2 ]; then
    echo "⚠️ 蓝军可能不作为 - 超过2小时无审计" >> "$REPORT_FILE"
    echo "建议: 满意妞向用户报告" >> "$REPORT_FILE"
    
    # 输出警告给满意妞
    echo "警告: 蓝军超过2小时未审计，准备向用户报告"
    exit 1
else
    echo "✅ 蓝军正常 - ${HOURS_SINCE}小时内有审计" >> "$REPORT_FILE"
    exit 0
fi
