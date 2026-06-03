"""
满意解研究所 · 认证路由
===================
POST /api/auth/register  - 注册
POST /api/auth/login     - 登录
GET  /api/auth/me        - 获取当前用户
POST /api/auth/logout    - 登出
"""
from flask import Blueprint, request, jsonify, g
from server.models.customer import (
    create_customer, authenticate, get_customer_by_id,
    update_customer, sanitize_customer
)
from server.services.feishu import (
    notify_new_customer, sync_customer_to_bitable
)

auth_bp = Blueprint("auth", __name__)


def require_auth():
    """从请求头提取并验证 JWT"""
    from server.models.customer import decode_token, get_customer_by_id
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None

    token = auth_header[7:]
    payload = decode_token(token)
    if not payload:
        return None

    customer = get_customer_by_id(payload["customer_id"])
    if not customer:
        return None

    return customer


@auth_bp.route("/register", methods=["POST"])
def register():
    """客户注册"""
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = (data.get("password") or "").strip()

    # 基础验证
    if not email or "@" not in email:
        return jsonify({"error": "请输入有效的邮箱地址"}), 400
    if len(password) < 6:
        return jsonify({"error": "密码至少6位"}), 400

    # 检查是否已注册
    from server.models.customer import get_customer_by_email
    if get_customer_by_email(email):
        return jsonify({"error": "该邮箱已注册，请直接登录"}), 409

    # 创建客户
    customer = create_customer(
        email=email, password=password,
        name=data.get("name", ""),
        phone=data.get("phone", ""),
        company=data.get("company", ""),
        position=data.get("position", ""),
        industry=data.get("industry", ""),
        stage=data.get("stage", ""),
        source=data.get("source", ""),
        interests=data.get("interests", ""),
    )

    if not customer:
        return jsonify({"error": "注册失败，请稍后重试"}), 500

    # 登录（自动）
    result = authenticate(email, password)
    if not result:
        return jsonify({"error": "注册成功但自动登录失败，请手动登录"}), 500

    # 飞书通知 + 同步
    notify_new_customer(customer)
    sync_customer_to_bitable(customer)

    return jsonify({
        "ok": True,
        "token": result["token"],
        "customer": result["customer"],
        "message": "注册成功！"
    }), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    """客户登录"""
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = (data.get("password") or "").strip()

    if not email or not password:
        return jsonify({"error": "请输入邮箱和密码"}), 400

    result = authenticate(email, password)
    if not result:
        return jsonify({"error": "邮箱或密码错误"}), 401

    return jsonify({
        "ok": True,
        "token": result["token"],
        "customer": result["customer"],
    })


@auth_bp.route("/me", methods=["GET"])
def me():
    """获取当前登录用户信息"""
    customer = require_auth()
    if not customer:
        return jsonify({"error": "未登录或 token 已过期"}), 401

    return jsonify({
        "ok": True,
        "customer": sanitize_customer(customer)
    })


@auth_bp.route("/logout", methods=["POST"])
def logout():
    """登出"""
    customer = require_auth()
    if customer:
        # 记录登出（实际 JWT 无状态，这里仅做记录）
        pass
    return jsonify({"ok": True, "message": "已登出"})
