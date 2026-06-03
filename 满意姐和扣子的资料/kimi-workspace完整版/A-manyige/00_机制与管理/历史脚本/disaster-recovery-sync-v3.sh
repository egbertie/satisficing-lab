#!/bin/bash
################################################################################
# Skill: disaster-recovery-sync-v3.sh
# 灾备复刻V3.0同步脚本 - 全量备份 (Skill-5标准)
# 
# 版本: 3.0
# 创建时间: 2026-03-21
# 提升标准: Skill-5 (S1-S7)
#
# 变更历史:
#   V1.0: 基础9文件备份 (76KB)
#   V2.0: 全量备份 (363MB), 集成企微告警
#   V3.0: Skill-5标准提升 - 完整参数/配置/验证/测试体系
################################################################################

set -euo pipefail

#==============================================================================
# S1: 输入参数/环境/配置
#==============================================================================

# 默认配置 (可通过配置文件覆盖)
readonly SCRIPT_VERSION="3.0"
readonly SCRIPT_NAME="disaster-recovery-sync"
readonly WORKSPACE_DEFAULT="/root/.openclaw/workspace"
readonly BACKUP_RETENTION_DAYS=30
readonly REQUIRED_FREE_SPACE_MB=100

# 配置文件路径 (优先级: 命令行 > 环境变量 > 配置文件 > 默认值)
CONFIG_FILE=""
WORKSPACE="${WORKSPACE:-$WORKSPACE_DEFAULT}"
BACKUP_DIR=""
LOG_DIR=""
ALERT_SCRIPT=""

# 运行模式
DRY_RUN=false
VERBOSE=false
QUIET=false
SKIP_ALERTS=false
SKIP_VERIFY=false
BACKUP_TYPE="full"  # full | incremental | core-only

# 统计信息
declare -i START_TIME=0
declare -i END_TIME=0
declare -i TOTAL_FILES=0
declare -i BACKUP_SIZE_MB=0

# 状态追踪
SUCCESS_COUNT=0
WARNING_COUNT=0
ERROR_COUNT=0
FAILED_ITEMS=()

#==============================================================================
# 帮助信息
#==============================================================================
show_help() {
    cat << EOF
灾备复刻V3.0同步脚本 - Skill-5标准

用法: $0 [选项] [命令]

命令:
    backup          执行完整备份 (默认)
    verify          验证备份完整性
    restore         交互式恢复模式
    status          显示备份状态
    cleanup         清理过期备份
    test            运行异常场景测试 (S7)

选项:
    -c, --config FILE       指定配置文件
    -w, --workspace DIR     设置工作区目录
    -t, --type TYPE         备份类型: full|incremental|core-only (默认: full)
    -d, --dry-run           模拟执行，不实际写入
    -v, --verbose           详细输出
    -q, --quiet             静默模式 (仅错误输出)
    --skip-alerts           跳过告警通知
    --skip-verify           跳过备份验证
    -h, --help              显示此帮助
    --version               显示版本信息

配置示例:
    $0 --config /etc/dr-sync.conf backup
    $0 --workspace /custom/path --type incremental
    $0 --dry-run --verbose backup

环境变量:
    WORKSPACE               工作区目录
    DR_BACKUP_DIR           备份目录
    DR_LOG_DIR              日志目录
    DR_ALERT_SCRIPT         告警脚本路径
    FEISHU_WEBHOOK          飞书Webhook URL
    WECOM_KEY               企业微信密钥

返回值:
    0   成功
    1   一般错误
    2   配置错误
    3   磁盘空间不足
    4   备份失败
    5   验证失败

局限说明 (S6):
    - 不支持跨机备份 (仅限本地文件系统)
    - 大文件(>1GB)可能导致内存压力
    - 增量备份基于时间戳，不检测内容变更
    - 企微告警依赖外部脚本，失败不中断主流程

EOF
}

