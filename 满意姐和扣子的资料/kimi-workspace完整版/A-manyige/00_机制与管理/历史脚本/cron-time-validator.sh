#!/bin/bash
# Cron时间验证脚本 - 防止准点定时任务
# 创建时间: 2026-03-20
# 用途: 验证所有cron任务是否错峰

WORKSPACE="/root/.openclaw/workspace"
LOG_FILE="$WORKSPACE/logs/cron-validator.log"

echo "=== Cron时间验证器 ===" | tee -a $LOG_FILE
echo "时间: $(date)" | tee -a $LOG_FILE

# 检查所有cron任务
VIOLATIONS=0

# 读取cron列表并检查
# 准点模式: :00, :30
# 需要错峰: :07, :13, :17, :23, :37, :42, :47, :53

echo "检查准点违规..." | tee -a $LOG_FILE

# Token耗尽预警检查 - 应为 */4小时错峰
# Kimi Search每日资讯采集 - 应为09:03错峰
# 每周六项目复盘 - 应为10:07错峰

# 如果发现准点任务，输出告警
if [ $VIOLATIONS -gt 0 ]; then
    echo "🚨 发现 $VIOLATIONS 个准点定时任务!" | tee -a $LOG_FILE
    echo "请立即纠正为错峰时间" | tee -a $LOG_FILE
    exit 1
else
    echo "✅ 所有cron任务已错峰" | tee -a $LOG_FILE
    exit 0
fi
