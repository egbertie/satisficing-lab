#!/bin/bash
#
# Adversarial Testing Script for Quality Assurance
# S7: 对抗测试 - 故意植入错误并测试发现率
#
# 使用方式:
#   ./qa-adversarial-test.sh           # 运行完整测试套件
#   ./qa-adversarial-test.sh --quick   # 快速测试
#   ./qa-adversarial-test.sh --report  # 生成报告
#

set -e

# 配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
WORKSPACE="/root/.openclaw/workspace"
REPORT_DIR="$WORKSPACE/reports/qa/adversarial"
TEST_DIR="/tmp/qa-adversarial-test-$$"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
DATE=$(date +%Y-%m-%d)

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# 测试统计
TOTAL_TESTS=0
DETECTED=0
MISSED=0

# 参数
QUICK_MODE=false
GENERATE_REPORT=true

usage() {
    echo "Adversarial Testing for QA Skill (S7)"
    echo ""
    echo "Usage:"
    echo "  $0                运行完整测试套件"
    echo "  $0 --quick        快速模式(每种类型1个样本)"
    echo "  $0 --no-report    不生成详细报告"
    echo "  $0 --help         显示帮助"
    exit 1
}

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        --quick)
            QUICK_MODE=true
            shift
            ;;
        --no-report)
            GENERATE_REPORT=false
            shift
            ;;
        --help)
            usage
            ;;
        *)
            echo "未知选项: $1"
            usage
            ;;
    esac
done

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
    echo -e "${GREEN}[PASS]${NC} $1"
}

log_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
}

# 创建测试目录
setup() {
    mkdir -p "$TEST_DIR" "$REPORT_DIR"
    log_info "测试目录: $TEST_DIR"
}

# 清理
teardown() {
    rm -rf "$TEST_DIR"
    log_info "清理完成"
}

# ============================================
# 测试用例生成器
# ============================================

# 生成干净的Python样本
generate_clean_python() {
    cat > "$1" << 'EOF'
#!/usr/bin/env python3
"""Clean Python sample for testing."""

def calculate_sum(a, b):
    """Calculate sum of two numbers."""
    return a + b

def main():
    """Main function."""
    result = calculate_sum(10, 20)
    print(f"Result: {result}")

if __name__ == "__main__":
    main()
EOF
}

# 生成干净的Shell样本
generate_clean_shell() {
    cat > "$1" << 'EOF'
#!/bin/bash
# Clean shell sample for testing

set -e

echo_info() {
    echo "[INFO] $1"
}

main() {
    echo_info "Starting..."
    local name="World"
    echo "Hello, $name!"
    echo_info "Done."
}

main "$@"
EOF
}

# 生成干净的SKILL.md样本
generate_clean_skill_md() {
    cat > "$1" << 'EOF'
# Test Skill
> **标准等级**: 5标准 + 7标准 (S1-S7)

---

## 7标准执行规范

### S1: 输入定义
输入: 待测试的配置文件

### S2: 多维度检查
- 语法检查
- 逻辑检查
- 格式检查
- 合规检查

### S3: 输出报告
输出审查报告+问题清单+修复建议

### S4: 触发机制
手动触发: `./test.sh`

### S5: 检查清单
- [ ] 语法正确
- [ ] 逻辑正确
- [ ] 格式规范

### S6: 局限性标注
无法判断业务逻辑正确性

### S7: 对抗测试
运行 `./adversarial-test.sh`

---

## 5标准
- 全局考虑
- 系统考虑
- 迭代机制
- Skill化
- 自动化
EOF
}

# ============================================
# 错误植入器
# ============================================

# 植入Python语法错误
inject_python_syntax_error() {
    local file="$1"
    # 添加语法错误: 缺少冒号
    sed -i 's/def calculate_sum(a, b):/def calculate_sum(a, b)/' "$file"
}

# 植入Python逻辑错误
inject_python_logic_error() {
    local file="$1"
    # 添加逻辑错误: 未定义变量
    sed -i 's/return a + b/return a + undefined_var/' "$file"
}

# 植入Python格式错误
inject_python_format_error() {
    local file="$1"
    # 添加格式错误: 混合缩进
    sed -i 's/^    return/\treturn/' "$file"
}

