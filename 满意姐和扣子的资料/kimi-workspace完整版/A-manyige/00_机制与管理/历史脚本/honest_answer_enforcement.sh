#!/bin/bash
# 诚实回答强制检查脚本
# 每次回答前运行，确保符合诚实回答标准

WORKSPACE="/root/.openclaw/workspace"
ANSWER_LOG="$WORKSPACE/diary/honest_answer_enforcement.log"
TASK_ID="${1:-unknown}"

echo "=== 诚实回答强制检查 ===" | tee -a "$ANSWER_LOG"
echo "任务ID: $TASK_ID" | tee -a "$ANSWER_LOG"
echo "检查时间: $(date)" | tee -a "$ANSWER_LOG"
echo "" | tee -a "$ANSWER_LOG"

echo "思维方式应用检查（6项）:" | tee -a "$ANSWER_LOG"
echo "[ ] 五层深挖: 表象→原因→根因→预防→能力" | tee -a "$ANSWER_LOG"
echo "[ ] 反脆弱设计: 6类意外因素检查" | tee -a "$ANSWER_LOG"
echo "[ ] 满意解思维: 四可原则评估" | tee -a "$ANSWER_LOG"
echo "[ ] 信号机制: 可验证证据" | tee -a "$ANSWER_LOG"
echo "[ ] 全局思维: 先规划后执行" | tee -a "$ANSWER_LOG"
echo "[ ] 时间不对称性: 现在×时间=未来" | tee -a "$ANSWER_LOG"
echo "" | tee -a "$ANSWER_LOG"

echo "内容完整性检查（4项）:" | tee -a "$ANSWER_LOG"
echo "[ ] 好消息: 进展报告" | tee -a "$ANSWER_LOG"
echo "[ ] 坏消息: 问题报告" | tee -a "$ANSWER_LOG"
echo "[ ] 思考过程: 分析展示" | tee -a "$ANSWER_LOG"
echo "[ ] 物理证据: 可验证文件" | tee -a "$ANSWER_LOG"
echo "" | tee -a "$ANSWER_LOG"

echo "要求: 至少应用3项思维方式 + 提供物理证据" | tee -a "$ANSWER_LOG"
echo "日志: $ANSWER_LOG" | tee -a "$ANSWER_LOG"
