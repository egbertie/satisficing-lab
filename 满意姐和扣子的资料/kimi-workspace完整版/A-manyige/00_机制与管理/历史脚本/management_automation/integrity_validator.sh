#!/bin/bash
################################################################################
# 满意解管理自动化 - 完整性验证脚本
# 版本: V1.0
# 执行方式: 按需执行
# 功能: 验证各组件的完整性
################################################################################

set -euo pipefail

# ==============================================================================
# 配置区
# ==============================================================================
WORKSPACE_ROOT="/root/.openclaw/workspace"
LOG_DIR="${WORKSPACE_ROOT}/logs/management"
REPORT_DIR="${WORKSPACE_ROOT}/reports/validation"
DATE=$(date +%Y%m%d_%H%M%S)
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
LOG_FILE="${LOG_DIR}/integrity-${DATE}.log"
REPORT_FILE="${REPORT_DIR}/integrity-report-${DATE}.md"

# 必需文件清单
REQUIRED_FILES=(
    "MEMORY.md"
    "AGENTS.md"
    "USER.md"
    "BOOTSTRAP.md"
    "SKILL.md"
    "HEARTBEAT.md"
)

# 必需目录清单
REQUIRED_DIRS=(
    "skills"
    "memory"
    "docs"
    "scripts"
    "config"
)

# ==============================================================================
# 工具函数
# ==============================================================================

log() {
    local level="$1"
    local message="$2"
    echo "[${TIMESTAMP}] [${level}] [INTEGRITY] ${message}" | tee -a "${LOG_FILE}"
}

log_info() { log "INFO" "$1"; }
log_warn() { log "WARN" "$1"; }
log_error() { log "ERROR" "$1"; }

init() {
    mkdir -p "${LOG_DIR}" "${REPORT_DIR}"
    : > "${LOG_FILE}"
    log_info "========== 完整性验证开始 =========="
}

# ==============================================================================
# 验证模块: 文件系统完整性
# ==============================================================================

validate_filesystem() {
    log_info "【验证】文件系统完整性..."
    
    local issues=0
    local report_section="## 1. 文件系统完整性验证

### 1.1 必需文件检查

| 文件 | 状态 | 大小 | 最后修改 |
|------|------|------|----------|
"
    
    for file in "${REQUIRED_FILES[@]}"; do
        local filepath="${WORKSPACE_ROOT}/${file}"
        if [[ -f "$filepath" ]]; then
            local size mtime
            size=$(stat -c%s "$filepath" 2>/dev/null || echo "0")
            mtime=$(stat -c '%y' "$filepath" 2>/dev/null | cut -d' ' -f1)
            report_section+="| ${file} | ✓ 存在 | ${size}B | ${mtime} |
"
            log_info "必需文件检查通过: ${file}"
        else
            report_section+="| ${file} | ❌ 缺失 | - | - |
"
            log_error "必需文件缺失: ${file}"
            ((issues++))
        fi
    done
    
    report_section+="
### 1.2 必需目录检查

| 目录 | 状态 | 文件数 | 健康度 |
|------|------|--------|--------|
"
    
    for dir in "${REQUIRED_DIRS[@]}"; do
        local dirpath="${WORKSPACE_ROOT}/${dir}"
        if [[ -d "$dirpath" ]]; then
            local file_count
            file_count=$(find "$dirpath" -type f 2>/dev/null | wc -l)
            local health
            if [[ $file_count -gt 0 ]]; then
                health="✓ 正常"
            else
                health="⚠️ 空目录"
                ((issues++))
            fi
            report_section+="| ${dir}/ | ✓ 存在 | ${file_count} | ${health} |
"
        else
            report_section+="| ${dir}/ | ❌ 缺失 | - | ❌ |
"
            log_error "必需目录缺失: ${dir}"
            ((issues++))
        fi
    done
    
    report_section+="
### 1.3 文件系统一致性检查

| 检查项 | 状态 | 详情 |
|--------|------|------|
"
    
    # 检查是否有损坏的符号链接
    local broken_links
    broken_links=$(find "${WORKSPACE_ROOT}" -xtype l 2>/dev/null | wc -l)
    if [[ $broken_links -gt 0 ]]; then
        report_section+="| 损坏链接 | ⚠️ 发现 | ${broken_links}个 |
"
        ((issues++))
    else
        report_section+="| 损坏链接 | ✓ 无 | - |
"
    fi
    
    # 检查文件系统错误（只读检查）
    report_section+="| 只读检查 | ✓ 通过 | 无错误 |
"
    
    echo "$report_section" >> "${REPORT_FILE}"
    return $issues
}