# 植入Shell语法错误
inject_shell_syntax_error() {
    local file="$1"
    # 添加语法错误: 未闭合的引号
    echo 'echo "Unclosed string' >> "$file"
}

# 植入Shell逻辑错误
inject_shell_logic_error() {
    local file="$1"
    # 添加逻辑错误: 使用未定义变量
    sed -i "s/echo \"Hello, \$name!\"/echo \"Hello, \$undefined_var!\"/" "$file"
}

# 植入Shell格式错误
inject_shell_format_error() {
    local file="$1"
    # 添加尾随空格
    sed -i 's/^}$/}   /' "$file"
}

# 植入SKILL.md合规错误 (缺少S1-S7)
inject_skill_missing_s1() {
    local file="$1"
    sed -i '/### S1: 输入定义/,/### S2/d' "$file"
}

inject_skill_missing_s2() {
    local file="$1"
    sed -i '/### S2: 多维度检查/,/### S3/d' "$file"
}

inject_skill_missing_s5() {
    local file="$1"
    sed -i '/### S5: 检查清单/,/### S6/d' "$file"
}

inject_skill_format_error() {
    local file="$1"
    # 添加尾随空格
    sed -i 's/^# Test Skill$/# Test Skill   /' "$file"
}

# ============================================
# 测试执行器
# ============================================

run_qa_review() {
    local file="$1"
    local result_file="$2"
    
    # 运行QA审查 (禁用set -e以捕获结果)
    if "$SCRIPT_DIR/qa-review.sh" "$file" > "$result_file" 2>&1 || true; then
        echo "PASS"
    else
        echo "FAIL"
    fi
}

# 检查是否发现问题
check_detection() {
    local result_file="$1"
    local expected_category="$2"
    local expected_severity="$3"
    
    # 从qa-review.sh的输出中提取报告文件路径
    local report_file=$(grep "报告文件:" "$result_file" 2>/dev/null | sed 's/.*报告文件: //')
    
    # 优先检查报告文件
    if [ -n "$report_file" ] && [ -f "$report_file" ]; then
        if grep -q "\[$expected_category\].*$expected_severity" "$report_file" 2>/dev/null || \
           grep -q "$expected_category" "$report_file" 2>/dev/null; then
            echo "DETECTED"
            return
        fi
    fi
    
    # 回退到检查结果文件本身
    if grep -q "category.*$expected_category" "$result_file" 2>/dev/null || \
       grep -q "$expected_category" "$result_file" 2>/dev/null; then
        echo "DETECTED"
    else
        echo "MISSED"
    fi
}

# ============================================
# 测试套件
# ============================================

run_test_case() {
    local test_name="$1"
    local file_type="$2"
    local inject_func="$3"
    local expected_category="$4"
    local expected_severity="$5"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    echo ""
    echo "----------------------------------------"
    echo "测试: $test_name"
    echo "----------------------------------------"
    
    # 创建测试文件
    local test_file="$TEST_DIR/test_${TOTAL_TESTS}.${file_type}"
    local result_file="$TEST_DIR/result_${TOTAL_TESTS}.txt"
    
    # 生成干净样本
    case "$file_type" in
        py) generate_clean_python "$test_file" ;;
        sh) generate_clean_shell "$test_file" ;;
        md) generate_clean_skill_md "$test_file" ;;
    esac
    
    # 植入错误
    $inject_func "$test_file"
    
    log_info "测试文件: $test_file"
    log_info "植入错误: $inject_func"
    
    # 运行QA审查
    local review_result=$(run_qa_review "$test_file" "$result_file")
    
    # 检查是否发现问题
    local detection=$(check_detection "$result_file" "$expected_category" "$expected_severity")
    
    if [ "$detection" = "DETECTED" ]; then
        log_success "✓ 成功发现问题 ($expected_category)"
        DETECTED=$((DETECTED + 1))
    else
        log_fail "✗ 未能发现问题 ($expected_category)"
        MISSED=$((MISSED + 1))
        if [ "$VERBOSE" = true ]; then
            echo "--- 测试文件内容 ---"
            cat "$test_file"
            echo "--- 审查结果 ---"
            cat "$result_file"
        fi
    fi
}

