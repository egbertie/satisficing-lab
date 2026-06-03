#!/bin/bash
# =============================================================================
# 命名规范检查脚本 (Naming Standards Checker)
# =============================================================================
# 版本: v1.0
# 说明: 自动检查文件命名是否符合 MECHANISM_NAMING_STANDARDS.md 规范
# 用法: bash check-naming.sh [目录路径] [--report] [--log "消息"]
# =============================================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 版本
VERSION="v1.0"

# 统计变量
VIOLATIONS=0
WARNINGS=0
CHECKED=0

# 日志文件
LOG_FILE="logs/naming-check.log"
REPORT_FILE="logs/naming-violations.json"

# 检查目录
TARGET_DIR="${1:-.}"

# 确保日志目录存在
mkdir -p logs

# =============================================================================
# 帮助信息
# =============================================================================
show_help() {
    cat << EOF
命名规范检查脚本 ${VERSION}

用法:
  bash check-naming.sh [选项] [目录]

选项:
  -h, --help          显示帮助信息
  -r, --report        生成JSON格式的详细报告
  -l, --log "消息"    记录一条自定义日志
  -v, --version       显示版本信息

示例:
  bash check-naming.sh                    # 检查当前目录
  bash check-naming.sh docs/              # 检查指定目录
  bash check-naming.sh --report           # 检查并生成报告
  bash check-naming.sh --log "手动检查完成" # 记录日志

检查规则:
  1. 文件名必须全小写
  2. 使用连字符(-)分隔，禁止使用下划线(_)
  3. 禁止空格
  4. 禁止中文字符
  5. 禁止特殊字符
  6. 版本号格式必须为 vX.Y (如 v1.0, v2.1)
EOF
}

# =============================================================================
# 日志函数
# =============================================================================
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [INFO] $1" >> "$LOG_FILE"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [WARN] $1" >> "$LOG_FILE"
    ((WARNINGS++))
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [ERROR] $1" >> "$LOG_FILE"
    ((VIOLATIONS++))
}

log_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

# =============================================================================
# 检查函数
# =============================================================================

# 检查是否包含大写字母
check_uppercase() {
    local filename="$1"
    if [[ "$filename" =~ [A-Z] ]]; then
        log_error "包含大写字母: $filename"
        return 1
    fi
    return 0
}

# 检查是否使用下划线
check_underscore() {
    local filename="$1"
    if [[ "$filename" =~ _ ]]; then
        log_error "使用下划线分隔: $filename"
        return 1
    fi
    return 0
}

# 检查是否包含空格
check_space() {
    local filename="$1"
    if [[ "$filename" =~ [[:space:]] ]]; then
        log_error "包含空格: $filename"
        return 1
    fi
    return 0
}

# 检查是否包含中文字符
check_chinese() {
    local filename="$1"
    if echo "$filename" | grep -Pq '[\x{4e00}-\x{9fff}]'; then
        log_error "包含中文字符: $filename"
        return 1
    fi
    return 0
}

# 检查是否包含特殊字符
check_special_chars() {
    local filename="$1"
    # 允许: 小写字母、数字、连字符、点号
    # 禁止: 其他所有特殊字符
    if [[ "$filename" =~ [^a-z0-9.-] ]]; then
        log_error "包含特殊字符: $filename"
        return 1
    fi
    return 0
}

# 检查版本号格式
check_version() {
    local filename="$1"
    # 查找版本号模式
    if [[ "$filename" =~ [Vv][0-9]+\.[0-9]+\.[0-9]+ ]]; then
        log_error "版本号使用三段式 (vX.Y.Z): $filename"
        return 1
    fi
    if [[ "$filename" =~ [V][0-9]+\.[0-9]+ ]]; then
        log_error "版本号使用大写V: $filename"
        return 1
    fi
    return 0
}

# 检查是否有意义的描述
check_meaningful() {
    local filename="$1"
    local basename=$(basename "$filename" | sed 's/\.[a-z]*$//')
    
    # 禁止的无意义词汇
    local meaningless=("temp" "tmp" "test" "stuff" "thing" "new" "old" "final" "latest")
    
    for word in "${meaningless[@]}"; do
        if [[ "$basename" == "$word" ]] || [[ "$basename" == *"-$word"* ]] || [[ "$basename" == *"$word-"* ]]; then
            log_warn "可能无意义的命名 ($word): $filename"
            return 1
        fi
    done
    return 0
}

# 检查日期格式
check_date_format() {
    local filename="$1"
    # 检查是否包含8位数字日期 (20260331) 而非标准格式 (2026-03-31)
    if [[ "$filename" =~ [0-9]{8} ]] && ! [[ "$filename" =~ [0-9]{4}-[0-9]{2}-[0-9]{2} ]]; then
        log_warn "日期格式建议改为 YYYY-MM-DD: $filename"
        return 1
    fi
    return 0
}

