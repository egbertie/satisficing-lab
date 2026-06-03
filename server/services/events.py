"""
满意解研究所 · 事件采集引擎 v2.0
===============================
核心数据资产：客户行为轨迹
每个事件 = 一个可分析的数据点
"""
import json, uuid
from datetime import datetime
from server.models.database import get_db, query, execute


def track(customer_id: int | None, category: str, action: str, **kw) -> int:
    """
    记录一个行为事件
    
    使用示例:
      track(None, "page_view", "homepage_visit", page_url="/", referrer="google.com")
      track(42, "product_use", "assessment_complete", product_id="assessment", properties={"score": 85, "timeSpent": 180})
      track(42, "decision", "partner_selected", product_id="match", properties={"matchScore": 0.92})
      track(42, "social", "referral_link_create", properties={"code": "xxx"})
    """
    conn = get_db()
    try:
        session_id = kw.get("session_id", str(uuid.uuid4()))
        props = kw.get("properties", {})
        
        eid = conn.execute("""
            INSERT INTO events (customer_id, session_id, category, action, label,
                product_id, page_url, referrer, properties,
                ip_address, user_agent, device_type, client_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            customer_id, session_id, category, action,
            kw.get("label", ""), kw.get("product_id", ""),
            kw.get("page_url", ""), kw.get("referrer", ""),
            json.dumps(props, ensure_ascii=False),
            kw.get("ip", ""), kw.get("ua", ""),
            kw.get("device", ""), kw.get("client_time", datetime.now().isoformat())
        )).lastrowid
        
        # 更新会话统计
        conn.execute("""
            UPDATE sessions_tracking SET 
                page_views = page_views + 1,
                events_count = events_count + 1,
                end_at = datetime('now','localtime')
            WHERE session_id = ?
        """, (session_id,))
        
        conn.commit()
        return eid
    finally:
        conn.close()


def start_session(customer_id: int | None, **kw) -> str:
    """开始一个新的访问会话"""
    sid = str(uuid.uuid4())
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_db()
    conn.execute("""
        INSERT INTO sessions_tracking (customer_id, session_id, start_at, entry_page,
            referrer, utm_source, utm_medium, utm_campaign, device_type, ip_address)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (customer_id, sid, ts, kw.get("entry_page",""), kw.get("referrer",""),
          kw.get("utm_source",""), kw.get("utm_medium",""), kw.get("utm_campaign",""),
          kw.get("device",""), kw.get("ip","")))
    conn.commit()
    conn.close()
    return sid


def end_session(sid: str, converted: bool = False, conversion_type: str = ""):
    """结束会话并标记转化"""
    execute("""
        UPDATE sessions_tracking SET 
            end_at = datetime('now','localtime'),
            converted = ?, conversion_type = ?
        WHERE session_id = ?
    """, (1 if converted else 0, conversion_type, sid))


# ═══════════════════════════════════════
# 数据聚合分析
# ═══════════════════════════════════════

def get_funnel(stages: list, days: int = 30) -> list:
    """获客漏斗分析"""
    results = []
    for i, stage in enumerate(stages):
        if isinstance(stage, tuple):
            cat, action = stage
        else:
            cat, action = stage, None
        
        if action:
            rows = query("""
                SELECT COUNT(DISTINCT COALESCE(customer_id, session_id)) as c
                FROM events WHERE category=? AND action=? 
                AND created_at >= datetime('now','localtime','-%d days')
            """ % days, (cat, action))
        else:
            rows = query("""
                SELECT COUNT(DISTINCT COALESCE(customer_id, session_id)) as c
                FROM events WHERE category=?
                AND created_at >= datetime('now','localtime','-%d days')
            """ % days, (cat,))
        
        count = rows[0]["c"] if rows else 0
        prev = results[-1]["count"] if results else count
        rate = f"{(count/prev*100):.1f}%" if prev > 0 else "100%"
        results.append({"stage": cat if not action else f"{cat}/{action}", "count": count, "conversion_rate": rate})
    
    return results


def get_daily_active_users(days: int = 7) -> list:
    """日活跃用户"""
    return query("""
        SELECT DATE(created_at) as date, COUNT(DISTINCT COALESCE(customer_id, session_id)) as dau
        FROM events 
        WHERE created_at >= datetime('now','localtime','-%d days')
        GROUP BY DATE(created_at) ORDER BY date
    """ % days)


def get_product_usage(days: int = 30) -> list:
    """产品使用排行"""
    return query("""
        SELECT product_id, COUNT(*) as usage_count, COUNT(DISTINCT COALESCE(customer_id, session_id)) as unique_users
        FROM events 
        WHERE category='product_use' AND product_id != '' 
        AND created_at >= datetime('now','localtime','-%d days')
        GROUP BY product_id ORDER BY usage_count DESC
    """ % days)


def get_customer_journey(cid: int, limit: int = 100) -> list:
    """单个客户的行为轨迹"""
    return query("""
        SELECT * FROM events WHERE customer_id=? 
        ORDER BY created_at DESC LIMIT ?
    """, (cid, limit))


def get_event_stats() -> dict:
    """事件统计摘要"""
    return {
        "total_events": query("SELECT COUNT(*) as c FROM events")[0]["c"],
        "today_events": query("SELECT COUNT(*) as c FROM events WHERE created_at >= date('now','localtime')")[0]["c"],
        "total_sessions": query("SELECT COUNT(*) as c FROM sessions_tracking")[0]["c"],
        "today_sessions": query("SELECT COUNT(*) as c FROM sessions_tracking WHERE created_at >= date('now','localtime')")[0]["c"],
        "by_category": {r["category"]: r["c"] for r in
                        query("SELECT category, COUNT(*) as c FROM events GROUP BY category")},
        "by_action": {r["action"]: r["c"] for r in
                      query("SELECT action, COUNT(*) as c FROM events WHERE category='product_use' GROUP BY action ORDER BY c DESC LIMIT 20")},
    }