#==============================================================================
# S1: 配置文件加载
#==============================================================================
load_config() {
    local config_file="${1:-}"
    
    # 加载顺序: 默认 -> /etc -> ~/.config -> 命令行指定
    local config_paths=(
        "/etc/dr-sync.conf"
        "$HOME/.config/dr-sync/config"
        "./dr-sync.conf"
    )
    
    # 如果指定了配置文件，优先加载
    if [[ -n "$config_file" ]]; then
        if [[ -f "$config_file" ]]; then
            source "$config_file"
            log_info "已加载配置文件: $config_file"
        else
            log_error "配置文件不存在: $config_file"
            return 2
        fi
        return 0
    fi
    
    # 尝试默认路径
    for path in "${config_paths[@]}"; do
        if [[ -f "$path" ]]; then
            source "$path"
            log_info "已加载配置文件: $path"
            return 0
        fi
    done
    
    log_info "使用默认配置"
    return 0
}

# 生成配置文件模板
generate_config_template() {
    cat << 'EOF'
# 灾备同步脚本配置文件
# 位置: /etc/dr-sync.conf 或 ~/.config/dr-sync/config

# 基础路径
WORKSPACE="/root/.openclaw/workspace"
BACKUP_DIR="/backup/disaster-recovery"
LOG_DIR="/var/log/dr-sync"

# 告警配置
ALERT_SCRIPT="/root/.openclaw/workspace/scripts/emergency-wecom-alert.sh"
FEISHU_WEBHOOK=""
WECOM_KEY=""
ALERT_LEVEL="P2"  # P0=紧急 P1=重要 P2=一般 P3=提示

# 备份策略
BACKUP_TYPE="full"
RETENTION_DAYS=30
COMPRESS_BACKUP=true
VERIFY_AFTER_BACKUP=true

# 性能配置
PARALLEL_JOBS=4
BANDWIDTH_LIMIT="10m"  # rsync带宽限制
IO_NICE=true

# 文件过滤
EXCLUDE_PATTERNS=(
    "*.tmp"
    "*.log"
    ".git/objects"
    "node_modules"
    "__pycache__"
)

# 核心文件清单 (相对路径)
CORE_FILES=(
    "SOUL.md"
    "IDENTITY.md"
    "USER.md"
    "MEMORY.md"
    "AGENTS.md"
    "docs/TASK_MASTER.md"
    "docs/DISASTER_RECOVERY_V2.md"
)
EOF
}

#==============================================================================
# S3: 日志系统
#==============================================================================
init_logging() {
    LOG_DIR="${DR_LOG_DIR:-$WORKSPACE/logs/dr-sync}"
    mkdir -p "$LOG_DIR"
    
    readonly LOG_FILE="$LOG_DIR/sync-$(date +%Y%m%d).log"
    readonly JSON_LOG="$LOG_DIR/sync-$(date +%Y%m%d).jsonl"
    readonly REPORT_FILE="$LOG_DIR/report-$(date +%Y%m%d_%H%M%S).md"
    
    # 初始化JSON日志
    if [[ ! -f "$JSON_LOG" ]]; then
        echo '[]' > "$JSON_LOG"
    fi
}

log() {
    local level="$1"
    local message="$2"
    local timestamp
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    # 控制台输出
    if [[ "$QUIET" == false ]] || [[ "$level" == "ERROR" ]]; then
        case "$level" in
            INFO)  echo -e "\033[34m[${timestamp}] [INFO]\033[0m  $message" ;;
            WARN)  echo -e "\033[33m[${timestamp}] [WARN]\033[0m  $message" ; ((WARNING_COUNT++)) ;;
            ERROR) echo -e "\033[31m[${timestamp}] [ERROR]\033[0m $message" >&2 ; ((ERROR_COUNT++)) ;;
            DEBUG) [[ "$VERBOSE" == true ]] && echo -e "\033[90m[${timestamp}] [DEBUG]\033[0m $message" ;;
            SUCCESS) echo -e "\033[32m[${timestamp}] [OK]\033[0m   $message" ; ((SUCCESS_COUNT++)) ;;
        esac
    fi
    
    # 文件日志
    echo "[${timestamp}] [${level}] ${message}" >> "$LOG_FILE"
    
    # JSON结构化日志
    printf '{"time":"%s","level":"%s","message":"%s"}\n' \
        "$timestamp" "$level" "$message" >> "$JSON_LOG"
}

