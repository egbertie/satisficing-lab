#!/bin/bash
# Skill安装安全包装脚本
# 所有skill安装必须通过此脚本
# 强制嵌入检查点机制

SKILL_NAME=$1
CHECKPOINT_SCRIPT="/root/.openclaw/workspace/scripts/skill_install_checkpoint.sh"

echo "=============================================="
echo "    Skill安装安全通道"
echo "=============================================="
echo ""
echo "⚠️  重要提醒：根据管理规则，所有skill安装前必须完成评估！"
echo ""

# 执行强制检查点
if [ -f "$CHECKPOINT_SCRIPT" ]; then
    bash "$CHECKPOINT_SCRIPT" "$SKILL_NAME"
    CHECKPOINT_RESULT=$?
    
    if [ $CHECKPOINT_RESULT -ne 0 ]; then
        echo ""
        echo "❌ 检查点未通过，安装被阻止！"
        echo ""
        echo "如需绕过检查点（不推荐），请使用："
        echo "  clawhub install $SKILL_NAME --force"
        echo ""
        echo "但请注意：绕过检查点将被记录在案。"
        exit 1
    fi
else
    echo "⚠️  警告：检查点脚本缺失，但仍继续安装"
    echo "（请确认这是预期行为）"
    read -p "是否继续？(yes/no): " CONFIRM
    if [ "$CONFIRM" != "yes" ]; then
        exit 1
    fi
fi

# 检查点通过，执行安装
echo ""
echo "✅ 检查点通过，开始安装..."
echo ""

# 执行实际安装命令
clawhub install "$SKILL_NAME"

exit $?
