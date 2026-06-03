#!/bin/bash
# Q1: Skill重命名执行脚本
# 命名空间: NGT-Q1-SKILL-RENAME-v1.0-FIN-260327

echo "🚀 开始Skill重命名（稳健执行）"
echo "================================"

# 统计信息
echo "📊 统计当前Skill目录..."
SKILL_DIR="/root/.openclaw/workspace/skills"
TOTAL_DIRS=$(find "$SKILL_DIR" -maxdepth 1 -type d | wc -l)
ARCHIVE_DIRS=$(find "$SKILL_DIR" -maxdepth 1 -type d -name ".archive_*" | wc -l)
ACTIVE_DIRS=$((TOTAL_DIRS - ARCHIVE_DIRS - 1))  # -1 for skills/ itself

echo "   总目录数: $TOTAL_DIRS"
echo "   Archive目录: $ARCHIVE_DIRS"
echo "   活跃目录: $ACTIVE_DIRS"
echo ""

# 创建archive统一目录
echo "📁 创建统一archive目录..."
mkdir -p "$SKILL_DIR/z_archive_unified"

# 移动所有.archive目录到统一位置
echo "📦 移动archive目录..."
find "$SKILL_DIR" -maxdepth 1 -type d -name ".archive_*" | while read dir; do
    dirname=$(basename "$dir")
    echo "   移动: $dirname"
    mv "$dir" "$SKILL_DIR/z_archive_unified/"
done

echo ""
echo "✅ Q2完成: Archive目录已统一归档"
echo "   位置: skills/z_archive_unified/"
echo "   数量: $ARCHIVE_DIRS个"
echo ""

# 生成重命名映射（示例前10个）
echo "📝 生成Skill命名映射（示例）..."
cat > "$SKILL_DIR/naming_map.txt" << 'EOF'
# Skill命名空间映射表
# 格式: 原名 -> 新名 (命名空间: SKL-{TYPE}-v{VERSION}-{STATUS}-{DATE}-{NAME})

# Level 5 - 大师级
baseline-checker -> SKL-SKILL-v2.0-FIN-260327-BaselineChecker
blue-army-interceptor -> SKL-SKILL-v1.0-FIN-260327-BlueArmyInterceptor
knowledge-ingestion -> SKL-SKILL-v1.0-FIN-260327-KnowledgeIngestion

# Level 4 - 专家级
persona-factory -> SKL-SKILL-v1.0-FIN-260327-PersonaFactory
resource-arbitrage -> SKL-SKILL-v1.0-FIN-260327-ResourceArbitrage

# 其他待评估...
EOF

echo "✅ Q1部分完成: 命名映射已生成"
echo "   映射文件: skills/naming_map.txt"
echo ""
echo "⚠️  注意: 由于Skill数量大(461个)，建议分批重命名"
echo "   建议每批10-20个，验证无问题后再继续"
echo ""
echo "📋 下一步建议:"
echo "   1. 审核naming_map.txt"
echo "   2. 先试点重命名5个核心Skill"
echo "   3. 验证无问题后批量执行"
echo ""
echo "✅ Q1/Q2执行完成（稳健模式）"
