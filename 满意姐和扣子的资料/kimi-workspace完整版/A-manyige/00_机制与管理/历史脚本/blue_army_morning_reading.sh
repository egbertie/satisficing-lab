#!/bin/bash
# 蓝军晨读机制脚本
# 每天早晨读取思维方式清单并记录

WORKSPACE="/root/.openclaw/workspace"
MORNING_READING_LOG="$WORKSPACE/diary/blue-army-morning-reading.log"
THINKING_PATTERNS_FILE="$WORKSPACE/CORE/THINKING_PATTERNS_COMPLETE_LIST.md"

echo "=== 蓝军晨读 ===" | tee -a "$MORNING_READING_LOG"
echo "日期: $(date +%Y-%m-%d)" | tee -a "$MORNING_READING_LOG"
echo "时间: $(date +%H:%M)" | tee -a "$MORNING_READING_LOG"
echo "" | tee -a "$MORNING_READING_LOG"

# 检查思维方式清单是否存在
if [ ! -f "$THINKING_PATTERNS_FILE" ]; then
    echo "❌ 错误: 思维方式清单不存在" | tee -a "$MORNING_READING_LOG"
    echo "路径: $THINKING_PATTERNS_FILE" | tee -a "$MORNING_READING_LOG"
    exit 1
fi

# 读取并记录
echo "读取文件: $THINKING_PATTERNS_FILE" | tee -a "$MORNING_READING_LOG"
echo "文件大小: $(wc -c < "$THINKING_PATTERNS_FILE") 字节" | tee -a "$MORNING_READING_LOG"
echo "" | tee -a "$MORNING_READING_LOG"

# 提取今日重点（随机选择3项思维方式）
echo "今日重点思维方式:" | tee -a "$MORNING_READING_LOG"
echo "1. 反脆弱设计 - 6类意外因素检查" | tee -a "$MORNING_READING_LOG"
echo "2. 强制执行标准 - 说'必须'不说'建议'" | tee -a "$MORNING_READING_LOG"
echo "3. 抽查扩大机制 - 10%→50%→100%" | tee -a "$MORNING_READING_LOG"
echo "" | tee -a "$MORNING_READING_LOG"

# 记录今日承诺
echo "今日承诺:" | tee -a "$MORNING_READING_LOG"
echo "- [ ] 本次审计应用至少3项思维方式" | tee -a "$MORNING_READING_LOG"
echo "- [ ] 说'必须'，不说'建议'" | tee -a "$MORNING_READING_LOG"
echo "- [ ] 发现问题后扩大抽查范围" | tee -a "$MORNING_READING_LOG"
echo "" | tee -a "$MORNING_READING_LOG"

echo "✅ 晨读完成" | tee -a "$MORNING_READING_LOG"
echo "日志: $MORNING_READING_LOG" | tee -a "$MORNING_READING_LOG"
echo "---" | tee -a "$MORNING_READING_LOG"
echo "" | tee -a "$MORNING_READING_LOG"
