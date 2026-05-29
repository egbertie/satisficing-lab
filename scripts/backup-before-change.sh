#!/bin/bash
# 修改页面前自动备份
# 用法: bash scripts/backup-before-change.sh dashboard.html

FILE="$1"
SITE="/Users/egbertielau/.openclaw/workspace/site"
BACKUP_DIR="$SITE/.bak"

if [ -z "$FILE" ]; then
  echo "用法: bash backup-before-change.sh <页面名.html>"
  exit 1
fi

mkdir -p "$BACKUP_DIR"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP="$BACKUP_DIR/${FILE%.html}_${TIMESTAMP}.html"
cp "$SITE/$FILE" "$BACKUP"
echo "✅ 已备份: $FILE → $(basename $BACKUP)"

# 打tag
cd "$SITE"
TAG="${FILE%.html}-v$(date +%Y%m%d%H%M)"
git tag "$TAG"
echo "✅ 已打tag: $TAG"
