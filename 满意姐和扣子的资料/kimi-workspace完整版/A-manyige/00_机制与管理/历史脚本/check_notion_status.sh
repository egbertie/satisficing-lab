#!/bin/bash
# 生成Notion同步状态报告

echo "========================================"
echo "📊 Notion 同步状态报告"
echo "========================================"
echo "生成时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 统计本地文件
echo "📁 本地文件统计:"
TOTAL=$(find /root/.openclaw/workspace -type f \( -name "*.md" -o -name "*.html" -o -name "*.py" -o -name "*.json" -o -name "*.txt" -o -name "*.js" -o -name "*.css" -o -name "*.yml" -o -name "*.yaml" \) ! -path "*/.git/*" ! -path "*/node_modules/*" | wc -l)
echo "  • 总文件数: $TOTAL"

# 按类型统计
echo ""
echo "📂 文件类型分布:"
for ext in md html py json txt js css yml yaml; do
    count=$(find /root/.openclaw/workspace -type f -name "*.$ext" ! -path "*/.git/*" ! -path "*/node_modules/*" | wc -l)
    [ $count -gt 0 ] && echo "  • .$ext: $count 个"
done

# 关键目录统计
echo ""
echo "📂 关键目录文件数:"
for dir in docs memory knowledge_base tools skills scripts; do
    if [ -d "/root/.openclaw/workspace/$dir" ]; then
        count=$(find "/root/.openclaw/workspace/$dir" -type f \( -name "*.md" -o -name "*.html" -o -name "*.py" -o -name "*.json" -o -name "*.txt" \) 2>/dev/null | wc -l)
        echo "  • $dir/: $count 个文件"
    fi
done

# Notion状态
echo ""
echo "☁️ Notion状态:"
NOTION_COUNT=$(curl -s -X POST "https://api.notion.com/v1/search" \
    -H "Authorization: Bearer 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" \
    -H "Notion-Version: 2022-06-28" \
    -H "Content-Type: application/json" \
    -d '{"query":"","page_size":100}' | \
    python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d.get('results',[])))" 2>/dev/null)
echo "  • Notion中已有: $NOTION_COUNT 个页面"

# 同步进度（从日志读取）
echo ""
echo "🔄 同步进度:"
if [ -f /root/.openclaw/workspace/.notion_bg_sync.log ]; then
    tail -5 /root/.openclaw/workspace/.notion_bg_sync.log
else
    echo "  • 后台同步日志尚未生成"
fi

# 计算
echo ""
echo "📈 同步统计:"
NEED_SYNC=$((TOTAL - NOTION_COUNT))
echo "  • 总文件: $TOTAL"
echo "  • 已同步: $NOTION_COUNT"
echo "  • 待同步: $NEED_SYNC"
if [ $TOTAL -gt 0 ]; then
    PERCENT=$((NOTION_COUNT * 100 / TOTAL))
    echo "  • 完成率: $PERCENT%"
fi

echo ""
echo "========================================"
echo "Notion工作空间: 满意解研究所"
echo "知识库链接: https://notion.so/31fa8a0e2bba81fab98ad61da835051e"
echo "========================================"
