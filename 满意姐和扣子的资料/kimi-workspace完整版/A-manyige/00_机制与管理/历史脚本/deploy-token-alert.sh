#!/bin/bash
# Token耗尽预警机制部署脚本
# 部署时间: 2026-03-15
# 优先级: P0-紧急

echo "🚨 部署Token耗尽预警机制..."

# 1. 创建预警检查脚本
cat > /root/.openclaw/workspace/scripts/token-alert.sh << 'EOF'
#!/bin/bash
# Token预警检查脚本
# 每小时检查一次Token余量

# 获取当前Token余量（从OpenClaw状态API）
TOKEN_STATUS=$(openclaw status --json 2>/dev/null | jq -r '.tokens.percent // 100')

echo "当前Token余量: ${TOKEN_STATUS}%"

# 三级预警阈值
CRITICAL=10   # 紧急: 10%
WARNING=20    # 警告: 20%
CAUTION=30    # 注意: 30%

if [ "$TOKEN_STATUS" -le "$CRITICAL" ]; then
    echo "🔴 CRITICAL: Token余量低于10%，系统即将停摆！"
    # 发送紧急通知（多渠道）
    openclaw notify --level critical --message "Token余量低于10%，请立即停止所有非紧急任务" --channels kimi,feishu
    # 自动禁用非必要Cron
    openclaw cron disable --pattern "info-collection" --pattern "learning" --pattern "deep-dive"
    exit 2
elif [ "$TOKEN_STATUS" -le "$WARNING" ]; then
    echo "🟠 WARNING: Token余量低于20%，建议优化任务"
    openclaw notify --level warning --message "Token余量低于20%，建议启动优化模式" --channels kimi
    exit 1
elif [ "$TOKEN_STATUS" -le "$CAUTION" ]; then
    echo "🟡 CAUTION: Token余量低于30%，请关注消耗"
    openclaw notify --level info --message "Token余量30%，当前消耗正常" --channels kimi
    exit 0
fi

echo "✅ Token余量健康: ${TOKEN_STATUS}%"
exit 0
EOF

chmod +x /root/.openclaw/workspace/scripts/token-alert.sh

# 2. 添加到Cron（每小时检查）
echo "添加Token预警Cron..."
(
    crontab -l 2>/dev/null
    echo "# Token耗尽预警机制 - P0紧急"
    echo "0 * * * * /root/.openclaw/workspace/scripts/token-alert.sh >> /root/.openclaw/workspace/logs/token-alert.log 2>&1"
) | crontab -

echo "✅ Token耗尽预警机制部署完成"
echo ""
echo "配置详情:"
echo "  - 检查频率: 每小时"
echo "  - 紧急阈值: 10% (自动禁用非必要Cron)"
echo "  - 警告阈值: 20% (建议优化)"
echo "  - 注意阈值: 30% (关注消耗)"
echo "  - 日志位置: /root/.openclaw/workspace/logs/token-alert.log"
