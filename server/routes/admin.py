"""
满意解研究所 · 管理后台 API
=========================
驾驶舱专属数据接口（内部使用）
"""
from flask import Blueprint, request, jsonify, g
from server.middleware.security import require_auth
from server.models.customer import get_customer_stats
from server.models.database import query
from server.services.events import get_event_stats, get_funnel, get_daily_active_users, get_product_usage
from server.services.mailer import get_email_stats

admin_bp = Blueprint("admin", __name__)

# 简单管理员验证（通过邮箱白名单）
ADMIN_EMAILS = {"egbertie@satisficing.io"}  # TODO: 配置到 config


def admin_required(f):
    """要求管理员权限"""
    @require_auth
    def wrapper(*args, **kwargs):
        if g.customer["email"] not in ADMIN_EMAILS:
            return jsonify({"error": "无管理员权限"}), 403
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper


@admin_bp.route("/dashboard/summary", methods=["GET"])
@admin_required
def dashboard_summary():
    """驾驶舱总览数据"""
    cs = get_customer_stats()
    es = get_event_stats()
    em = get_email_stats()
    today_sessions = query("SELECT COUNT(*) as c FROM sessions_tracking WHERE created_at >= date('now','localtime')")[0]["c"]
    
    return jsonify({
        "ok": True,
        "customers": {
            "total": cs["total"], "new_today": cs["new_today"],
            "active_today": cs["active_today"],
            "by_lifecycle": cs["by_stage"], "by_role": cs["by_role"],
            "by_industry": cs["by_industry"],
        },
        "events": {
            "total": es["total_events"], "today": es["today_events"],
            "by_category": es["by_category"],
        },
        "sessions": {"today": today_sessions},
        "emails": {"total": em["total_sent"], "today": em["today_sent"]},
        "referrals": {"total": query("SELECT COUNT(*) as c FROM referrals")[0]["c"]},
        "inquiries": {
            "open": query("SELECT COUNT(*) as c FROM inquiries WHERE status IN ('new','assigned','in_progress')")[0]["c"],
            "total": query("SELECT COUNT(*) as c FROM inquiries")[0]["c"],
        }
    })


@admin_bp.route("/dashboard/funnel", methods=["GET"])
@admin_required
def dashboard_funnel():
    """获客漏斗"""
    days = request.args.get("days", 30, type=int)
    funnel = get_funnel([
        ("page_view", "homepage_visit"),
        ("product_use", "assessment_start"),
        ("product_use", "assessment_complete"),
        ("conversion", "register"),
        ("conversion", "contact_form"),
    ], days)
    return jsonify({"ok": True, "funnel": funnel, "days": days})


@admin_bp.route("/dashboard/dau", methods=["GET"])
@admin_required
def dashboard_dau():
    """日活数据"""
    days = request.args.get("days", 7, type=int)
    return jsonify({"ok": True, "dau": get_daily_active_users(days)})


@admin_bp.route("/dashboard/products", methods=["GET"])
@admin_required
def dashboard_products():
    """产品使用排行"""
    days = request.args.get("days", 30, type=int)
    return jsonify({"ok": True, "products": get_product_usage(days)})


@admin_bp.route("/dashboard/events/recent", methods=["GET"])
@admin_required
def dashboard_recent_events():
    """最近事件"""
    limit = request.args.get("limit", 100, type=int)
    rows = query("""
        SELECT e.*, c.name, c.email FROM events e 
        LEFT JOIN customers c ON e.customer_id = c.id
        ORDER BY e.created_at DESC LIMIT ?
    """, (limit,))
    return jsonify({"ok": True, "events": rows})


@admin_bp.route("/dashboard/customers", methods=["GET"])
@admin_required
def dashboard_customers():
    """客户列表（支持筛选）"""
    stage = request.args.get("stage", "")
    role = request.args.get("role", "")
    limit = request.args.get("limit", 50, type=int)
    
    q = "SELECT id,name,email,company,industry,company_stage,lifecycle_stage,role,health_score,risk_score,last_active_at,registered_at FROM customers WHERE is_active=1"
    params = []
    if stage:
        q += " AND lifecycle_stage=?"
        params.append(stage)
    if role:
        q += " AND role=?"
        params.append(role)
    q += " ORDER BY last_active_at DESC LIMIT ?"
    params.append(limit)
    
    return jsonify({"ok": True, "customers": query(q, tuple(params))})
