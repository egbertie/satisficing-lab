#!/bin/bash
# 质量报告脚本
# 使用方式: ./quality-report.sh [daily|weekly]

PERIOD=$1
WORKSPACE="/root/.openclaw/workspace"
QUALITY_DIR="$WORKSPACE/memory/quality"
DATE=$(date +%Y%m%d)

mkdir -p "$QUALITY_DIR"

echo "=== 质量保证报告 ==="
echo "生成时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 检查质量日志
if [ -f "$QUALITY_DIR/quality-log.jsonl" ]; then
    TOTAL_RECORDS=$(wc -l < "$QUALITY_DIR/quality-log.jsonl")
    echo "📊 总质量记录数: $TOTAL_RECORDS"
    
    if [ "$PERIOD" == "daily" ] || [ -z "$PERIOD" ]; then
        echo ""
        echo "=== 今日质量概况 ==="
        TODAY_COUNT=$(grep "\"date\":\"$DATE\"" "$QUALITY_DIR/quality-log.jsonl" | wc -l)
        echo "今日记录数: $TODAY_COUNT"
        
        # 置信度分布
        echo ""
        echo "📈 置信度分布:"
        grep "\"date\":\"$DATE\"" "$QUALITY_DIR/quality-log.jsonl" | \
            python3 -c "
import sys, json
from collections import defaultdict
stats = defaultdict(int)
for line in sys.stdin:
    try:
        d = json.loads(line)
        stats[d.get('confidence', 'unknown')] += 1
    except: pass
for level, count in sorted(stats.items()):
    bar = '█' * count
    print(f'  {level}: {count} {bar}')
" 2>/dev/null
    fi
    
    # 交叉验证统计
    if [ -d "$QUALITY_DIR/cross-validation" ]; then
        VALIDATION_COUNT=$(find "$QUALITY_DIR/cross-validation" -name "*.md" | wc -l)
        echo ""
        echo "🔄 交叉验证记录: $VALIDATION_COUNT 次"
    fi
else
    echo "暂无质量记录"
fi

echo ""
echo "=== 报告完成 ==="