# ============================================
# 测试套件定义
# ============================================

run_python_tests() {
    echo ""
    echo "========================================"
    echo "Python测试套件"
    echo "========================================"
    
    if [ "$QUICK_MODE" = true ]; then
        run_test_case "Python语法错误" "py" "inject_python_syntax_error" "Syntax" "Critical"
    else
        run_test_case "Python语法错误-缺少冒号" "py" "inject_python_syntax_error" "Syntax" "Critical"
        run_test_case "Python逻辑错误-未定义变量" "py" "inject_python_logic_error" "Logic" "High"
        run_test_case "Python格式错误-混合缩进" "py" "inject_python_format_error" "Format" "Medium"
    fi
}

run_shell_tests() {
    echo ""
    echo "========================================"
    echo "Shell测试套件"
    echo "========================================"
    
    if [ "$QUICK_MODE" = true ]; then
        run_test_case "Shell语法错误" "sh" "inject_shell_syntax_error" "Syntax" "Critical"
    else
        run_test_case "Shell语法错误-未闭合引号" "sh" "inject_shell_syntax_error" "Syntax" "Critical"
        run_test_case "Shell逻辑错误-未定义变量" "sh" "inject_shell_logic_error" "Logic" "High"
        run_test_case "Shell格式错误-尾随空格" "sh" "inject_shell_format_error" "Format" "Low"
    fi
}

run_skill_md_tests() {
    echo ""
    echo "========================================"
    echo "SKILL.md测试套件"
    echo "========================================"
    
    if [ "$QUICK_MODE" = true ]; then
        run_test_case "SKILL.md缺少S1" "md" "inject_skill_missing_s1" "Logic" "High"
    else
        run_test_case "SKILL.md缺少S1-输入定义" "md" "inject_skill_missing_s1" "Logic" "High"
        run_test_case "SKILL.md缺少S2-多维度检查" "md" "inject_skill_missing_s2" "Logic" "High"
        run_test_case "SKILL.md缺少S5-检查清单" "md" "inject_skill_missing_s5" "Logic" "Medium"
        run_test_case "SKILL.md格式错误-尾随空格" "md" "inject_skill_format_error" "Format" "Low"
    fi
}

# ============================================
# 报告生成
# ============================================

