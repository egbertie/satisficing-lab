#!/bin/bash
#
# Quality Assurance Review Script
# 7标准审查脚本: S1输入 → S2多维度检查 → S3输出报告 → S4触发机制 → S5检查清单 → S6局限标注
#
# 使用方式:
#   ./qa-review.sh <file>              # 审查单个文件
#   ./qa-review.sh --batch <dir>       # 批量审查目录
#   ./qa-review.sh --ci --gate=A       # CI集成 (gate: A/B/C/D)
#   ./qa-review.sh --ci --block-on=Critical,High  # 阻断级别
#

set -e

# 配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="/root/.openclaw/workspace"
REPORT_DIR="$WORKSPACE/reports/qa"
ISSUES_DIR="$REPORT_DIR/issues"
FIXES_DIR="$REPORT_DIR/fixes"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
DATE=$(date +%Y-%m-%d)

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 参数解析
TARGET=""
MODE="single"  # single, batch, ci
GATE="C"       # A/B/C/D 最低通过等级
BLOCK_ON=""    # Critical,High,Medium,Low
VERBOSE=false

usage() {
    echo "Quality Assurance Review Tool (7标准)"
    echo ""
    echo "Usage:"
    echo "  $0 <file>                    审查单个文件"
    echo "  $0 --batch <dir>             批量审查目录"
    echo "  $0 --ci [options] <file>     CI模式"
    echo ""
    echo "Options:"
    echo "  --gate=A|B|C|D              最低通过等级 (默认: C)"
    echo "  --block-on=LEVELS           阻断级别 (如: Critical,High)"
    echo "  --verbose                   详细输出"
    echo "  --help                      显示帮助"
    echo ""
    echo "Examples:"
    echo "  $0 skills/my-skill/SKILL.md"
    echo "  $0 --batch skills/"
    echo "  $0 --ci --gate=A --block-on=Critical,High skills/my-skill/"
    exit 1
}

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        --batch)
            MODE="batch"
            shift
            TARGET="$1"
            shift
            ;;
        --ci)
            MODE="ci"
            shift
            ;;
        --gate=*)
            GATE="${1#*=}"
            shift
            ;;
        --block-on=*)
            BLOCK_ON="${1#*=}"
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --help)
            usage
            ;;
        -*)
            echo "未知选项: $1"
            usage
            ;;
        *)
            TARGET="$1"
            shift
            ;;
    esac
done

# 检查目标
if [ -z "$TARGET" ]; then
    echo "错误: 未指定审查目标"
    usage
fi

# 创建报告目录
mkdir -p "$REPORT_DIR" "$ISSUES_DIR" "$FIXES_DIR"

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# ============================================
# S1: 输入定义与识别
# ============================================
identify_file_type() {
    local file="$1"
    local ext="${file##*.}"
    local basename=$(basename "$file")
    
    # 识别文件类型
    case "$basename" in
        SKILL.md)
            echo "skill_md"
            ;;
        AGENTS.md|USER.md|SOUL.md)
            echo "agent_doc"
            ;;
        *.md)
            echo "markdown"
            ;;
        *.py)
            echo "python"
            ;;
        *.sh)
            echo "shell"
            ;;
        *.js|*.ts)
            echo "javascript"
            ;;
        *.json)
            echo "json"
            ;;
        *.yaml|*.yml)
            echo "yaml"
            ;;
        *.toml)
            echo "toml"
            ;;
        Dockerfile|Makefile|Docker*)
            echo "config"
            ;;
        *)
            echo "text"
            ;;
    esac
}

# ============================================
# S2: 多维度检查
# ============================================

