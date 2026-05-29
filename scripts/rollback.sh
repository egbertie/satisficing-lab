#!/bin/bash
# 回滚到指定tag或备份
# 用法: bash scripts/rollback.sh dashboard.html [tag名]
#      bash scripts/rollback.sh dashboard.html  (列出可选tag)
FILE="$1"
TAG="$2"
SITE="/Users/egbertielau/.openclaw/workspace/site"

if [ -z "$FILE" ]; then
  echo "用法: bash rollback.sh <页面名.html> [tag]"
  exit 1
fi

cd "$SITE"

if [ -z "$TAG" ]; then
  echo "📋 $FILE 可用版本:"
  git tag | grep "${FILE%.html}" | tail -10
  echo ""
  echo "最近的备份:"
  ls -t ".bak/${FILE%.html}_"* 2>/dev/null | head -5
  echo ""
  echo "用法: bash rollback.sh $FILE <tag名>"
  exit 0
fi

# 回滚
cp "$SITE/$FILE" "$SITE/.bak/${FILE%.html}_ROLLBACK_$(date +%Y%m%d_%H%M%S).html"
git checkout "$TAG" -- "$FILE"
echo "✅ 已回滚 $FILE → $TAG"
echo "   原版本备份在 .bak/ 目录"
git add "$FILE"
git commit -m "revert: $FILE 回滚到 $TAG"
git push origin main
