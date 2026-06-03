#!/bin/bash
# 蓝军违规检测与惩罚执行脚本
# 自动检测违规行为并执行相应惩罚

WORKSPACE="/root/.openclaw/workspace"
RULES_FILE="$WORKSPACE/rules/PUNISHMENT_RULES.md"
VIOLATIONS_DIR="$WORKSPACE/logs/violations"
PUNISHMENTS_DIR="$WORKSPACE/logs/punishments"

echo "=== 蓝军违规检测与惩罚执行系统 ==="
echo "执行时间: $(date)"
echo ""

# 创建目录
mkdir -p "$VIOLATIONS_DIR"
mkdir -p "$PUNISHMENTS_DIR"

# 检查惩罚规则是否存在
if [ ! -f "$RULES_FILE" ]; then
    echo "❌ 错误: 惩罚规则文件不存在"
    exit 1
fi

# 违规检测函数
detect_violations() {
    echo "【违规检测】扫描潜在违规..."
    
    local violations_found=0
    
    # 检测1: 检查虚报完成度（对比审计报告和实际状态）
    echo "  检测P0-001: 虚报完成度..."
    # 这里应该对比声称和实际，简化版本检查标记文件
    if [ -f "$WORKSPACE/.claimed_complete" ] && [ -f "$WORKSPACE/.audit_failed" ]; then
        echo "    ⚠️ 发现潜在虚报"
        record_violation "P0-001" "声称完成但审计失败" "high"
        ((violations_found++))
    fi
    
    # 检测2: 检查遗漏易忽略项
    echo "  检测P1-001: 遗漏易忽略检查项..."
    # 简化检查：检查是否有Token管理相关文件
    if [ ! -f "$WORKSPACE/checklists/TOKEN_MANAGEMENT_CHECKLIST.md" ]; then
        echo "    ⚠️ Token管理检查清单缺失"
        record_violation "P1-001" "Token管理检查清单不存在" "medium"
        ((violations_found++))
    fi
    
    # 检测3: 检查重复违规（简化版本）
    echo "  检测P1-004: 重复违规..."
    # 检查过去7天的违规记录
    local recent_violations=$(find "$VIOLATIONS_DIR" -name "*.json" -mtime -7 | wc -l)
    if [ "$recent_violations" -gt 3 ]; then
        echo "    ⚠️ 发现高频违规 ($recent_violations次/7天)"
        record_violation "P1-004" "高频违规模式" "medium"
        ((violations_found++))
    fi
    
    echo ""
    echo "检测完成，发现 $violations_found 个违规"
    return $violations_found
}

# 记录违规
record_violation() {
    local code="$1"
    local desc="$2"
    local severity="$3"
    
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local id="V-$(date +%Y%m%d)-$(cat /dev/urandom | tr -dc '0-9' | fold -w 3 | head -n 1)"
    local file="$VIOLATIONS_DIR/${id}.json"
    
    cat > "$file" << EOF
{
  "violation_id": "$id",
  "violation_code": "$code",
  "severity": "$severity",
  "description": "$desc",
  "timestamp": "$(date -Iseconds)",
  "detected_by": "punishment_enforcer.sh",
  "status": "detected"
}
EOF

    echo "    📝 已记录违规: $id"
}

# 执行惩罚
execute_punishment() {
    echo "【惩罚执行】根据违规记录执行惩罚..."
    
    local punishment_count=0
    
    # 查找待执行的违规
    for violation_file in "$VIOLATIONS_DIR"/*.json; do
        [ -f "$violation_file" ] || continue
        
        local status=$(grep '"status"' "$violation_file" | sed 's/.*: "\([^"]*\)".*/\1/')
        
        if [ "$status" = "detected" ]; then
            local code=$(grep '"violation_code"' "$violation_file" | sed 's/.*: "\([^"]*\)".*/\1/')
            local id=$(grep '"violation_id"' "$violation_file" | sed 's/.*: "\([^"]*\)".*/\1/')
            
            echo "  处理违规: $id ($code)"
            
            # 根据代码确定惩罚
            case "${code:0:2}" in
                "P0")
                    apply_p0_punishment "$id"
                    ;;
                "P1")
                    apply_p1_punishment "$id"
                    ;;
                "P2")
                    apply_p2_punishment "$id"
                    ;;
            esac
            
            # 更新状态
            sed -i 's/"status": "detected"/"status": "punishment_applied"/' "$violation_file"
            ((punishment_count++))
        fi
    done
    
    echo ""
    echo "惩罚执行完成，处理 $punishment_count 个违规"
}

