#!/bin/bash
# ============================================
# 满意解研究所 · 本地测试 & 定版脚本
# ============================================
cd "$(dirname "$0")"

PASS=0; FAIL=0
check() { if [ "$2" = "0" ]; then echo "  ✅ $1"; PASS=$((PASS+1)); else echo "  ❌ $1"; FAIL=$((FAIL+1)); fi; }
check_inv() { if [ "$2" != "0" ]; then echo "  ✅ $1"; PASS=$((PASS+1)); else echo "  ❌ $1 (不应存在)"; FAIL=$((FAIL+1)); fi; }

verify() {
  PASS=0; FAIL=0

  echo "--- 语法检查 ---"
  node -e "const vm=require('vm');const js=require('fs').readFileSync('dashboard-v3.html','utf8').match(/<script>([\\s\\S]*?)<\\/script>/)[1];new vm.Script(js)" 2>/dev/null && R=0 || R=1
  check "dashboard-v3.html" $R
  node -e "const vm=require('vm');const js=require('fs').readFileSync('admin-tools.html','utf8').match(/<script>([\\s\\S]*?)<\\/script>/)[1];new vm.Script(js)" 2>/dev/null && R=0 || R=1
  check "admin-tools.html" $R

  echo "--- 品牌检查 ---"
  C=$(grep -r "满意红" *.html 2>/dev/null | grep -v ".bak" | wc -l | tr -d ' ')
  check "满意红已清零" "$([ "$C" = "0" ] && echo 0 || echo 1)"

  echo "--- escHtml / 误替换检查 ---"
  grep -q "function escHtml" dashboard-v3.html; check "escHtml定义" $?
  grep -q "function h(" dashboard-v3.html; check_inv "function h已移除" $?
  grep -q "pusescHtml" dashboard-v3.html; check_inv "无push误替换" $?
  grep -q "fetcescHtml" dashboard-v3.html; check_inv "无fetch误替换" $?

  echo "--- 数据文件 ---"
  python3 -c "import json;json.load(open('entities_index.json'))" 2>/dev/null && R=0 || R=1
  check "entities_index.json有效" $R
  python3 -c "import json;json.load(open('open_tasks_audit.json'))" 2>/dev/null && R=0 || R=1
  check "open_tasks_audit.json有效" $R

  echo ""
  echo "================ 验收: $PASS / $((PASS+FAIL)) 通过 ================"
  return $FAIL
}

case "${1:-help}" in
  test)
    echo "🏠 满意解研究所 · 本地测试"
    echo "   打开: http://localhost:8766/index.html"
    echo "   Ctrl+C 停止"
    python3 devserver.py 8766
    ;;
  verify)
    verify
    ;;
  push)
    verify || { echo "❌ 验收未通过，取消推送"; exit 1; }
    echo ""
    read -p "推送至 GitHub？[y/N] " yn
    [ "$yn" != "y" ] && { echo "已取消"; exit 0; }
    git add -A
    git commit -m "定版: $(date '+%Y-%m-%d %H:%M')" || echo "(无变更)"
    git pull --rebase && git push
    echo "✅ 已推送。https://egbertie.github.io/satisficing-lab/"
    ;;
  *)
    echo "满意解研究所 · 开发工具"
    echo "  ./dev.sh test      本地测试 (localhost:8766)"
    echo "  ./dev.sh verify    代码验收"
    echo "  ./dev.sh push      验收+推送"
    ;;
esac
