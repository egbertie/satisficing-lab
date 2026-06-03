#!/bin/bash
################################################################################
# 满意解管理自动化 - 每月清理脚本
# 版本: V1.0
# 执行频率: 每月1日03:00
# 功能: 过期文件清理、归档压缩、备份清理
################################################################################

set -euo pipefail

# ==============================================================================
# 配置区
# ==============================================================================
WORKSPACE_ROOT="/root/.openclaw/workspace"
LOG_DIR="${WORKSPACE_ROOT}/logs/management"
REPORT_DIR="${WORKSPACE_ROOT}/reports/monthly"
TEMP_DIR="${WORKSPACE_ROOT}/05-TEMP"
ARCHIVE_DIR="${WORKSPACE_ROOT}/04-ARCHIVES"
DATE=$(date +%Y%m)
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
LOG_FILE="${LOG_DIR}/monthly-${DATE}.log"
REPORT_FILE="${REPORT_DIR}/monthly-cleanup-${DATE}.md"

# 清理配置
KEEP_DAYS_TEMP=7          # 临时文件保留天数
KEEP_DAYS_LOGS=30         # 日志保留天数
KEEP_DAYS_BACKUP_DAILY=7  # 每日备份保留天数
KEEP_DAYS_BACKUP_WEEKLY=28 # 每周备份保留天数
KEEP_DAYS_REPORTS=90      # 报告保留天数

# 大小阈值（MB）
LARGE_FILE_THRESHOLD=10

# ==============================================================================
# 工具函数
# ==============================================================================

log() {
    local level="$1"
    local message="$2"
    echo "[${TIMESTAMP}] [${level}] [MONTHLY_CLEANUP] ${message}" | tee -a "${LOG_FILE}"
}

log_info() { log "INFO" "$1"; }
log_warn() { log "WARN" "$1"; }
log_error() { log "ERROR" "$1"; }

# 统计函数
bytes_to_mb() {
    echo $(($1 / 1024 / 1024))
}

format_size() {
    local size=$1
    if [[ $size -gt 1073741824 ]]; then
        echo "$(echo "scale=2; $size/1073741824" | bc)GB"
    elif [[ $size -gt 1048576 ]]; then
        echo "$(($size / 1048576))MB"
    elif [[ $size -gt 1024 ]]; then
        echo "$(($size / 1024))KB"
    else
        echo "${size}B"
    fi
}

init() {
    mkdir -p "${LOG_DIR}" "${REPORT_DIR}" "${ARCHIVE_DIR}"
    : > "${LOG_FILE}"
    log_info "========== 每月清理开始 =========="
    log_info "清理月份: ${DATE}"
    log_info "配置: 临时文件${KEEP_DAYS_TEMP}天, 日志${KEEP_DAYS_LOGS}天"
}

# ==============================================================================
# 清理模块1: 临时文件清理
# ==============================================================================

