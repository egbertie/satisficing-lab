#!/bin/bash
#===============================================================================
# AI灵魂复刻重建检查脚本
# 文件名: restore-checklist.sh
# 版本: V1.0
# 用途: 主控AI失效后，新AI实例的完整重建验证
# 适用项目: 满意解研究所
#===============================================================================

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 计数器
CHECKS_PASSED=0
CHECKS_FAILED=0
CHECKS_WARNING=0

# 打印函数
print_header() {
    echo ""
    echo "==================================================================="
    echo "  $1"
    echo "==================================================================="
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
    ((CHECKS_PASSED++))
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
    ((CHECKS_FAILED++))
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
    ((CHECKS_WARNING++))
}

print_info() {
    echo -e "${BLUE}[i]${NC} $1"
}

#===============================================================================
# 检查1: 工作区结构
#===============================================================================
check_workspace_structure() {
    print_header "检查1: 工作区结构完整性"
    
    REQUIRED_DIRS=(
        "docs"
        "memory"
        "scripts"
        "skills"
        "diary"
    )
    
    for dir in "${REQUIRED_DIRS[@]}"; do
        if [ -d "$dir" ]; then
            print_success "目录存在: $dir"
        else
            print_error "目录缺失: $dir"
        fi
    done
    
    # 检查灾备包目录
    if [ -d "memory/RECOVERY_PACKAGE_V1" ]; then
        print_success "灾备包目录存在: memory/RECOVERY_PACKAGE_V1"
    else
        print_warning "灾备包目录缺失: memory/RECOVERY_PACKAGE_V1"
    fi
}

#===============================================================================
# 检查2: 核心身份文件
#===============================================================================
check_identity_files() {
    print_header "检查2: 核心身份文件"
    
    REQUIRED_FILES=(
        "SOUL.md"
        "IDENTITY.md"
        "USER.md"
        "MEMORY.md"
    )
    
    for file in "${REQUIRED_FILES[@]}"; do
        if [ -f "$file" ]; then
            SIZE=$(stat -c%s "$file" 2>/dev/null || stat -f%z "$file" 2>/dev/null || echo "未知")
            print_success "文件存在: $file (${SIZE} bytes)"
        else
            print_error "文件缺失: $file"
        fi
    done
}

#===============================================================================
# 检查3: 灾备手册与脚本
#===============================================================================
check_disaster_recovery() {
    print_header "检查3: 灾备重建方案"
    
    if [ -f "docs/DISASTER_RECOVERY_V1.md" ]; then
        print_success "灾备手册存在: docs/DISASTER_RECOVERY_V1.md"
    else
        print_error "灾备手册缺失: docs/DISASTER_RECOVERY_V1.md"
    fi
    
    if [ -f "scripts/restore-checklist.sh" ]; then
        print_success "重建脚本存在: scripts/restore-checklist.sh"
    else
        print_error "重建脚本缺失: scripts/restore-checklist.sh"
    fi
}

#===============================================================================
# 检查4: 记忆文件
#===============================================================================
check_memory_files() {
    print_header "检查4: 记忆文件状态"
    
    # 查找最近的记忆文件
    LATEST_MEMORY=$(ls -1 memory/2026-*.md 2>/dev/null | sort -r | head -1)
    
    if [ -n "$LATEST_MEMORY" ]; then
        print_success "最新记忆文件: $LATEST_MEMORY"
        
        # 检查文件内容
        if grep -q "任务状态\|进度\|完成" "$LATEST_MEMORY" 2>/dev/null; then
            print_success "记忆文件包含任务状态信息"
        else
            print_warning "记忆文件可能缺少任务状态信息"
        fi
    else
        print_error "未找到记忆文件 (memory/2026-*.md)"
    fi
    
    # 统计记忆文件数量
    MEMORY_COUNT=$(ls -1 memory/2026-*.md 2>/dev/null | wc -l)
    print_info "记忆文件总数: $MEMORY_COUNT"
}

#===============================================================================
# 检查5: Git版本控制
#===============================================================================
check_git_status() {
    print_header "检查5: Git版本控制状态"
    
    if [ -d ".git" ]; then
        print_success "Git仓库已初始化"
        
        # 检查最近的提交
        LATEST_COMMIT=$(git log -1 --format="%h - %s (%ar)" 2>/dev/null || echo "无法获取")
        print_info "最新提交: $LATEST_COMMIT"
        
        # 检查未提交的更改
        if git diff-index --quiet HEAD -- 2>/dev/null; then
            print_success "工作区干净，无未提交更改"
        else
            print_warning "存在未提交的更改，建议执行: git status"
        fi
        
        # 检查远程仓库
        REMOTE_URL=$(git remote get-url origin 2>/dev/null || echo "未配置")
        if [ "$REMOTE_URL" != "未配置" ]; then
            print_success "远程仓库已配置: $REMOTE_URL"
        else
            print_warning "远程仓库未配置"
        fi
    else
        print_error "Git仓库未初始化"
    fi
}

#===============================================================================
# 检查6: 关键项目文档
#===============================================================================
check_project_docs() {
    print_header "检查6: 关键项目文档"
    
    PROJECT_DOCS=(
        "docs/MANAGEMENT_RULES.md"
        "docs/TASK_MASTER.md"
    )
    
    for doc in "${PROJECT_DOCS[@]}"; do
        if [ -f "$doc" ]; then
            print_success "文档存在: $doc"
        else
            print_warning "文档缺失: $doc"
        fi
    done
}