# 语法检查
check_syntax() {
    local file="$1"
    local file_type="$2"
    local issues=()
    
    log_info "执行语法检查..."
    
    case "$file_type" in
        shell)
            if command -v shellcheck &> /dev/null; then
                while IFS= read -r line; do
                    if [ -n "$line" ]; then
                        issues+=("{\"category\":\"Syntax\",\"severity\":\"High\",\"message\":\"$line\",\"auto_fixable\":false}")
                    fi
                done < <(shellcheck -f gcc "$file" 2>/dev/null | grep -v "^$" || true)
            else
                # 基础bash语法检查
                if ! bash -n "$file" 2>/dev/null; then
                    local err=$(bash -n "$file" 2>&1)
                    issues+=("{\"category\":\"Syntax\",\"severity\":\"Critical\",\"message\":\"Shell语法错误: $err\",\"auto_fixable\":false}")
                fi
            fi
            ;;
        python)
            if ! python3 -m py_compile "$file" 2>/dev/null; then
                local err=$(python3 -m py_compile "$file" 2>&1 | head -1)
                issues+=("{\"category\":\"Syntax\",\"severity\":\"Critical\",\"message\":\"Python语法错误: $err\",\"auto_fixable\":false}")
            fi
            ;;
        json)
            if ! python3 -c "import json; json.load(open('$file'))" 2>/dev/null; then
                issues+=("{\"category\":\"Syntax\",\"severity\":\"Critical\",\"message\":\"JSON格式错误\",\"auto_fixable\":false}")
            fi
            ;;
        yaml)
            if command -v yamllint &> /dev/null; then
                while IFS= read -r line; do
                    if [ -n "$line" ]; then
                        issues+=("{\"category\":\"Syntax\",\"severity\":\"High\",\"message\":\"YAML错误: $line\",\"auto_fixable\":false}")
                    fi
                done < <(yamllint "$file" 2>/dev/null | grep "error" || true)
            fi
            ;;
    esac
    
    # 通用检查: 非法字符
    if grep -q $'\r' "$file" 2>/dev/null; then
        issues+=("{\"category\":\"Syntax\",\"severity\":\"Medium\",\"message\":\"包含Windows换行符(CRLF)\",\"auto_fixable\":true}")
    fi
    
    printf '%s\n' "${issues[@]}"
}

# 逻辑检查
check_logic() {
    local file="$1"
    local file_type="$2"
    local issues=()
    
    log_info "执行逻辑检查..."
    
    case "$file_type" in
        shell)
            # 检查未定义变量
            while IFS= read -r line; do
                if [ -n "$line" ]; then
                    issues+=("{\"category\":\"Logic\",\"severity\":\"High\",\"message\":\"潜在未定义变量: $line\",\"auto_fixable\":false}")
                fi
            done < <(grep -n '\$[A-Za-z_][A-Za-z0-9_]*' "$file" | grep -v '\${' | head -5 || true)
            
            # 检查错误处理
            if ! grep -q 'set -e\|set -o errexit\||| exit\||| return' "$file" 2>/dev/null; then
                issues+=("{\"category\":\"Logic\",\"severity\":\"Medium\",\"message\":\"建议添加错误处理 (set -e)\",\"auto_fixable\":true}")
            fi
            ;;
        python)
            # 检查裸except
            if grep -q 'except:' "$file" 2>/dev/null; then
                issues+=("{\"category\":\"Logic\",\"severity\":\"Medium\",\"message\":\"发现裸except:语句，建议指定异常类型\",\"auto_fixable\":false}")
            fi
            
            # 检查print语句(应使用logging)
            if grep -q '^print(' "$file" 2>/dev/null; then
                issues+=("{\"category\":\"Logic\",\"severity\":\"Low\",\"message\":\"建议使用logging替代print\",\"auto_fixable\":false}")
            fi
            ;;
        skill_md)
            # SKILL.md特有逻辑检查
            if ! grep -q "S1.*输入\|输入定义\|Input" "$file" 2>/dev/null; then
                issues+=("{\"category\":\"Logic\",\"severity\":\"High\",\"message\":\"缺少S1输入定义章节\",\"auto_fixable\":false}")
            fi
            if ! grep -q "S2.*检查\|多维度检查\|Check" "$file" 2>/dev/null; then
                issues+=("{\"category\":\"Logic\",\"severity\":\"High\",\"message\":\"缺少S2多维度检查章节\",\"auto_fixable\":false}")
            fi
            if ! grep -q "S3.*输出\|Output" "$file" 2>/dev/null; then
                issues+=("{\"category\":\"Logic\",\"severity\":\"High\",\"message\":\"缺少S3输出章节\",\"auto_fixable\":false}")
            fi
            if ! grep -q "S4.*触发\|Trigger" "$file" 2>/dev/null; then
                issues+=("{\"category\":\"Logic\",\"severity\":\"Medium\",\"message\":\"缺少S4触发机制章节\",\"auto_fixable\":false}")
            fi
            if ! grep -q "S5.*清单\|Checklist" "$file" 2>/dev/null; then
                issues+=("{\"category\":\"Logic\",\"severity\":\"Medium\",\"message\":\"缺少S5检查清单章节\",\"auto_fixable\":false}")
            fi
            if ! grep -q "S6.*局限\|Limitations" "$file" 2>/dev/null; then
                issues+=("{\"category\":\"Logic\",\"severity\":\"Medium\",\"message\":\"缺少S6局限性标注章节\",\"auto_fixable\":false}")
            fi
            if ! grep -q "S7.*对抗\|Adversarial" "$file" 2>/dev/null; then
                issues+=("{\"category\":\"Logic\",\"severity\":\"Medium\",\"message\":\"缺少S7对抗测试章节\",\"auto_fixable\":false}")
            fi
            # 检查5标准
            if ! grep -q "5标准\|全局考虑\|系统考虑\|迭代机制\|Skill化\|自动化" "$file" 2>/dev/null; then
                issues+=("{\"category\":\"Logic\",\"severity\":\"High\",\"message\":\"缺少5标准相关内容\",\"auto_fixable\":false}")
            fi
            ;;
    esac
    
    printf '%s\n' "${issues[@]}"
}

