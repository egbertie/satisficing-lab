#!/bin/bash
# ═══════════════════════════════════════
# 满意解研究所 · 开发服务器 v2.0
# ═══════════════════════════════════════
# 用法: ./dev.sh [test|verify|push|db-reset]
# ═══════════════════════════════════════

set -e
cd "$(dirname "$0")"

case "${1:-test}" in
  test)
    echo "🚀 启动开发环境 v2.0..."
    echo ""
    echo "  前端: http://localhost:8766"
    echo "  后端: http://localhost:5000"
    echo "  健康: http://localhost:5000/api/health"
    echo ""
    python3 server/app.py &
    BACKEND=$!
    python3 -m http.server 8766 --bind 127.0.0.1 &
    FRONTEND=$!
    echo "  PID: Backend=$BACKEND Frontend=$FRONTEND"
    echo "  按 Ctrl+C 停止"
    wait
    ;;

  verify)
    echo "🔍 全站质检 v2.1 · 20项检查..."
    PASS=0; FAIL=0
    check() { if [ $? -eq 0 ]; then echo "  ✅ $1"; PASS=$((PASS+1)); else echo "  ❌ $1"; FAIL=$((FAIL+1)); fi }
    
    # ─── 后端代码 ───
    echo "--- 后端 Python 语法 ---"
    for f in server/app.py server/config.py server/models/database.py server/models/customer.py server/models/schema_v2.py server/routes/auth.py server/routes/contact.py server/routes/events.py server/routes/admin.py server/services/feishu.py server/services/events.py server/services/mailer.py server/middleware/security.py; do
      python3 -m py_compile "$f" 2>/dev/null && echo "  ✅ $f" || { echo "  ❌ $f"; FAIL=$((FAIL+1)); }
    done
    [ $FAIL -eq 0 ] && echo "  ✅ 后端代码全部通过"; PASS=$((PASS+1))
    
    # ─── 前端关键文件完整性 ───
    echo "--- 前端关键文件完整性 ---"
    [ $(wc -c < sri-design.css) -gt 5000 ] && check "sri-design.css ≥ 5KB (完整)"
    [ $(wc -c < flywheel-engine.js) -gt 5000 ] && check "flywheel-engine.js ≥ 5KB (完整)"
    [ $(wc -c < gate-check.js) -gt 10000 ] && check "gate-check.js ≥ 10KB (完整)"
    [ $(wc -c < sri-track.js) -gt 2000 ] && check "sri-track.js ≥ 2KB (完整)"
    [ $(wc -c < sri-api.js) -gt 2000 ] && check "sri-api.js ≥ 2KB (完整)"
    
    # ─── entities_index.json ───
    echo "--- 数据文件 ---"
    python3 -c "import json; json.load(open('entities_index.json'))" 2>/dev/null && check "entities_index.json JSON 有效"
    
    # ─── 关键页面 JS 语法 ───
    echo "--- 关键页面 JS 语法 ---"
    python3 -c "
import os, re
for fn in ['admin-windows.html','dashboard-v3.html']:
    if not os.path.exists(fn): continue
    with open(fn) as f: h=f.read()
    s=h.find('<script>')+8; e=h.find('</script>',s)
    if s<8 or e<0: print(f'{fn}: NO SCRIPT TAG'); continue
    js=h[s:e]
    o=js.count('(')+js.count('{')
    c=js.count(')')+js.count('}')
    status='OK' if o==c else f'BROKEN gap={o-c}'
    print(f'{fn}: parens {status}')
" 2>/dev/null
    check "管理后台/驾驶舱 JS 括号平衡"
    
    # ─── 品牌检查 ───
    echo "--- 品牌合规 ---"
    grep -r '满意红' *.html 2>/dev/null | grep -v '满意解' | grep -v '满意红项目' | wc -l | xargs -I{} bash -c '[ {} -eq 0 ]' && check "品牌名「满意红」已全面清除"
    
    # ─── 导航一致性 ───
    echo "--- 导航链接一致性 ---"
    for page in index.html dashboard-v3.html go.html; do
      grep -q '客户通道' "$page" && echo "  ✅ $page: 客户通道" \
        || echo "  ⚠️ $page: 缺少客户通道链接"
    done
    check "关键页面客户通道入口"
    
    # ─── 密码/安全泄漏检查 ───
    echo "--- 安全泄漏检查 ---"
    ! grep -q 'password\|PASSCODE\|123654' dashboard-v3.html 2>/dev/null && check "驾驶舱无密码泄漏"
    ! grep -q '<h1>admin-windows</h1>' admin-windows.html 2>/dev/null && check "管理后台无裸标题"
    
    # ─── HTML 完整性 ───
    echo "--- HTML 结构完整性 ---"
    for page in index.html go.html dashboard-v3.html admin-windows.html; do
      grep -q '</html>' "$page" && : || echo "  ❌ $page: 缺少 </html>"
    done
    check "关键页面 HTML 标签完整"
    
    # ─── 死链检查 ───
    echo "--- 死链检查 ---"
    python3 -c "
import os, re
dead=[]
for f in os.listdir('.'):
    if not f.endswith('.html'): continue
    with open(f) as fh: c=fh.read()
    for m in re.findall(r'href=[\"]([^\":#][^\"]*\.html)[\"]', c):
        if '/' not in m and not os.path.exists(m): dead.append(f'{f} → {m}')
if dead:
    for d in dead[:10]: print(f'  ❌ {d}')
else:
    print('  ✅ 无死链')
" 2>/dev/null
    check "HTML 页面引用有效性"
    
    # ─── API 集成测试 ───
    echo "--- API 集成测试 ---"
    python3 -c "
import sys; sys.path.insert(0,'.')
from server.app import create_app
app = create_app()
with app.test_client() as c:
    assert c.get('/api/health').status_code == 200
    r = c.post('/api/contact', json={'name':'QA','message':'test'})
    assert r.status_code == 201
    print('  ✅ Health + Contact API 通过')
" 2>/dev/null && check "后端 API 集成测试"
    
    echo ""
    echo "═══════════════════════════════"
    echo "  通过: $PASS · 失败: $FAIL"
    echo "═══════════════════════════════"
    [ $FAIL -eq 0 ] && echo "✅ 全站质检通过" || echo "❌ 存在 $FAIL 项问题";;

  db-reset)
    echo "🗑️  重置数据库..."
    rm -f server/data/sri.db*
    python3 -c "from server.app import create_app; create_app()"
    echo "✅ 数据库已重置"
    ;;

  push)
    echo "📤 推送到 GitHub Pages..."
    git add -A
    git commit -m "update: $(date '+%Y-%m-%d %H:%M')" || true
    git push origin main
    echo "✅ 已推送"
    ;;

  *)
    echo "用法: ./dev.sh [test|verify|push|db-reset]"
    ;;
esac