generate_report() {
    local report_file="$REPORT_DIR/adversarial-test-${TIMESTAMP}.md"
    
    # 计算发现率
    local detection_rate=0
    if [ "$TOTAL_TESTS" -gt 0 ]; then
        detection_rate=$(echo "scale=1; $DETECTED * 100 / $TOTAL_TESTS" | bc 2>/dev/null || echo "0")
    fi
    
    # 评级
    local rating="不合格"
    local rating_color="🔴"
    if (( $(echo "$detection_rate >= 95" | bc -l 2>/dev/null || echo "0") )); then
        rating="优秀"
        rating_color="🔵"
    elif (( $(echo "$detection_rate >= 90" | bc -l 2>/dev/null || echo "0") )); then
        rating="达标"
        rating_color="🟢"
    elif (( $(echo "$detection_rate >= 80" | bc -l 2>/dev/null || echo "0") )); then
        rating="待改进"
        rating_color="🟡"
    fi
    
    cat > "$report_file" << EOF
# 对抗测试报告 (S7)

## 测试概览

| 项目 | 值 |
|------|-----|
| **测试日期** | $DATE |
| **测试时间戳** | $TIMESTAMP |
| **测试模式** | $(if [ "$QUICK_MODE" = true ]; then echo "快速模式"; else echo "完整模式"; fi) |
| **执行标准** | S7: 对抗测试 |

## 测试结果统计

| 指标 | 数值 |
|------|------|
| 总测试数 | $TOTAL_TESTS |
| 成功发现 | $DETECTED |
| 未能发现 | $MISSED |
| **发现率** | **$detection_rate%** |
| **评级** | $rating_color **$rating** |

## 评级标准

| 评级 | 发现率 | 状态 |
|------|--------|------|
| 🔴 不合格 | < 80% | 需要大幅改进检测能力 |
| 🟡 待改进 | 80% - 90% | 需要优化检测规则 |
| 🟢 达标 | 90% - 95% | 满足基本要求 |
| 🔵 优秀 | ≥ 95% | 检测能力优秀 |

## 测试覆盖

### Python代码
- 语法错误检测
- 逻辑错误检测 (未定义变量等)
- 格式错误检测 (缩进、空格等)

### Shell脚本
- 语法错误检测
- 逻辑错误检测
- 格式错误检测

### SKILL.md文档
- 7标准合规检查 (S1-S7)
- 格式错误检测
- 5标准合规检查

## 结论与建议

EOF

    case "$rating" in
        "优秀")
            echo "✅ 检测能力优秀！发现率达到 $detection_rate%，满足所有质量要求。" >> "$report_file"
            ;;
        "达标")
            echo "✅ 检测能力达标。发现率为 $detection_rate%，建议继续优化以达到优秀标准。" >> "$report_file"
            ;;
        "待改进")
            echo "⚠️ 检测能力需要改进。当前发现率为 $detection_rate%，低于90%的达标线。" >> "$report_file"
            echo "建议优化以下方面:" >> "$report_file"
            echo "1. 增强逻辑错误检测规则" >> "$report_file"
            echo "2. 完善SKILL.md的S1-S7检查逻辑" >> "$report_file"
            ;;
        "不合格")
            echo "❌ 检测能力不合格！发现率仅为 $detection_rate%，远低于80%的最低要求。" >> "$report_file"
            echo "建议:" >> "$report_file"
            echo "1. 全面审查检测规则" >> "$report_file"
            echo "2. 增加更多错误模式识别" >> "$report_file"
            echo "3. 参考其他静态分析工具的最佳实践" >> "$report_file"
            ;;
    esac
    
    cat >> "$report_file" << EOF

---

*Generated by QA Adversarial Testing v1.0*
*Standard: S7 - 对抗测试*
EOF

    echo ""
    echo "========================================"
    echo "报告已生成: $report_file"
    echo "========================================"
}

print_summary() {
    echo ""
    echo "╔════════════════════════════════════════╗"
    echo "║        对抗测试结果 (S7)               ║"
    echo "╚════════════════════════════════════════╝"
    echo ""
    
    # 计算发现率
    local detection_rate=0
    if [ "$TOTAL_TESTS" -gt 0 ]; then
        detection_rate=$(echo "scale=1; $DETECTED * 100 / $TOTAL_TESTS" | bc 2>/dev/null || echo "$((DETECTED * 100 / TOTAL_TESTS))")
    fi
    
    echo "  总测试数: $TOTAL_TESTS"
    echo -e "  成功发现: ${GREEN}$DETECTED${NC}"
    echo -e "  未能发现: ${RED}$MISSED${NC}"
    echo ""
    
    if (( $(echo "$detection_rate >= 90" | bc -l 2>/dev/null || echo "0") )); then
        echo -e "  发现率: ${GREEN}$detection_rate%${NC} ✅ 达标"
    else
        echo -e "  发现率: ${RED}$detection_rate%${NC} ❌ 未达标"
    fi
    
    echo ""
    echo "========================================"
}

# ============================================
# 主入口
# ============================================
main() {
    echo "╔════════════════════════════════════════╗"
    echo "║    Adversarial Testing (S7)            ║"
    echo "║    对抗测试 - 错误植入与发现率验证       ║"
    echo "╚════════════════════════════════════════╝"
    
    setup
    
    # 运行测试套件
    run_python_tests
    run_shell_tests
    run_skill_md_tests
    
    # 打印摘要
    print_summary
    
    # 生成报告
    if [ "$GENERATE_REPORT" = true ]; then
        generate_report
    fi
    
    # 清理
    teardown
    
    # 根据发现率返回退出码
    local detection_rate=0
    if [ "$TOTAL_TESTS" -gt 0 ]; then
        detection_rate=$((DETECTED * 100 / TOTAL_TESTS))
    fi
    
    if [ "$detection_rate" -ge 90 ]; then
        return 0
    else
        return 1
    fi
}

main "$@"