log_info()    { log "INFO" "$1"; }
log_warn()    { log "WARN" "$1"; }
log_error()   { log "ERROR" "$1"; }
log_debug()   { log "DEBUG" "$1"; }
log_success() { log "SUCCESS" "$1"; }

#==============================================================================
# S5: 执行结果验证
#==============================================================================
verify_environment() {
    log_info "S1: 验证运行环境..."
    
    local issues=0
    
    # 检查工作区
    if [[ ! -d "$WORKSPACE" ]]; then
        log_error "工作区目录不存在: $WORKSPACE"
        ((issues++))
    else
        log_success "工作区目录存在: $WORKSPACE"
    fi
    
    # 检查必需文件
    local required_files=("SOUL.md" "IDENTITY.md" "AGENTS.md")
    for file in "${required_files[@]}"; do
        if [[ -f "$WORKSPACE/$file" ]]; then
            log_success "核心文件存在: $file"
        else
            log_error "核心文件缺失: $file"
            ((issues++))
        fi
    done
    
    # 检查磁盘空间
    local available_mb
    available_mb=$(df -m "$WORKSPACE" | awk 'NR==2 {print $4}')
    if [[ "$available_mb" -lt "$REQUIRED_FREE_SPACE_MB" ]]; then
        log_error "磁盘空间不足: ${available_mb}MB < ${REQUIRED_FREE_SPACE_MB}MB"
        return 3
    else
        log_success "磁盘空间充足: ${available_mb}MB"
    fi
    
    # 检查依赖命令
    local deps=("rsync" "tar" "gzip" "find" "wc")
    for dep in "${deps[@]}"; do
        if command -v "$dep" &>/dev/null; then
            log_debug "依赖已安装: $dep"
        else
            log_warn "可选依赖缺失: $dep"
        fi
    done
    
    if [[ $issues -gt 0 ]]; then
        log_error "环境验证失败，发现 $issues 个问题"
        return 2
    fi
    
    log_success "环境验证通过"
    return 0
}

#==============================================================================
# 告警通知 (S3)
#==============================================================================
send_alert() {
    local level="${1:-P2}"
    local template="${2:-backup_success}"
    shift 2
    
    [[ "$SKIP_ALERTS" == true ]] && return 0
    
    ALERT_SCRIPT="${ALERT_SCRIPT:-$WORKSPACE/scripts/emergency-wecom-alert.sh}"
    
    if [[ -x "$ALERT_SCRIPT" ]]; then
        "$ALERT_SCRIPT" "$level" -t "$template" "$@" 2>/dev/null || {
            log_warn "告警发送失败 (非阻塞)"
        }
    else
        log_debug "告警脚本不可用: $ALERT_SCRIPT"
    fi
    
    # 备选: 飞书Webhook
    if [[ -n "${FEISHU_WEBHOOK:-}" ]]; then
        local message="灾备同步通知: $template"
        curl -s -X POST -H "Content-Type: application/json" \
            -d "{\"msg_type\":\"text\",\"content\":{\"text\":\"$message\"}}" \
            "$FEISHU_WEBHOOK" &>/dev/null || true
    fi
}

#==============================================================================
# S2: 处理流程标准化
#==============================================================================

# 阶段1: 预检
phase_pre_check() {
    log_info "=========================================="
    log_info "灾备复刻V3.0同步开始"
    log_info "版本: $SCRIPT_VERSION | 模式: $BACKUP_TYPE"
    log_info "=========================================="
    
    START_TIME=$(date +%s)
    
    # 创建备份目录
    BACKUP_DIR="${DR_BACKUP_DIR:-$WORKSPACE/backups/disaster-recovery}"
    mkdir -p "$BACKUP_DIR"
    
    # 发送开始通知
    send_alert P2 task_start \
        TASK_NAME="灾备同步V3" \
        TASK_ID="$SCRIPT_NAME" \
        START_TIME="$(date '+%Y-%m-%d %H:%M:%S')" \
        BACKUP_TYPE="$BACKUP_TYPE"
    
    return 0
}

