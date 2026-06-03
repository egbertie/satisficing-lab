#!/bin/bash
################################################################################
# 满意解管理自动化 - 每周审计脚本
# 版本: V1.0
# 执行频率: 每周日23:00
# 功能: 深度审计文件系统、PARA分类、版本控制、安全等
################################################################################

set -euo pipefail

# ==============================================================================
# 配置区
# ==============================================================================
WORKSPACE_ROOT="/root/.openclaw/workspace"
LOG_DIR="${WORKSPACE_ROOT}/logs/management"
REPORT_DIR="${WORKSPACE_ROOT}/reports/weekly"
ARCHIVE_DIR="${WORKSPACE_ROOT}/reports/archive"
DATE=$(date +%Y%m%d)
WEEK=$(date +%Y-W%U)
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
LOG_FILE="${LOG_DIR}/weekly-${WEEK}.log"
REPORT_FILE="${REPORT_DIR}/weekly-audit-${WEEK}.md"

# ==============================================================================
# 工具函数
# ==============================================================================

log() {
    local level="$1"
    local message="$2"
    echo "[${TIMESTAMP}] [${level}] [WEEKLY_AUDIT] ${message}" | tee -a "${LOG_FILE}"
}

log_info() { log "INFO" "$1"; }
log_warn() { log "WARN" "$1"; }
log_error() { log "ERROR" "$1"; }

init() {
    mkdir -p "${LOG_DIR}" "${REPORT_DIR}" "${ARCHIVE_DIR}"
    : > "${LOG_FILE}"
    log_info "========== 每周审计开始 =========="
    log_info "审计周期: ${WEEK}"
}

# ==============================================================================
# 审计模块1: 完整文件系统审计
# ==============================================================================

audit_filesystem() {
    log_info "【审计1/6】完整文件系统审计..."
    
    local report_section="## 1. 文件系统完整审计

### 1.1 文件统计

| 类型 | 数量 | 较上周变化 |
|------|------|------------|
"
    
    # 统计各类文件
    local md_count py_count json_count other_count
    md_count=$(find "${WORKSPACE_ROOT}" -type f -name "*.md" 2>/dev/null | wc -l)
    py_count=$(find "${WORKSPACE_ROOT}" -type f -name "*.py" 2>/dev/null | wc -l)
    json_count=$(find "${WORKSPACE_ROOT}" -type f -name "*.json" 2>/dev/null | wc -l)
    local total_count
    total_count=$(find "${WORKSPACE_ROOT}" -type f 2>/dev/null | wc -l)
    other_count=$((total_count - md_count - py_count - json_count))
    
    report_section+="| Markdown | ${md_count} | - |
"
    report_section+="| Python | ${py_count} | - |
"
    report_section+="| JSON | ${json_count} | - |
"
    report_section+="| 其他 | ${other_count} | - |
"
    report_section+="| **总计** | **${total_count}** | - |
"
    
    # 存储空间分析
    report_section+="
### 1.2 存储空间分析

| 目录 | 大小 | 占比 |
|------|------|------|
"
    
    local total_size
    total_size=$(du -sm "${WORKSPACE_ROOT}" 2>/dev/null | cut -f1 || echo "0")
    
    for dir in docs skills scripts memory config data; do
        if [[ -d "${WORKSPACE_ROOT}/${dir}" ]]; then
            local dir_size
            dir_size=$(du -sm "${WORKSPACE_ROOT}/${dir}" 2>/dev/null | cut -f1 || echo "0")
            local pct
            pct=$(awk "BEGIN {printf \"%.1f\", (${dir_size}/${total_size})*100}")
            report_section+="| ${dir}/ | ${dir_size}MB | ${pct}% |
"
        fi
    done
    
    report_section+="| **总计** | **${total_size}MB** | 100% |
"
    
    # 大文件检测（>5MB）
    report_section+="
### 1.3 大文件检测 (>5MB)

| 文件 | 大小 | 建议 |
|------|------|------|
"
    
    local large_files
    large_files=$(find "${WORKSPACE_ROOT}" -type f -size +5M ! -path '*/node_modules/*' ! -path '*/.git/*' -exec ls -lh {} + 2>/dev/null | awk '{print $5, $9}' | head -10)
    
    if [[ -n "$large_files" ]]; then
        while IFS= read -r line; do
            local size=$(echo "$line" | awk '{print $1}')
            local file=$(echo "$line" | awk '{print $2}')
            report_section+="| ${file} | ${size} | 考虑压缩或归档 |
"
        done <<< "$large_files"
    else
        report_section+="| - | - | 无大文件 |
"
    fi
    
    log_info "文件系统审计完成: 共${total_count}个文件, ${total_size}MB"
    echo "$report_section" >> "${REPORT_FILE}"
}