cleanup_temp_files() {
    log_info "【清理1/7】临时文件清理..."
    
    local deleted_count=0
    local freed_space=0
    local report_section="## 1. 临时文件清理

| 文件类型 | 删除数量 | 释放空间 | 状态 |
|----------|----------|----------|------|
"
    
    # 清理05-TEMP目录
    if [[ -d "$TEMP_DIR" ]]; then
        local temp_count temp_size
        temp_count=$(find "$TEMP_DIR" -type f -mtime +${KEEP_DAYS_TEMP} 2>/dev/null | wc -l)
        temp_size=$(find "$TEMP_DIR" -type f -mtime +${KEEP_DAYS_TEMP} -exec stat -c%s {} + 2>/dev/null | awk '{sum+=$1} END {print sum}' || echo "0")
        
        if [[ $temp_count -gt 0 ]]; then
            find "$TEMP_DIR" -type f -mtime +${KEEP_DAYS_TEMP} -delete 2>/dev/null || true
            log_info "清理临时文件: ${temp_count}个, 释放$(format_size ${temp_size})"
            ((deleted_count += temp_count))
            ((freed_space += temp_size))
        fi
        
        report_section+="| 05-TEMP文件 | ${temp_count} | $(format_size ${temp_size}) | ✓ |
"
    fi
    
    # 清理各种临时文件扩展名
    local temp_patterns=("*.tmp" "*.temp" "*.swp" "*.swo" "*~" ".DS_Store" "Thumbs.db" "*.bak" "*.old")
    
    for pattern in "${temp_patterns[@]}"; do
        local count size
        count=$(find "${WORKSPACE_ROOT}" -name "$pattern" -type f -mtime +${KEEP_DAYS_TEMP} ! -path '*/node_modules/*' ! -path '*/.git/*' 2>/dev/null | wc -l)
        
        if [[ $count -gt 0 ]]; then
            size=$(find "${WORKSPACE_ROOT}" -name "$pattern" -type f -mtime +${KEEP_DAYS_TEMP} -exec stat -c%s {} + 2>/dev/null | awk '{sum+=$1} END {print sum}' || echo "0")
            find "${WORKSPACE_ROOT}" -name "$pattern" -type f -mtime +${KEEP_DAYS_TEMP} -delete 2>/dev/null || true
            log_info "清理${pattern}: ${count}个"
            ((deleted_count += count))
            ((freed_space += size))
            report_section+="| ${pattern} | ${count} | $(format_size ${size}) | ✓ |
"
        fi
    done
    
    # 清理__pycache__
    local pycache_count=0
    pycache_count=$(find "${WORKSPACE_ROOT}" -type d -name "__pycache__" 2>/dev/null | wc -l)
    if [[ $pycache_count -gt 0 ]]; then
        find "${WORKSPACE_ROOT}" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
        log_info "清理__pycache__目录: ${pycache_count}个"
        report_section+="| __pycache__ | ${pycache_count} | - | ✓ |
"
    fi
    
    if [[ $deleted_count -eq 0 ]]; then
        report_section+="| - | 0 | 0B | 无需清理 |
"
    fi
    
    echo "$report_section" >> "${REPORT_FILE}"
    
    return $freed_space
}

# ==============================================================================
# 清理模块2: 日志归档压缩
# ==============================================================================

cleanup_logs() {
    log_info "【清理2/7】日志归档压缩..."
    
    local archived_count=0
    local archived_size=0
    local report_section="## 2. 日志归档压缩

| 日志类型 | 压缩数量 | 原始大小 | 压缩后大小 | 节省空间 |
|----------|----------|----------|------------|----------|
"
    
    # 归档旧日志
    if [[ -d "${LOG_DIR}" ]]; then
        local old_logs
        old_logs=$(find "${LOG_DIR}" -name "*.log" -mtime +${KEEP_DAYS_LOGS} 2>/dev/null)
        
        if [[ -n "$old_logs" ]]; then
            local archive_name="logs-archive-$(date +%Y%m).tar.gz"
            local archive_path="${ARCHIVE_DIR}/${archive_name}"
            local total_size=0
            
            # 计算原始大小
            total_size=$(echo "$old_logs" | xargs -I{} stat -c%s {} 2>/dev/null | awk '{sum+=$1} END {print sum}' || echo "0")
            
            # 创建压缩包
            tar -czf "$archive_path" -C "${WORKSPACE_ROOT}" $(echo "$old_logs" | sed "s|${WORKSPACE_ROOT}/||g") 2>/dev/null || true
            
            # 删除原始日志
            echo "$old_logs" | xargs rm -f 2>/dev/null || true
            
            local archive_size
            archive_size=$(stat -c%s "$archive_path" 2>/dev/null || echo "0")
            local saved=$((total_size - archive_size))
            local count
            count=$(echo "$old_logs" | wc -l)
            
            log_info "归档日志: ${count}个文件, 原始$(format_size ${total_size}), 节省$(format_size ${saved})"
            report_section+="| 旧日志 | ${count} | $(format_size ${total_size}) | $(format_size ${archive_size}) | $(format_size ${saved}) |
"
            
            ((archived_count += count))
            ((archived_size += saved))
        else
            report_section+="| 旧日志 | 0 | - | - | - |
"
        fi
    fi
    
    echo "$report_section" >> "${REPORT_FILE}"
    
    return $archived_size
}

