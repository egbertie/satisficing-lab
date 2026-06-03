"""
满意解研究所 · 客户业务逻辑层
=======================
封装所有客户相关的数据库操作
"""
import bcrypt
import jwt
import hashlib
from datetime import datetime, timedelta
from server.config import JWT_SECRET, JWT_EXPIRES_HOURS
from server.models.database import get_db


# ═══════════════════════════════════════════
# 密码管理
# ═══════════════════════════════════════════

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


# ═══════════════════════════════════════════
# JWT 令牌
# ═══════════════════════════════════════════

def create_token(customer_id: int, email: str) -> str:
    payload = {
        "customer_id": customer_id,
        "email": email,
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRES_HOURS),
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def decode_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


# ═══════════════════════════════════════════
# 客户 CRUD
# ═══════════════════════════════════════════

def create_customer(email: str, password: str, **kwargs) -> dict | None:
    """注册新客户"""
    conn = get_db()
    try:
        h = hash_password(password)
        cursor = conn.execute(
            """INSERT INTO customers (email, password_hash, name, phone, company, position,
               industry, stage, source, interests)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (email, h,
             kwargs.get("name", ""), kwargs.get("phone", ""),
             kwargs.get("company", ""), kwargs.get("position", ""),
             kwargs.get("industry", ""), kwargs.get("stage", ""),
             kwargs.get("source", ""), kwargs.get("interests", ""))
        )
        conn.commit()
        return get_customer_by_id(cursor.lastrowid)
    except sqlite3.IntegrityError:
        return None  # 邮箱已存在
    finally:
        conn.close()


def get_customer_by_email(email: str) -> dict | None:
    conn = get_db()
    row = conn.execute("SELECT * FROM customers WHERE email = ? AND is_active = 1", (email,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_customer_by_id(customer_id: int) -> dict | None:
    conn = get_db()
    row = conn.execute("SELECT * FROM customers WHERE id = ? AND is_active = 1", (customer_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def update_customer(customer_id: int, **kwargs) -> dict | None:
    """更新客户信息"""
    allowed = ["name", "phone", "company", "position", "industry", "stage", "interests", "avatar_url"]
    updates = {k: v for k, v in kwargs.items() if k in allowed and v is not None}
    if not updates:
        return get_customer_by_id(customer_id)

    updates["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sets = ", ".join(f"{k} = ?" for k in updates)
    values = list(updates.values()) + [customer_id]

    conn = get_db()
    conn.execute(f"UPDATE customers SET {sets} WHERE id = ?", values)
    conn.commit()
    conn.close()
    return get_customer_by_id(customer_id)


def update_password(customer_id: int, new_password: str) -> bool:
    conn = get_db()
    h = hash_password(new_password)
    conn.execute("UPDATE customers SET password_hash = ?, updated_at = datetime('now','localtime') WHERE id = ?",
                 (h, customer_id))
    conn.commit()
    conn.close()
    return True


def update_last_login(customer_id: int):
    conn = get_db()
    conn.execute("UPDATE customers SET last_login_at = datetime('now','localtime') WHERE id = ?", (customer_id,))
    conn.commit()
    conn.close()


# ═══════════════════════════════════════════
# 认证流程
# ═══════════════════════════════════════════

def authenticate(email: str, password: str) -> dict | None:
    """登录验证，成功返回 token 和客户信息"""
    customer = get_customer_by_email(email)
    if not customer:
        return None
    if not verify_password(password, customer["password_hash"]):
        return None

    token = create_token(customer["id"], customer["email"])
    update_last_login(customer["id"])

    # 保存会话
    conn = get_db()
    conn.execute(
        "INSERT INTO sessions (customer_id, token_hash, expires_at) VALUES (?, ?, ?)",
        (customer["id"], hash_token(token),
         (datetime.utcnow() + timedelta(hours=JWT_EXPIRES_HOURS)).isoformat())
    )
    conn.commit()
    conn.close()

    return {
        "token": token,
        "customer": sanitize_customer(customer)
    }


def sanitize_customer(customer: dict) -> dict:
    """去除敏感字段，用于返回前端"""
    return {
        "id": customer["id"],
        "email": customer["email"],
        "name": customer["name"],
        "phone": customer.get("phone", ""),
        "company": customer.get("company", ""),
        "position": customer.get("position", ""),
        "industry": customer.get("industry", ""),
        "stage": customer.get("stage", ""),
        "role": customer.get("role", "trial"),
        "avatar_url": customer.get("avatar_url", ""),
        "email_verified": bool(customer.get("email_verified", 0)),
        "created_at": customer.get("created_at", ""),
        "last_login_at": customer.get("last_login_at", ""),
    }


# ═══════════════════════════════════════════
# 客户产品交付
# ═══════════════════════════════════════════

def get_customer_deliveries(customer_id: int) -> list:
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM deliveries WHERE customer_id = ? AND status = 'active' ORDER BY granted_at DESC",
        (customer_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def grant_product(customer_id: int, product_id: str, product_name: str, expires_at: str = None):
    conn = get_db()
    conn.execute(
        "INSERT OR IGNORE INTO deliveries (customer_id, product_id, product_name, expires_at) VALUES (?, ?, ?, ?)",
        (customer_id, product_id, product_name, expires_at)
    )
    conn.commit()
    conn.close()


def revoke_product(customer_id: int, product_id: str):
    conn = get_db()
    conn.execute(
        "UPDATE deliveries SET status = 'revoked' WHERE customer_id = ? AND product_id = ?",
        (customer_id, product_id)
    )
    conn.commit()
    conn.close()


# ═══════════════════════════════════════════
# 客户留言/咨询
# ═══════════════════════════════════════════

def create_inquiry(customer_id: int | None, name: str, email: str,
                   company: str, message: str, category: str = "general") -> int:
    conn = get_db()
    cursor = conn.execute(
        "INSERT INTO inquiries (customer_id, name, email, company, message, category) VALUES (?, ?, ?, ?, ?, ?)",
        (customer_id, name, email, company, message, category)
    )
    conn.commit()
    inquiry_id = cursor.lastrowid
    conn.close()
    return inquiry_id


def get_inquiries(customer_id: int = None, status: str = None, limit: int = 50) -> list:
    conn = get_db()
    query = "SELECT * FROM inquiries WHERE 1=1"
    params = []
    if customer_id:
        query += " AND customer_id = ?"
        params.append(customer_id)
    if status:
        query += " AND status = ?"
        params.append(status)
    query += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_inquiry_status(inquiry_id: int, status: str, replied_by: str = None):
    conn = get_db()
    conn.execute(
        "UPDATE inquiries SET status = ?, replied_at = datetime('now','localtime'), replied_by = ? WHERE id = ?",
        (status, replied_by, inquiry_id)
    )
    conn.commit()
    conn.close()