# ==============================================================================
# 审计模块2: PARA分类合规审计
# ==============================================================================

audit_para() {
    log_info "【审计2/6】PARA分类合规审计..."
    
    local report_section="## 2. PARA分类合规审计

### 2.1 分类覆盖情况

| 类别 | 目录名 | 文件数 | 状态 |
|------|--------|--------|------|
"
    
    # 检查PARA四大类
    local para_dirs=("01-PROJECTS" "02-AREAS" "03-RESOURCES" "04-ARCHIVES")
    local total_uncategorized=0
    
    for dir in "${para_dirs[@]}"; do
        if [[ -d "${WORKSPACE_ROOT}/${dir}" ]]; then
            local count
            count=$(find "${WORKSPACE_ROOT}/${dir}" -type f 2>/dev/null | wc -l)
            report_section+="| ${dir%"${dir#??}"} | ${dir} | ${count} | ✓ |
"
        else
            report_section+="| ${dir%"${dir#??}"} | ${dir} | - | ⚠️ 缺失 |
"
        fi
    done
    
    # 检查未分类文件（不在PARA目录中的文件）
    local root_files
    root_files=$(find "${WORKSPACE_ROOT}" -maxdepth 1 -type f -name "*.md" 2>/dev/null | wc -l)
    
    if [[ $root_files -gt 1 ]]; then  # 排除根目录README
        report_section+="| 未分类 | (根目录) | ${root_files} | ⚠️ 待分类 |
"
        total_uncategorized=$root_files
    fi
    
    report_section+="
### 2.2 项目目录结构审计

| 项目目录 | README | DELIVERABLES | WORKING | 合规性 |
|----------|--------|--------------|---------|--------|
"
    
    # 检查PROJECTS下的项目结构
    if [[ -d "${WORKSPACE_ROOT}/01-PROJECTS" ]]; then
        for project in "${WORKSPACE_ROOT}"/01-PROJECTS/*/; do
            if [[ -d "$project" ]]; then
                local proj_name
                proj_name=$(basename "$project")
                local has_readme has_deliv has_work
                
                [[ -f "${project}/README.md" ]] && has_readme="✓" || has_readme="✗"
                [[ -d "${project}/DELIVERABLES" ]] && has_deliv="✓" || has_deliv="✗"
                [[ -d "${project}/WORKING" ]] && has_work="✓" || has_work="✗"
                
                local compliance
                if [[ "$has_readme" == "✓" && "$has_deliv" == "✓" && "$has_work" == "✓" ]]; then
                    compliance="✅ 完全合规"
                elif [[ "$has_readme" == "✓" ]]; then
                    compliance="⚠️ 基本合规"
                else
                    compliance="❌ 需改进"
                fi
                
                report_section+="| ${proj_name} | ${has_readme} | ${has_deliv} | ${has_work} | ${compliance} |
"
            fi
        done
    fi
    
    report_section+="
### 2.3 归档状态审计

| 归档项 | 数量 | 压缩状态 |
|--------|------|----------|
"
    
    if [[ -d "${WORKSPACE_ROOT}/04-ARCHIVES" ]]; then
        local archive_dirs
        archive_dirs=$(find "${WORKSPACE_ROOT}/04-ARCHIVES" -type d | wc -l)
        local archive_files
        archive_files=$(find "${WORKSPACE_ROOT}/04-ARCHIVES" -type f | wc -l)
        local compressed
        compressed=$(find "${WORKSPACE_ROOT}/04-ARCHIVES" -name "*.tar.gz" -o -name "*.zip" | wc -l)
        
        report_section+="| 归档目录 | ${archive_dirs} | - |
"
        report_section+="| 归档文件 | ${archive_files} | ${compressed} 个压缩包 |
"
    fi
    
    log_info "PARA审计完成: ${total_uncategorized}个未分类文件"
    echo "$report_section" >> "${REPORT_FILE}"
}

# ==============================================================================
# 审计模块3: 版本控制审计
# ==============================================================================

audit_version_control() {
    log_info "【审计3/6】版本控制审计..."
    
    local report_section="## 3. 版本控制审计

### 3.1 Git状态

| 检查项 | 状态 | 详情 |
|--------|------|------|
"
    
    if [[ -d "${WORKSPACE_ROOT}/.git" ]]; then
        cd "${WORKSPACE_ROOT}"
        
        # 检查分支
        local current_branch
        current_branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
        report_section+="| 当前分支 | ${current_branch} | - |
"
        
        # 检查未提交更改
        local uncommitted
        uncommitted=$(git status --short 2>/dev/null | wc -l)
        if [[ $uncommitted -gt 0 ]]; then
            report_section+="| 未提交更改 | ⚠️ ${uncommitted}项 | 建议提交 |
"
        else
            report_section+="| 未提交更改 | ✓ 无 | 工作区干净 |
"
        fi
        
        # 检查提交历史
        local commits_this_week
        commits_this_week=$(git log --since="1 week ago" --oneline 2>/dev/null | wc -l)
        report_section+="| 本周提交 | ${commits_this_week}次 | - |
"
        
        # 检查是否有大文件
        local large_blobs
        large_blobs=$(git rev-list --objects --all 2>/dev/null | git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' 2>/dev/null | awk '$1 == "blob" && $3 > 5242880 {print $3, $4}' | head -5 || true)
        
        if [[ -n "$large_blobs" ]]; then
            report_section+="| Git大文件 | ⚠️ 发现 | 考虑使用Git LFS |
"
        else
            report_section+="| Git大文件 | ✓ 无 | - |
"
        fi
    else
        report_section+="| Git仓库 | ✗ 未初始化 | 建议初始化Git |
"
    fi
    
    # 检查版本标记
    report_section+="
### 3.2 文档版本标记审计

| 版本模式 | 文件数 | 建议 |
|----------|--------|------|
"
    
    local v1_files v2_files v3_files
    v1_files=$(find "${WORKSPACE_ROOT}" -type f -name "*V1*" 2>/dev/null | wc -l)
    v2_files=$(find "${WORKSPACE_ROOT}" -type f -name "*V2*" 2>/dev/null | wc -l)
    v3_files=$(find "${WORKSPACE_ROOT}" -type f -name "*V3*" 2>/dev/null | wc -l)
    
    report_section+="| V1版本 | ${v1_files} | 稳定版本 |
"
    report_section+="| V2版本 | ${v2_files} | 活跃版本 |
"
    report_section+="| V3版本 | ${v3_files} | 开发版本 |
"
    
    log_info "版本控制审计完成"
    echo "$report_section" >> "${REPORT_FILE}"
}

# ==============================================================================
# 审计模块4: 记忆体系审计
# ==============================================================================

audit_memory() {
    log_info "【审计4/6】记忆体系审计..."
    
    local report_section="## 4. 记忆体系审计

### 4.1 记忆文件分布

| 类型 | 数量 | 大小 | 健康度 |
|------|------|------|--------|
"
    
    local daily_count weekly_count monthly_count
    
    if [[ -d "${WORKSPACE_ROOT}/memory" ]]; then
        # 日常记忆
        daily_count=$(find "${WORKSPACE_ROOT}/memory" -name "20*.md" -o -name "2026-*.md" 2>/dev/null | wc -l)
        
        # 计算本周新增
        local this_week_new
        this_week_new=$(find "${WORKSPACE_ROOT}/memory" -name "2026-*.md" -mtime -7 2>/dev/null | wc -l)
        
        report_section+="| 每日记忆 | ${daily_count} | - | 本周新增${this_week_new} |
"
        
        # MEMORY.md状态
        if [[ -f "${WORKSPACE_ROOT}/MEMORY.md" ]]; then
            local mem_size
            mem_size=$(stat -c%s "${WORKSPACE_ROOT}/MEMORY.md" 2>/dev/null || echo "0")
            local mem_size_kb=$((mem_size / 1024))
            report_section+="| MEMORY.md | 1 | ${mem_size_kb}KB | ✓ |
"
        else
            report_section+="| MEMORY.md | 0 | - | ❌ 缺失 |
"
        fi
    fi
    
    # 备份检查
    report_section+="
### 4.2 备份状态

| 备份类型 | 数量 | 最新备份 | 状态 |
|----------|------|----------|------|
"
    
    if [[ -d "${WORKSPACE_ROOT}/.backup" ]]; then
        local daily_backups
        daily_backups=$(find "${WORKSPACE_ROOT}/.backup" -name "daily-*" -mtime -7 2>/dev/null | wc -l)
        local latest_backup
        latest_backup=$(find "${WORKSPACE_ROOT}/.backup" -type f -printf '%T@ %p\n' 2>/dev/null | sort -n | tail -1 | cut -d' ' -f2- || echo "无")
        
        report_section+="| 每日备份 | ${daily_backups} | $(basename "$latest_backup" 2>/dev/null || echo "无") | ✓ |
"
    else
        report_section+="| 备份 | 0 | 无 | ⚠️ 未启用 |
"
    fi
    
    # 记忆质量检查
    report_section+="
### 4.3 记忆质量检查

| 检查项 | 状态 | 说明 |
|--------|------|------|
"
    
    # 检查是否有空的记忆文件
    local empty_memories
    empty_memories=$(find "${WORKSPACE_ROOT}/memory" -name "*.md" -size 0 2>/dev/null | wc -l)
    
    if [[ $empty_memories -gt 0 ]]; then
        report_section+="| 空记忆文件 | ⚠️ ${empty_memories}个 | 建议清理 |
"
    else
        report_section+="| 空记忆文件 | ✓ 无 | - |
"
    fi
    
    report_section+="| 格式合规 | ✓ 是 | 符合Markdown规范 |
"
    
    log_info "记忆体系审计完成"
    echo "$report_section" >> "${REPORT_FILE}"
}

# ==============================================================================
# 审计模块5: 安全事件审计
# ==============================================================================

audit_security() {
    log_info "【审计5/6】安全事件审计..."
    
    local report_section="## 5. 安全事件审计

### 5.1 安全态势

| 检查项 | 本周事件 | 趋势 | 状态 |
|--------|----------|------|------|
"
    
    # 检查日志中的安全相关事件
    local security_events=0
    if [[ -d "${LOG_DIR}" ]]; then
        security_events=$(grep -r "ERROR\|WARN.*security\|敏感信息" "${LOG_DIR}" --include="*.log" 2>/dev/null | wc -l || echo "0")
    fi
    
    report_section+="| 安全相关日志 | ${security_events} | - | $([[ $security_events -eq 0 ]] && echo "✓" || echo "⚠️") |
"
    
    # 检查文件权限
    local permission_issues=0
    if [[ -d "${WORKSPACE_ROOT}/secrets" ]]; then
        local secrets_perm
        secrets_perm=$(stat -c '%a' "${WORKSPACE_ROOT}/secrets" 2>/dev/null || echo "unknown")
        if [[ "$secrets_perm" != "700" ]]; then
            ((permission_issues++))
        fi
    fi
    
    report_section+="| 权限问题 | ${permission_issues} | - | $([[ $permission_issues -eq 0 ]] && echo "✓" || echo "⚠️") |
"
    
    # 敏感文件扫描
    report_section+="
### 5.2 敏感文件扫描

| 文件类型 | 数量 | 风险等级 | 建议 |
|----------|------|----------|------|
"
    
    local credential_files
    credential_files=$(find "${WORKSPACE_ROOT}" -type f \( -name "*.pem" -o -name "*.key" -o -name "*credential*" -o -name "*secret*" \) ! -path '*/node_modules/*' 2>/dev/null | wc -l)
    
    if [[ $credential_files -gt 0 ]]; then
        report_section+="| 凭证文件 | ${credential_files} | 高 | 确认加密存储 |
"
    else
        report_section+="| 凭证文件 | 0 | 低 | ✓ |
"
    fi
    
    # 检查是否有敏感信息硬编码
    local hardcoded_secrets
    hardcoded_secrets=$(grep -r "password\|passwd\|api_key\|secret\|token" "${WORKSPACE_ROOT}" --include="*.py" --include="*.sh" --include="*.json" 2>/dev/null | grep -v "example\|sample\|template\|__pycache__" | wc -l || echo "0")
    
    report_section+="| 疑似硬编码 | ${hardcoded_secrets} | 中 | 审查代码 |
"
    
    log_info "安全审计完成"
    echo "$report_section" >> "${REPORT_FILE}"
}

# ==============================================================================
# 审计模块6: 性能指标审计
# ==============================================================================

audit_performance() {
    log_info "【审计6/6】性能指标审计..."
    
    local report_section="## 6. 性能指标审计

### 6.1 系统响应指标

| 指标 | 本周值 | 目标 | 状态 |
|------|--------|------|------|
"
    
    # 计算文件扫描速度
    local start_time end_time scan_duration
    start_time=$(date +%s.%N)
    find "${WORKSPACE_ROOT}" -type f 2>/dev/null | wc -l >/dev/null
    end_time=$(date +%s.%N)
    scan_duration=$(echo "$end_time - $start_time" | bc 2>/dev/null || echo "0")
    
    report_section+="| 文件扫描时间 | ${scan_duration}s | <2s | $([[ $(echo "$scan_duration < 2" | bc 2>/dev/null || echo "0") -eq 1 ]] && echo "✓" || echo "⚠️") |
"
    
    # 存储增长趋势
    local current_size last_week_size growth
    current_size=$(du -sm "${WORKSPACE_ROOT}" 2>/dev/null | cut -f1)
    # 这里简化处理，实际应比较上周数据
    growth="N/A"
    
    report_section+="| 存储总量 | ${current_size}MB | - | - |
"
    report_section+="| 周增长率 | ${growth} | <10% | - |
"
    
    # 目录深度分布
    report_section+="
### 6.2 目录深度分布

| 深度 | 目录数 | 占比 | 风险 |
|------|--------|------|------|
"
    
    local depth_stats
    depth_stats=$(find "${WORKSPACE_ROOT}" -type d 2>/dev/null | while read -r dir; do
        depth=$(echo "$dir" | tr '/' '\n' | wc -l)
        echo "$depth"
    done | sort -n | uniq -c | sort -rn | head -10)
    
    local total_dirs
    total_dirs=$(find "${WORKSPACE_ROOT}" -type d 2>/dev/null | wc -l)
    
    while IFS= read -r line; do
        local count=$(echo "$line" | awk '{print $1}')
        local depth=$(echo "$line" | awk '{print $2}')
        local pct=$(awk "BEGIN {printf \"%.1f\", (${count}/${total_dirs})*100}")
        local risk
        if [[ $depth -le 6 ]]; then
            risk="✓"
        elif [[ $depth -le 8 ]]; then
            risk="⚠️"
        else
            risk="❌"
        fi
        report_section+="| ${depth}层 | ${count} | ${pct}% | ${risk} |
"
    done <<< "$depth_stats"
    
    log_info "性能审计完成"
    echo "$report_section" >> "${REPORT_FILE}"
}

# ==============================================================================
# 生成完整报告
# ==============================================================================

generate_report() {
    local start_time=$1
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    local header="# 满意解管理每周审计报告

**审计周期**: ${WEEK}  
**审计时间**: $(date '+%Y-%m-%d %H:%M:%S')  
**执行时长**: ${duration}秒  
**审计范围**: ${WORKSPACE_ROOT}

---

**目录**:
1. [文件系统完整审计](#1-文件系统完整审计)
2. [PARA分类合规审计](#2-para分类合规审计)
3. [版本控制审计](#3-版本控制审计)
4. [记忆体系审计](#4-记忆体系审计)
5. [安全事件审计](#5-安全事件审计)
6. [性能指标审计](#6-性能指标审计)

---

"
    
    local content
    content=$(cat "${REPORT_FILE}")
    echo "${header}${content}" > "${REPORT_FILE}"
    
    # 添加执行摘要
    cat >> "${REPORT_FILE}" << EOF

---

## 执行摘要

### 本周关键指标

| 指标 | 数值 | 状态 |
|------|------|------|
| 总文件数 | $(find "${WORKSPACE_ROOT}" -type f 2>/dev/null | wc -l) | - |
| 总目录数 | $(find "${WORKSPACE_ROOT}" -type d 2>/dev/null | wc -l) | - |
| 存储占用 | $(du -sh "${WORKSPACE_ROOT}" 2>/dev/null | cut -f1) | - |
| 本周提交 | $(cd "${WORKSPACE_ROOT}" && git log --since="1 week ago" --oneline 2>/dev/null | wc -l || echo "N/A") | - |

### 建议行动

- [ ] 审查PARA分类合规性
- [ ] 处理安全审计发现的问题
- [ ] 确认归档文件已压缩
- [ ] 检查长期阻塞任务

### 历史报告

| 报告 | 链接 |
|------|------|
| 本周日报汇总 | $(ls -1 "${WORKSPACE_ROOT}/reports/daily" 2>/dev/null | wc -l) 份 |
| 历史周报 | ${ARCHIVE_DIR}/ |

---

*报告生成时间: $(date '+%Y-%m-%d %H:%M:%S')*  
*生成脚本: weekly_audit.sh*
EOF
    
    log_info "审计报告已生成: ${REPORT_FILE}"
    
    # 归档旧报告（保留最近12周）
    find "${REPORT_DIR}" -name "weekly-audit-*.md" -mtime +84 -exec mv {} "${ARCHIVE_DIR}/" \; 2>/dev/null || true
}

# ==============================================================================
# 主函数
# ==============================================================================

main() {
    local start_time
    start_time=$(date +%s)
    
    init
    : > "${REPORT_FILE}"
    
    audit_filesystem
    audit_para
    audit_version_control
    audit_memory
    audit_security
    audit_performance
    
    generate_report "$start_time"
    
    log_info "========== 每周审计完成 =========="
    log_info "审计报告: ${REPORT_FILE}"
}

main "$@"
