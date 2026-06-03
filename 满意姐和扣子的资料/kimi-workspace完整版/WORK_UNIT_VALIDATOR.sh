#!/bin/bash
# WORK_UNIT_VALIDATOR.sh - 工作单元验证器
# 功能: 每个工作单元执行前自动验证，确保不遗漏关键步骤
# 创建时间: 2026-04-04
# 版本: 1.0

set -euo pipefail

# 配置
VALIDATOR_DB="/root/.openclaw/workspace/.work_units"
VALIDATOR_LOG="/root/.openclaw/workspace/.validator_log"
CHECKSUM_DIR="/root/.openclay/workspace/.unit_checksums"

mkdir -p "$VALIDATOR_DB" "$CHECKSUM_DIR"

# 日志
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$VALIDATOR_LOG"
}

# 定义标准工作单元（文件处理7步法）
define_file_processing_unit() {
    local unit_id="FILE_PROC_7STEP"
    
    cat > "$VALIDATOR_DB/${unit_id}.json" << 'EOF'
{
    "unit_name": "文件处理7步法",
    "unit_id": "FILE_PROC_7STEP",
    "version": "1.0",
    "mandatory_steps": [
        {
            "step_id": "S0",
            "name": "前置确认",
            "checks": ["文件存在性", "文件类型", "序号确认", "上一文件闭环"],
            "block_if_fail": true
        },
        {
            "step_id": "S1", 
            "name": "全量提取",
            "checks": ["内容提取完整", "段落数统计", "字符数统计"],
            "block_if_fail": true
        },
        {
            "step_id": "S2",
            "name": "深度洞察",
            "checks": ["核心内容识别", "架构提取", "关键点标记"],
            "block_if_fail": false
        },
        {
            "step_id": "S3",
            "name": "实际实施",
            "checks": ["方案识别", "实施状态标注", "缺口识别"],
            "block_if_fail": false
        },
        {
            "step_id": "S4",
            "name": "条件记录",
            "checks": ["技术债务识别", "依赖关系记录"],
            "block_if_fail": false
        },
        {
            "step_id": "S5",
            "name": "资产整合",
            "checks": ["知识提取", "资产归档"],
            "block_if_fail": false
        },
        {
            "step_id": "S6",
            "name": "任务登记",
            "checks": ["报告生成", "记忆更新", "用户确认"],
            "block_if_fail": true
        }
    ],
    "block_rules": {
        "skip_mandatory": false,
        "partial_completion_warning": true
    }
}
EOF
    
    log "UNIT_DEFINED: $unit_id 已定义"
}

# 开始一个工作单元实例
start_unit() {
    local unit_id="$1"
    local instance_id="${2:-$(date +%s)}"
    
    local instance_file="$VALIDATOR_DB/${unit_id}_${instance_id}.running"
    
    cat > "$instance_file" << EOF
{
    "unit_id": "$unit_id",
    "instance_id": "$instance_id",
    "start_time": "$(date '+%Y-%m-%d %H:%M:%S')",
    "status": "RUNNING",
    "completed_steps": [],
    "current_step": null,
    "validation_results": {}
}
EOF
    
    log "UNIT_STARTED: $unit_id instance $instance_id"
    echo "$instance_id"
}

# 报告步骤完成
complete_step() {
    local unit_id="$1"
    local instance_id="$2"
    local step_id="$3"
    local result="${4:-PASS}"
    local notes="${5:-}"
    
    local instance_file="$VALIDATOR_DB/${unit_id}_${instance_id}.running"
    
    if [[ ! -f "$instance_file" ]]; then
        log "ERROR: 实例不存在 $unit_id $instance_id"
        return 1
    fi
    
    # 更新JSON（简化处理，实际应该用jq）
    local temp_file
    temp_file=$(mktemp)
    
    # 添加步骤完成记录
    echo "STEP_COMPLETED: $step_id - $result - $notes" >> "$instance_file.log"
    
    log "STEP_COMPLETE: $step_id = $result"
    
    # 如果关键步骤失败，触发熔断
    if [[ "$result" == "FAIL" ]]; then
        local step_def
        step_def=$(grep -A5 "\"step_id\": \"$step_id\"" "$VALIDATOR_DB/${unit_id}.json" 2>/dev/null || true)
        
        if echo "$step_def" | grep -q '"block_if_fail": true'; then
            log "BLOCKING_STEP_FAIL: $step_id 为强制步骤，失败即阻断"
            
            # 调用熔断器
            if [[ -x ./CIRCUIT_BREAKER.sh ]]; then
                ./CIRCUIT_BREAKER.sh error "STEP_FAIL_$step_id" "$notes"
            fi
            
            return 1
        fi
    fi
    
    return 0
}

