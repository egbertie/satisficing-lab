#!/bin/bash
################################################################################
# 满意解管理自动化 - 每日检查脚本
# 版本: V1.0
# 执行频率: 每日06:00
# 功能: 全面检查文件系统、记忆、任务、安全合规性
################################################################################

set -euo pipefail

# ==============================================================================
# 配置区
# ==============================================================================
WORKSPACE_ROOT="/root/.openclaw/workspace"
LOG_DIR="${WORKSPACE_ROOT}/logs/management"
REPORT_DIR="${WORKSPACE_ROOT}/reports/daily"
CONFIG_FILE="${WORKSPACE_ROOT}/config/management.json"
DATE=$(date +%Y%m%d)
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
LOG_FILE="${LOG_DIR}/daily-${DATE}.log"
REPORT_FILE="${REPORT_DIR}/daily-report-${DATE}.md"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# ==============================================================================
# 工具函数
# ==============================================================================

log() {
    local level="$1"
    local message="$2"
    local log_entry="[${TIMESTAMP}] [${level}] [DAILY_CHECK] ${message}"
    echo -e "${log_entry}" | tee -a "${LOG_FILE}"
}

log_info() { log "INFO" "$1"; }
log_warn() { log "WARN" "$1"; }
log_error() { log "ERROR" "$1"; }

init() {
    mkdir -p "${LOG_DIR}" "${REPORT_DIR}"
    : > "${LOG_FILE}"  # 清空日志
    log_info "========== 每日检查开始 =========="
    log_info "工作目录: ${WORKSPACE_ROOT}"
    log_info "日志文件: ${LOG_FILE}"
}

# ==============================================================================
# 检查模块1: 文件命名规范
# ==============================================================================

check_naming() {
    log_info "【检查1/8】文件命名规范检查..."
    
    local issues=0
    local report_section="## 1. 文件命名规范检查

| 类型 | 违规文件 | 建议 |
|------|----------|------|
"
    
    # 检查包含emoji的文件名
    local emoji_files
    emoji_files=$(find "${WORKSPACE_ROOT}" -type f -name '*[^[:print:]]*' 2>/dev/null | head -20 || true)
    if [[ -n "$emoji_files" ]]; then
        while IFS= read -r file; do
            log_warn "发现emoji命名: ${file}"
            report_section+="| emoji命名 | ${file} | 移除emoji，使用英文字母 |
"
            ((issues++))
        done <<< "$emoji_files"
    fi
    
    # 检查包含空格的文件名
    local space_files
    space_files=$(find "${WORKSPACE_ROOT}" -type f -name '* *' ! -path '*/node_modules/*' ! -path '*/__pycache__/*' ! -path '*/.git/*' 2>/dev/null | head -20 || true)
    if [[ -n "$space_files" ]]; then
        while IFS= read -r file; do
            log_warn "发现空格命名: ${file}"
            report_section+="| 空格命名 | ${file} | 使用连字符或下划线替代 |
"
            ((issues++))
        done <<< "$space_files"
    fi
    
    # 检查中文序号的文件名
    local chinese_num_files
    chinese_num_files=$(find "${WORKSPACE_ROOT}" -type f \( -name '*一*' -o -name '*二*' -o -name '*三*' -o -name '第*' \) ! -path '*/node_modules/*' ! -path '*/__pycache__/*' 2>/dev/null | head -20 || true)
    if [[ -n "$chinese_num_files" ]]; then
        while IFS= read -r file; do
            log_warn "发现中文序号: ${file}"
            report_section+="| 中文序号 | ${file} | 使用阿拉伯数字 |
"
            ((issues++))
        done <<< "$chinese_num_files"
    fi
    
    if [[ $issues -eq 0 ]]; then
        log_info "✓ 命名规范检查通过"
        report_section+="| ✓ | 无违规 | 命名规范良好 |
"
    else
        log_warn "✗ 发现 ${issues} 个命名规范问题"
    fi
    
    echo "$report_section" >> "${REPORT_FILE}"
    return $issues
}

# ==============================================================================
# 检查模块2: 目录层级深度
# ==============================================================================

