"""
满意解研究所 · 客户交互路由
=======================
POST /api/contact   - 客户留言/咨询
GET  /api/profile   - 获取/更新客户档案
"""
from flask import Blueprint, request, jsonify
from server.routes.auth import require_auth
from server.models.customer import (
    create_inquiry, get_inquiries,
    get_customer_deliveries, update_customer, sanitize_customer
)
from server.services.feishu import notify_new_inquiry, sync_inquiry_to_bitable

contact_bp = Blueprint("contact", __name__)


@contact_bp.route("/contact", methods=["POST"])
def submit_contact():
    """客户留言（可匿名，无需登录）"""
    data = request.get_json(silent=True) or {}

    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip()
    message = (data.get("message") or "").strip()

    if not name:
        return jsonify({"error": "请填写姓名"}), 400
    if not message:
        return jsonify({"error": "请填写留言内容"}), 400

    # 尝试获取登录用户
    customer = require_auth()
    customer_id = customer["id"] if customer else None

    # 保存留言
    inquiry_id = create_inquiry(
        customer_id=customer_id,
        name=name,
        email=email,
        company=data.get("company", ""),
        message=message,
        category=data.get("category", "general")
    )

    inquiry = {
        "id": inquiry_id, "name": name, "email": email,
        "company": data.get("company", ""), "message": message
    }

    # 飞书通知
    notify_new_inquiry(inquiry)
    sync_inquiry_to_bitable(inquiry)

    return jsonify({
        "ok": True,
        "message": "留言已收到，我们会尽快联系您！",
        "inquiry_id": inquiry_id
    }), 201


@contact_bp.route("/inquiries", methods=["GET"])
def list_inquiries():
    """获取客户的留言记录（需登录）"""
    customer = require_auth()
    if not customer:
        return jsonify({"error": "请先登录"}), 401

    inquiries = get_inquiries(customer_id=customer["id"])
    return jsonify({"ok": True, "inquiries": inquiries})


@contact_bp.route("/profile", methods=["GET", "PATCH"])
def profile():
    """获取或更新客户档案"""
    customer = require_auth()
    if not customer:
        return jsonify({"error": "请先登录"}), 401

    if request.method == "GET":
        return jsonify({
            "ok": True,
            "customer": sanitize_customer(customer)
        })

    # PATCH: 更新档案
    data = request.get_json(silent=True) or {}
    updated = update_customer(customer["id"], **data)
    return jsonify({
        "ok": True,
        "customer": sanitize_customer(updated)
    })


@contact_bp.route("/deliveries", methods=["GET"])
def my_deliveries():
    """获取客户已购产品列表"""
    customer = require_auth()
    if not customer:
        return jsonify({"error": "请先登录"}), 401

    deliveries = get_customer_deliveries(customer["id"])
    return jsonify({"ok": True, "deliveries": deliveries})
