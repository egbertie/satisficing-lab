#!/bin/bash
# 思维方式强制检查脚本
# 每次对话前强制检查是否应用了思维方式

WORKSPACE="/root/.openclaw/workspace"
LOG_FILE="$WORKSPACE/diary/thinking_pattern_check.log"

# 记录检查时间
echo "=== 思维方式检查 ===" >> "$LOG_FILE"
echo "检查时间: $(date)" >> "$LOG_FILE"

# 检查1: 是否应用了至少3项思维方式
echo "检查1: 思维方式应用" >> "$LOG_FILE"
echo "要求: 本次对话必须应用至少3项思维方式" >> "$LOG_FILE"
echo "状态: 需人工确认" >> "$LOG_FILE"

# 检查2: 是否展示思考过程
echo "检查2: 思考过程展示" >> "$LOG_FILE"
echo "要求: 必须展示思考过程（5 Why/分析/推理）" >> "$LOG_FILE"
echo "状态: 需人工确认" >> "$LOG_FILE"

# 检查3: 是否提供可验证证据
echo "检查3: 可验证证据" >> "$LOG_FILE"
echo "要求: 提供文件路径、具体数据、检查命令" >> "$LOG_FILE"
echo "状态: 需人工确认" >> "$LOG_FILE"

# 输出提示
echo "思维方式强制检查提醒:"
echo "1. 本次对话是否应用了至少3项思维方式？"
echo "2. 是否展示思考过程（不是只给结果）？"
echo "3. 是否提供可验证的证据（文件路径/数据）？"
echo ""
echo "如果以上任何一项不满足，请停止并补充。"
echo ""
echo "日志位置: $LOG_FILE"

# 不强制exit 1，因为这是提醒机制不是拦截机制
# 真正的强制由蓝军审计完成
exit 0
