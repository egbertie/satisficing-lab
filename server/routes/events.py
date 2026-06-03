"""
满意解研究所 · 事件路由
====================
前端自动上报行为事件 → 数据资产沉淀
"""
from flask import Blueprint, request, jsonify, g
from server.middleware.security import optional_auth
from server.services.events import track, start_session, end_session

event_bp = Blueprint("events", __name__)


@event_bp.route("/track", methods=["POST"])
@optional_auth
def event_track():
    """前端事件上报（所有页面自动调用）"""
    data = request.get_json(silent=True) or {}
    
    if not data.get("action"):
        return jsonify({"ok": False, "error": "缺少 action"}), 400
    
    eid = track(
        customer_id=getattr(g, "customer_id", None),
        category=data.get("category", "page_view"),
        action=data["action"],
        label=data.get("label", ""),
        product_id=data.get("product_id", ""),
        page_url=data.get("page_url", ""),
        referrer=data.get("referrer", ""),
        session_id=data.get("session_id", ""),
        properties=data.get("properties", {}),
        ip=request.remote_addr,
        ua=request.headers.get("User-Agent", "")[:200],
        device=data.get("device", ""),
        client_time=data.get("client_time", ""),
    )
    return jsonify({"ok": True, "event_id": eid}), 201


@event_bp.route("/session/start", methods=["POST"])
@optional_auth
def session_start():
    """开始新会话"""
    data = request.get_json(silent=True) or {}
    sid = start_session(
        customer_id=getattr(g, "customer_id", None),
        entry_page=data.get("entry_page", ""),
        referrer=data.get("referrer", ""),
        utm_source=data.get("utm_source", ""),
        utm_medium=data.get("utm_medium", ""),
        utm_campaign=data.get("utm_campaign", ""),
        device=data.get("device", ""),
        ip=request.remote_addr,
    )
    return jsonify({"ok": True, "session_id": sid}), 201


@event_bp.route("/session/end", methods=["POST"])
def session_end():
    """结束会话"""
    data = request.get_json(silent=True) or {}
    sid = data.get("session_id", "")
    if not sid:
        return jsonify({"ok": False, "error": "缺少 session_id"}), 400
    
    end_session(sid, data.get("converted", False), data.get("conversion_type", ""))
    return jsonify({"ok": True})
