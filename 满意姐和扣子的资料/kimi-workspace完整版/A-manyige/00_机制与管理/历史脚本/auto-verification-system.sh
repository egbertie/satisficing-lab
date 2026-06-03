#!/bin/bash
# 自运行验证系统 V1.0
# 核心：自动检测声称完成的机制，无需人工全量检查
# 应用：反脆弱性 + 时间不对称防护 + 自动信号生成

set -e

WORKSPACE="/root/.openclaw/workspace"
REPORT_DIR="$WORKSPACE/reports/auto-verification"
DATE=$(date +%Y-%m-%d)
LOG_FILE="$REPORT_DIR/verification-${DATE}.log"

mkdir -p "$REPORT_DIR"

echo "=== 自运行验证系统 ===" | tee -a "$LOG_FILE"
echo "时间: $(date)" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# ============================================================================
# 1. 自动提取声称完成的机制（从memory文件）
# ============================================================================
echo "【步骤1】提取声称完成的机制..." | tee -a "$LOG_FILE"

CLAIMED_FILE="$REPORT_DIR/claimed-${DATE}.txt"

# 从所有memory文件提取声称完成的记录
grep -rE "✅|完成|FIN-26|已部署|建立.*完成" $WORKSPACE/memory/*.md 2>/dev/null | \
    grep -v "Binary" | \
    awk -F: '{print $1 "|" $2}' | \
    sort -u > "$CLAIMED_FILE"

CLAIMED_COUNT=$(wc -l < "$CLAIMED_FILE")
echo "发现声称完成记录: $CLAIMED_COUNT条" | tee -a "$LOG_FILE"

# ============================================================================
# 2. 自动扫描实际存在的机制
# ============================================================================
echo "" | tee -a "$LOG_FILE"
echo "【步骤2】扫描实际存在的机制..." | tee -a "$LOG_FILE"

EXISTING_FILE="$REPORT_DIR/existing-${DATE}.txt"

# 扫描Skill
find $WORKSPACE/skills -maxdepth 1 -type d | while read dir; do
    skill_name=$(basename "$dir")
    if [ -f "$dir/SKILL.md" ]; then
        echo "SKILL|$skill_name|$dir/SKILL.md" >> "$EXISTING_FILE"
    fi
done

# 扫描文档
find $WORKSPACE/docs -name "*.md" -type f | while read file; do
    doc_name=$(basename "$file" .md)
    echo "DOC|$doc_name|$file" >> "$EXISTING_FILE"
done

# 扫描交付物
find $WORKSPACE/deliverables -name "*.md" -type f 2>/dev/null | while read file; do
    deliv_name=$(basename "$file" .md)
    echo "DELIV|$deliv_name|$file" >> "$EXISTING_FILE"
done

EXISTING_COUNT=$(wc -l < "$EXISTING_FILE")
echo "发现实际存在文件: $EXISTING_COUNT个" | tee -a "$LOG_FILE"

# ============================================================================
# 3. 自动匹配与差异分析
# ============================================================================
echo "" | tee -a "$LOG_FILE"
echo "【步骤3】匹配分析..." | tee -a "$LOG_FILE"

VERIFIED_FILE="$REPORT_DIR/verified-${DATE}.txt"
MISSING_FILE="$REPORT_DIR/missing-${DATE}.txt"

# 简单匹配（实际应该更复杂）
while IFS='|' read -r source claimed; do
    # 提取可能的关键词
    keywords=$(echo "$claimed" | grep -oE "[a-zA-Z0-9_-]+" | tr '\n' '|' | sed 's/|$//')
    
    if [ -n "$keywords" ]; then
        # 在存在的文件中搜索
        if grep -qiE "$keywords" "$EXISTING_FILE"; then
            echo "$claimed|EXISTS" >> "$VERIFIED_FILE"
        else
            echo "$claimed|MISSING" >> "$MISSING_FILE"
        fi
    fi
done < "$CLAIMED_FILE"

VERIFIED_COUNT=$(wc -l < "$VERIFIED_FILE" 2>/dev/null || echo "0")
MISSING_COUNT=$(wc -l < "$MISSING_FILE" 2>/dev/null || echo "0")

echo "已验证存在: $VERIFIED_COUNT条" | tee -a "$LOG_FILE"
echo "疑似丢失: $MISSING_COUNT条" | tee -a "$LOG_FILE"

# ============================================================================
# 4. 计算丢失率
# ============================================================================
echo "" | tee -a "$LOG_FILE"
echo "【步骤4】丢失率统计..." | tee -a "$LOG_FILE"

if [ "$CLAIMED_COUNT" -gt 0 ]; then
    LOSS_RATE=$(echo "scale=2; $MISSING_COUNT * 100 / $CLAIMED_COUNT" | bc)
    echo "当前丢失率: ${LOSS_RATE}%" | tee -a "$LOG_FILE"
else
    echo "当前丢失率: N/A" | tee -a "$LOG_FILE"
fi

# ============================================================================
# 5. 生成报告
# ============================================================================
echo "" | tee -a "$LOG_FILE"
echo "【步骤5】生成报告..." | tee -a "$LOG_FILE"

REPORT_FILE="$REPORT_DIR/report-${DATE}.md"

cat > "$REPORT_FILE" << EOF
# 自动验证报告 - ${DATE}

## 统计摘要
| 指标 | 数值 |
|------|------|
| 声称完成记录 | $CLAIMED_COUNT |
| 实际存在文件 | $EXISTING_COUNT |
| 已验证匹配 | $VERIFIED_COUNT |
| 疑似丢失 | $MISSING_COUNT |
| **丢失率** | **${LOSS_RATE}%** |

## 趋势分析
$(if [ -f "$REPORT_DIR/report-$(date -d '7 days ago' +%Y-%m-%d).md" ]; then
    echo "查看上周报告对比..."
else
    echo "无历史数据（首次运行）"
fi)

## 疑似丢失清单（前20条）
$(head -20 "$MISSING_FILE" 2>/dev/null || echo "无")

## 建议行动
$(if [ "${LOSS_RATE%.*}" -gt 50 ]; then
    echo "🔴 丢失率过高，建议立即启动全量验证"
elif [ "${LOSS_RATE%.*}" -gt 20 ]; then
    echo "🟡 丢失率较高，建议分批验证"
else
    echo "🟢 丢失率可控，建议持续监控"
fi)

---
生成时间: $(date)
EOF

echo "报告生成: $REPORT_FILE" | tee -a "$LOG_FILE"

# ============================================================================
# 6. 时间不对称防护 - 检查新增债务
# ============================================================================
echo "" | tee -a "$LOG_FILE"
echo "【步骤6】时间不对称防护..." | tee -a "$LOG_FILE"

# 检查今天新增的声称
TODAY_CLAIMED=$(grep -c "$(date +%Y-%m-%d)" "$CLAIMED_FILE" 2>/dev/null || echo "0")
echo "今日新增声称: $TODAY_CLAIMED条" | tee -a "$LOG_FILE"

if [ "$TODAY_CLAIMED" -gt 0 ]; then
    echo "⚠️  警告: 今日有$TODAY_CLAIMED条新的声称完成记录" | tee -a "$LOG_FILE"
    echo "建议: 立即验证今日新增，防止债务累积" | tee -a "$LOG_FILE"
fi

# ============================================================================
# 7. 输出摘要
# ============================================================================
echo "" | tee -a "$LOG_FILE"
echo "=== 验证完成 ===" | tee -a "$LOG_FILE"
echo "详细报告: $REPORT_FILE" | tee -a "$LOG_FILE"
echo "日志文件: $LOG_FILE" | tee -a "$LOG_FILE"

# 返回码：如果丢失率>50%则返回1（触发告警）
if [ "${LOSS_RATE%.*}" -gt 50 ]; then
    echo "🔴 丢失率过高!" | tee -a "$LOG_FILE"
    exit 1
else
    echo "🟢 验证通过" | tee -a "$LOG_FILE"
    exit 0
fi
