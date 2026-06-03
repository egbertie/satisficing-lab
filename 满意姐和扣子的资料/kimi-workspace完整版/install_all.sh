#!/bin/bash
# install_all.sh
# 统一安装脚本：五元资产飞轮 + P8/OpenSpec整合方案

set -e

echo "🚀 开始安装五元资产飞轮 + P8/OpenSpec整合方案..."

# 1. 目录结构
echo "📁 步骤1/4: 创建目录结构..."
mkdir -p assets_flywheel/generated_skills
mkdir -p skills/p8_engine skills/openspec_manager council/pua_pressure bridge_rules
mkdir -p openspec/{specs,changes,archive}
mkdir -p A-manyige/汇报 cognitive_ecosystem/docs
echo "✅ 目录结构已创建"

# 2. Python依赖
echo "📦 步骤2/4: 检查Python依赖..."
python3 -c "import yaml" 2>/dev/null || pip install -q pyyaml
echo "✅ 依赖已就绪"

# 3. 配置OpenSpec
echo "🏗️  步骤3/4: 初始化OpenSpec..."
if [ ! -f "openspec/config.yaml" ]; then
python3 -c "
import yaml
cfg = {
    'project': {'name': 'satisfying-ecosystem', 'tech_stack': ['python'], 'architecture': 'cognitive_ecosystem'},
    'rules': {'max_tasks_per_change': 15, 'require_tests': True, 'coding_standards': 'strict'}
}
with open('openspec/config.yaml', 'w') as f:
    yaml.dump(cfg, f)
"
    echo "✅ OpenSpec默认配置已创建"
else
    echo "✅ OpenSpec配置已存在"
fi

# 4. 端到端验收测试
echo "🧪 步骤4/4: 运行端到端验收测试..."
export PYTHONPATH=/root/.openclaw/workspace:/root/.openclaw/workspace/cognitive_ecosystem
cd /root/.openclaw/workspace
python3 demo_unified.py
echo "✅ 端到端测试通过"

echo ""
echo "🎉 全部安装与验收测试通过！"
echo "五元资产飞轮 + P8/OpenSpec整合方案已就绪。"
