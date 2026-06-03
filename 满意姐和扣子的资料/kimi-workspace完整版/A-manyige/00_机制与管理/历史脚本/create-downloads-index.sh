#!/bin/bash
# create-downloads-index.sh - 创建Downloads目录文件索引
# 用途: 立即知道downloads目录里有什么
# 执行频率: 按需（建议每日一次）

set -e

WORKSPACE="/root/.openclaw/workspace"
DOWNLOADS="/root/openclaw/kimi/downloads"
INDEX_FILE="$WORKSPACE/docs/DOWNLOADS_INDEX.md"

echo "正在生成Downloads目录索引..."

# 创建文档头
cat > "$INDEX_FILE" << EOF
# Downloads目录文件索引

**生成时间**: $(date '+%Y-%m-%d %H:%M:%S')  
**总文件数**: $(ls "$DOWNLOADS" 2>/dev/null | wc -l)  
**总大小**: $(du -sh "$DOWNLOADS" 2>/dev/null | cut -f1)

---

## 统计概览

| 类型 | 数量 | 建议操作 |
|------|------|----------|
| Word文档 (.docx) | $(ls $DOWNLOADS/*.docx 2>/dev/null | wc -l) | 归档到知识库 |
| Markdown (.md) | $(ls $DOWNLOADS/*.md 2>/dev/null | wc -l) | 分类整理 |
| 图片文件 | $(ls $DOWNLOADS/*.{png,jpg,jpeg,gif} 2>/dev/null | wc -l) | 移入素材库 |
| Python脚本 | $(ls $DOWNLOADS/*.py 2>/dev/null | wc -l) | 评估后归档 |
| Shell脚本 | $(ls $DOWNLOADS/*.sh 2>/dev/null | wc -l) | 评估后归档 |
| 其他 | $(ls $DOWNLOADS/* 2>/dev/null | wc -l) | 人工审查 |

---

## 紧急处理建议

EOF

# 检查文件数量并给出建议
FILE_COUNT=$(ls "$DOWNLOADS" 2>/dev/null | wc -l)
if [ $FILE_COUNT -gt 1000 ]; then
    echo "⚠️ **警告**: Downloads目录文件数超过1000，建议立即整理" >> "$INDEX_FILE"
elif [ $FILE_COUNT -gt 500 ]; then
    echo "⚡ **提醒**: Downloads目录文件数超过500，建议本周内整理" >> "$INDEX_FILE"
else
    echo "✅ **正常**: Downloads目录文件数在合理范围内" >> "$INDEX_FILE"
fi

# 添加详细文件列表
cat >> "$INDEX_FILE" << EOF

---

## Word文档详细列表 (最近20个)

EOF

ls -lt "$DOWNLOADS"/*.docx 2>/dev/null | head -20 >> "$INDEX_FILE" || echo "无Word文档" >> "$INDEX_FILE"

cat >> "$INDEX_FILE" << EOF

---

## Markdown文件详细列表 (最近20个)

EOF

ls -lt "$DOWNLOADS"/*.md 2>/dev/null | head -20 >> "$INDEX_FILE" || echo "无Markdown文档" >> "$INDEX_FILE"

cat >> "$INDEX_FILE" << EOF

---

## 处理清单

- [ ] 已识别需要归档的文档
- [ ] 已删除临时文件
- [ ] 已移动重要文件到workspace
- [ ] 已更新文件索引

---

*索引由 create-downloads-index.sh 自动生成*
EOF

echo "✅ 索引已生成: $INDEX_FILE"
