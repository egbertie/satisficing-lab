#!/bin/bash
# 今日重点文件夹同步与清理脚本
# 规则：保留最近 5 天内修改的文件，删除更早的副本（不删原件）

FOCUS_DIR="/root/.openclaw/workspace/A-manyige/01_🔥今日重点"

# 清理超过 5 天的文件
find "$FOCUS_DIR" -type f -mtime +5 -delete

# 日志
logger -t sri-today-focus "Cleaned files older than 5 days in $FOCUS_DIR"
