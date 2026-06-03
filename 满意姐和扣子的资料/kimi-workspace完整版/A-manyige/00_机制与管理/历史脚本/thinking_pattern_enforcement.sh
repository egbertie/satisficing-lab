#!/bin/bash
# 思维方式强制检查脚本
# 每次任务执行前必须运行，检查思维方式应用

WORKSPACE="/root/.openclaw/workspace"
CHECK_LOG="$WORKSPACE/diary/thinking_pattern_enforcement.log"
TASK_ID="${1:-unknown}"

echo "=== 思维方式强制检查 ===" | tee -a "$CHECK_LOG"
echo "任务ID: $TASK_ID" | tee -a "$CHECK_LOG"
echo "检查时间: $(date)" | tee -a "$CHECK_LOG"
echo "" | tee -a "$CHECK_LOG"

echo "检查清单（6项思维方式）:" | tee -a "$CHECK_LOG"
echo "1. 五层深挖: 表象→原因→根因→预防→能力" | tee -a "$CHECK_LOG"
echo "2. 反脆弱设计: 6类意外因素检查" | tee -a "$CHECK_LOG"
echo "3. 满意解思维: 四可原则（可运行/可验证/可持续/可培养）" | tee -a "$CHECK_LOG"
echo "4. 信号机制: 可验证证据（文件路径/数据）" | tee -a "$CHECK_LOG"
echo "5. 全局思维: 先规划结构，再执行" | tee -a "$CHECK_LOG"
echo "6. 时间不对称性: 现在×时间=未来" | tee -a "$CHECK_LOG"
echo "" | tee -a "$CHECK_LOG"
echo "要求: 至少应用3项" | tee -a "$CHECK_LOG"
echo "日志: $CHECK_LOG" | tee -a "$CHECK_LOG"
