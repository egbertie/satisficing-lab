#!/bin/bash
# 全面文件盘点脚本

echo "=========================================="
echo "满意解研究所 - 全文件盘点"
echo "=========================================="
echo ""

WORKSPACE="/root/.openclaw/workspace"

echo "📊 按目录统计："
echo "------------------------------------------"

# 根目录文件
echo -n "根目录 (.md): "
find $WORKSPACE -maxdepth 1 -name "*.md" -type f 2>/dev/null | wc -l

echo -n "根目录 (.py): "
find $WORKSPACE -maxdepth 1 -name "*.py" -type f 2>/dev/null | wc -l

echo -n "根目录 (.json): "
find $WORKSPACE -maxdepth 1 -name "*.json" -type f 2>/dev/null | wc -l

echo ""
echo "📁 关键目录文件数："
echo "------------------------------------------"

echo -n "docs/: "
find $WORKSPACE/docs -type f 2>/dev/null | wc -l

echo -n "memory/: "
find $WORKSPACE/memory -type f 2>/dev/null | wc -l

echo -n "knowledge_base/: "
find $WORKSPACE/knowledge_base -type f 2>/dev/null | wc -l

echo -n "skills/: "
find $WORKSPACE/skills -type f 2>/dev/null | wc -l

echo -n "tools/: "
find $WORKSPACE/tools -type f 2>/dev/null | wc -l

echo -n "scripts/: "
find $WORKSPACE/scripts -type f 2>/dev/null | wc -l

echo -n "feishu_export/: "
find $WORKSPACE/feishu_export -type f 2>/dev/null | wc -l

echo -n "reports/: "
find $WORKSPACE/reports -type f 2>/dev/null | wc -l

echo -n "config/: "
find $WORKSPACE/config -type f 2>/dev/null | wc -l

echo ""
echo "📝 按文件类型统计："
echo "------------------------------------------"

echo -n "Markdown (.md): "
find $WORKSPACE -name "*.md" -type f 2>/dev/null | grep -v ".git" | wc -l

echo -n "Python (.py): "
find $WORKSPACE -name "*.py" -type f 2>/dev/null | grep -v ".git" | wc -l

echo -n "JSON (.json): "
find $WORKSPACE -name "*.json" -type f 2>/dev/null | grep -v ".git" | wc -l

echo -n "HTML (.html): "
find $WORKSPACE -name "*.html" -type f 2>/dev/null | grep -v ".git" | wc -l

echo -n "YAML (.yaml/.yml): "
find $WORKSPACE -name "*.yaml" -o -name "*.yml" -type f 2>/dev/null | grep -v ".git" | wc -l

echo -n "Shell (.sh): "
find $WORKSPACE -name "*.sh" -type f 2>/dev/null | grep -v ".git" | wc -l

echo -n "Text (.txt): "
find $WORKSPACE -name "*.txt" -type f 2>/dev/null | grep -v ".git" | wc -l

echo ""
echo "------------------------------------------"
echo -n "总计文件数: "
find $WORKSPACE -type f \( -name "*.md" -o -name "*.py" -o -name "*.json" -o -name "*.yaml" -o -name "*.yml" -o -name "*.html" -o -name "*.txt" -o -name "*.sh" \) 2>/dev/null | grep -v ".git" | grep -v "node_modules" | wc -l
echo "=========================================="