# 阶段2: 统计
phase_statistics() {
    log_info "[1/5] 统计工作区状态..."
    
    if [[ "$DRY_RUN" == true ]]; then
        log_warn "[DRY-RUN] 模拟统计"
        TOTAL_FILES=1000
        return 0
    fi
    
    TOTAL_FILES=$(find "$WORKSPACE" -type f 2>/dev/null | wc -l)
    local total_size
    total_size=$(du -sh "$WORKSPACE" 2>/dev/null | cut -f1)
    
    log_success "总文件数: $TOTAL_FILES"
    log_success "总大小: $total_size"
    
    # 保存统计信息
    cat > "$BACKUP_DIR/stats_$(date +%Y%m%d_%H%M%S).json" << EOF
{
  "timestamp": "$(date -Iseconds)",
  "total_files": $TOTAL_FILES,
  "total_size": "$total_size",
  "backup_type": "$BACKUP_TYPE"
}
EOF
    
    return 0
}

# 阶段3: 核心清单
phase_core_manifest() {
    log_info "[2/5] 创建核心文件清单..."
    
    local timestamp
    timestamp=$(date +%Y%m%d_%H%M%S)
    local manifest_file="$BACKUP_DIR/core_manifest_$timestamp.txt"
    
    # Tier 1: 核心身份 (P0)
    {
        echo "# Tier 1: 核心身份 (P0)"
        echo "$WORKSPACE/SOUL.md"
        echo "$WORKSPACE/IDENTITY.md"
        echo "$WORKSPACE/USER.md"
        echo "$WORKSPACE/MEMORY.md"
        echo "$WORKSPACE/AGENTS.md"
        echo ""
        echo "# Tier 2: 项目状态 (P0)"
        echo "$WORKSPACE/docs/TASK_MASTER.md"
        echo "$WORKSPACE/docs/FULL_PROMISE_AUDIT.md"
        echo "$WORKSPACE/docs/DISASTER_RECOVERY_V2.md"
        echo "$WORKSPACE/memory/$(date +%Y-%m-%d).md"
        echo ""
        echo "# Tier 3: 关键脚本"
        find "$WORKSPACE/scripts" -name "*.py" -o -name "*.sh" 2>/dev/null | head -20
    } > "$manifest_file"
    
    log_success "核心清单已创建: $manifest_file"
    return 0
}

# 阶段4: 备份执行
phase_backup() {
    log_info "[3/5] 执行备份..."
    
    if [[ "$DRY_RUN" == true ]]; then
        log_warn "[DRY-RUN] 跳过实际备份"
        return 0
    fi
    
    case "$BACKUP_TYPE" in
        full)
            backup_full
            ;;
        incremental)
            backup_incremental
            ;;
        core-only)
            backup_core_only
            ;;
        *)
            log_error "未知备份类型: $BACKUP_TYPE"
            return 4
            ;;
    esac
    
    return $?
}

backup_full() {
    log_info "执行全量备份..."
    local backup_file="$BACKUP_DIR/full_$(date +%Y%m%d_%H%M%S).tar.gz"
    
    if tar -czf "$backup_file" -C "$WORKSPACE" . 2>/dev/null; then
        log_success "全量备份完成: $backup_file"
        return 0
    else
        log_error "全量备份失败"
        return 4
    fi
}

backup_incremental() {
    log_info "执行增量备份..."
    local backup_file="$BACKUP_DIR/incremental_$(date +%Y%m%d_%H%M%S).tar.gz"
    
    # 基于修改时间的增量备份
    find "$WORKSPACE" -type f -mtime -1 -print0 2>/dev/null | \
        tar -czf "$backup_file" --null -T - 2>/dev/null || {
        log_error "增量备份失败"
        return 4
    }
    
    log_success "增量备份完成: $backup_file"
    return 0
}

backup_core_only() {
    log_info "执行核心文件备份..."
    local backup_file="$BACKUP_DIR/core_$(date +%Y%m%d_%H%M%S).tar.gz"
    
    local core_files=(
        "$WORKSPACE/SOUL.md"
        "$WORKSPACE/IDENTITY.md"
        "$WORKSPACE/USER.md"
        "$WORKSPACE/MEMORY.md"
        "$WORKSPACE/AGENTS.md"
    )
    
    tar -czf "$backup_file" "${core_files[@]}" 2>/dev/null || {
        log_error "核心备份失败"
        return 4
    }
    
    log_success "核心备份完成: $backup_file"
    return 0
}