# P0级惩罚
apply_p0_punishment() {
    local id="$1"
    echo "    🔴 应用P0级惩罚: 3天强制完整汇报"
    
    # 创建惩罚标记
    local punishment_file="$PUNISHMENTS_DIR/punishment_${id}.json"
    cat > "$punishment_file" << EOF
{
  "punishment_id": "P-$id",
  "type": "强制完整汇报",
  "duration_days": 3,
  "start_date": "$(date +%Y-%m-%d)",
  "end_date": "$(date -d '+3 days' +%Y-%m-%d)",
  "related_violation": "$id",
  "requirements": [
    "每次对话包含五部分汇报",
    "每小时报告进度",
    "所有任务有量化证据",
    "所有声称可验证"
  ]
}
EOF

    # 创建系统标记
    touch "$WORKSPACE/.p0_punishment_active"
    echo "$(date +%Y-%m-%d)" > "$WORKSPACE/.punishment_start_date"
    
    echo "    ✅ 惩罚已应用，标记文件已创建"
}

# P1级惩罚
apply_p1_punishment() {
    local id="$1"
    echo "    🟠 应用P1级惩罚: 警告 + 24小时整改"
    
    local punishment_file="$PUNISHMENTS_DIR/punishment_${id}.json"
    cat > "$punishment_file" << EOF
{
  "punishment_id": "P-$id",
  "type": "警告+24小时整改",
  "duration_days": 1,
  "start_date": "$(date +%Y-%m-%d)",
  "end_date": "$(date -d '+1 day' +%Y-%m-%d)",
  "related_violation": "$id"
}
EOF

    echo "    ✅ 警告已记录"
}

# P2级惩罚
apply_p2_punishment() {
    local id="$1"
    echo "    🟡 应用P2级惩罚: 提醒 + 立即修正"
    
    local punishment_file="$PUNISHMENTS_DIR/punishment_${id}.json"
    cat > "$punishment_file" << EOF
{
  "punishment_id": "P-$id",
  "type": "提醒+立即修正",
  "duration_days": 0,
  "start_date": "$(date +%Y-%m-%d)",
  "related_violation": "$id"
}
EOF

    echo "    ✅ 提醒已记录"
}

# 检查当前是否有执行中的惩罚
check_active_punishments() {
    echo "【状态检查】检查执行中的惩罚..."
    
    if [ -f "$WORKSPACE/.p0_punishment_active" ]; then
        local start_date=$(cat "$WORKSPACE/.punishment_start_date" 2>/dev/null || echo "$(date +%Y-%m-%d)")
        local current_date=$(date +%Y-%m-%d)
        local days_diff=$(( ($(date -d "$current_date" +%s) - $(date -d "$start_date" +%s)) / 86400 ))
        local days_remaining=$((3 - days_diff))
        
        if [ $days_remaining -le 0 ]; then
            echo "  ✅ P0惩罚已到期，自动解除"
            rm -f "$WORKSPACE/.p0_punishment_active"
            rm -f "$WORKSPACE/.punishment_start_date"
        else
            echo "  🔴 P0惩罚执行中，剩余 $days_remaining 天"
            echo "  要求: 强制完整汇报"
        fi
    else
        echo "  ✅ 无执行中的惩罚"
    fi
    
    echo ""
}

# 生成统计报告
generate_stats() {
    echo "【统计报告】违规与惩罚统计"
    echo ""
    
    local total_violations=$(find "$VIOLATIONS_DIR" -name "*.json" | wc -l)
    local total_punishments=$(find "$PUNISHMENTS_DIR" -name "*.json" | wc -l)
    local recent_violations=$(find "$VIOLATIONS_DIR" -name "*.json" -mtime -30 | wc -l)
    
    echo "  累计违规: $total_violations"
    echo "  累计惩罚: $total_punishments"
    echo "  最近30天违规: $recent_violations"
    echo ""
}

# 主执行流程
main() {
    check_active_punishments
    detect_violations
    local violation_count=$?
    
    if [ $violation_count -gt 0 ]; then
        execute_punishment
    fi
    
    generate_stats
    
    echo "=== 执行完成 ==="
    echo "下次检查: $(date -d '+1 day' '+%Y-%m-%d 09:00')"
}

# 执行主流程
main
