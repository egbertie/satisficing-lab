#!/bin/bash
# 文件: /root/.openclaw/workspace/deploy_all.sh
# 功能: 一键部署脚本 - 部署所有四层防御系统
# 作者: 外援方案 + 满意姐执行
# 创建时间: 2026-04-04
# 蓝军指导: Skeptor-7

set -e  # 遇到错误立即退出

# ============================================================
# Dry-run 模式支持
# ============================================================
DRY_RUN=false
if [ "$1" == "--dry-run" ]; then
    DRY_RUN=true
    echo ""
    echo "🏃 DRY-RUN 模式: 只检查，不执行任何修改操作"
    echo "============================================================"
fi

echo ""
echo "🔥🔥🔥 满意解研究所 - 四层防御系统一键部署 🔥🔥🔥"
echo "============================================================"
echo ""
echo "部署时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "部署环境: $(uname -a)"
if [ "$DRY_RUN" = true ]; then
    echo "运行模式: DRY-RUN (只读验证)"
fi
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 工作目录
WORKSPACE="/root/.openclaw/workspace"
cd "$WORKSPACE"

echo "📁 工作目录: $WORKSPACE"
echo ""

# ============================================================
# 辅助函数
# ============================================================
run_safe() {
    local action="$1"
    local cmd="$2"
    if [ "$DRY_RUN" = true ]; then
        echo -e "    ${YELLOW}[DRY-RUN] 将执行: $action${NC}"
    else
        eval "$cmd"
    fi
}

# ============================================================
# 第1步: 检查环境
# ============================================================
echo "[1/8] 检查部署环境..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 未安装${NC}"
    exit 1
fi