# 主检查函数
check_file() {
    local filepath="$1"
    local filename=$(basename "$filepath")
    
    ((CHECKED++))
    
    # 跳过隐藏文件和特定目录
    if [[ "$filename" == .* ]] || [[ "$filepath" == */.git/* ]] || [[ "$filepath" == */node_modules/* ]]; then
        return 0
    fi
    
    # 执行各项检查
    local has_error=0
    
    check_uppercase "$filename" || has_error=1
    check_underscore "$filename" || has_error=1
    check_space "$filename" || has_error=1
    check_chinese "$filename" || has_error=1
    check_special_chars "$filename" || has_error=1
    check_version "$filename" || has_error=1
    check_meaningful "$filename" || true  # 警告级别
    check_date_format "$filename" || true  # 警告级别
    
    if [[ $has_error -eq 0 ]]; then
        log_success "$filename"
    fi
}

# 递归检查目录
check_directory() {
    local dir="$1"
    
    log_info "开始检查目录: $dir"
    
    while IFS= read -r -d '' file; do
        check_file "$file"
    done < <(find "$dir" -type f -print0 2>/dev/null)
    
    # 检查目录名
    while IFS= read -r -d '' subdir; do
        local dirname=$(basename "$subdir")
        ((CHECKED++))
        
        # 跳过隐藏目录
        if [[ "$dirname" == .* ]]; then
            continue
        fi
        
        check_uppercase "$dirname" || true
        check_underscore "$dirname" || true
        check_space "$dirname" || true
        check_chinese "$dirname" || true
        check_special_chars "$dirname" || true
    done < <(find "$dir" -type d -print0 2>/dev/null)
}

# =============================================================================
# 报告生成
# =============================================================================
generate_report() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    cat > "$REPORT_FILE" << EOF
{
  "report_version": "${VERSION}",
  "timestamp": "${timestamp}",
  "target_directory": "${TARGET_DIR}",
  "summary": {
    "total_checked": ${CHECKED},
    "violations": ${VIOLATIONS},
    "warnings": ${WARNINGS},
    "pass_rate": "$(awk "BEGIN {printf \"%.1f%%\", (($CHECKED - $VIOLATIONS) / $CHECKED) * 100}")"
  },
  "status": "$([[ $VIOLATIONS -eq 0 ]] && echo "PASS" || echo "FAIL")",
  "log_file": "${LOG_FILE}",
  "next_steps": [
    "检查日志文件: cat ${LOG_FILE}",
    "修复违规命名",
    "重新运行检查: bash scripts/check-naming.sh"
  ]
}
EOF

    log_info "报告已生成: $REPORT_FILE"
}

# =============================================================================
# 主函数
# =============================================================================
main() {
    # 解析参数
    local generate_report_flag=false
    local custom_log=""
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -v|--version)
                echo "命名规范检查脚本 ${VERSION}"
                exit 0
                ;;
            -r|--report)
                generate_report_flag=true
                shift
                ;;
            -l|--log)
                custom_log="$2"
                shift 2
                ;;
            -*)
                echo "未知选项: $1"
                show_help
                exit 1
                ;;
            *)
                TARGET_DIR="$1"
                shift
                ;;
        esac
    done
    
    # 检查目录是否存在
    if [[ ! -d "$TARGET_DIR" ]]; then
        echo -e "${RED}错误: 目录不存在: $TARGET_DIR${NC}"
        exit 1
    fi
    
    # 记录自定义日志
    if [[ -n "$custom_log" ]]; then
        log_info "$custom_log"
        exit 0
    fi
    
    # 执行检查
    echo "========================================"
    echo "  命名规范检查脚本 ${VERSION}"
    echo "========================================"
    echo ""
    
    check_directory "$TARGET_DIR"
    
    # 生成报告
    if [[ "$generate_report_flag" == true ]]; then
        generate_report
    fi
    
    # 输出汇总
    echo ""
    echo "========================================"
    echo "  检查结果汇总"
    echo "========================================"
    echo -e "检查文件数: ${BLUE}${CHECKED}${NC}"
    echo -e "违规数:     ${RED}${VIOLATIONS}${NC}"
    echo -e "警告数:     ${YELLOW}${WARNINGS}${NC}"
    
    if [[ $VIOLATIONS -eq 0 ]]; then
        echo -e "状态:       ${GREEN}通过 ✓${NC}"
        exit 0
    else
        echo -e "状态:       ${RED}失败 ✗${NC}"
        echo ""
        echo "查看详细日志: cat $LOG_FILE"
        exit 1
    fi
}

# 运行主函数
main "$@"