check_depth() {
    log_info "【检查2/8】目录层级深度检查..."
    
    local max_depth=4
    local deep_dirs
    local issues=0
    
    local report_section="## 2. 目录层级深度检查

| 目录 | 深度 | 建议 |
|------|------|------|
"
    
    # 查找超过4层的目录
    deep_dirs=$(find "${WORKSPACE_ROOT}" -maxdepth 10 -type d ! -path '*/node_modules/*' ! -path '*/__pycache__/*' ! -path '*/.git/*' 2>/dev/null | while read -r dir; do
        depth=$(echo "$dir" | tr '/' '\n' | wc -l)
        if [[ $depth -gt $(( $(echo "$WORKSPACE_ROOT" | tr '/' '\n' | wc -l) + $max_depth )) ]]; then
            echo "${depth}:${dir}"
        fi
    done | head -20)
    
    if [[ -n "$deep_dirs" ]]; then
        while IFS=: read -r depth dir; do
            log_warn "目录层级超标: ${dir} (深度: ${depth})"
            report_section+="| ${dir} | ${depth} | 考虑扁平化重构 |
"
            ((issues++))
        done <<< "$deep_dirs"
    fi
    
    if [[ $issues -eq 0 ]]; then
        log_info "✓ 目录层级检查通过 (最大深度: ${max_depth})"
        report_section+="| ✓ | ≤4 | 目录层级合规 |
"
    else
        log_warn "✗ 发现 ${issues} 个目录层级超标"
    fi
    
    echo "$report_section" >> "${REPORT_FILE}"
    return $issues
}

# ==============================================================================
# 检查模块3: 重复文件扫描
# ==============================================================================

check_duplicates() {
    log_info "【检查3/8】重复文件扫描..."
    
    local issues=0
    local temp_file=$(mktemp)
    
    local report_section="## 3. 重复文件扫描

| MD5 | 文件数 | 文件列表 |
|-----|--------|----------|
"
    
    # 计算文件MD5并找出重复
    find "${WORKSPACE_ROOT}" -type f ! -path '*/node_modules/*' ! -path '*/__pycache__/*' ! -path '*/.git/*' -size +0 2>/dev/null | while read -r file; do
        md5sum "$file" 2>/dev/null || true
    done | sort | uniq -w32 -d > "$temp_file"
    
    if [[ -s "$temp_file" ]]; then
        while read -r hash file; do
            local duplicates
            duplicates=$(find "${WORKSPACE_ROOT}" -type f -exec md5sum {} + 2>/dev/null | grep "^${hash}" | cut -d' ' -f3- | tr '\n' '; ')
            log_warn "发现重复文件: ${duplicates}"
            report_section+="| ${hash:0:8}... | $(echo "$duplicates" | tr ';' '\n' | wc -l) | ${duplicates:0:100}... |
"
            ((issues++))
        done < "$temp_file"
    fi
    
    rm -f "$temp_file"
    
    if [[ $issues -eq 0 ]]; then
        log_info "✓ 重复文件检查通过 (扫描了约$(find "${WORKSPACE_ROOT}" -type f 2>/dev/null | wc -l)个文件)"
        report_section+="| ✓ | - | 未发现重复文件 |
"
    else
        log_warn "✗ 发现 ${issues} 组重复文件"
    fi
    
    echo "$report_section" >> "${REPORT_FILE}"
    return $issues
}

# ==============================================================================
# 检查模块4: 空目录检测
# ==============================================================================

check_empty_dirs() {
    log_info "【检查4/8】空目录检测..."
    
    local issues=0
    local report_section="## 4. 空目录检测

| 目录路径 | 最后修改 | 建议 |
|----------|----------|------|
"
    
    local empty_dirs
    empty_dirs=$(find "${WORKSPACE_ROOT}" -type d -empty ! -path '*/node_modules/*' ! -path '*/__pycache__/*' ! -path '*/.git/*' 2>/dev/null | head -20)
    
    if [[ -n "$empty_dirs" ]]; then
        while IFS= read -r dir; do
            local mtime
            mtime=$(stat -c '%Y' "$dir" 2>/dev/null | xargs -I{} date -d @{} '+%Y-%m-%d' 2>/dev/null || echo "unknown")
            log_warn "发现空目录: ${dir}"
            report_section+="| ${dir} | ${mtime} | 删除或添加占位文件 |
"
            ((issues++))
        done <<< "$empty_dirs"
    fi
    
    if [[ $issues -eq 0 ]]; then
        log_info "✓ 空目录检查通过"
        report_section+="| ✓ | - | 无空目录 |
"
    else
        log_warn "✗ 发现 ${issues} 个空目录"
    fi
    
    echo "$report_section" >> "${REPORT_FILE}"
    return $issues
}

