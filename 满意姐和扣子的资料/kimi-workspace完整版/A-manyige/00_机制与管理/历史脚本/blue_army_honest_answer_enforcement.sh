#!/bin/bash
# 蓝军诚实回答强制检查脚本
# 每次审计报告前必须运行

WORKSPACE="/root/.openclaw/workspace"
LOG_FILE="$WORKSPACE/diary/blue_army_honest_answer.log"
AUDIT_ID="${1:-unknown}"

echo "=== 蓝军诚实回答强制检查 ===" | tee -a "$LOG_FILE"
echo "审计ID: $AUDIT_ID" | tee -a "$LOG_FILE"
echo "检查时间: $(date)" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

echo "【第一部分】思维方式应用（6项全部必须）" | tee -a "$LOG_FILE"
echo "[ ] 五层深挖（审计版）: 表象→原因→根因→预防→能力" | tee -a "$LOG_FILE"
echo "[ ] 反脆弱设计（审计版）: 6类审计方法抗干扰检查" | tee -a "$LOG_FILE"
echo "[ ] 满意解思维（审计版）: 四可原则" | tee -a "$LOG_FILE"
echo "[ ] 信号机制（审计版）: 可独立验证的证据" | tee -a "$LOG_FILE"
echo "[ ] 全局思维（审计版）: 先规划后执行" | tee -a "$LOG_FILE"
echo "[ ] 时间不对称性（审计版）: 审计不严的复利代价" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

echo "【第二部分】审计专属检查（6项）" | tee -a "$LOG_FILE"
echo "[ ] 独立性验证: 独立抽样/独立验证/独立结论" | tee -a "$LOG_FILE"
echo "[ ] 抽查→扩大→全量: 10%→50%→100%" | tee -a "$LOG_FILE"
echo "[ ] FAIL完整性: 问题+要求+时限+后果" | tee -a "$LOG_FILE"
echo "[ ] 执行监督: 运行监督脚本/发现超期/申请介入" | tee -a "$LOG_FILE"
echo "[ ] 诚实度自评: 数据/抽查/独立/强制 四维度" | tee -a "$LOG_FILE"
echo "[ ] 蓝军自我审计: 运行自检/发现违规/自罚" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

echo "【第三部分】内容完整性（3项）" | tee -a "$LOG_FILE"
echo "[ ] 好消息: PASS项清单" | tee -a "$LOG_FILE"
echo "[ ] 坏消息: FAIL项清单（含4要素）" | tee -a "$LOG_FILE"
echo "[ ] 思考过程: 思维方式应用展示" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

echo "检查完成标准:" | tee -a "$LOG_FILE"
echo "- 思维方式6项全部应用" | tee -a "$LOG_FILE"
echo "- 审计专属6项全部通过" | tee -a "$LOG_FILE"
echo "- 内容3项全部完整" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "日志: $LOG_FILE" | tee -a "$LOG_FILE"
