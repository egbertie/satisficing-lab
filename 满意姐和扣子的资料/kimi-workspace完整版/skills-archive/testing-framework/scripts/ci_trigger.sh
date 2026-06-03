#!/bin/bash
# CI触发脚本 - S4标准实现
# 用于在CI/CD环境中触发测试

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查依赖
check_dependencies() {
    log_info "检查依赖..."
    
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 未安装"
        exit 1
    fi
    
    if ! command -v pip &> /dev/null; then
        log_error "pip 未安装"
        exit 1
    fi
}

# 安装依赖
install_deps() {
    log_info "安装测试依赖..."
    cd "$PROJECT_DIR"
    pip install -q -r requirements.txt
}

# 预检查
precheck() {
    log_info "运行预检查..."
    
    # 检查skills目录变更
    if git diff --name-only HEAD^ HEAD 2>/dev/null | grep -q "skills/"; then
        log_info "检测到Skill变更，需要运行测试"
        return 0
    else
        log_warn "无Skill变更，跳过测试"
        return 1
    fi
}

# 运行静态分析
run_static_analysis() {
    log_info "运行静态分析..."
    cd "$PROJECT_DIR"
    
    # flake8检查
    log_info "  - flake8代码检查"
    python -m flake8 tests/ --max-line-length=120 --ignore=E501,W503 || true
    
    # black格式检查
    log_info "  - black格式检查"
    python -m black --check tests/ || log_warn "格式检查失败，建议运行: black tests/"
    
    # isort导入检查
    log_info "  - isort导入检查"
    python -m isort --check-only tests/ || true
}

# 运行单元测试
run_unit_tests() {
    log_info "运行单元测试..."
    cd "$PROJECT_DIR"
    python run_tests.py --all
}

# 运行集成测试
run_integration_tests() {
    log_info "运行集成测试..."
    cd "$PROJECT_DIR"
    python -m pytest tests/integration -v --tb=short
}

# 运行E2E测试
run_e2e_tests() {
    log_info "运行端到端测试..."
    cd "$PROJECT_DIR"
    python -m pytest tests/e2e -v --tb=short
}

# 运行覆盖率检查
run_coverage_check() {
    log_info "运行覆盖率检查..."
    cd "$PROJECT_DIR"
    python run_coverage.py --threshold 80
}

# 运行测试质量检查
run_quality_check() {
    log_info "运行测试质量自检..."
    cd "$PROJECT_DIR"
    python test_quality_checker.py --threshold 80
}

# 运行对抗测试
run_adversarial_tests() {
    log_info "运行对抗测试..."
    cd "$PROJECT_DIR"
    python adversarial_test.py --threshold 90
}

# 生成报告
generate_reports() {
    log_info "生成测试报告..."
    cd "$PROJECT_DIR"
    
    # 覆盖率报告
    python run_coverage.py
    
    # 缺陷报告
    python defect_tracker.py --report
    
    # 质量报告
    python test_quality_checker.py --report
}

# 主函数
main() {
    local test_type="${1:-all}"
    
    log_info "开始CI测试流程 - 类型: $test_type"
    
    check_dependencies
    install_deps
    
    case "$test_type" in
        precheck)
            precheck
            ;;
        static)
            run_static_analysis
            ;;
        unit)
            run_unit_tests
            ;;
        integration)
            run_integration_tests
            ;;
        e2e)
            run_e2e_tests
            ;;
        coverage)
            run_coverage_check
            ;;
        quality)
            run_quality_check
            ;;
        adversarial)
            run_adversarial_tests
            ;;
        all|full)
            precheck || exit 0
            run_static_analysis
            run_unit_tests
            run_integration_tests
            run_e2e_tests
            run_coverage_check
            run_quality_check
            run_adversarial_tests
            generate_reports
            ;;
        *)
            echo "用法: $0 {precheck|static|unit|integration|e2e|coverage|quality|adversarial|all}"
            exit 1
            ;;
    esac
    
    log_info "CI测试流程完成"
}

main "$@"
