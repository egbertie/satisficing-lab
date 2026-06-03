#!/bin/bash
# ===========================================
# 满意解研究所 · 开发服务器启动脚本
# ===========================================
# 用法: ./dev.sh [test|verify|push]
#   test   - 启动本地测试服务器（前端+后端）
#   verify - 运行代码检查
#   push   - 推送到 GitHub Pages
# ===========================================

set -e
cd "$(dirname "$0")"

case "${1:-test}" in
  test)
    echo "🚀 启动开发环境..."
    echo ""
    echo "  前端: http://localhost:8766"
    echo "  后端: http://localhost:5000"
    echo "  健康: http://localhost:5000/api/health"
    echo ""
    # 启动后端
    python3 server/app.py &
    BACKEND_PID=$!
    # 启动前端
    python3 -m http.server 8766 --bind 127.0.0.1 &
    FRONTEND_PID=$!
    echo "  PID: Backend=$BACKEND_PID Frontend=$FRONTEND_PID"
    echo "  按 Ctrl+C 停止所有服务"
    wait
    ;;

  verify)
    echo "🔍 代码验证..."
    # Python 语法
    python3 -m py_compile server/app.py && echo "  ✅ server/app.py"
    python3 -m py_compile server/config.py && echo "  ✅ server/config.py"
    python3 -m py_compile server/models/database.py && echo "  ✅ server/models/database.py"
    python3 -m py_compile server/models/customer.py && echo "  ✅ server/models/customer.py"
    python3 -m py_compile server/routes/auth.py && echo "  ✅ server/routes/auth.py"
    python3 -m py_compile server/routes/contact.py && echo "  ✅ server/routes/contact.py"
    python3 -m py_compile server/services/feishu.py && echo "  ✅ server/services/feishu.py"
    # API 测试
    python3 -c "
import sys; sys.path.insert(0,'.')
from server.app import create_app
app = create_app()
with app.test_client() as c:
    assert c.get('/api/health').status_code == 200
    print('  ✅ /api/health')
    r = c.post('/api/contact', json={'name':'QA','message':'test'})
    assert r.status_code == 201
    print('  ✅ /api/contact')
print('\\n✅ 全部验证通过')
"
    ;;

  push)
    echo "📤 推送到 GitHub Pages..."
    git add -A
    git commit -m "update: $(date '+%Y-%m-%d %H:%M')" || true
    git push origin main
    echo "✅ 已推送"
    ;;

  *)
    echo "用法: ./dev.sh [test|verify|push]"
    ;;
esac