# ==============================================================================
# 检查模块5: 临时文件清理检查
# ==============================================================================

check_temp_files() {
    log_info "【检查5/8】临时文件清理检查..."
    
    local issues=0
    local old_files=0
    local report_section="## 5. 临时文件清理检查

| 文件类型 | 数量 | 超期文件 | 建议 |
|----------|------|----------|------|
"
    
    # 检查各种临时文件
    local temp_patterns=("*.tmp" "*.temp" "*.swp" "*.swo" "*~" ".DS_Store" "Thumbs.db")
    local total_temp=0
    
    for pattern in "${temp_patterns[@]}"; do
        local count
        count=$(find "${WORKSPACE_ROOT}" -name "$pattern" ! -path '*/node_modules/*' ! -path '*/__pycache__/*' 2>/dev/null | wc -l)
        total_temp=$((total_temp + count))
    done
    
    # 检查超过7天的临时文件
    local old_temp
    old_temp=$(find "${WORKSPACE_ROOT}" -type f \( -name "*.tmp" -o -name "*.temp" \) -mtime +7 ! -path '*/node_modules/*' 2>/dev/null | wc -l)
    
    # 检查pycache
    local pycache_dirs
    pycache_dirs=$(find "${WORKSPACE_ROOT}" -type d -name "__pycache__" 2>/dev/null | wc -l)
    
    # 检查logs目录大小
    local logs_size
    logs_size=$(du -sm "${WORKSPACE_ROOT}/logs" 2>/dev/null | cut -f1 || echo "0")
    
    report_section+="| 临时文件(*.tmp/*.temp) | ${total_temp} | ${old_temp} | 超7天文件应清理 |
"
    report_section+="| __pycache__目录 | ${pycache_dirs} | - | 可定期清理 |
"
    report_section+="| 日志目录大小 | ${logs_size}MB | - | 超100MB应归档 |
"
    
    if [[ $old_temp -gt 0 ]]; then
        log_warn "发现 ${old_temp} 个超期临时文件"
        ((issues++))
    fi
    
    if [[ $logs_size -gt 100 ]]; then
        log_warn "日志目录过大: ${logs_size}MB"
        ((issues++))
    fi
    
    if [[ $issues -eq 0 ]]; then
        log_info "✓ 临时文件检查通过"
    else
        log_warn "✗ 发现 ${issues} 个临时文件问题"
    fi
    
    echo "$report_section" >> "${REPORT_FILE}"
    return $issues
}

# ==============================================================================
# 检查模块6: 记忆文件完整性
# ==============================================================================

check_memory() {
    log_info "【检查6/8】记忆文件完整性检查..."
    
    local issues=0
    local report_section="## 6. 记忆文件完整性检查

| 检查项 | 状态 | 详情 |
|--------|------|------|
"
    
    # 检查MEMORY.md
    if [[ ! -f "${WORKSPACE_ROOT}/MEMORY.md" ]]; then
        log_error "MEMORY.md 不存在!"
        report_section+="| MEMORY.md | ❌ 缺失 | 核心记忆文件丢失 |
"
        ((issues++))
    else
        local mem_size
        mem_size=$(stat -c%s "${WORKSPACE_ROOT}/MEMORY.md" 2>/dev/null || echo "0")
        log_info "MEMORY.md 存在 (${mem_size} bytes)"
        report_section+="| MEMORY.md | ✓ 正常 | ${mem_size} bytes |
"
    fi
    
    # 检查今日记忆文件
    local today_file="${WORKSPACE_ROOT}/memory/$(date +%Y-%m-%d).md"
    if [[ ! -f "$today_file" ]]; then
        log_warn "今日记忆文件不存在: ${today_file}"
        report_section+="| 今日记忆 | ⚠️ 缺失 | ${today_file} |
"
        # 不记为严重问题，因为可能是当天未创建
    else
        report_section+="| 今日记忆 | ✓ 存在 | 已创建 |
"
    fi
    
    # 检查记忆目录结构
    if [[ ! -d "${WORKSPACE_ROOT}/memory" ]]; then
        log_error "memory目录不存在!"
        report_section+="| memory目录 | ❌ 缺失 | 记忆系统损坏 |
"
        ((issues++))
    else
        local mem_count
        mem_count=$(find "${WORKSPACE_ROOT}/memory" -type f -name "*.md" 2>/dev/null | wc -l)
        log_info "记忆文件数量: ${mem_count}"
        report_section+="| 记忆文件数 | ✓ 正常 | ${mem_count} 个文件 |
"
    fi
    
    # 检查备份
    if [[ -d "${WORKSPACE_ROOT}/.backup/memory" ]]; then
        local backup_count
        backup_count=$(find "${WORKSPACE_ROOT}/.backup/memory" -type f 2>/dev/null | wc -l)
        report_section+="| 记忆备份 | ✓ 存在 | ${backup_count} 个备份 |
"
    else
        report_section+="| 记忆备份 | ⚠️ 缺失 | 建议启用备份 |
"
    fi
    
    echo "$report_section" >> "${REPORT_FILE}"
    return $issues
}

