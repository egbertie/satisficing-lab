"""
满意解研究所 · 客户交互路由 v2.0
===============================
POST /api/contact     - 留言（匿名/登陆均可）
GET  /api/inquiries   - 查看留言记录
GET  /api/profile     - 获取档案
PATCH /api/profile    - 更新档案
GET  /api/deliveries  - 已购产品
POST /api/referral/create  - 生成推荐码
GET  /api/referrals   - 查看推荐记录
"""
from flask import Blueprint, request, jsonify, g
from server.middleware.security import require_auth, optional_auth
from server.models.customer import (
    create_inquiry, get_inquiries, get_deliveries,
    update_customer, sanitize, create_referral_code, get_referrals,
)
from server.services.feishu import notify_new_inquiry, sync_inquiry_to_bitable

contact_bp = Blueprint("contact", __name__)


@contact_bp.route("/contact", methods=["POST"])
@optional_auth
def submit_contact():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip()
    message = (data.get("message") or "").strip()

    if not name: return jsonify({"error": "请填写姓名"}), 400
    if not message: return jsonify({"error": "请填写留言内容"}), 400

    cid = getattr(g, "customer_id", None)
    iid = create_inquiry(cid, name, email, data.get("company",""), message, data.get("category","general"))

    inquiry = {"id": iid, "name": name, "email": email,
               "company": data.get("company",""), "message": message}
    notify_new_inquiry(inquiry)
    sync_inquiry_to_bitable(inquiry)

    return jsonify({"ok": True, "message": "留言已收到，我们会尽快联系您！", "inquiry_id": iid}), 201


@contact_bp.route("/inquiries", methods=["GET"])
@require_auth
def list_inquiries():
    return jsonify({"ok": True, "inquiries": get_inquiries(g.customer_id)})


@contact_bp.route("/profile", methods=["GET", "PATCH"])
@require_auth
def profile():
    if request.method == "GET":
        return jsonify({"ok": True, "customer": sanitize(g.customer)})
    data = request.get_json(silent=True) or {}
    updated = update_customer(g.customer_id, **data)
    return jsonify({"ok": True, "customer": sanitize(updated)})


@contact_bp.route("/deliveries", methods=["GET"])
@require_auth
def deliveries():
    return jsonify({"ok": True, "deliveries": get_deliveries(g.customer_id)})


@contact_bp.route("/referral/create", methods=["POST"])
@require_auth
def referral_create():
    code = create_referral_code(g.customer_id)
    link = f"https://egbertie.github.io/satisficing-lab/?ref={code}"
    return jsonify({"ok": True, "code": code, "link": link}), 201


@contact_bp.route("/referrals", methods=["GET"])
@require_auth
def referral_list():
    return jsonify({"ok": True, "referrals": get_referrals(g.customer_id)})
