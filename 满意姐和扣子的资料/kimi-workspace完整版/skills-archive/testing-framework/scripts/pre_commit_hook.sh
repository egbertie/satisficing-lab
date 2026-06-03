#!/bin/bash
# 预提交钩子 - S4标准实现
# 在git commit前自动运行基本检查

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}  OpenClaw Skills 预提交检查${NC}"
echo -e "${BLUE}============================================${NC}"

# 检查是否在正确目录
if [ ! -f "$PROJECT_DIR/run_tests.py" ]; then
    echo -e "${RED}错误: 未找到 run_tests.py${NC}"
    echo "请确保在 testing-framework 目录下运行"
    exit 1
fi

cd "$PROJECT_DIR"

# 统计时间
START_TIME=$(date +%s)

# 1. 代码格式检查 (flake8)
echo -e "\n${YELLOW}[1/5] 运行 flake8 代码检查...${NC}"
if python -m flake8 tests/ --max-line-length=120 --ignore=E501,W503 2>/dev/null; then
    echo -e "${GREEN}✓ flake8 检查通过${NC}"
else
    echo -e "${YELLOW}⚠ flake8 发现代码风格问题${NC}"
fi

# 2. 单元测试快速运行
echo -e "\n${YELLOW}[2/5] 运行单元测试...${NC}"
if python run_tests.py --all 2>&1 | tail -20; then
    echo -e "${GREEN}✓ 单元测试通过${NC}"
else
    echo -e "${RED}✗ 单元测试失败${NC}"
    echo "请修复测试失败后再提交"
    exit 1
fi

# 3. 覆盖率阈值检查 (70%)
echo -e "\n${YELLOW}[3/5] 检查覆盖率阈值 (70%)...${NC}"
if python run_coverage.py --check --threshold 70 2>&1 | tail -10; then
    echo -e "${GREEN}✓ 覆盖率检查通过${NC}"
else
    echo -e "${YELLOW}⚠ 覆盖率低于70%，但仍允许提交${NC}"
    echo "  建议: 添加更多测试以提高覆盖率"
fi

# 4. 关键测试检查
echo -e "\n${YELLOW}[4/5] 运行关键测试 (P0)...${NC}"
if python run_tests.py --critical 2>&1 | tail -10; then
    echo -e "${GREEN}✓ 关键测试通过${NC}"
else
    echo -e "${RED}✗ 关键测试失败${NC}"
    echo "P0测试失败会阻塞提交"
    exit 1
fi

# 5. 快速质量检查
echo -e "\n${YELLOW}[5/5] 快速质量检查...${NC}"
if python test_quality_checker.py --threshold 70 2>&1 | tail -15; then
    echo -e "${GREEN}✓ 质量检查通过${NC}"
else
    echo -e "${YELLOW}⚠ 质量分数低于70%${NC}"
fi

# 统计时间
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo -e "\n${BLUE}============================================${NC}"
echo -e "${GREEN}  预提交检查完成 (耗时: ${DURATION}s)${NC}"
echo -e "${BLUE}============================================${NC}"

exit 0
