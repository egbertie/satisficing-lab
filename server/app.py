"""
满意解研究所 · API 服务器 v2.0
=============================
前端-中端-后端-驾驶舱 四层统一架构

启动: python3 server/app.py
"""
import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from flask import Flask, jsonify, request
from flask_cors import CORS
from server.config import HOST, PORT, DEBUG, CORS_ORIGINS
from server.models.database import migrate
from server.middleware.security import log_api_request


def create_app() -> Flask:
    app = Flask(__name__)

    # CORS
    CORS(app, origins=CORS_ORIGINS, supports_credentials=True)

    # 数据库
    migrate()

    # ─── 注册路由蓝图 ───
    from server.routes.auth import auth_bp
    from server.routes.contact import contact_bp
    from server.routes.events import event_bp
    from server.routes.admin import admin_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(contact_bp, url_prefix="/api")
    app.register_blueprint(event_bp, url_prefix="/api")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")

    # ─── 请求日志 ───
    app.after_request(log_api_request)

    # ─── 健康检查 ───
    @app.route("/api/health")
    def health():
        from server.models.database import query
        db_ok = True
        try:
            query("SELECT 1")
        except:
            db_ok = False
        
        return jsonify({
            "status": "ok" if db_ok else "degraded",
            "version": "2.0.0",
            "service": "满意解研究所 API",
            "database": "connected" if db_ok else "disconnected",
            "modules": {
                "auth": True,
                "events": True,
                "delivery": True,
                "email": True,
                "referral": True,
                "admin": True,
            },
            "docs": {
                "register": "POST /api/auth/register",
                "login": "POST /api/auth/login",
                "events": "POST /api/track",
                "contact": "POST /api/contact",
                "admin": "GET /api/admin/dashboard/summary",
            }
        })

    # ─── 错误处理 ───
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "接口不存在", "code": 404}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": "服务器内部错误", "code": 500}), 500

    # ─── 请求日志（控制台）───
    @app.before_request
    def log():
        if request.path.startswith("/api/"):
            print(f"➡️  {request.method} {request.path} [{request.remote_addr}]")

    return app


# Gunicorn entry point (for production deployment)
app = create_app()


if __name__ == "__main__":
    app = create_app()
    print(f"""
╔══════════════════════════════════════════════╗
║   🔥 满意解研究所 · API 服务器 v2.0         ║
║                                              ║
║   地址: http://{HOST}:{PORT}                ║
║   健康: http://{HOST}:{PORT}/api/health      ║
║                                              ║
║   🏠 前端层                                   ║
║   POST /api/track         事件上报            ║
║   POST /api/auth/register 客户注册            ║
║   POST /api/auth/login    客户登录            ║
║   POST /api/contact       客户留言            ║
║   GET  /api/deliveries    已购产品            ║
║                                              ║
║   ⚙️ 中端层                                   ║
║   POST /api/track         行为事件采集        ║
║   POST /api/session/*     会话管理            ║
║                                              ║
║   💾 后端层                                   ║
║   飞书邮箱 API  ·  飞书通知  ·  多维表格同步    ║
║                                              ║
║   📊 驾驶舱层                                ║
║   GET  /api/admin/dashboard/summary 总览      ║
║   GET  /api/admin/dashboard/funnel  漏斗      ║
║   GET  /api/admin/dashboard/dau     日活      ║
║   GET  /api/admin/dashboard/products 产品    ║
║                                              ║
╚══════════════════════════════════════════════╝
    """)
    app.run(host=HOST, port=PORT, debug=DEBUG)