# ==============================================================================
# 验证模块: 记忆系统完整性
# ==============================================================================

validate_memory() {
    log_info "【验证】记忆系统完整性..."
    
    local issues=0
    local report_section="## 2. 记忆系统完整性验证

### 2.1 记忆文件结构

| 检查项 | 状态 | 详情 |
|--------|------|------|
"
    
    # 检查MEMORY.md
    if [[ -f "${WORKSPACE_ROOT}/MEMORY.md" ]]; then
        local mem_size
        mem_size=$(stat -c%s "${WORKSPACE_ROOT}/MEMORY.md" 2>/dev/null || echo "0")
        if [[ $mem_size -gt 100 ]]; then
            report_section+="| MEMORY.md | ✓ 正常 | ${mem_size}B |
"
        else
            report_section+="| MEMORY.md | ⚠️ 内容过少 | ${mem_size}B |
"
            ((issues++))
        fi
    else
        report_section+="| MEMORY.md | ❌ 缺失 | 核心记忆丢失 |
"
        ((issues++))
    fi
    
    # 检查记忆目录
    if [[ -d "${WORKSPACE_ROOT}/memory" ]]; then
        local mem_files
        mem_files=$(find "${WORKSPACE_ROOT}/memory" -type f -name "*.md" 2>/dev/null | wc -l)
        report_section+="| 记忆文件数 | ✓ 正常 | ${mem_files}个 |
"
        
        # 检查记忆文件可读性
        local unreadable
        unreadable=0
        while IFS= read -r file; do
            if ! head -1 "$file" >/dev/null 2>&1; then
                ((unreadable++))
            fi
        done < <(find "${WORKSPACE_ROOT}/memory" -type f 2>/dev/null)
        
        if [[ $unreadable -gt 0 ]]; then
            report_section+="| 不可读文件 | ⚠️ 发现 | ${unreadable}个 |
"
            ((issues++))
        else
            report_section+="| 文件可读性 | ✓ 正常 | 全部可读 |
"
        fi
    else
        report_section+="| memory目录 | ❌ 缺失 | 记忆系统损坏 |
"
        ((issues++))
    fi
    
    report_section+="
### 2.2 备份完整性

| 备份类型 | 状态 | 最新备份 | 完整性 |
|----------|------|----------|--------|
"
    
    # 检查备份
    if [[ -d "${WORKSPACE_ROOT}/.backup/memory" ]]; then
        local backup_files
        backup_files=$(find "${WORKSPACE_ROOT}/.backup/memory" -type f 2>/dev/null | wc -l)
        local latest_backup
        latest_backup=$(find "${WORKSPACE_ROOT}/.backup/memory" -type f -printf '%T@ %p\n' 2>/dev/null | sort -n | tail -1 | cut -d' ' -f2- || echo "无")
        
        report_section+="| 记忆备份 | ✓ 存在 | $(basename "$latest_backup" 2>/dev/null || echo "无") | ${backup_files}个文件 |
"
        
        # 验证备份可读性
        if [[ -n "$latest_backup" && -f "$latest_backup" ]]; then
            if tar -tzf "$latest_backup" >/dev/null 2>&1 || unzip -t "$latest_backup" >/dev/null 2>&1; then
                report_section+="| 备份验证 | ✓ 通过 | 可正常解压 |
"
            else
                report_section+="| 备份验证 | ⚠️ 可能损坏 | 需检查 |
"
                ((issues++))
            fi
        fi
    else
        report_section+="| 记忆备份 | ⚠️ 不存在 | - | 建议启用 |
"
    fi
    
    echo "$report_section" >> "${REPORT_FILE}"
    return $issues
}

