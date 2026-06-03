#!/bin/bash
# 晨报 - 每日08:47
# 使用新的TODO集成晨报生成器

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 开始生成晨报..." >> /tmp/morning_report.log

# 执行Python晨报生成器
/usr/bin/python3 /root/.openclaw/workspace/skills/todo-management/morning_report.py >> /tmp/morning_report.log 2>&1

# 同时发送到用户消息（通过OpenClaw消息系统）
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 晨报生成完成" >> /tmp/morning_report.log
