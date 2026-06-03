"""
满意解研究所 · 认证路由 v2.0
===========================
POST /api/auth/register  - 注册（自动激活+事件追踪）
POST /api/auth/login     - 登录
GET  /api/auth/me        - 当前用户
POST /api/auth/logout    - 登出
"""
from flask import Blueprint, request, jsonify, g
from server.models.customer import (
    create_customer, authenticate, get_by_id, get_by_email,
    update_customer, sanitize
)
from server.middleware.security import require_auth
from server.services.feishu import notify_new_customer, sync_customer_to_bitable

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    """客户注册 → 自动激活 → 飞书通知 → 事件记录"""
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = (data.get("password") or "").strip()

    if not email or "@" not in email:
        return jsonify({"error": "请输入有效的邮箱地址"}), 400
    if len(password) < 6:
        return jsonify({"error": "密码至少6位"}), 400

    if get_by_email(email):
        return jsonify({"error": "该邮箱已注册，请直接登录"}), 409

    customer = create_customer(
        email=email, password=password,
        name=data.get("name", ""), phone=data.get("phone", ""),
        company=data.get("company", ""), position=data.get("position", ""),
        industry=data.get("industry", ""), stage=data.get("stage", ""),
        source=data.get("source", ""), source_detail=data.get("source_detail", ""),
        first_visit_at=data.get("first_visit_at", ""),
        lifecycle_stage="lead",
    )

    if not customer:
        return jsonify({"error": "注册失败，请稍后重试"}), 500

    # 自动登录
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
@require_auth
def me():
    return jsonify({"ok": True, "customer": sanitize(g.customer)})


@auth_bp.route("/logout", methods=["POST"])
@require_auth
def logout():
    return jsonify({"ok": True, "message": "已登出"})