#===============================================================================
# 检查7: 技能目录
#===============================================================================
check_skills() {
    print_header "检查7: 技能模块"
    
    if [ -d "skills" ]; then
        SKILL_COUNT=$(ls -1 skills/ 2>/dev/null | wc -l)
        print_info "技能模块数量: $SKILL_COUNT"
        
        # 列出技能
        if [ $SKILL_COUNT -gt 0 ]; then
            echo "    已安装技能:"
            ls -1 skills/ | while read skill; do
                echo "      - $skill"
            done
        fi
    else
        print_warning "技能目录不存在"
    fi
}

#===============================================================================
# 检查8: 飞书/外部集成配置
#===============================================================================
check_external_integrations() {
    print_header "检查8: 外部集成配置"
    
    # 检查飞书配置（如果存在）
    if [ -f ".env" ]; then
        if grep -q "FEISHU" .env 2>/dev/null; then
            print_success "飞书配置存在 (.env)"
        else
            print_info "飞书配置未找到 (可能在环境变量中)"
        fi
    else
        print_info "环境文件 .env 不存在"
    fi
    
    # 检查工具配置
    print_info "工具链检查:"
    
    # 检查常用工具
    command -v python3 &>/dev/null && print_success "Python3 已安装" || print_warning "Python3 未安装"
    command -v node &>/dev/null && print_success "Node.js 已安装" || print_warning "Node.js 未安装"
    command -v git &>/dev/null && print_success "Git 已安装" || print_error "Git 未安装"
}

#===============================================================================
# 检查9: 用户与项目信息验证
#===============================================================================
check_user_project_info() {
    print_header "检查9: 用户与项目信息"
    
    if [ -f "USER.md" ]; then
        USER_NAME=$(grep -E "^\*\*Name:\*\*|^Name:" USER.md | head -1 | cut -d':' -f2- | xargs)
        if [ -n "$USER_NAME" ]; then
            print_success "用户名称: $USER_NAME"
        else
            print_warning "无法解析用户名称"
        fi
    fi
    
    if [ -f "MEMORY.md" ]; then
        PROJECT_NAME=$(grep -E "满意解研究所" MEMORY.md | head -1 | cut -d'：' -f2 | xargs)
        if [ -n "$PROJECT_NAME" ]; then
            print_success "项目名称: 满意解研究所"
        fi
        
        # 检查五路图腾
        if grep -q "五路图腾" MEMORY.md; then
            print_success "五路图腾体系已记录"
        fi
    fi
}

#===============================================================================
# 检查10: 关键任务状态摘要
#===============================================================================
check_task_status() {
    print_header "检查10: 关键任务状态摘要"
    
    print_info "从MEMORY.md提取的任务状态:"
    
    # 提取进行中任务（如果有grep可用）
    if [ -f "MEMORY.md" ]; then
        echo ""
        echo "  严重过期任务:"
        grep -E "WIP-001|WIP-003|WIP-004|WIP-005" MEMORY.md 2>/dev/null | head -5 | while read line; do
            echo "    $line"
        done || echo "    (请手动检查MEMORY.md)"
    fi
    
    echo ""
    print_info "待办事项提醒:"
    echo "  - WIP-001: V1.0蓝军意见整理 (80%, 等待附件确认)"
    echo "  - WIP-003: 五路图腾信息图制作 (30%)"
    echo "  - WIP-006: 官宣文案V1.0定稿 (截止: 2026-03-15)"
}

#===============================================================================
# 生成重建报告
#===============================================================================
generate_report() {
    print_header "重建检查完成"
    
    echo ""
    echo "  检查结果摘要:"
    echo -e "    ${GREEN}通过: $CHECKS_PASSED${NC}"
    echo -e "    ${RED}失败: $CHECKS_FAILED${NC}"
    echo -e "    ${YELLOW}警告: $CHECKS_WARNING${NC}"
    echo ""
    
    if [ $CHECKS_FAILED -eq 0 ]; then
        echo -e "  ${GREEN}✓ 重建检查全部通过！${NC}"
        echo ""
        echo "  下一步操作:"
        echo "    1. 阅读 docs/DISASTER_RECOVERY_V1.md 获取完整信息"
        echo "    2. 与Egbertie确认当前任务优先级"
        echo "    3. 开始正常工作"
        echo ""
        echo "  标准问候语:"
        echo '    "Egbertie，我已重建完成。身份确认: 满意妞，满意解研究所AI助手。等待你的指令。"'
    else
        echo -e "  ${YELLOW}! 重建检查发现问题，建议处理后再开始工作${NC}"
        echo ""
        echo "  关键问题可能包括:"
        echo "    - 核心身份文件缺失 (SOUL.md, IDENTITY.md等)"
        echo "    - Git仓库异常"
        echo "    - 记忆文件丢失"
    fi
    
    echo ""
    echo "==================================================================="
    echo "  文档版本: V1.0 | 满意解研究所 | 满意妞"
    echo "==================================================================="
}

#===============================================================================
# 主函数
#===============================================================================
main() {
    echo ""
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║         AI灵魂复刻重建检查脚本 V1.0                          ║"
    echo "║         满意解研究所 - 灾备重建方案                          ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo ""
    
    # 记录开始时间
    START_TIME=$(date +%s)
    print_info "检查开始时间: $(date '+%Y-%m-%d %H:%M:%S')"
    echo ""
    
    # 执行所有检查
    check_workspace_structure
    check_identity_files
    check_disaster_recovery
    check_memory_files
    check_git_status
    check_project_docs
    check_skills
    check_external_integrations
    check_user_project_info
    check_task_status
    
    # 生成报告
    generate_report
    
    # 记录结束时间
    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))
    echo ""
    print_info "检查耗时: ${DURATION}秒"
    echo ""
}

# 执行主函数
main "$@"