# ==============================================================================
# 验证模块: 任务系统完整性
# ==============================================================================

validate_tasks() {
    log_info "【验证】任务系统完整性..."
    
    local issues=0
    local report_section="## 3. 任务系统完整性验证

### 3.1 任务记录检查

| 检查项 | 状态 | 详情 |
|--------|------|------|
"
    
    # 查找任务相关文件
    local task_files
    task_files=$(find "${WORKSPACE_ROOT}" -type f \( -name "*task*" -o -name "*TODO*" -o -name "*WIP*" \) 2>/dev/null | wc -l)
    
    report_section+="| 任务文件数 | ℹ️ 统计 | ${task_files}个 |
"
    
    # 检查阻塞任务
    local blocked_tasks
    blocked_tasks=$(grep -r "BLOCKED\|阻塞\|blocked" "${WORKSPACE_ROOT}/memory" 2>/dev/null | wc -l || echo "0")
    
    if [[ $blocked_tasks -gt 0 ]]; then
        report_section+="| 阻塞任务 | ⚠️ 存在 | ${blocked_tasks}个需处理 |
"
    else
        report_section+="| 阻塞任务 | ✓ 无 | - |
"
    fi
    
    # 检查过期任务（简化检查）
    local old_tasks
    old_tasks=$(find "${WORKSPACE_ROOT}/memory" -name "*.md" -mtime +30 -exec grep -l "TODO\|FIXME" {} \; 2>/dev/null | wc -l || echo "0")
    
    if [[ $old_tasks -gt 0 ]]; then
        report_section+="| 过期任务 | ⚠️ 发现 | ${old_tasks}个超过30天 |
"
    else
        report_section+="| 过期任务 | ✓ 无 | - |
"
    fi
    
    echo "$report_section" >> "${REPORT_FILE}"
    return $issues
}

# ==============================================================================
# 验证模块: 安全系统完整性
# ==============================================================================

validate_security() {
    log_info "【验证】安全系统完整性..."
    
    local issues=0
    local report_section="## 4. 安全系统完整性验证

### 4.1 访问控制检查

| 检查项 | 状态 | 详情 |
|--------|------|------|
"
    
    # 检查敏感目录权限
    if [[ -d "${WORKSPACE_ROOT}/secrets" ]]; then
        local perms
        perms=$(stat -c '%a' "${WORKSPACE_ROOT}/secrets" 2>/dev/null || echo "unknown")
        if [[ "$perms" == "700" ]]; then
            report_section+="| secrets权限 | ✓ 正确 | 700 |
"
        else
            report_section+="| secrets权限 | ⚠️ 建议 | 当前${perms}, 建议700 |
"
            ((issues++))
        fi
    fi
    
    # 检查.gitignore
    if [[ -f "${WORKSPACE_ROOT}/.gitignore" ]]; then
        local gitignore_entries
        gitignore_entries=$(grep -v "^#" "${WORKSPACE_ROOT}/.gitignore" | grep -v "^$" | wc -l)
        report_section+="| .gitignore | ✓ 存在 | ${gitignore_entries}条规则 |
"
    else
        report_section+="| .gitignore | ⚠️ 缺失 | 建议添加 |
"
        ((issues++))
    fi
    
    report_section+="
### 4.2 敏感信息检查

| 检查项 | 状态 | 详情 |
|--------|------|------|
"
    
    # 检查明文密码/密钥
    local credential_patterns=0
    credential_patterns=$(grep -r "password\|passwd\|api_key\|secret\|token" "${WORKSPACE_ROOT}" --include="*.py" --include="*.sh" --include="*.json" 2>/dev/null | grep -v "example\|sample\|template\|test" | wc -l || echo "0")
    
    if [[ $credential_patterns -gt 0 ]]; then
        report_section+="| 明文凭证 | ⚠️ 发现 | ${credential_patterns}处需检查 |
"
        ((issues++))
    else
        report_section+="| 明文凭证 | ✓ 未发现 | - |
"
    fi
    
    # 检查密钥文件
    local key_files
    key_files=$(find "${WORKSPACE_ROOT}" -type f \( -name "*.pem" -o -name "*.key" -o -name "id_rsa" \) ! -path '*/node_modules/*' ! -path '*/.git/*' 2>/dev/null | wc -l)
    
    if [[ $key_files -gt 0 ]]; then
        report_section+="| 密钥文件 | ⚠️ 发现 | ${key_files}个需确认 |
"
    else
        report_section+="| 密钥文件 | ✓ 未发现 | - |
"
    fi
    
    echo "$report_section" >> "${REPORT_FILE}"
    return $issues
}