# ==============================================================================
# 清理模块3: 旧备份清理
# ==============================================================================

cleanup_backups() {
    log_info "【清理3/7】旧备份清理..."
    
    local deleted_count=0
    local freed_space=0
    local report_section="## 3. 旧备份清理

| 备份类型 | 保留策略 | 删除数量 | 释放空间 |
|----------|----------|----------|----------|
"
    
    local backup_dir="${WORKSPACE_ROOT}/backup"
    
    if [[ -d "$backup_dir" ]]; then
        # 清理旧每日备份
        if [[ -d "${backup_dir}/daily" ]]; then
            local old_daily
            old_daily=$(find "${backup_dir}/daily" -type f -mtime +${KEEP_DAYS_BACKUP_DAILY} 2>/dev/null)
            
            if [[ -n "$old_daily" ]]; then
                local count size
                count=$(echo "$old_daily" | wc -l)
                size=$(echo "$old_daily" | xargs -I{} stat -c%s {} 2>/dev/null | awk '{sum+=$1} END {print sum}' || echo "0")
                
                echo "$old_daily" | xargs rm -f 2>/dev/null || true
                log_info "清理旧每日备份: ${count}个, 释放$(format_size ${size})"
                ((deleted_count += count))
                ((freed_space += size))
                report_section+="| 每日备份 | ${KEEP_DAYS_BACKUP_DAILY}天 | ${count} | $(format_size ${size}) |
"
            else
                report_section+="| 每日备份 | ${KEEP_DAYS_BACKUP_DAILY}天 | 0 | - |
"
            fi
        fi
        
        # 清理旧每周备份
        if [[ -d "${backup_dir}/weekly" ]]; then
            local old_weekly
            old_weekly=$(find "${backup_dir}/weekly" -type f -mtime +${KEEP_DAYS_BACKUP_WEEKLY} 2>/dev/null)
            
            if [[ -n "$old_weekly" ]]; then
                local count size
                count=$(echo "$old_weekly" | wc -l)
                size=$(echo "$old_weekly" | xargs -I{} stat -c%s {} 2>/dev/null | awk '{sum+=$1} END {print sum}' || echo "0")
                
                echo "$old_weekly" | xargs rm -f 2>/dev/null || true
                log_info "清理旧每周备份: ${count}个, 释放$(format_size ${size})"
                ((deleted_count += count))
                ((freed_space += size))
                report_section+="| 每周备份 | ${KEEP_DAYS_BACKUP_WEEKLY}天 | ${count} | $(format_size ${size}) |
"
            else
                report_section+="| 每周备份 | ${KEEP_DAYS_BACKUP_WEEKLY}天 | 0 | - |
"
            fi
        fi
    else
        report_section+="| 备份目录 | - | 不存在 | - |
"
    fi
    
    echo "$report_section" >> "${REPORT_FILE}"
    
    return $freed_space
}

# ==============================================================================
# 清理模块4: 重复文件清理
# ==============================================================================