# 验证工作单元完整性
validate_unit() {
    local unit_id="$1"
    local instance_id="$2"
    
    local instance_file="$VALIDATOR_DB/${unit_id}_${instance_id}.running"
    local log_file="$instance_file.log"
    
    if [[ ! -f "$log_file" ]]; then
        log "VALIDATION_FAIL: 无执行日志"
        return 1
    fi
    
    # 检查强制步骤是否全部完成
    local mandatory_steps
    mandatory_steps=$(grep '"block_if_fail": true' "$VALIDATOR_DB/${unit_id}.json" -B2 | grep '"step_id"' | cut -d'"' -f4)
    
    local failed_steps=""
    for step in $mandatory_steps; do
        if ! grep -q "STEP_COMPLETED: $step" "$log_file"; then
            failed_steps="$failed_steps $step"
        fi
    done
    
    if [[ -n "$failed_steps" ]]; then
        log "VALIDATION_FAIL: 强制步骤未完成: $failed_steps"
        return 1
    fi
    
    # 标记完成
    mv "$instance_file" "$VALIDATOR_DB/${unit_id}_${instance_id}.completed"
    log "VALIDATION_PASS: $unit_id 实例 $instance_id 验证通过"
    
    return 0
}

# 生成完成证明
generate_certificate() {
    local unit_id="$1"
    local instance_id="$2"
    
    local cert_file="$CHECKSUM_DIR/${unit_id}_${instance_id}.cert"
    local completed_file="$VALIDATOR_DB/${unit_id}_${instance_id}.completed"
    
    if [[ ! -f "$completed_file" ]]; then
        log "ERROR: 未完成的工作单元无法生成证明"
        return 1
    fi
    
    # 生成哈希证明
    local checksum
    checksum=$(sha256sum "$completed_file" | cut -d' ' -f1)
    
    cat > "$cert_file" << EOF
{
    "unit_id": "$unit_id",
    "instance_id": "$instance_id",
    "completion_time": "$(date '+%Y-%m-%d %H:%M:%S')",
    "checksum": "$checksum",
    "validator": "WORK_UNIT_VALIDATOR_v1.0"
}
EOF
    
    echo "✅ 完成证明: $cert_file"
    log "CERTIFICATE_GENERATED: $cert_file"
}

# 主入口
case "${1:-help}" in
    define)
        define_file_processing_unit
        ;;
    start)
        start_unit "${2:-FILE_PROC_7STEP}" "${3:-}"
        ;;
    step)
        complete_step "${2}" "${3}" "${4}" "${5:-PASS}" "${6:-}"
        ;;
    validate)
        validate_unit "${2}" "${3}"
        ;;
    cert)
        generate_certificate "${2}" "${3}"
        ;;
    help|*)
        echo "工作单元验证器 v1.0"
        echo ""
        echo "用法:"
        echo "  $0 define                    - 定义标准工作单元"
        echo "  $0 start [单元ID] [实例ID]    - 开始工作单元"
        echo "  $0 step 单元ID 实例ID 步骤ID [结果] [备注] - 完成步骤"
        echo "  $0 validate 单元ID 实例ID     - 验证完整性"
        echo "  $0 cert 单元ID 实例ID         - 生成完成证明"
        ;;
esac