# ==============================================================================
# 检查模块7: 任务状态检查
# ==============================================================================

check_tasks() {
    log_info "【检查7/8】任务状态检查..."
    
    local issues=0
    local report_section="## 7. 任务状态检查

| 状态 | 数量 | 需关注 |
|------|------|--------|
"
    
    # 检查任务记录文件
    local task_files
    task_files=$(find "${WORKSPACE_ROOT}" -name "*task*" -o -name "*TODO*" 2>/dev/null | head -10)
    
    # 模拟任务统计（实际应从任务系统获取）
    local pending_tasks=0
    local overdue_tasks=0
    local blocked_tasks=0
    
    # 查找可能的任务标记
    if [[ -d "${WORKSPACE_ROOT}/memory" ]]; then
        pending_tasks=$(grep -r "TODO\|FIXME\|PENDING" "${WORKSPACE_ROOT}/memory" 2>/dev/null | wc -l || echo "0")
        blocked_tasks=$(grep -r "BLOCKED\|阻塞" "${WORKSPACE_ROOT}/memory" 2>/dev/null | wc -l || echo "0")
    fi
    
    report_section+="| 待办任务 | ${pending_tasks} | - |
"
    report_section+="| 阻塞任务 | ${blocked_tasks} | $([[ $blocked_tasks -gt 0 ]] && echo "需处理" || echo "-") |
"
    report_section+="| 超期任务 | ${overdue_tasks} | - |
"
    
    if [[ $blocked_tasks -gt 0 ]]; then
        log_warn "发现 ${blocked_tasks} 个阻塞任务"
        ((issues++))
    fi
    
    log_info "✓ 任务状态检查完成"
    echo "$report_section" >> "${REPORT_FILE}"
    return $issues
}

# ==============================================================================
# 检查模块8: 安全合规检查
# ==============================================================================

check_security() {
    log_info "【检查8/8】安全合规检查..."
    
    local issues=0
    local report_section="## 8. 安全合规检查

| 检查项 | 状态 | 详情 |
|--------|------|------|
"
    
    # 检查敏感文件权限
    local secrets_dir="${WORKSPACE_ROOT}/secrets"
    if [[ -d "$secrets_dir" ]]; then
        local perms
        perms=$(stat -c '%a' "$secrets_dir" 2>/dev/null || echo "unknown")
        if [[ "$perms" != "700" ]]; then
            log_warn "secrets目录权限不正确: ${perms} (应为700)"
            report_section+="| secrets权限 | ⚠️ 警告 | 当前:${perms}, 建议:700 |
"
            ((issues++))
        else
            report_section+="| secrets权限 | ✓ 正常 | 700 |
"
        fi
    else
        report_section+="| secrets目录 | ℹ️ 不存在 | 无需检查 |
"
    fi
    
    # 检查.gitignore是否存在
    if [[ ! -f "${WORKSPACE_ROOT}/.gitignore" ]]; then
        log_warn ".gitignore 不存在"
        report_section+="| .gitignore | ⚠️ 缺失 | 建议添加 |
"
    else
        report_section+="| .gitignore | ✓ 存在 | - |
"
    fi
    
    # 检查可能的明文密码
    local password_patterns
    password_patterns=$(grep -ri "password.*=\|passwd.*=\|pwd.*=\|api_key.*=\|secret.*=" "${WORKSPACE_ROOT}" --include="*.py" --include="*.sh" --include="*.json" 2>/dev/null | grep -v "example\|sample\|template\|__pycache__" | head -10 || true)
    
    if [[ -n "$password_patterns" ]]; then
        local count
        count=$(echo "$password_patterns" | wc -l)
        log_warn "发现 ${count} 处可能的敏感信息硬编码"
        report_section+="| 敏感信息 | ⚠️ 警告 | ${count} 处需检查 |
"
        ((issues++))
    else
        report_section+="| 敏感信息 | ✓ 未检出 | - |
"
    fi
    
    echo "$report_section" >> "${REPORT_FILE}"
    return $issues
}

