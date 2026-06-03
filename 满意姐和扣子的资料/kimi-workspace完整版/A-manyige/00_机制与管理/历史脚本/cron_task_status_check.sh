#!/bin/bash
# 第三项全量任务：Cron任务实际运行状态验证
# 验证所有配置的Cron任务是否真正运行

WORKSPACE="/root/.openclaw/workspace"
REPORT_DIR="$WORKSPACE/reports"
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
REPORT_FILE="$REPORT_DIR/cron_task_status_report_${TIMESTAMP}.md"

echo "=== 第三项全量任务：Cron任务运行状态验证 ==="
echo "时间: $(date)"
echo ""

mkdir -p "$REPORT_DIR"

# 获取当前cron配置
crontab -l > /tmp/current_cron.txt 2>/dev/null || echo "NO_CRON" > /tmp/current_cron.txt

cat > "$REPORT_FILE" << EOF
# Cron任务运行状态验证报告

**验证时间**: $(date)
**验证方法**: 检查crontab配置 + 日志文件存在性

---

## 当前Cron配置

\`\`\`
$(cat /tmp/current_cron.txt)
\`\`\`

---

## 配置任务列表

| 任务 | 调度 | 脚本路径 | 日志路径 | 状态 |
|------|------|----------|----------|------|

EOF

# 解析cron条目
grep -v "^#" /tmp/current_cron.txt | grep -v "^$" | while read line; do
    schedule=$(echo "$line" | awk '{print $1, $2, $3, $4, $5}')
    script=$(echo "$line" | awk '{print $6}')
    log=$(echo "$line" | grep -o ">>.*" | awk '{print $1}' | sed 's/>>//' 2>/dev/null)
    
    # 检查脚本是否存在
    if [ -f "$script" ]; then
        script_status="✅"
    else
        script_status="❌"
    fi
    
    # 检查日志是否存在
    if [ -n "$log" ] && [ -f "$log" ]; then
        log_status="✅"
        # 检查日志最近更新时间
        last_update=$(stat -c %Y "$log" 2>/dev/null)
        now=$(date +%s)
        diff=$(( (now - last_update) / 3600 ))
        if [ $diff -lt 24 ]; then
            status="🟢 活跃（${diff}小时前）"
        elif [ $diff -lt 72 ]; then
            status="🟡 滞后（${diff}小时前）"
        else
            status="🔴 停滞（${diff}小时前）"
        fi
    else
        log_status="❌"
        status="⚠️ 无日志"
    fi
    
    task_name=$(basename "$script" 2>/dev/null | sed 's/\.sh$//' | sed 's/\.py$//')
    echo "| $task_name | $schedule | $script_status | $log_status | $status |" >> "$REPORT_FILE"
done

cat >> "$REPORT_FILE" << EOF

---

## 建议

1. **无日志任务**: 检查脚本是否正确配置日志输出
2. **停滞任务**: 检查脚本是否有错误，查看日志内容
3. **活跃任务**: 保持监控

---

*报告生成: $(date)*
EOF

echo "=== 第三项任务完成 ==="
echo "报告位置: $REPORT_FILE"
