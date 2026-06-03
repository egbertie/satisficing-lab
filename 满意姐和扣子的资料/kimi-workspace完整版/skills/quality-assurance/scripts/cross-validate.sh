#!/bin/bash
# 交叉验证记录脚本
# 使用方式: ./cross-validate.sh "需要验证的决策内容"

CONTENT=$1
WORKSPACE="/root/.openclaw/workspace"
VALIDATION_DIR="$WORKSPACE/memory/quality/cross-validation"

if [ -z "$CONTENT" ]; then
    echo "使用方式: $0 '需要验证的决策内容'"
    echo ""
    echo "最近交叉验证记录:"
    ls -la "$VALIDATION_DIR"/*.md 2>/dev/null | tail -10 || echo "  无记录"
    exit 1
fi

mkdir -p "$VALIDATION_DIR"

TIMESTAMP=$(date +%Y%m%d-%H%M%S)
VALIDATION_FILE="$VALIDATION_DIR/${TIMESTAMP}.md"

cat > "$VALIDATION_FILE" << EOF
# 交叉验证记录

## 验证时间
$(date '+%Y-%m-%d %H:%M:%S')

## 待验证内容
$CONTENT

## 模型A响应 (当前模型)
待记录...

## 模型B响应 (验证模型)
待记录...

## 一致性评估
- 一致性评分: 待评估
- 差异点: 待记录
- 建议: 待生成

## 验证结论
待生成...

---
*交叉验证进行中，请用另一模型运行相同问题后补充结果*
EOF

echo "✅ 交叉验证记录已创建: $VALIDATION_FILE"
echo ""
echo "📋 下一步操作:"
echo "1. 使用另一模型询问相同问题"
echo "2. 将两个模型的响应补充到该文件中"
echo "3. 评估一致性并生成结论"