# 格式检查
check_format() {
    local file="$1"
    local file_type="$2"
    local issues=()
    
    log_info "执行格式检查..."
    
    # 检查尾随空格
    if grep -n '[[:space:]]$' "$file" > /dev/null 2>&1; then
        local count=$(grep -c '[[:space:]]$' "$file" 2>/dev/null || echo "0")
        issues+=("{\"category\":\"Format\",\"severity\":\"Low\",\"message\":\"发现 $count 行尾随空格\",\"auto_fixable\":true}")
    fi
    
    # 检查Tab字符
    if grep -n $'\t' "$file" > /dev/null 2>&1; then
        local count=$(grep -c $'\t' "$file" 2>/dev/null || echo "0")
        issues+=("{\"category\":\"Format\",\"severity\":\"Low\",\"message\":\"发现 $count 行包含Tab字符\",\"auto_fixable\":true}")
    fi
    
    # 检查文件末尾空行
    if [ -s "$file" ] && [ "$(tail -c 1 "$file" | wc -l)" -eq 0 ]; then
        issues+=("{\"category\":\"Format\",\"severity\":\"Low\",\"message\":\"文件末尾缺少空行\",\"auto_fixable\":true}")
    fi
    
    case "$file_type" in
        python)
            # Python缩进检查(4空格)
            local wrong_indent=$(grep -n '^  [^ ]' "$file" 2>/dev/null | grep -v '^[0-9]*:    ' | wc -l || echo "0")
            if [ "$wrong_indent" -gt 0 ]; then
                issues+=("{\"category\":\"Format\",\"severity\":\"Medium\",\"message\":\"发现 $wrong_indent 行非4空格缩进\",\"auto_fixable\":true}")
            fi
            ;;
        shell)
            # Shell缩进一致性
            local mixed_indent=$(grep -c $'\t' "$file" 2>/dev/null || echo "0")
            local space_indent=$(grep -c '^    ' "$file" 2>/dev/null || echo "0")
            if [ "$mixed_indent" -gt 0 ] && [ "$space_indent" -gt 0 ]; then
                issues+=("{\"category\":\"Format\",\"severity\":\"Medium\",\"message\":\"缩进混合使用Tab和空格\",\"auto_fixable\":true}")
            fi
            ;;
    esac
    
    printf '%s\n' "${issues[@]}"
}

# 合规检查 (5标准 + 隐性规则)
check_compliance() {
    local file="$1"
    local file_type="$2"
    local issues=()
    
    log_info "执行合规检查..."
    
    case "$file_type" in
        skill_md)
            # 检查规则8: 置信度标注
            if ! grep -q "置信度\|confidence" "$file" 2>/dev/null; then
                issues+=("{\"category\":\"Compliance\",\"severity\":\"Medium\",\"message\":\"未提及规则8(置信度标注)\",\"auto_fixable\":false}")
            fi
            
            # 检查规则9: 交叉验证
            if ! grep -q "交叉验证\|cross.validation\|cross_validation" "$file" 2>/dev/null; then
                issues+=("{\"category\":\"Compliance\",\"severity\":\"Medium\",\"message\":\"未提及规则9(交叉验证)\",\"auto_fixable\":false}")
            fi
            
            # 检查产出标准
            if ! grep -q "产出标准\|产出物" "$file" 2>/dev/null; then
                issues+=("{\"category\":\"Compliance\",\"severity\":\"Low\",\"message\":\"缺少产出标准说明\",\"auto_fixable\":false}")
            fi
            ;;
    esac
    
    printf '%s\n' "${issues[@]}"
}