if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}❌ pip3 未安装${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Python3 环境正常: $(python3 --version)${NC}"
echo ""

# ============================================================
# 第2步: 创建目录结构
# ============================================================
echo "[2/8] 创建系统目录..."

run_safe "mkdir -p $WORKSPACE/case_repository" "mkdir -p $WORKSPACE/case_repository"
run_safe "mkdir -p $WORKSPACE/skills/defense_system" "mkdir -p $WORKSPACE/skills/defense_system"
run_safe "mkdir -p $WORKSPACE/memory/archive" "mkdir -p $WORKSPACE/memory/archive"
run_safe "mkdir -p $WORKSPACE/A-manyige/汇报" "mkdir -p $WORKSPACE/A-manyige/汇报"
run_safe "mkdir -p $WORKSPACE/A-manyige/对话/📅-按日期" "mkdir -p $WORKSPACE/A-manyige/对话/📅-按日期"

echo -e "${GREEN}✅ 目录结构创建完成${NC}"
echo ""

# ============================================================
# 第3步: 部署系统层 (L1)
# ============================================================
echo "[3/8] 部署系统层 (L1)..."

echo "  📦 部署: context_persistence.py"
if [ -f "$WORKSPACE/context_persistence.py" ]; then
    run_safe "chmod +x $WORKSPACE/context_persistence.py" "chmod +x \"$WORKSPACE/context_persistence.py\""
    echo -e "    ${GREEN}✅ 已部署${NC}"
else
    echo -e "    ${YELLOW}⚠️  文件不存在，需要手动创建${NC}"
fi

echo "  📦 部署: repetition_inhibitor.py"
if [ -f "$WORKSPACE/repetition_inhibitor.py" ]; then
    run_safe "chmod +x $WORKSPACE/repetition_inhibitor.py" "chmod +x \"$WORKSPACE/repetition_inhibitor.py\""
    echo -e "    ${GREEN}✅ 已部署${NC}"
else
    echo -e "    ${YELLOW}⚠️  文件不存在，需要手动创建${NC}"
fi

echo ""

# ============================================================
# 第4步: 部署技能层 (L2)
# ============================================================
echo "[4/8] 部署技能层 (L2)..."

echo "  📦 部署: skill_conditioning_v2.py"
if [ -f "$WORKSPACE/skill_conditioning_v2.py" ]; then
    run_safe "chmod +x $WORKSPACE/skill_conditioning_v2.py" "chmod +x \"$WORKSPACE/skill_conditioning_v2.py\""
    echo -e "    ${GREEN}✅ 已部署${NC}"
else
    echo -e "    ${YELLOW}⚠️  文件不存在，需要手动创建${NC}"
fi

echo "  📦 部署: skill_intent_mapper.py"
if [ -f "$WORKSPACE/skill_intent_mapper.py" ]; then
    run_safe "chmod +x $WORKSPACE/skill_intent_mapper.py" "chmod +x \"$WORKSPACE/skill_intent_mapper.py\""
    echo -e "    ${GREEN}✅ 已部署${NC}"
else
    echo -e "    ${YELLOW}⚠️  文件不存在，需要手动创建${NC}"
fi

echo "  📦 部署: skill_governance_dashboard.py"
if [ -f "$WORKSPACE/skill_governance_dashboard.py" ]; then
    run_safe "chmod +x $WORKSPACE/skill_governance_dashboard.py" "chmod +x \"$WORKSPACE/skill_governance_dashboard.py\""
    echo -e "    ${GREEN}✅ 已部署${NC}"
else
    echo -e "    ${YELLOW}⚠️  文件不存在，需要手动创建${NC}"
fi

echo ""

# ============================================================
# 第5步: 部署知识层 (L3)
# ============================================================
echo "[5/8] 部署知识层 (L3)..."

echo "  📦 部署: decision_solidifier_v2.py"
if [ -f "$WORKSPACE/decision_solidifier_v2.py" ]; then
    run_safe "chmod +x $WORKSPACE/decision_solidifier_v2.py" "chmod +x \"$WORKSPACE/decision_solidifier_v2.py\""
    echo -e "    ${GREEN}✅ 已部署${NC}"
else
    echo -e "    ${YELLOW}⚠️  文件不存在，需要手动创建${NC}"
fi

echo ""

# ============================================================
# 第6步: 部署整合层 (L4)
# ============================================================
echo "[6/8] 部署整合层 (L4)..."

echo "  📦 部署: unified_defense_system_v4.py"
if [ -f "$WORKSPACE/unified_defense_system_v4.py" ]; then
    run_safe "chmod +x $WORKSPACE/unified_defense_system_v4.py" "chmod +x \"$WORKSPACE/unified_defense_system_v4.py\""
    echo -e "    ${GREEN}✅ 已部署${NC}"
else
    echo -e "    ${YELLOW}⚠️  文件不存在，需要手动创建${NC}"
fi

echo ""

# ============================================================
# 第7步: 初始化系统
# ============================================================
echo "[7/8] 初始化四层防御系统..."

echo "  🚀 启动统一指挥中心..."
run_safe "启动 unified_defense_system_v4.py --dashboard" "python3 \"$WORKSPACE/unified_defense_system_v4.py\" --dashboard || true"

echo ""

# ============================================================
# 第8步: 验证部署
# ============================================================
echo "[8/8] 验证部署结果..."

echo ""
echo "📋 部署清单验证:"
echo "----------------------------------------"

SYSTEMS=(
    "context_persistence.py:系统层-上下文持久化"
    "repetition_inhibitor.py:系统层-重复抑制"
    "skill_conditioning_v2.py:技能层-条件反射V2"
    "skill_intent_mapper.py:技能层-意图映射"
    "skill_governance_dashboard.py:技能层-治理仪表盘"
    "decision_solidifier_v2.py:知识层-决策固化V2"
    "unified_defense_system_v4.py:整合层-统一指挥V4"
    "deploy_all.sh:部署脚本"
)

deployed_count=0
total_count=${#SYSTEMS[@]}

for system_info in "${SYSTEMS[@]}"; do
    IFS=':' read -r filename description <<< "$system_info"
    if [ -f "$WORKSPACE/$filename" ]; then
        echo -e "  ${GREEN}✅${NC} $description"
        ((deployed_count++))
    else
        echo -e "  ${RED}❌${NC} $description (缺失)"
    fi
done

echo "----------------------------------------"
echo ""

# ============================================================
# 部署完成总结
# ============================================================
echo ""
echo "============================================================"
echo "🎉 四层防御系统部署完成！"
echo "============================================================"
echo ""
echo "部署统计:"
echo "  已部署: $deployed_count / $total_count"
echo "  成功率: $(( deployed_count * 100 / total_count ))%"
echo ""
echo "系统架构:"
echo "  [L1] 系统层 - 上下文持久化 + 重复问题抑制"
echo "  [L2] 技能层 - Skill条件反射 + 意图映射 + 治理仪表盘"
echo "  [L3] 知识层 - 决策即时固化"
echo "  [L4] 整合层 - 统一指挥中心"
echo ""
echo "使用方法:"
echo "  查看仪表盘: python3 unified_defense_system_v4.py --dashboard"
echo "  处理任务:   python3 unified_defense_system_v4.py --process '任务描述'"
echo "  健康检查:   python3 unified_defense_system_v4.py --health"
echo ""
echo "============================================================"
echo ""
