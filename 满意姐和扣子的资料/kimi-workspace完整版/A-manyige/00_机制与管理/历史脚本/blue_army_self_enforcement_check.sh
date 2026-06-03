#!/bin/bash
# 蓝军强制执行检查脚本
# 每次蓝军审计后必须运行，检查自己是否做到位

WORKSPACE="/root/.openclaw/workspace"
SELF_AUDIT_LOG="$WORKSPACE/diary/blue-army-self-audit-execution.log"

echo "=== 蓝军自我强制执行检查 ===" | tee -a "$SELF_AUDIT_LOG"
echo "检查时间: $(date)" | tee -a "$SELF_AUDIT_LOG"
echo "" | tee -a "$SELF_AUDIT_LOG"

# 检查1: 是否说"必须"而不是"建议"
echo "检查1: 语言检查" | tee -a "$SELF_AUDIT_LOG"
echo "标准: 本次审计是否只使用'必须'、'要求'、'FAIL'，没有'建议'、'可以考虑'" | tee -a "$SELF_AUDIT_LOG"
echo "结果: 需人工确认" | tee -a "$SELF_AUDIT_LOG"
echo "" | tee -a "$SELF_AUDIT_LOG"

# 检查2: 是否应用至少3项思维方式
echo "检查2: 思维方式应用检查" | tee -a "$SELF_AUDIT_LOG"
echo "标准: 本次审计是否应用了至少3项思维方式" | tee -a "$SELF_AUDIT_LOG"
echo "结果: 需人工确认" | tee -a "$SELF_AUDIT_LOG"
echo "" | tee -a "$SELF_AUDIT_LOG"

# 检查3: 抽查是否扩大到全量
echo "检查3: 抽查范围检查" | tee -a "$SELF_AUDIT_LOG"
echo "标准: 发现问题后是否扩大抽查至50%或全量" | tee -a "$SELF_AUDIT_LOG"
echo "结果: 需人工确认" | tee -a "$SELF_AUDIT_LOG"
echo "" | tee -a "$SELF_AUDIT_LOG"

# 检查4: 是否明确问题+要求+时限+后果
echo "检查4: FAIL完整性检查" | tee -a "$SELF_AUDIT_LOG"
echo "标准: 每个FAIL是否都包含：问题+要求+时限+后果" | tee -a "$SELF_AUDIT_LOG"
echo "结果: 需人工确认" | tee -a "$SELF_AUDIT_LOG"
echo "" | tee -a "$SELF_AUDIT_LOG"

# 检查5: 是否真正阻断了不合格交付
echo "检查5: 阻断执行检查" | tee -a "$SELF_AUDIT_LOG"
echo "标准: 对于FAIL的交付物，是否真正阻止其进入下一阶段" | tee -a "$SELF_AUDIT_LOG"
echo "结果: 需人工确认" | tee -a "$SELF_AUDIT_LOG"
echo "" | tee -a "$SELF_AUDIT_LOG"

echo "=== 检查完成 ===" | tee -a "$SELF_AUDIT_LOG"
echo "如有任何一项未通过，蓝军必须立即整改" | tee -a "$SELF_AUDIT_LOG"
echo "" | tee -a "$SELF_AUDIT_LOG"