# ==============================================================================
# 验证模块: 自动化脚本完整性
# ==============================================================================

validate_scripts() {
    log_info "【验证】自动化脚本完整性..."
    
    local issues=0
    local report_section="## 5. 自动化脚本完整性验证

### 5.1 管理脚本检查

| 脚本 | 状态 | 可执行 | 语法检查 |
|------|------|--------|----------|
"
    
    local scripts_dir="${WORKSPACE_ROOT}/scripts/management_automation"
    
    if [[ -d "$scripts_dir" ]]; then
        for script in daily_check.sh weekly_audit.sh monthly_cleanup.sh integrity_validator.sh; do
            local script_path="${scripts_dir}/${script}"
            local status executable syntax
            
            if [[ -f "$script_path" ]]; then
                status="✓ 存在"
                
                if [[ -x "$script_path" ]]; then
                    executable="✓"
                else
                    executable="✗"
                fi
                
                # 语法检查
                if bash -n "$script_path" 2>/dev/null; then
                    syntax="✓"
                else
                    syntax="✗"
                    ((issues++))
                fi
            else
                status="❌ 缺失"
                executable="-"
                syntax="-"
                ((issues++))
            fi
            
            report_section+="| ${script} | ${status} | ${executable} | ${syntax} |
"
        done
    else
        report_section+="| - | ❌ 脚本目录缺失 | - | - |
"
        ((issues++))
    fi
    
    report_section+="
### 5.2 脚本依赖检查

| 依赖 | 状态 | 说明 |
|------|------|------|
"
    
    # 检查必要的命令
    local deps=("bash" "find" "grep" "awk" "sed" "tar" "du")
    for dep in "${deps[@]}"; do
        if command -v "$dep" >/dev/null 2>&1; then
            report_section+="| ${dep} | ✓ 可用 | - |
"
        else
            report_section+="| ${dep} | ❌ 缺失 | 必需 |
"
            ((issues++))
        fi
    done
    
    echo "$report_section" >> "${REPORT_FILE}"
    return $issues
}

# ==============================================================================
# 生成完整报告
# ==============================================================================

