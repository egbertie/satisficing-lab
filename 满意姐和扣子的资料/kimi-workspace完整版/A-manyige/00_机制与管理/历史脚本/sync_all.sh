#!/bin/bash
# 一键全量同步脚本
# 从所有Core定义同步到Working层

echo "========================================"
echo " 满意解知识管理系统 - 全量同步"
echo "========================================"
echo ""

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到Python3"
    exit 1
fi

# 检查PyYAML
if ! python3 -c "import yaml" 2>/dev/null; then
    echo "⚠️  安装PyYAML..."
    pip install pyyaml -q
fi

echo "🔄 开始同步..."
echo ""

# 运行所有同步脚本
cd /root/.openclaw/workspace

echo "1️⃣ 同步案例库..."
python3 scripts/sync_cases.py
echo ""

echo "2️⃣ 同步专家档案..."
python3 scripts/sync_experts.py
echo ""

echo "3️⃣ 同步技术文档..."
python3 scripts/sync_tech.py
echo ""

echo "4️⃣ 同步运营文档..."
python3 scripts/sync_ops.py
echo ""

echo "5️⃣ 同步Skill注册表..."
python3 scripts/sync_skills.py
echo ""

echo "6️⃣ 迁移历史记忆..."
python3 scripts/migrate_memory.py
echo ""

echo "7️⃣ 运行一致性检查..."
python3 scripts/consistency_check.py
echo ""

echo "========================================"
echo " ✅ 全量同步完成"
echo "========================================"
echo ""
echo "📁 Working层输出:"
echo "   - working/cases/          (案例库)"
echo "   - working/experts/        (专家档案)"
echo "   - working/tech/           (技术文档)"
echo "   - working/operations/     (运营文档)"
echo "   - working/skills/         (Skill目录)"
echo ""
echo "📁 归档层输出:"
echo "   - memory/archive/logs/    (历史日志)"
echo ""