cleanup_duplicates() {
    log_info "【清理4/7】重复文件清理..."
    
    local deleted_count=0
    local freed_space=0
    local report_section="## 4. 重复文件清理

| MD5前8位 | 重复数 | 处理结果 | 释放空间 |
|----------|--------|----------|----------|
"
    
    # 查找重复文件（基于MD5）
    local temp_file
    temp_file=$(mktemp)
    
    find "${WORKSPACE_ROOT}" -type f ! -path '*/node_modules/*' ! -path '*/__pycache__/*' ! -path '*/.git/*' -size +1k 2>/dev/null | while read -r file; do
        md5sum "$file" 2>/dev/null || true
    done | sort | uniq -w32 -d > "$temp_file" 2>/dev/null || true
    
    if [[ -s "$temp_file" ]]; then
        while read -r hash file; do
            # 找出所有重复文件
            local duplicates
            duplicates=$(find "${WORKSPACE_ROOT}" -type f -exec md5sum {} + 2>/dev/null | grep "^${hash}" | cut -d' ' -f3-)
            
            local dup_count
            dup_count=$(echo "$duplicates" | wc -l)
            
            if [[ $dup_count -gt 1 ]]; then
                # 保留最新的，删除其他
                local newest
                newest=$(echo "$duplicates" | xargs -I{} stat -c '%Y %n' {} 2>/dev/null | sort -rn | head -1 | cut -d' ' -f2-)
                
                local deleted_in_group=0
                local freed_in_group=0
                
                echo "$duplicates" | while read -r dup_file; do
                    if [[ "$dup_file" != "$newest" ]]; then
                        local fsize
                        fsize=$(stat -c%s "$dup_file" 2>/dev/null || echo "0")
                        rm -f "$dup_file" 2>/dev/null || true
                        log_info "删除重复: ${dup_file}"
                        ((deleted_in_group++))
                        ((freed_in_group += fsize))
                    fi
                done
                
                ((deleted_count += deleted_in_group))
                ((freed_space += freed_in_group))
                report_section+="| ${hash:0:8}... | ${dup_count} | 保留最新 | $(format_size ${freed_in_group}) |
"
            fi
        done < "$temp_file"
    fi
    
    rm -f "$temp_file"
    
    if [[ $deleted_count -eq 0 ]]; then
        report_section+="| - | - | 无重复 | - |
"
    fi
    
    echo "$report_section" >> "${REPORT_FILE}"
    
    return $freed_space
}

# ==============================================================================
# 清理模块5: 空目录清理
# ==============================================================================

cleanup_empty_dirs() {
    log_info "【清理5/7】空目录清理..."
    
    local deleted_count=0
    local report_section="## 5. 空目录清理

| 清理范围 | 删除数量 | 状态 |
|----------|----------|------|
"
    
    # 查找并删除空目录（排除重要目录）
    local empty_dirs
    empty_dirs=$(find "${WORKSPACE_ROOT}" -type d -empty ! -path '*/node_modules/*' ! -path '*/.git/*' ! -path '*/backup/*' 2>/dev/null)
    
    if [[ -n "$empty_dirs" ]]; then
        local count
        count=$(echo "$empty_dirs" | wc -l)
        echo "$empty_dirs" | xargs -I{} rmdir {} 2>/dev/null || true
        log_info "清理空目录: ${count}个"
        ((deleted_count += count))
        report_section+="| 全工作区 | ${count} | ✓ |
"
    else
        report_section+="| 全工作区 | 0 | 无需清理 |
"
    fi
    
    echo "$report_section" >> "${REPORT_FILE}"
    
    return 0
}

# ==============================================================================
# 清理模块6: 归档文件压缩
# ==============================================================================

