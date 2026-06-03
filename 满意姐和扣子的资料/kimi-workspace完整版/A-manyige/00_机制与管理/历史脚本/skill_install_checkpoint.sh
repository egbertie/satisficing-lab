#!/bin/bash
# Skill安装强制检查点脚本
# 用途: 确保所有skill安装前完成评估
# 执行位置: 嵌入所有安装流程

SKILL_NAME=$1
CHECKPOINT_FILE="/root/.openclaw/workspace/.skill_install_checkpoint"
EVALUATION_LIST="/root/.openclaw/workspace/CLAWHUB_SKILL_INSTALL_LIST.md"
REPORT_FILE="/root/.openclaw/workspace/reports/SKILL_INSTALL_CHECKPOINT_LOG.md"

echo "=============================================="
echo "    Skill安装强制检查点"
echo "=============================================="
echo "检查时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "Skill名称: $SKILL_NAME"
echo ""

# 检查点1: 是否在已评估清单中
echo "【检查点1】是否已完成评估？"
if grep -q "$SKILL_NAME" "$EVALUATION_LIST" 2>/dev/null; then
    echo "  ✅ 已找到评估记录"
    EVALUATED=true
else
    echo "  ❌ 未找到评估记录"
    EVALUATED=false
fi
echo ""

# 检查点2: 评估结果是什么
echo "【检查点2】评估结果分类（P0/P1/P2/P3）"
if [ "$EVALUATED" = true ]; then
    # 提取评估结果
    P0_CHECK=$(grep -A2 "$SKILL_NAME" "$EVALUATION_LIST" | grep -i "p0\|立即安装" | head -1)
    P1_CHECK=$(grep -A2 "$SKILL_NAME" "$EVALUATION_LIST" | grep -i "p1\|合并" | head -1)
    P2_CHECK=$(grep -A2 "$SKILL_NAME" "$EVALUATION_LIST" | grep -i "p2\|延迟" | head -1)
    P3_CHECK=$(grep -A2 "$SKILL_NAME" "$EVALUATION_LIST" | grep -i "p3\|拒绝" | head -1)
    
    if [ -n "$P0_CHECK" ]; then
        echo "  ✅ P0-立即安装"
        CATEGORY="P0"
    elif [ -n "$P1_CHECK" ]; then
        echo "  ✅ P1-合并安装"
        CATEGORY="P1"
    elif [ -n "$P2_CHECK" ]; then
        echo "  ⚠️ P2-延迟安装（不建议现在安装）"
        CATEGORY="P2"
    elif [ -n "$P3_CHECK" ]; then
        echo "  ❌ P3-拒绝安装（禁止安装）"
        CATEGORY="P3"
    else
        echo "  ⚠️ 已评估但分类不明"
        CATEGORY="UNKNOWN"
    fi
else
    echo "  ❌ 未评估，无法分类"
    CATEGORY="UNEVALUATED"
fi
echo ""

# 检查点3: 是否允许安装
echo "【检查点3】安装权限检查"
CAN_INSTALL=false
if [ "$CATEGORY" = "P0" ] || [ "$CATEGORY" = "P1" ]; then
    echo "  ✅ 允许安装"
    CAN_INSTALL=true
elif [ "$CATEGORY" = "P2" ]; then
    echo "  ⚠️ P2类别，需要人工确认"
    read -p "  是否强制安装？(yes/no): " CONFIRM
    if [ "$CONFIRM" = "yes" ]; then
        CAN_INSTALL=true
        FORCED=true
    fi
elif [ "$CATEGORY" = "P3" ]; then
    echo "  ❌ P3类别，禁止安装"
    echo "  原因: 重复/高风险/高成本"
    CAN_INSTALL=false
elif [ "$CATEGORY" = "UNEVALUATED" ]; then
    echo "  ❌ 未评估，禁止安装"
    echo "  请先执行评估流程"
    CAN_INSTALL=false
fi
echo ""

# 检查点4: 安全审计（简化版）
echo "【检查点4】安全检查"
echo "  ⚠️ 详细安全审计需人工执行"
echo "  检查项:"
echo "    - 代码权限审查"
echo "    - 数据流向检查"
echo "    - 外部依赖分析"
read -p "  是否已人工审计安全？(yes/no): " SECURITY_CHECK
if [ "$SECURITY_CHECK" = "yes" ]; then
    echo "  ✅ 安全审计通过"
    SECURITY_PASSED=true
else
    echo "  ⚠️ 未审计，建议先审计"
    SECURITY_PASSED=false
fi
echo ""

# 最终决策
echo "=============================================="
echo "    检查点总结"
echo "=============================================="
echo "评估状态: $([ "$EVALUATED" = true ] && echo '✅ 已评估' || echo '❌ 未评估')"
echo "评估分类: $CATEGORY"
echo "安装权限: $([ "$CAN_INSTALL" = true ] && echo '✅ 允许' || echo '❌ 禁止')"
echo "安全审计: $([ "$SECURITY_PASSED" = true ] && echo '✅ 通过' || echo '⚠️ 未通过')"
echo ""

if [ "$CAN_INSTALL" = true ] && [ "$SECURITY_PASSED" = true ]; then
    echo "🎉 所有检查点通过，允许安装！"
    RESULT="PASSED"
else
    echo "❌ 检查点未通过，禁止安装！"
    echo ""
    echo "请完成以下事项后再试："
    [ "$EVALUATED" = false ] && echo "  - 完成skill评估"
    [ "$CATEGORY" = "P3" ] && echo "  - 该skill为P3类别，不应安装"
    [ "$SECURITY_PASSED" = false ] && echo "  - 完成安全审计"
    RESULT="BLOCKED"
fi

# 记录日志
echo "" >> "$REPORT_FILE"
echo "## $(date '+%Y-%m-%d %H:%M:%S') - $SKILL_NAME" >> "$REPORT_FILE"
echo "- 评估状态: $([ "$EVALUATED" = true ] && echo '已评估' || echo '未评估')" >> "$REPORT_FILE"
echo "- 评估分类: $CATEGORY" >> "$REPORT_FILE"
echo "- 安装权限: $([ "$CAN_INSTALL" = true ] && echo '允许' || echo '禁止')" >> "$REPORT_FILE"
echo "- 安全审计: $([ "$SECURITY_PASSED" = true ] && echo '通过' || echo '未通过')" >> "$REPORT_FILE"
echo "- 强制安装: $([ "$FORCED" = true ] && echo '是' || echo '否')" >> "$REPORT_FILE"
echo "- 结果: $RESULT" >> "$REPORT_FILE"

# 返回结果
if [ "$RESULT" = "PASSED" ]; then
    exit 0
else
    exit 1
fi