# ============================================
# S3: 生成输出报告
# ============================================
generate_report() {
    local file="$1"
    local file_type="$2"
    local issues_json="$3"
    local report_file="$4"
    
    log_info "生成审查报告..."
    
    # 统计数据
    local total=$(echo "$issues_json" | grep -c 'category' || echo "0")
    local critical=$(echo "$issues_json" | grep -o '"severity":"Critical"' | wc -l || echo "0")
    local high=$(echo "$issues_json" | grep -o '"severity":"High"' | wc -l || echo "0")
    local medium=$(echo "$issues_json" | grep -o '"severity":"Medium"' | wc -l || echo "0")
    local low=$(echo "$issues_json" | grep -o '"severity":"Low"' | wc -l || echo "0")
    local auto_fixable=$(echo "$issues_json" | grep -o '"auto_fixable":true' | wc -l || echo "0")
    
    # 计算等级
    local grade="A"
    if [ "$critical" -gt 0 ]; then
        grade="D"
    elif [ "$high" -gt 2 ]; then
        grade="C"
    elif [ "$high" -gt 0 ] || [ "$medium" -gt 5 ]; then
        grade="B"
    fi
    
    # 生成Markdown报告
    cat > "$report_file" << EOF
# QA审查报告

## 基本信息
| 项目 | 值 |
|------|-----|
| **审查目标** | $file |
| **文件类型** | $file_type |
| **审查时间** | $(date '+%Y-%m-%d %H:%M:%S') |
| **执行标准** | 7标准 (S1-S7) + 5标准 |

## 质量评级

### 总体评级: **$grade**

| 指标 | 数值 |
|------|------|
| 问题总数 | $total |
| 🔴 Critical | $critical |
| 🟠 High | $high |
| 🟡 Medium | $medium |
| 🔵 Low | $low |
| 可自动修复 | $auto_fixable |

### 评级标准
- **A**: 优秀 (无Critical/High, Medium≤2)
- **B**: 良好 (无Critical, High≤2, Medium≤5)
- **C**: 需改进 (无Critical, High≤5)
- **D**: 不合格 (存在Critical)

## 问题分布

| 维度 | Critical | High | Medium | Low |
|------|----------|------|--------|-----|
| 语法 (Syntax) | $(echo "$issues_json" | grep -c '"category":"Syntax".*"severity":"Critical"' || echo 0) | $(echo "$issues_json" | grep -c '"category":"Syntax".*"severity":"High"' || echo 0) | $(echo "$issues_json" | grep -c '"category":"Syntax".*"severity":"Medium"' || echo 0) | $(echo "$issues_json" | grep -c '"category":"Syntax".*"severity":"Low"' || echo 0) |
| 逻辑 (Logic) | $(echo "$issues_json" | grep -c '"category":"Logic".*"severity":"Critical"' || echo 0) | $(echo "$issues_json" | grep -c '"category":"Logic".*"severity":"High"' || echo 0) | $(echo "$issues_json" | grep -c '"category":"Logic".*"severity":"Medium"' || echo 0) | $(echo "$issues_json" | grep -c '"category":"Logic".*"severity":"Low"' || echo 0) |
| 格式 (Format) | $(echo "$issues_json" | grep -c '"category":"Format".*"severity":"Critical"' || echo 0) | $(echo "$issues_json" | grep -c '"category":"Format".*"severity":"High"' || echo 0) | $(echo "$issues_json" | grep -c '"category":"Format".*"severity":"Medium"' || echo 0) | $(echo "$issues_json" | grep -c '"category":"Format".*"severity":"Low"' || echo 0) |
| 合规 (Compliance) | $(echo "$issues_json" | grep -c '"category":"Compliance".*"severity":"Critical"' || echo 0) | $(echo "$issues_json" | grep -c '"category":"Compliance".*"severity":"High"' || echo 0) | $(echo "$issues_json" | grep -c '"category":"Compliance".*"severity":"Medium"' || echo 0) | $(echo "$issues_json" | grep -c '"category":"Compliance".*"severity":"Low"' || echo 0) |

## 详细问题清单

EOF

    # 添加问题列表
    if [ "$total" -gt 0 ]; then
        echo "$issues_json" | while IFS= read -r issue; do
            if [ -n "$issue" ]; then
                local cat=$(echo "$issue" | grep -o '"category":"[^"]*"' | cut -d'"' -f4)
                local sev=$(echo "$issue" | grep -o '"severity":"[^"]*"' | cut -d'"' -f4)
                local msg=$(echo "$issue" | grep -o '"message":"[^"]*"' | cut -d'"' -f4)
                local auto=$(echo "$issue" | grep -o '"auto_fixable":[^,}]*' | cut -d':' -f2)
                
                local sev_emoji=""
                case "$sev" in
                    Critical) sev_emoji="🔴" ;;
                    High) sev_emoji="🟠" ;;
                    Medium) sev_emoji="🟡" ;;
                    Low) sev_emoji="🔵" ;;
                esac
                
                local auto_text=""
                if [ "$auto" = "true" ]; then
                    auto_text=" | ✅可自动修复"
                fi
                
                echo "### $sev_emoji [$cat] $sev$auto_text" >> "$report_file"
                echo "" >> "$report_file"
                echo "$msg" >> "$report_file"
                echo "" >> "$report_file"
            fi
        done
    else
        echo "✅ 未发现质量问题" >> "$report_file"
        echo "" >> "$report_file"
    fi
    
    # 添加S6: 局限性标注
    cat >> "$report_file" << EOF

