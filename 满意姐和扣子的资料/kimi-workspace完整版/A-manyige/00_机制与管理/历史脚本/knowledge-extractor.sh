#!/bin/bash
# 知识萃取脚本 - 每日对话自动提炼
# 创建时间: 2026-03-20
# 用途: 从每日对话中提取知识入图谱

WORKSPACE="/root/.openclaw/workspace"
TODAY=$(date +%Y-%m-%d)
LOG_FILE="$WORKSPACE/logs/knowledge-extraction.log"
OUTPUT_FILE="$WORKSPACE/memory/knowledge_extracted_$TODAY.json"

echo "=== 每日知识萃取 ===" | tee -a $LOG_FILE
echo "日期: $TODAY" | tee -a $LOG_FILE

# 读取今日memory文件
MEMORY_FILE="$WORKSPACE/memory/$TODAY.md"

if [ ! -f "$MEMORY_FILE" ]; then
    echo "⚠️ 今日memory文件不存在" | tee -a $LOG_FILE
    exit 0
fi

# 提取关键信息
echo "提取关键信息..." | tee -a $LOG_FILE

# 1. 提取决策
echo "  - 提取决策..." | tee -a $LOG_FILE
DECISIONS=$(grep -E "^##.*-.*决策|决定|确认" "$MEMORY_FILE" | head -10)

# 2. 提取新信息
echo "  - 提取新信息..." | tee -a $LOG_FILE
NEW_INFO=$(grep -E "发现|新增|创建|完成" "$MEMORY_FILE" | head -10)

# 3. 提取待办
echo "  - 提取待办..." | tee -a $LOG_FILE
TODOS=$(grep -E "\[ \]|待办|TODO" "$MEMORY_FILE" | head -10)

# 4. 生成JSON输出
cat > "$OUTPUT_FILE" << EOF
{
  "date": "$TODAY",
  "extraction_time": "$(date -Iseconds)",
  "source": "$MEMORY_FILE",
  "decisions": [
$(echo "$DECISIONS" | sed 's/^/    "/; s/$/",/' | sed '$ s/,$//')
  ],
  "new_information": [
$(echo "$NEW_INFO" | sed 's/^/    "/; s/$/",/' | sed '$ s/,$//')
  ],
  "todos": [
$(echo "$TODOS" | sed 's/^/    "/; s/$/",/' | sed '$ s/,$//')
  ]
}
EOF

echo "✅ 知识萃取完成: $OUTPUT_FILE" | tee -a $LOG_FILE

# 可选: 自动更新知识图谱
# python3 $WORKSPACE/scripts/update-knowledge-graph.py "$OUTPUT_FILE"

echo "=== 萃取结束 ===" | tee -a $LOG_FILE