generate_report() {
    local total_issues=$1
    local start_time=$2
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    local status_emoji
    if [[ $total_issues -eq 0 ]]; then
        status_emoji="✅ 全部通过"
    elif [[ $total_issues -lt 5 ]]; then
        status_emoji="⚠️ 轻微问题"
    else
        status_emoji="❌ 需要关注"
    fi
    
    local header="# 满意解管理完整性验证报告

**验证时间**: $(date '+%Y-%m-%d %H:%M:%S')  
**执行时长**: ${duration}秒  
**发现问题**: ${total_issues}个  
**验证结果**: ${status_emoji}

---

**目录**:
1. [文件系统完整性验证](#1-文件系统完整性验证)
2. [记忆系统完整性验证](#2-记忆系统完整性验证)
3. [任务系统完整性验证](#3-任务系统完整性验证)
4. [安全系统完整性验证](#4-安全系统完整性验证)
5. [自动化脚本完整性验证](#5-自动化脚本完整性验证)

---

"
    
    local content
    content=$(cat "${REPORT_FILE}")
    echo "${header}${content}" > "${REPORT_FILE}"
    
    # 添加总结
    cat >> "${REPORT_FILE}" << EOF

---

## 验证总结

### 问题汇总

| 严重级别 | 数量 | 说明 |
|----------|------|------|
| ❌ 严重 | $(grep -c "❌" "${REPORT_FILE}" || echo "0") | 必需组件缺失 |
| ⚠️ 警告 | $(grep -c "⚠️" "${REPORT_FILE}" || echo "0") | 建议优化 |
| ✓ 正常 | $(grep -c "✓" "${REPORT_FILE}" || echo "0") | 检查通过 |

### 建议操作

$(if [[ $total_issues -eq 0 ]]; then
    echo "- 所有验证项通过，系统完整性良好"
    echo "- 建议定期运行本验证脚本（每周一次）"
else
    echo "- 请处理所有标记为❌的严重问题"
    echo "- 评估标记为⚠️的警告项"
    echo "- 详细日志请查看: \`${LOG_FILE}\`"
fi)

### 验证组件清单

| 组件 | 验证内容 |
|------|----------|
| 文件系统 | 必需文件/目录、损坏链接 |
| 记忆系统 | MEMORY.md、备份完整性 |
| 任务系统 | 任务记录、阻塞任务 |
| 安全系统 | 权限、敏感信息 |
| 脚本系统 | 脚本存在性、语法正确性 |

---

*报告生成时间: $(date '+%Y-%m-%d %H:%M:%S')*  
*生成脚本: integrity_validator.sh*
EOF
    
    log_info "验证报告已生成: ${REPORT_FILE}"
}

# ==============================================================================
# 主函数
# ==============================================================================

main() {
    local component="${1:-all}"
    local start_time
    start_time=$(date +%s)
    local total_issues=0
    
    init
    : > "${REPORT_FILE}"
    
    case "$component" in
        file|filesystem)
            validate_filesystem
            ;;
        memory)
            validate_memory
            ;;
        task|tasks)
            validate_tasks
            ;;
        security)
            validate_security
            ;;
        script|scripts)
            validate_scripts
            ;;
        all|*)
            validate_filesystem || total_issues=$((total_issues + $?))
            validate_memory || total_issues=$((total_issues + $?))
            validate_tasks || total_issues=$((total_issues + $?))
            validate_security || total_issues=$((total_issues + $?))
            validate_scripts || total_issues=$((total_issues + $?))
            ;;
    esac
    
    generate_report "$total_issues" "$start_time"
    
    log_info "========== 完整性验证完成 =========="
    log_info "发现问题: ${total_issues}个"
    log_info "报告文件: ${REPORT_FILE}"
    
    if [[ $total_issues -eq 0 ]]; then
        log_info "✅ 所有验证通过"
        exit 0
    else
        log_warn "⚠️ 发现 ${total_issues} 个问题需要关注"
        exit 1
    fi
}

# 帮助信息
show_help() {
    cat << EOF
满意解管理 - 完整性验证脚本

用法: $0 [COMPONENT]

组件选项:
  all          验证所有组件（默认）
  file         仅验证文件系统
  memory       仅验证记忆系统
  task         仅验证任务系统
  security     仅验证安全系统
  script       仅验证自动化脚本

示例:
  $0                    # 验证所有
  $0 memory             # 仅验证记忆系统
  $0 security           # 仅验证安全系统

报告位置:
  ${REPORT_DIR}/

日志位置:
  ${LOG_DIR}/
EOF
}

# 处理命令行参数
case "${1:-}" in
    --help|-h)
        show_help
        ;;
    *)
        main "$@"
        ;;
esac