## S6: 局限性标注

以下问题**无法**通过本工具自动检测:

1. **业务逻辑正确性**: 本工具无法判断代码/配置是否满足业务需求
2. **安全漏洞深度检测**: 需结合专业安全审计工具 (bandit, snyk等)
3. **性能优化建议**: 需结合性能测试和profiling工具
4. **设计模式合理性**: 需架构师人工评审
5. **语义正确性**: 文档描述准确性需领域专家审核

## 修复建议

EOF

    if [ "$auto_fixable" -gt 0 ]; then
        echo "### 可自动修复的问题" >> "$report_file"
        echo "" >> "$report_file"
        echo "运行以下命令自动修复格式问题:" >> "$report_file"
        echo '```bash' >> "$report_file"
        echo "# 修复尾随空格和Tab" >> "$report_file"
        echo "sed -i 's/[[:space:]]*$//' '$file'" >> "$report_file"
        echo "sed -i 's/\t/    /g' '$file'" >> "$report_file"
        echo '```' >> "$report_file"
        echo "" >> "$report_file"
    fi
    
    cat >> "$report_file" << EOF
### 手动修复清单

根据上述问题清单，逐项修复:
1. 优先处理 🔴 Critical 和 🟠 High 级别问题
2. 然后处理 🟡 Medium 级别问题
3. 最后处理 🔵 Low 级别问题

## 元数据

| 字段 | 值 |
|------|-----|
| report_version | 2.0 |
| standard | 7标准+5标准 |
| total_issues | $total |
| grade | $grade |
| passed | $(if [ "$grade" \< "$GATE" ] || [ "$grade" = "$GATE" ]; then echo "true"; else echo "false"; fi) |

---
*Generated by Quality Assurance Skill v2.0*
EOF

    echo "$grade"
}

# ============================================
# S3: 生成JSON问题清单
# ============================================
generate_issues_json() {
    local file="$1"
    local issues_raw="$2"
    local issues_file="$3"
    
    # 构建JSON数组 (使用process substitution避免子shell问题)
    local json_array="["
    local first=true
    
    while IFS= read -r issue; do
        if [ -n "$issue" ]; then
            if [ "$first" = true ]; then
                first=false
            else
                json_array="${json_array},"
            fi
            json_array="${json_array}${issue}"
        fi
    done <<< "$issues_raw"
    
    json_array="${json_array}]"
    
    # 写入文件
    cat > "$issues_file" << EOF
{
    "target": "$file",
    "timestamp": "$(date -Iseconds)",
    "issues": $json_array
}
EOF
}

# ============================================
# S5: 检查清单验证
# ============================================
validate_checklist() {
    local file="$1"
    local file_type="$2"
    
    log_info "执行检查清单验证 (S5)..."
    
    case "$file_type" in
        skill_md)
            echo ""
            echo "=== SKILL.md 检查清单 ==="
            local checks=(
                "S1:输入定义"
                "S2:多维度检查"
                "S3:输出报告"
                "S4:触发机制"
                "S5:检查清单"
                "S6:局限性标注"
                "S7:对抗测试"
                "5标准"
            )
            for check in "${checks[@]}"; do
                if grep -q "${check:0:2}.*${check:3}" "$file" 2>/dev/null || \
                   grep -q "${check:3}" "$file" 2>/dev/null; then
                    echo "  ✅ $check"
                else
                    echo "  ❌ $check"
                fi
            done
            ;;
    esac
}