cleanup_archives() {
    log_info "【清理6/7】归档文件压缩..."
    
    local compressed_count=0
    local saved_space=0
    local report_section="## 6. 归档文件压缩

| 归档项 | 处理方式 | 原始大小 | 压缩后大小 | 节省空间 |
|--------|----------|----------|------------|----------|
"
    
    # 压缩超过3个月的归档目录
    if [[ -d "$ARCHIVE_DIR" ]]; then
        for dir in "${ARCHIVE_DIR}"/*/; do
            if [[ -d "$dir" ]]; then
                local dir_age
                dir_age=$(stat -c '%Y' "$dir" 2>/dev/null || echo "0")
                local current_time
                current_time=$(date +%s)
                local age_days=$(( (current_time - dir_age) / 86400 ))
                
                if [[ $age_days -gt 90 ]]; then
                    local dir_name
                    dir_name=$(basename "$dir")
                    local tar_name="${dir_name}-$(date +%Y%m).tar.gz"
                    local dir_size
                    dir_size=$(du -sb "$dir" 2>/dev/null | cut -f1)
                    
                    # 压缩目录
                    tar -czf "${ARCHIVE_DIR}/${tar_name}" -C "${ARCHIVE_DIR}" "$dir_name" 2>/dev/null || true
                    
                    local tar_size
                    tar_size=$(stat -c%s "${ARCHIVE_DIR}/${tar_name}" 2>/dev/null || echo "0")
                    local saved=$((dir_size - tar_size))
                    
                    # 删除原目录
                    rm -rf "$dir" 2>/dev/null || true
                    
                    log_info "压缩归档: ${dir_name}, 原始$(format_size ${dir_size}), 节省$(format_size ${saved})"
                    ((compressed_count++))
                    ((saved_space += saved))
                    report_section+="| ${dir_name} | tar.gz | $(format_size ${dir_size}) | $(format_size ${tar_size}) | $(format_size ${saved}) |
"
                fi
            fi
        done
    fi
    
    if [[ $compressed_count -eq 0 ]]; then
        report_section+="| - | - | - | - | 无需要压缩的归档 |
"
    fi
    
    echo "$report_section" >> "${REPORT_FILE}"
    
    return $saved_space
}

# ==============================================================================
# 清理模块7: 旧报告清理
# ==============================================================================

cleanup_reports() {
    log_info "【清理7/7】旧报告清理..."
    
    local deleted_count=0
    local freed_space=0
    local report_section="## 7. 旧报告清理

| 报告类型 | 保留天数 | 删除数量 | 释放空间 |
|----------|----------|----------|----------|
"
    
    # 清理旧日报
    local daily_report_dir="${WORKSPACE_ROOT}/reports/daily"
    if [[ -d "$daily_report_dir" ]]; then
        local old_daily
        old_daily=$(find "$daily_report_dir" -type f -mtime +${KEEP_DAYS_REPORTS} 2>/dev/null)
        
        if [[ -n "$old_daily" ]]; then
            local count size
            count=$(echo "$old_daily" | wc -l)
            size=$(echo "$old_daily" | xargs -I{} stat -c%s {} 2>/dev/null | awk '{sum+=$1} END {print sum}' || echo "0")
            
            echo "$old_daily" | xargs rm -f 2>/dev/null || true
            log_info "清理旧日报: ${count}个, 释放$(format_size ${size})"
            ((deleted_count += count))
            ((freed_space += size))
            report_section+="| 日报 | ${KEEP_DAYS_REPORTS}天 | ${count} | $(format_size ${size}) |
"
        else
            report_section+="| 日报 | ${KEEP_DAYS_REPORTS}天 | 0 | - |
"
        fi
    fi
    
    # 归档旧周报（保留最近12周）
    local weekly_report_dir="${WORKSPACE_ROOT}/reports/weekly"
    if [[ -d "$weekly_report_dir" ]]; then
        local old_weekly
        old_weekly=$(find "$weekly_report_dir" -type f -mtime +84 2>/dev/null)
        
        if [[ -n "$old_weekly" ]]; then
            # 移动到归档
            mkdir -p "${ARCHIVE_DIR}/reports"
            echo "$old_weekly" | while read -r file; do
                mv "$file" "${ARCHIVE_DIR}/reports/" 2>/dev/null || true
            done
            
            local count
            count=$(echo "$old_weekly" | wc -l)
            log_info "归档旧周报: ${count}个"
            ((deleted_count += count))
            report_section+="| 周报 | 84天 | ${count} | 已归档 |
"
        else
            report_section+="| 周报 | 84天 | 0 | - |
"
        fi
    fi
    
    echo "$report_section" >> "${REPORT_FILE}"
    
    return $freed_space
}

# ==============================================================================
# 生成完整报告
# ==============================================================================

generate_report() {
    local total_freed=$1
    local start_time=$2
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    local before_size=$3
    local after_size=$(du -sb "${WORKSPACE_ROOT}" 2>/dev/null | cut -f1)
    
    local header="# 满意解管理每月清理报告

**清理月份**: ${DATE}  
**执行时间**: $(date '+%Y-%m-%d %H:%M:%S')  
**执行时长**: ${duration}秒  
**释放空间**: $(format_size ${total_freed})

---

**目录**:
1. [临时文件清理](#1-临时文件清理)
2. [日志归档压缩](#2-日志归档压缩)
3. [旧备份清理](#3-旧备份清理)
4. [重复文件清理](#4-重复文件清理)
5. [空目录清理](#5-空目录清理)
6. [归档文件压缩](#6-归档文件压缩)
7. [旧报告清理](#7-旧报告清理)

---

"
    
    local content
    content=$(cat "${REPORT_FILE}")
    echo "${header}${content}" > "${REPORT_FILE}"
    
    # 添加总结
    cat >> "${REPORT_FILE}" << EOF

---

## 清理总结

### 空间变化

| 指标 | 数值 |
|------|------|
| 清理前总大小 | $(format_size ${before_size}) |
| 清理后总大小 | $(format_size ${after_size}) |
| 释放空间 | $(format_size ${total_freed}) |
| 空间节省率 | $(awk "BEGIN {printf \"%.2f%%\", (${total_freed}/${before_size})*100}") |

### 清理策略配置

| 项目 | 保留策略 |
|------|----------|
| 临时文件 | ${KEEP_DAYS_TEMP}天 |
| 日志文件 | ${KEEP_DAYS_LOGS}天 |
| 每日备份 | ${KEEP_DAYS_BACKUP_DAILY}天 |
| 每周备份 | ${KEEP_DAYS_BACKUP_WEEKLY}天 |
| 报告文件 | ${KEEP_DAYS_REPORTS}天 |

### 下次清理建议

- [ ] 检查存储增长趋势
- [ ] 评估是否需要调整保留策略
- [ ] 确认归档压缩率
- [ ] 验证备份完整性

---

*报告生成时间: $(date '+%Y-%m-%d %H:%M:%S')*  
*生成脚本: monthly_cleanup.sh*
EOF
    
    log_info "清理报告已生成: ${REPORT_FILE}"
}

# ==============================================================================
# 主函数
# ==============================================================================

main() {
    local start_time
    start_time=$(date +%s)
    local total_freed=0
    local before_size
    before_size=$(du -sb "${WORKSPACE_ROOT}" 2>/dev/null | cut -f1)
    
    init
    : > "${REPORT_FILE}"
    
    local freed
    
    cleanup_temp_files
    freed=$?
    ((total_freed += freed))
    
    cleanup_logs
    freed=$?
    ((total_freed += freed))
    
    cleanup_backups
    freed=$?
    ((total_freed += freed))
    
    cleanup_duplicates
    freed=$?
    ((total_freed += freed))
    
    cleanup_empty_dirs
    
    cleanup_archives
    freed=$?
    ((total_freed += freed))
    
    cleanup_reports
    freed=$?
    ((total_freed += freed))
    
    generate_report "$total_freed" "$start_time" "$before_size"
    
    log_info "========== 每月清理完成 =========="
    log_info "释放空间: $(format_size ${total_freed})"
    log_info "清理报告: ${REPORT_FILE}"
}

# 添加命令行参数支持
case "${1:-}" in
    --dry-run)
        log_info "干运行模式 - 仅显示将要清理的内容"
        # TODO: 实现干运行模式
        ;;
    --help|-h)
        echo "Usage: $0 [OPTIONS]"
        echo ""
        echo "Options:"
        echo "  --dry-run    干运行模式，不实际删除文件"
        echo "  --help, -h   显示帮助信息"
        ;;
    *)
        main
        ;;
esac
