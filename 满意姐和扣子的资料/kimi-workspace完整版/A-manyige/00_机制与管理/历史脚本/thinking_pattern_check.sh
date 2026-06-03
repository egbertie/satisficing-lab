#!/bin/bash
# 思维方式强制检查脚本
# 每次对话前强制检查是否应用了思维方式

WORKSPACE="/root/.openclaw/workspace"
LOG_FILE="$WORKSPACE/diary/thinking_pattern_check.log"

# 记录检查时间
echo "=== 思维方式检查 ===" >> "$LOG_FILE"
echo "检查时间: $(date)" >> "$LOG_FILE"

echo "思维方式强制检查提醒:"
echo "1. 本次对话是否应用了至少3项思维方式？"
echo "2. 是否展示思考过程（不是只给结果）？"
echo "3. 是否提供可验证的证据（文件路径/数据）？"
echo ""
echo "如果以上任何一项不满足，请停止并补充。"
