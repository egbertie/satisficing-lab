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
    echo "🔍 代码验证 v2.0..."
    FILES=(
      server/app.py server/config.py
      server/models/database.py server/models/customer.py server/models/schema_v2.py
      server/routes/auth.py server/routes/contact.py server/routes/events.py server/routes/admin.py
      server/services/feishu.py server/services/events.py server/services/mailer.py
      server/middleware/security.py
    )
    for f in "${FILES[@]}"; do
      python3 -m py_compile "$f" && echo "  ✅ $f"
    done
    
    # API 集成测试
    python3 -c "
import sys; sys.path.insert(0,'.')
from server.app import create_app
app = create_app()
with app.test_client() as c:
    assert c.get('/api/health').status_code == 200
    r = c.post('/api/contact', json={'name':'QA','message':'test'})
    assert r.status_code == 201
    print('  ✅ API 集成测试通过')
"
    echo -e "\n✅ 全部验证通过"
    ;;

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
