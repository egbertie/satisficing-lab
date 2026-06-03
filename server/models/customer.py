"""
满意解研究所 · 客户管理 v2.0
===========================
客户360°画像 CRUD + 生命周期管理 + 分群
"""
import sqlite3, bcrypt, jwt, hashlib
from datetime import datetime, timedelta
from server.config import JWT_SECRET, JWT_EXPIRES_HOURS
from server.models.database import get_db, query, execute


# ═══════════════════════════════════════
# 密码管理
# ═══════════════════════════════════════

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


# ═══════════════════════════════════════
# JWT
# ═══════════════════════════════════════

def create_token(cid: int, email: str) -> str:
    p = {"customer_id": cid, "email": email, "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRES_HOURS), "iat": datetime.utcnow()}
    return jwt.encode(p, JWT_SECRET, algorithm="HS256")

def decode_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except:
        return None

def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


# ═══════════════════════════════════════
# CRUD
# ═══════════════════════════════════════

def create_customer(email: str, password: str, **kw) -> dict | None:
    conn = get_db()
    try:
        h = hash_password(password)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cid = conn.execute("""
            INSERT INTO customers (email,password_hash,name,phone,company,position,industry,company_stage,
                source,source_detail,first_visit_at,registered_at,lifecycle_stage,role)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (email, h, kw.get("name",""), kw.get("phone",""), kw.get("company",""),
              kw.get("position",""), kw.get("industry",""), kw.get("stage",""),
              kw.get("source",""), kw.get("source_detail",""),
              kw.get("first_visit_at", now), now,
              kw.get("lifecycle_stage", "lead"),
              kw.get("role", "trial"))).lastrowid
        conn.commit()
        return get_by_id(cid)
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()


def get_by_id(cid: int) -> dict | None:
    rows = query("SELECT * FROM customers WHERE id=? AND is_active=1", (cid,))
    return rows[0] if rows else None

def get_by_email(email: str) -> dict | None:
    rows = query("SELECT * FROM customers WHERE email=? AND is_active=1", (email.lower().strip(),))
    return rows[0] if rows else None

def update_customer(cid: int, **kw) -> dict | None:
    allowed = ["name","phone","company","position","industry","company_stage",
               "company_size","city","funding","decision_style","decision_maturity",
               "pain_points","goals","tags","lifecycle_stage","role","source",
               "health_score","risk_score","avatar_url"]
    updates = {k:v for k,v in kw.items() if k in allowed and v is not None}
    if not updates: return get_by_id(cid)
    updates["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sets = ", ".join(f"{k}=?" for k in updates)
    vals = list(updates.values()) + [cid]
    conn = get_db()
    conn.execute(f"UPDATE customers SET {sets} WHERE id=?", vals)
    conn.commit()
    conn.close()
    return get_by_id(cid)

def update_last_active(cid: int):
    execute("UPDATE customers SET last_active_at=datetime('now','localtime') WHERE id=?", (cid,))

def update_lifecycle(cid: int, stage: str):
    """更新生命周期阶段并记录时间戳"""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    updates = {"lifecycle_stage": stage}
    if stage == "activated": updates["activated_at"] = ts
    elif stage == "paying": updates["converted_at"] = ts
    elif stage == "churned": updates["churned_at"] = ts
    update_customer(cid, **updates)


# ═══════════════════════════════════════
# 认证
# ═══════════════════════════════════════

def authenticate(email: str, password: str) -> dict | None:
    c = get_by_email(email)
    if not c or not verify_password(password, c["password_hash"]): return None
    token = create_token(c["id"], c["email"])
    execute("UPDATE customers SET last_active_at=datetime('now','localtime') WHERE id=?", (c["id"],))
    execute("INSERT INTO sessions (customer_id,token_hash,expires_at) VALUES (?,?,?)",
            (c["id"], hash_token(token), (datetime.utcnow() + timedelta(hours=JWT_EXPIRES_HOURS)).isoformat()))
    return {"token": token, "customer": sanitize(c)}


def sanitize(c: dict) -> dict:
    """去敏感字段，返回前端安全数据"""
    return {
        "id": c["id"], "email": c["email"], "name": c.get("name",""),
        "phone": c.get("phone",""), "company": c.get("company",""), "position": c.get("position",""),
        "industry": c.get("industry",""), "stage": c.get("company_stage",""),
        "role": c.get("role","trial"), "lifecycle_stage": c.get("lifecycle_stage",""),
        "health_score": c.get("health_score",50), "risk_score": c.get("risk_score",0),
        "avatar_url": c.get("avatar_url",""), "email_verified": bool(c.get("email_verified",0)),
        "created_at": c.get("registered_at",""), "last_active_at": c.get("last_active_at",""),
        "decision_style": c.get("decision_style",""), "tags": c.get("tags",""),
    }


# ═══════════════════════════════════════
# 统计
# ═══════════════════════════════════════

def get_customer_stats() -> dict:
    """客户统计数据"""
    return {
        "total": query("SELECT COUNT(*) as c FROM customers WHERE is_active=1")[0]["c"],
        "by_stage": {r["lifecycle_stage"]: r["c"] for r in
                     query("SELECT lifecycle_stage, COUNT(*) as c FROM customers WHERE is_active=1 GROUP BY lifecycle_stage")},
        "by_role": {r["role"]: r["c"] for r in
                    query("SELECT role, COUNT(*) as c FROM customers WHERE is_active=1 GROUP BY role")},
        "by_industry": {r["industry"]: r["c"] for r in
                        query("SELECT industry, COUNT(*) as c FROM customers WHERE is_active=1 AND industry!='' GROUP BY industry")},
        "new_today": query("SELECT COUNT(*) as c FROM customers WHERE registered_at>=date('now','localtime')")[0]["c"],
        "active_today": query("SELECT COUNT(*) as c FROM customers WHERE last_active_at>=date('now','localtime')")[0]["c"],
    }


# ═══════════════════════════════════════
# 交付
# ═══════════════════════════════════════

def get_deliveries(cid: int) -> list:
    return query("SELECT * FROM deliveries WHERE customer_id=? AND status='active' ORDER BY granted_at DESC", (cid,))

def grant_product(cid: int, pid: str, pname: str, pfamily: str = "", expires: str = None):
    execute("INSERT OR IGNORE INTO deliveries (customer_id,product_id,product_name,product_family,expires_at) VALUES (?,?,?,?,?)",
            (cid, pid, pname, pfamily, expires))

def revoke_product(cid: int, pid: str):
    execute("UPDATE deliveries SET status='revoked' WHERE customer_id=? AND product_id=?", (cid, pid))


# ═══════════════════════════════════════
# 留言
# ═══════════════════════════════════════

def create_inquiry(cid: int | None, name: str, email: str, company: str, message: str, category: str = "general") -> int:
    return execute("INSERT INTO inquiries (customer_id,name,email,company,message,category) VALUES (?,?,?,?,?,?)",
                   (cid, name, email, company, message, category))

def get_inquiries(cid: int = None, status: str = None, limit: int = 50) -> list:
    q, p = "SELECT * FROM inquiries WHERE 1=1", []
    if cid: q += " AND customer_id=?"; p.append(cid)
    if status: q += " AND status=?"; p.append(status)
    q += " ORDER BY created_at DESC LIMIT ?"; p.append(limit)
    return query(q, tuple(p))

def update_inquiry_status(iid: int, status: str, by: str = None):
    execute("UPDATE inquiries SET status=?, replied_at=datetime('now','localtime'), replied_by=? WHERE id=?", (status, by, iid))


# ═══════════════════════════════════════
# 转介绍
# ═══════════════════════════════════════

def create_referral_code(cid: int) -> str:
    import uuid
    code = str(cid) + "_" + uuid.uuid4().hex[:10]
    execute("INSERT INTO referrals (referrer_id,referral_code,status) VALUES (?,?,'created')", (cid, code))
    return code

def track_referral(code: str, action: str, referred_id: int = None):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    updates = {"status": action}
    if action == "clicked": updates["clicked_at"] = ts
    elif action == "registered":
        updates["registered_at"] = ts
        if referred_id: updates["referred_id"] = referred_id
    elif action == "converted": updates["converted_at"] = ts
    sets = ", ".join(f"{k}=?" for k in updates)
    vals = list(updates.values()) + [code]
    execute(f"UPDATE referrals SET {sets} WHERE referral_code=?", tuple(vals))

def get_referrals(cid: int) -> list:
    return query("SELECT * FROM referrals WHERE referrer_id=? ORDER BY sent_at DESC", (cid,))