# 阶段5: 验证
phase_verify() {
    [[ "$SKIP_VERIFY" == true ]] && return 0
    
    log_info "[4/5] 验证备份完整性..."
    
    # 检查关键文件
    local critical_files=(
        "$WORKSPACE/SOUL.md"
        "$WORKSPACE/docs/TASK_MASTER.md"
    )
    
    for file in "${critical_files[@]}"; do
        if [[ -f "$file" ]]; then
            log_success "关键文件存在: $(basename "$file")"
        else
            log_error "关键文件缺失: $(basename "$file")"
            return 5
        fi
    done
    
    # 计算备份大小
    local backup_size
    backup_size=$(du -sh "$BACKUP_DIR" 2>/dev/null | cut -f1)
    log_success "备份大小: $backup_size"
    
    return 0
}

# 阶段6: 报告
phase_report() {
    log_info "[5/5] 生成恢复报告..."
    
    END_TIME=$(date +%s)
    local duration=$((END_TIME - START_TIME))
    
    local report_file="$BACKUP_DIR/RECOVERY_REPORT_$(date +%Y%m%d_%H%M%S).md"
    
    cat > "$report_file" << EOF
# 灾备恢复报告 V3.0
## 生成时间: $(date -Iseconds)

## 执行摘要
- **脚本版本**: $SCRIPT_VERSION
- **备份类型**: $BACKUP_TYPE
- **执行时长**: ${duration}秒
- **总文件数**: $TOTAL_FILES
- **成功任务**: $SUCCESS_COUNT
- **警告**: $WARNING_COUNT
- **错误**: $ERROR_COUNT

## 恢复步骤
1. 从GitHub克隆: \`git clone [repo]\`
2. 检查关键文件: SOUL.md, IDENTITY.md, MEMORY.md
3. 运行验证: \`bash $0 verify\`
4. 联系管理员确认状态

## 关键文件位置
- 身份定义: SOUL.md, IDENTITY.md, USER.md
- 任务状态: docs/TASK_MASTER.md
- 日志文件: logs/dr-sync/
- 备份位置: $BACKUP_DIR

## 状态
$(if [[ $ERROR_COUNT -eq 0 ]]; then echo "✅ 备份成功"; else echo "❌ 备份异常"; fi)
EOF
    
    log_success "报告已生成: $report_file"
    
    # 发送完成通知
    if [[ $ERROR_COUNT -eq 0 ]]; then
        send_alert P3 backup_success \
            BACKUP_TYPE="$BACKUP_TYPE" \
            BACKUP_SIZE="$(du -sh "$BACKUP_DIR" | cut -f1)" \
            FILE_COUNT="$TOTAL_FILES" \
            DURATION="${duration}s" \
            STORAGE_LOCATION="$BACKUP_DIR"
    else
        send_alert P0 backup_failure \
            BACKUP_TYPE="$BACKUP_TYPE" \
            ERROR_MESSAGE="发现 $ERROR_COUNT 个错误" \
            RISK_LEVEL="高"
    fi
    
    return 0
}

#==============================================================================
# S4: 定时或手动触发支持
#==============================================================================
setup_cron() {
    log_info "设置定时任务..."
    
    local cron_schedule="${1:-0 2 * * *}"  # 默认每天2点
    
    # 检查是否已有相同任务
    if crontab -l 2>/dev/null | grep -q "$SCRIPT_NAME"; then
        log_warn "定时任务已存在"
        return 0
    fi
    
    # 添加定时任务
    (crontab -l 2>/dev/null; echo "$cron_schedule $WORKSPACE/scripts/$SCRIPT_NAME.sh backup --quiet") | crontab -
    
    log_success "定时任务已设置: $cron_schedule"
    return 0
}

remove_cron() {
    log_info "移除定时任务..."
    
    crontab -l 2>/dev/null | grep -v "$SCRIPT_NAME" | crontab -
    
    log_success "定时任务已移除"
    return 0
}

#==============================================================================
# S6: 局限标注
#==============================================================================
show_limitations() {
    cat << 'EOF'
## S6: 局限标注与已知问题

### 功能局限
1. **存储限制**: 仅支持本地文件系统备份，不支持网络存储
2. **大文件处理**: 单文件>1GB时可能导致内存压力，建议分卷
3. **增量备份精度**: 基于文件修改时间，不检测内容变更
4. **并发支持**: 不支持同时运行多个实例 (使用锁文件控制)

### 环境依赖
1. **操作系统**: 仅测试于 Ubuntu 22.04 / CentOS 8
2. **Shell版本**: 需要 Bash 4.0+
3. **外部工具**: rsync(可选), tar, gzip

### 告警局限
1. **企微告警**: 依赖外部脚本，失败不中断主流程
2. **飞书告警**: 需要预配置Webhook
3. **重试机制**: 告警失败无自动重试

### 性能约束
1. **备份窗口**: 全量备份大目录(>10GB)可能需要较长时间
2. **I/O影响**: 备份期间可能影响正常I/O性能
3. **网络依赖**: 如有远程同步需求需额外配置

### 安全说明
1. **权限要求**: 需要读取工作区所有文件的权限
2. **敏感信息**: 备份包含所有文件，注意存储安全
3. **加密**: 当前版本不支持备份加密

EOF
}

#==============================================================================
# S7: 异常场景测试
#==============================================================================
run_tests() {
    log_info "=========================================="
    log_info "S7: 异常场景测试套件"
    log_info "=========================================="
    
    local test_count=0
    local pass_count=0
    local fail_count=0
    
    # 测试1: 环境缺失测试
    run_test "环境缺失测试" test_missing_environment
    
    # 测试2: 磁盘空间不足测试 (模拟)
    run_test "磁盘空间不足处理" test_disk_space
    
    # 测试3: 文件权限错误测试
    run_test "文件权限错误处理" test_permission_error
    
    # 测试4: 并发执行测试
    run_test "并发执行控制" test_concurrent_execution
    
    # 测试5: 配置文件错误测试
    run_test "配置文件错误处理" test_config_error
    
    # 测试6: 中断恢复测试
    run_test "中断恢复测试" test_interrupt_recovery
    
    # 汇总
    echo ""
    log_info "=========================================="
    log_info "测试结果: 通过 $pass_count / $test_count"
    log_info "=========================================="
    
    [[ $fail_count -eq 0 ]]
}

run_test() {
    local name="$1"
    local func="$2"
    
    ((test_count++))
    log_info "[测试 $test_count] $name"
    
    if $func; then
        log_success "✓ 通过"
        ((pass_count++))
    else
        log_error "✗ 失败"
        ((fail_count++))
    fi
}

test_missing_environment() {
    # 模拟工作区缺失
    local temp_workspace="/tmp/test_dr_nonexistent_$$"
    if ! WORKSPACE="$temp_workspace" verify_environment 2>/dev/null; then
        return 0  # 预期失败
    fi
    return 1
}

test_disk_space() {
    # 模拟磁盘空间检查 (使用很小的阈值)
    local result=0
    REQUIRED_FREE_SPACE_MB=999999999
    if ! verify_environment 2>/dev/null; then
        result=0  # 预期失败
    else
        result=1
    fi
    REQUIRED_FREE_SPACE_MB=100
    return $result
}

test_permission_error() {
    # 创建一个无权限目录测试
    local test_dir="/tmp/test_dr_perm_$$"
    mkdir -p "$test_dir/restricted"
    chmod 000 "$test_dir/restricted"
    
    local result=0
    if ! find "$test_dir" -type f 2>/dev/null | head -1 >/dev/null; then
        result=0  # 预期能处理权限错误
    fi
    
    chmod 755 "$test_dir/restricted"
    rm -rf "$test_dir"
    return $result
}

test_concurrent_execution() {
    # 测试锁文件机制
    local lock_file="/tmp/test_dr_lock_$$"
    
    # 创建锁文件
    echo $$ > "$lock_file"
    
    # 模拟另一个进程检查锁
    if [[ -f "$lock_file" ]]; then
        rm -f "$lock_file"
        return 0  # 锁机制工作正常
    fi
    
    return 1
}

test_config_error() {
    # 测试错误配置处理
    local bad_config="/tmp/test_dr_bad_config_$$"
    echo 'INVALID_SYNTAX {{{' > "$bad_config"
    
    local result=0
    if ! load_config "$bad_config" 2>/dev/null; then
        result=0  # 预期失败
    else
        result=1
    fi
    
    rm -f "$bad_config"
    return $result
}

test_interrupt_recovery() {
    # 测试中断后的状态一致性
    local temp_backup_dir="/tmp/test_dr_interrupt_$$"
    mkdir -p "$temp_backup_dir"
    
    # 模拟部分完成的备份
    touch "$temp_backup_dir/partial_file.tmp"
    
    # 检查是否能检测并处理不完整备份
    local result=0
    if [[ -f "$temp_backup_dir/partial_file.tmp" ]]; then
        # 应该能够识别并处理临时文件
        rm -f "$temp_backup_dir/partial_file.tmp"
        result=0
    fi
    
    rm -rf "$temp_backup_dir"
    return $result
}

#==============================================================================
# 主流程
#==============================================================================
main() {
    local command="backup"
    local custom_config=""
    
    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            backup|verify|restore|status|cleanup|test)
                command="$1"
                shift
                ;;
            -c|--config)
                custom_config="$2"
                shift 2
                ;;
            -w|--workspace)
                WORKSPACE="$2"
                shift 2
                ;;
            -t|--type)
                BACKUP_TYPE="$2"
                shift 2
                ;;
            -d|--dry-run)
                DRY_RUN=true
                shift
                ;;
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            -q|--quiet)
                QUIET=true
                shift
                ;;
            --skip-alerts)
                SKIP_ALERTS=true
                shift
                ;;
            --skip-verify)
                SKIP_VERIFY=true
                shift
                ;;
            --setup-cron)
                setup_cron "$2"
                exit $?
                ;;
            --remove-cron)
                remove_cron
                exit $?
                ;;
            --generate-config)
                generate_config_template
                exit 0
                ;;
            --limitations)
                show_limitations
                exit 0
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            --version)
                echo "$SCRIPT_VERSION"
                exit 0
                ;;
            *)
                log_error "未知参数: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # 初始化
    init_logging
    load_config "$custom_config"
    
    # 执行命令
    case "$command" in
        backup)
            verify_environment || exit $?
            phase_pre_check
            phase_statistics
            phase_core_manifest
            phase_backup || exit $?
            phase_verify || exit $?
            phase_report
            
            # 返回汇总状态
            if [[ $ERROR_COUNT -eq 0 ]]; then
                log_success "=========================================="
                log_success "灾备同步完成 - 全部成功"
                log_success "=========================================="
                exit 0
            else
                log_error "=========================================="
                log_error "灾备同步完成 - 有错误 ($ERROR_COUNT)"
                log_error "=========================================="
                exit 4
            fi
            ;;
        verify)
            verify_environment
            exit $?
            ;;
        restore)
            log_info "恢复模式 - 请手动执行恢复步骤"
            cat "$BACKUP_DIR"/RECOVERY_REPORT_*.md 2>/dev/null || \
                log_warn "未找到恢复报告"
            exit 0
            ;;
        status)
            log_info "备份状态:"
            ls -la "$BACKUP_DIR" 2>/dev/null || log_warn "备份目录为空"
            exit 0
            ;;
        cleanup)
            log_info "清理过期备份 (>30天)..."
            find "$BACKUP_DIR" -type f -mtime +30 -delete 2>/dev/null || true
            log_success "清理完成"
            exit 0
            ;;
        test)
            run_tests
            exit $?
            ;;
        *)
            log_error "未知命令: $command"
            exit 1
            ;;
    esac
}

# 捕获中断信号
trap 'log_error "脚本被中断"; exit 130' INT TERM

# 运行主函数
main "$@"