# ============================================
# 主审查流程
# ============================================
review_file() {
    local file="$1"
    
    if [ ! -f "$file" ]; then
        log_error "文件不存在: $file"
        return 1
    fi
    
    echo ""
    echo "========================================"
    echo "QA审查: $file"
    echo "========================================"
    
    # S1: 识别输入
    local file_type=$(identify_file_type "$file")
    log_info "识别文件类型: $file_type"
    
    # S2: 多维度检查
    local issues=""
    issues="$issues$(check_syntax "$file" "$file_type")"
    issues="$issues$(check_logic "$file" "$file_type")"
    issues="$issues$(check_format "$file" "$file_type")"
    issues="$issues$(check_compliance "$file" "$file_type")"
    
    # 生成输出文件名
    local basename=$(basename "$file" | tr '/\\' '__')
    local report_file="$REPORT_DIR/${TIMESTAMP}-${basename}.md"
    local issues_file="$ISSUES_DIR/${TIMESTAMP}-${basename}.json"
    local fixes_file="$FIXES_DIR/${TIMESTAMP}-${basename}.patch"
    
    # S3: 生成报告
    local grade=$(generate_report "$file" "$file_type" "$issues" "$report_file")
    generate_issues_json "$file" "$issues" "$issues_file"
    
    # S5: 检查清单
    validate_checklist "$file" "$file_type"
    
    # 输出结果
    echo ""
    echo "========================================"
    echo "审查完成"
    echo "========================================"
    echo "质量评级: $grade"
    echo "报告文件: $report_file"
    echo "问题清单: $issues_file"
    
    # CI模式: 门控检查
    if [ "$MODE" = "ci" ]; then
        local grade_value
        case "$grade" in
            A) grade_value=4 ;;
            B) grade_value=3 ;;
            C) grade_value=2 ;;
            D) grade_value=1 ;;
        esac
        
        local gate_value
        case "$GATE" in
            A) gate_value=4 ;;
            B) gate_value=3 ;;
            C) gate_value=2 ;;
            D) gate_value=1 ;;
        esac
        
        if [ "$grade_value" -lt "$gate_value" ]; then
            log_error "质量检查未通过! 评级 $grade 低于门控 $GATE"
            return 1
        fi
        
        # 阻断级别检查
        if [ -n "$BLOCK_ON" ]; then
            local critical_count=$(grep -o '"severity":"Critical"' "$issues_file" | wc -l || echo "0")
            local high_count=$(grep -o '"severity":"High"' "$issues_file" | wc -l || echo "0")
            
            if [[ "$BLOCK_ON" == *"Critical"* ]] && [ "$critical_count" -gt 0 ]; then
                log_error "发现 $critical_count 个 Critical 问题，阻断发布"
                return 1
            fi
            
            if [[ "$BLOCK_ON" == *"High"* ]] && [ "$high_count" -gt 0 ]; then
                log_error "发现 $high_count 个 High 问题，阻断发布"
                return 1
            fi
        fi
        
        log_success "质量检查通过! 评级 $grade 满足门控 $GATE"
    fi
    
    return 0
}

# ============================================
# 批量审查
# ============================================
batch_review() {
    local dir="$1"
    
    if [ ! -d "$dir" ]; then
        log_error "目录不存在: $dir"
        return 1
    fi
    
    echo "批量审查目录: $dir"
    
    local total=0
    local passed=0
    local failed=0
    
    # 查找要审查的文件
    while IFS= read -r -d '' file; do
        ((total++))
        if review_file "$file"; then
            ((passed++))
        else
            ((failed++))
        fi
    done < <(find "$dir" -type f \( -name "SKILL.md" -o -name "*.py" -o -name "*.sh" -o -name "*.json" -o -name "*.yaml" -o -name "*.yml" \) -print0 2>/dev/null)
    
    echo ""
    echo "========================================"
    echo "批量审查完成"
    echo "========================================"
    echo "总文件数: $total"
    log_success "通过: $passed"
    if [ "$failed" -gt 0 ]; then
        log_error "失败: $failed"
        return 1
    fi
    
    return 0
}

# ============================================
# 主入口
# ============================================
main() {
    echo "╔════════════════════════════════════════╗"
    echo "║    Quality Assurance Review (7标准)    ║"
    echo "║    S1→S2→S3→S4→S5→S6                   ║"
    echo "╚════════════════════════════════════════╝"
    
    case "$MODE" in
        single)
            review_file "$TARGET"
            ;;
        batch)
            batch_review "$TARGET"
            ;;
        ci)
            review_file "$TARGET"
            ;;
        *)
            log_error "未知模式: $MODE"
            usage
            ;;
    esac
}

main "$@"