# ==============================================================================
# 生成报告
# ==============================================================================

generate_report() {
    local total_issues=$1
    local start_time=$2
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    # 报告头部
    local header="# 满意解管理每日检查报告

**检查日期**: $(date '+%Y-%m-%d %H:%M:%S')  
**执行时长**: ${duration}秒  
**总问题数**: ${total_issues}  
**检查结果**: $([[ $total_issues -eq 0 ]] && echo "✅ 全部通过" || echo "⚠️ 需关注")

---

**目录**:
1. [文件命名规范检查](#1-文件命名规范检查)
2. [目录层级深度检查](#2-目录层级深度检查)
3. [重复文件扫描](#3-重复文件扫描)
4. [空目录检测](#4-空目录检测)
5. [临时文件清理检查](#5-临时文件清理检查)
6. [记忆文件完整性检查](#6-记忆文件完整性检查)
7. [任务状态检查](#7-任务状态检查)
8. [安全合规检查](#8-安全合规检查)

---

"
    
    # 将头部插入报告开头
    local content
    content=$(cat "${REPORT_FILE}")
    echo "${header}${content}" > "${REPORT_FILE}"
    
    # 添加总结
    cat >> "${REPORT_FILE}" << EOF

---

## 执行摘要

| 指标 | 数值 |
|------|------|
| 检查文件总数 | $(find "${WORKSPACE_ROOT}" -type f 2>/dev/null | wc -l) |
| 检查目录总数 | $(find "${WORKSPACE_ROOT}" -type d 2>/dev/null | wc -l) |
| 发现问题总数 | ${total_issues} |
| 执行时长 | ${duration}秒 |
| 日志文件 | ${LOG_FILE} |

### 建议操作

$([[ $total_issues -eq 0 ]] && echo "- 所有检查项通过，系统运行良好" || echo "- 请查看上述问题列表，及时处理标记为❌和⚠️的项")
- 详细日志请查看: \`${LOG_FILE}\`

---

*报告生成时间: $(date '+%Y-%m-%d %H:%M:%S')*  
*生成脚本: daily_check.sh*
EOF
    
    log_info "报告已生成: ${REPORT_FILE}"
}

# ==============================================================================
# 主函数
# ==============================================================================

main() {
    local start_time
    start_time=$(date +%s)
    local total_issues=0
    
    # 初始化
    init
    
    # 创建报告文件
    : > "${REPORT_FILE}"
    
    # 执行各项检查
    check_naming || total_issues=$((total_issues + $?))
    check_depth || total_issues=$((total_issues + $?))
    check_duplicates || total_issues=$((total_issues + $?))
    check_empty_dirs || total_issues=$((total_issues + $?))
    check_temp_files || total_issues=$((total_issues + $?))
    check_memory || total_issues=$((total_issues + $?))
    check_tasks || total_issues=$((total_issues + $?))
    check_security || total_issues=$((total_issues + $?))
    
    # 生成完整报告
    generate_report "$total_issues" "$start_time"
    
    # 输出总结
    log_info "========== 每日检查完成 =========="
    log_info "发现问题总数: ${total_issues}"
    log_info "报告文件: ${REPORT_FILE}"
    
    if [[ $total_issues -eq 0 ]]; then
        log_info "✅ 所有检查通过"
        exit 0
    else
        log_warn "⚠️ 发现 ${total_issues} 个问题需要关注"
        exit 1
    fi
}

# 处理命令行参数
case "${1:-}" in
    naming)
        init
        check_naming
        ;;
    depth)
        init
        check_depth
        ;;
    duplicates)
        init
        check_duplicates
        ;;
    empty)
        init
        check_empty_dirs
        ;;
    temp)
        init
        check_temp_files
        ;;
    memory)
        init
        check_memory
        ;;
    tasks)
        init
        check_tasks
        ;;
    security)
        init
        check_security
        ;;
    *)
        main
        ;;
esac
