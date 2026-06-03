#!/bin/bash
# Cron部署验证脚本
# 用法: ./scripts/verify_cron_deployment.sh [任务名]

WORKSPACE="/root/.openclaw/workspace"
LOG_DIR="$WORKSPACE/logs/cron"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 确保日志目录存在
mkdir -p "$LOG_DIR"

# 定义已部署任务
DEPLOYED_TASKS=(
    "blue_army_weekly_audit.sh"
    "punishment_enforcer.sh"
    "auto-checkpoint.sh"
    "backup_to_external.py"
    "token_monitor.py"
)

verify_task() {
    local task="$1"
    if crontab -l 2>/dev/null | grep -q "$task"; then
        echo -e "${GREEN}✅${NC} $task - 已部署到crontab"
        return 0
    else
        echo -e "${RED}❌${NC} $task - 未找到crontab条目"
        return 1
    fi
}

# 主逻辑
if [ $# -eq 1 ]; then
    # 验证单个任务
    verify_task "$1"
    exit $?
else
    # 验证所有任务
    echo "=== Cron部署验证 ==="
    echo "验证时间: $(date)"
    echo ""
    
    local passed=0
    local failed=0
    
    for task in "${DEPLOYED_TASKS[@]}"; do
        if verify_task "$task"; then
            ((passed++))
        else
            ((failed++))
        fi
    done
    
    echo ""
    echo "=== 验证结果 ==="
    echo -e "通过: ${GREEN}$passed${NC}"
    echo -e "失败: ${RED}$failed${NC}"
    echo "总计: ${#DEPLOYED_TASKS[@]}"
    
    if [ $failed -eq 0 ]; then
        echo -e "\n${GREEN}✅ 所有任务验证通过${NC}"
        exit 0
    else
        echo -e "\n${RED}❌ 发现 $failed 个未部署任务${NC}"
        exit 1
    fi
fi
