"""
满意解研究所 · 后端服务器
======================
Flask API 服务器主入口

启动: python3 server/app.py
测试: curl http://localhost:5000/api/health
"""
import sys
from pathlib import Path

# 确保项目根目录在 Python path 中
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from flask import Flask, jsonify, request
from flask_cors import CORS
from server.config import HOST, PORT, DEBUG, CORS_ORIGINS
from server.models.database import migrate


def create_app() -> Flask:
    app = Flask(__name__)

    # CORS：允许前端跨域访问
    CORS(app, origins=CORS_ORIGINS, supports_credentials=True)

    # 初始化数据库
    migrate()

    # 注册路由
    from server.routes.auth import auth_bp
    from server.routes.contact import contact_bp
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(contact_bp, url_prefix="/api")

    # 健康检查
    @app.route("/api/health")
    def health():
        return jsonify({
            "status": "ok",
            "service": "满意解研究所 API v1.0",
            "docs": "/api/health"
        })

    # 全局错误处理
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "接口不存在"}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": "服务器内部错误"}), 500

    # 请求日志
    @app.before_request
    def log_request():
        if request.path.startswith("/api/"):
            print(f"➡️  {request.method} {request.path} from {request.remote_addr}")

    return app


if __name__ == "__main__":
    app = create_app()
    print(f"""
╔══════════════════════════════════════════╗
║   🔥 满意解研究所 · API 服务器 v1.0      ║
║                                          ║
║   地址: http://{HOST}:{PORT}             ║
║   文档: http://{HOST}:{PORT}/api/health   ║
║                                          ║
║   核心接口:                               ║
║   POST /api/auth/register  客户注册       ║
║   POST /api/auth/login     客户登录       ║
║   GET  /api/auth/me        当前用户       ║
║   POST /api/contact        客户留言       ║
║   GET  /api/deliveries     已购产品       ║
║   GET  /api/profile        客户档案       ║
║                                          ║
╚══════════════════════════════════════════╝
    """)
    app.run(host=HOST, port=PORT, debug=DEBUG)
