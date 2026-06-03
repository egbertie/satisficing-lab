#!/bin/bash
# 防复发Git Hooks — Pre-commit Hook
# 命名空间: NGT-HOOKS-v1.0-FIN-260327

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🔍 Running pre-commit checks..."

# 检查1: 敏感信息扫描
echo "📋 Check 1: Scanning for sensitive information..."
SENSITIVE_PATTERNS=(
    "api_key"
    "apikey"
    "api-key"
    "password"
    "passwd"
    "secret"
    "token"
    "ghp_"
    "sk-"
    "AKIA"  # AWS Key
)

FOUND_SENSITIVE=false
for pattern in "${SENSITIVE_PATTERNS[@]}"; do
    if git diff --cached --name-only | xargs grep -l "$pattern" 2>/dev/null; then
        echo -e "${RED}❌ Found sensitive pattern: $pattern${NC}"
        FOUND_SENSITIVE=true
    fi
done

if [ "$FOUND_SENSITIVE" = true ]; then
    echo -e "${RED}❌ Commit blocked: Sensitive information detected${NC}"
    echo "Please remove sensitive data before committing."
    exit 1
fi

# 检查2: 大文件检测
echo "📋 Check 2: Checking for large files..."
MAX_SIZE=10485760  # 10MB
LARGE_FILES=$(git diff --cached --name-only | while read file; do
    if [ -f "$file" ]; then
        SIZE=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null)
        if [ "$SIZE" -gt "$MAX_SIZE" ]; then
            echo "$file ($SIZE bytes)"
        fi
    fi
done)

if [ ! -z "$LARGE_FILES" ]; then
    echo -e "${YELLOW}⚠️  Large files detected:${NC}"
    echo "$LARGE_FILES"
    echo "Consider using Git LFS for large files."
fi

# 检查3: 未跟踪的私有文件
echo "📋 Check 3: Checking for untracked private files..."
PRIVATE_PATTERNS=(
    ".env"
    ".env.local"
    ".env.production"
    "*.pem"
    "*.key"
    "config.local.yaml"
)

for pattern in "${PRIVATE_PATTERNS[@]}"; do
    if git ls-files --others --exclude-standard | grep -q "$pattern"; then
        echo -e "${YELLOW}⚠️  Untracked private files matching: $pattern${NC}"
    fi
done

# 检查4: 文件名规范
echo "📋 Check 4: Checking filename conventions..."
INVALID_NAMES=$(git diff --cached --name-only | grep -E '[[:space:]]' || true)

if [ ! -z "$INVALID_NAMES" ]; then
    echo -e "${YELLOW}⚠️  Files with spaces in names:${NC}"
    echo "$INVALID_NAMES"
fi

# 检查5:  trailing whitespace
echo "📋 Check 5: Checking for trailing whitespace..."
if git diff --cached --check; then
    echo -e "${GREEN}✅ No trailing whitespace issues${NC}"
fi

# 检查6: YAML/JSON语法验证
echo "📋 Check 6: Validating YAML/JSON files..."
git diff --cached --name-only | grep -E '\.(yaml|yml|json)$' | while read file; do
    if [ -f "$file" ]; then
        if [[ "$file" == *.json ]]; then
            if ! python3 -c "import json; json.load(open('$file'))" 2>/dev/null; then
                echo -e "${RED}❌ Invalid JSON: $file${NC}"
                exit 1
            fi
        elif [[ "$file" == *.yaml ]] || [[ "$file" == *.yml ]]; then
            if ! python3 -c "import yaml; yaml.safe_load(open('$file'))" 2>/dev/null; then
                echo -e "${RED}❌ Invalid YAML: $file${NC}"
                exit 1
            fi
        fi
    fi
done

echo -e "${GREEN}✅ All pre-commit checks passed${NC}"
exit 0
