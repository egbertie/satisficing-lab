#!/bin/bash
# P0任务执行脚本 - 自动化检查
# 固化运用脚本

echo "=== P0任务执行检查 ==="
echo "时间: $(date)"
echo ""

# 检查是否五项维度检查清单存在
CHECKLIST="/root/.openclaw/workspace/checklists/FIVE_DIMENSION_CHECKLIST.md"
if [ ! -f "$CHECKLIST" ]; then
    echo "❌ 错误: 五项维度检查清单不存在"
    echo "请先创建: $CHECKLIST"
    exit 1
fi

echo "✅ 五项维度检查清单存在"

# 检查是否执行了5遍搜索
echo ""
echo "=== 5遍搜索检查 ==="
echo "提示: 必须执行以下5遍搜索"
echo "  第1遍: 基础关键词 (已部署/V1.0 FIN/建立)"
echo "  第2遍: 变体关键词 (完成/已/日期)"
echo "  第3遍: 标记符号 (✅/🟢/归档)"
echo "  第4遍: 文件内容深度 (状态完成/实现/可用)"
echo "  第5遍: 系统配置 (scripts/cron/REVIEW)"
echo ""
read -p "是否已完成5遍搜索？(yes/no): " FIVE_SEARCH

if [ "$FIVE_SEARCH" != "yes" ]; then
    echo "❌ 错误: 必须完成5遍搜索才能继续"
    exit 1
fi

echo "✅ 5遍搜索确认完成"

# 检查是否填写了五项维度
echo ""
echo "=== 五项维度检查 ==="
echo "请确认已完成以下检查:"
echo "  □ 时间维度 (重启/过期影响)"
echo "  □ 空间维度 (数据完整性%)"
echo "  □ 深度维度 (根本原因)"
echo "  □ 关联维度 (历史关联)"
echo "  □ 演进维度 (能力培养)"
echo ""
read -p "是否已完成五项维度检查？(yes/no): " FIVE_DIM

if [ "$FIVE_DIM" != "yes" ]; then
    echo "❌ 错误: 必须完成五项维度检查"
    exit 1
fi

echo "✅ 五项维度检查确认完成"

# 检查诚实声明
echo ""
echo "=== 诚实声明 ==="
read -p "是否偷工减料？(yes/no): " CORNER_CUTTING
read -p "是否粉饰太平？(yes/no): " WHITEWASH

if [ "$CORNER_CUTTING" = "yes" ] || [ "$WHITEWASH" = "yes" ]; then
    echo "❌ 错误: 存在偷工减料或粉饰太平"
    echo "请重新执行任务，确保诚实"
    exit 1
fi

echo "✅ 诚实声明确认"

# 记录到能力成长档案
echo ""
echo "=== 记录到能力成长档案 ==="
ARCHIVE="/root/.openclaw/workspace/docs/CAPABILITY_GROWTH_ARCHIVE.md"
echo ""
echo "#### 事件: P0任务执行" >> "$ARCHIVE"
echo "**时间**: $(date)" >> "$ARCHIVE"
echo "**任务**: $1" >> "$ARCHIVE"
echo "" >> "$ARCHIVE"
echo "**能力培养**: 五项维度检查、5遍搜索、绝对诚实" >> "$ARCHIVE"
echo "" >> "$ARCHIVE"

echo "✅ 已记录到能力成长档案"

echo ""
echo "=== P0任务检查通过 ==="
echo "可以继续执行任务"
