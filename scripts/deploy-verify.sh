#!/bin/bash
# 部署后自动验证
# 用法: bash scripts/deploy-verify.sh

SITE="/Users/egbertielau/.openclaw/workspace/site"
FAIL=0

echo "🚀 部署验证 $(date '+%H:%M:%S')"
echo ""

# 等待GitHub Pages更新
echo "⏳ 等待GitHub Pages CDN更新..."
sleep 5

# 检查关键页面是否200
PAGES=("index.html" "dashboard.html" "cases.html" "about.html" "decision-theatre.html" "checklist.html" "gate.html")
for p in "${PAGES[@]}"; do
  CODE=$(curl -sI "https://egbertie.github.io/satisficing-lab/$p" -o /dev/null -w '%{http_code}')
  if [ "$CODE" = "200" ]; then
    echo "   ✅ $p"
  else
    echo "   ❌ $p (HTTP $CODE)"
    FAIL=$((FAIL+1))
  fi
done

# MD5一致性
echo ""
echo "📋 MD5一致性"
for p in dashboard.html cases.html index.html; do
  L=$(md5 -q "$SITE/$p" 2>/dev/null)
  R=$(curl -sL "https://egbertie.github.io/satisficing-lab/$p" 2>/dev/null | md5 -q 2>/dev/null)
  if [ "$L" = "$R" ] && [ -n "$L" ]; then
    echo "   ✅ $p"
  else
    echo "   ❌ $p (本地:$L 线上:$R)"
    FAIL=$((FAIL+1))
  fi
done

echo ""
if [ $FAIL -eq 0 ]; then
  echo "✅ 全部验证通过！"
else
  echo "❌ $FAIL 项验证失败"
  exit 1
fi
