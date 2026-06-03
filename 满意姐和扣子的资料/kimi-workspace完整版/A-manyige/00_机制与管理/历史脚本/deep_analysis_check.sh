#!/bin/bash
# 深度分析检查脚本
# 自动验证深度分析是否符合DEEP_ANALYSIS_CHECKLIST.md要求

set -e

CHECKLIST_FILE="/root/.openclaw/workspace/checklists/DEEP_ANALYSIS_CHECKLIST.md"
REPORT_FILE="/root/.openclaw/workspace/reports/deep_analysis_audit_$(date +%Y%m%d_%H%M%S).md"

echo "=== 深度分析强制检查 ==="
echo "检查时间: $(date)"
echo ""

# 创建报告目录
mkdir -p /root/.openclaw/workspace/reports

# 初始化检查结果
PASS_COUNT=0
FAIL_COUNT=0
CHECK_ITEMS=()

# 检查函数
check_item() {
    local name="$1"
    local condition="$2"
    
    if eval "$condition"; then
        echo "  ✅ $name"
        ((PASS_COUNT++)) || true
        CHECK_ITEMS+=("| $name | ✅ PASS |")
    else
        echo "  ❌ $name"
        ((FAIL_COUNT++)) || true
        CHECK_ITEMS+=("| $name | ❌ FAIL |")
    fi
}

echo "【检查1】原始数据提取..."
check_item "读取全部源数据" "[ -f ~/.openclaw/workspace/.last_analysis_data ]"
check_item "保存原始数据文件" "[ -d ~/.openclaw/workspace/data ]"
check_item "记录提取数量" "[ -f ~/.openclaw/workspace/.last_analysis_count ]"

echo ""
echo "【检查2】量化统计..."
check_item "样本数量记录" "grep -q '样本数量' ~/.openclaw/workspace/.last_analysis_report 2>/dev/null || false"
check_item "统计结果记录" "grep -q '统计结果' ~/.openclaw/workspace/.last_analysis_report 2>/dev/null || false"
check_item "置信度标注" "grep -q '置信度' ~/.openclaw/workspace/.last_analysis_report 2>/dev/null || false"

echo ""
echo "【检查3】分层分析（L1-L5）..."
check_item "L1原始数据" "grep -q 'L1' ~/.openclaw/workspace/.last_analysis_report 2>/dev/null || false"
check_item "L2分类统计" "grep -q 'L2' ~/.openclaw/workspace/.last_analysis_report 2>/dev/null || false"
check_item "L3模式识别" "grep -q 'L3' ~/.openclaw/workspace/.last_analysis_report 2>/dev/null || false"
check_item "L4原因分析" "grep -q 'L4' ~/.openclaw/workspace/.last_analysis_report 2>/dev/null || false"
check_item "L5 Actionable Insights" "grep -q 'L5\|Actionable' ~/.openclaw/workspace/.last_analysis_report 2>/dev/null || false"

echo ""
echo "【检查4】五维度深度检查..."
check_item "时间维度检查" "grep -q '时间维度' ~/.openclaw/workspace/.last_analysis_report 2>/dev/null || false"
check_item "空间维度检查" "grep -q '空间维度' ~/.openclaw/workspace/.last_analysis_report 2>/dev/null || false"
check_item "深度维度检查" "grep -q '深度维度' ~/.openclaw/workspace/.last_analysis_report 2>/dev/null || false"
check_item "关联维度检查" "grep -q '关联维度' ~/.openclaw/workspace/.last_analysis_report 2>/dev/null || false"
check_item "演进维度检查" "grep -q '演进维度' ~/.openclaw/workspace/.last_analysis_report 2>/dev/null || false"

echo ""
echo "【检查5】交付物验证..."
check_item "原始数据文件存在" "[ -d ~/.openclaw/workspace/data ]"
check_item "分析脚本存在" "[ -f ~/.openclaw/workspace/scripts/deep_analysis_check.sh ]"
check_item "结果文件存在" "[ -f ~/.openclaw/workspace/.last_analysis_report ]"

# 生成报告
cat > "$REPORT_FILE" << EOF
# 深度分析审计报告

**审计时间**: $(date)
**审计人**: 蓝军自动审计系统
**检查清单版本**: v1.1.0

---

## 检查结果汇总

| 检查项 | 结果 |
|--------|------|
EOF

for item in "${CHECK_ITEMS[@]}"; do
    echo "$item" >> "$REPORT_FILE"
done

cat >> "$REPORT_FILE" << EOF

---

## 统计

- **通过**: $PASS_COUNT 项
- **失败**: $FAIL_COUNT 项
- **总计**: $((PASS_COUNT + FAIL_COUNT)) 项

## 结论

EOF

if [ $FAIL_COUNT -eq 0 ]; then
    echo "✅ 所有检查通过" >> "$REPORT_FILE"
    echo "**状态**: PASS" >> "$REPORT_FILE"
else
    echo "❌ 发现 $FAIL_COUNT 项未通过" >> "$REPORT_FILE"
    echo "**状态**: FAIL" >> "$REPORT_FILE"
fi

echo ""
echo "---"
echo "检查结果: 通过 $PASS_COUNT / 失败 $FAIL_COUNT"
echo "报告已保存: $REPORT_FILE"

if [ $FAIL_COUNT -eq 0 ]; then
    echo "✅ 所有检查通过"
    exit 0
else
    echo "❌ 存在未通过项，请补充后重试"
    exit 1
fi
