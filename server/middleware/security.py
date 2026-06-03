"""
满意解研究所 · 中间件 v2.0
========================
JWT验证 · 限流 · IP黑名单 · CORS · 请求日志
"""
import time, json
from functools import wraps
from flask import request, jsonify, g
from server.models.customer import decode_token, get_by_id, update_last_active


# ═══════════════════════════════════════
# JWT 认证装饰器
# ═══════════════════════════════════════

def require_auth(f):
    """要求登录"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return jsonify({"error": "请先登录"}), 401
        
        payload = decode_token(auth[7:])
        if not payload:
            return jsonify({"error": "登录已过期，请重新登录"}), 401
        
        customer = get_by_id(payload["customer_id"])
        if not customer:
            return jsonify({"error": "用户不存在"}), 401
        
        g.customer = customer
        g.customer_id = customer["id"]
        update_last_active(customer["id"])
        
        return f(*args, **kwargs)
    return wrapper


def optional_auth(f):
    """可选登录（登录了就给 g.customer，没登录就 None）"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        g.customer = None
        g.customer_id = None
        if auth.startswith("Bearer "):
            payload = decode_token(auth[7:])
            if payload:
                g.customer = get_by_id(payload["customer_id"])
                if g.customer:
                    g.customer_id = g.customer["id"]
                    update_last_active(g.customer["id"])
        return f(*args, **kwargs)
    return wrapper


# ═══════════════════════════════════════
# 简易限流（IP级别）
# ═══════════════════════════════════════

_rate_limits = {}  # {ip: [(timestamp, endpoint), ...]}

def rate_limit(max_requests: int = 60, window_seconds: int = 60):
    """限流装饰器：每分钟最多 max_requests 次"""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            ip = request.remote_addr or "127.0.0.1"
            now = time.time()
            
            if ip not in _rate_limits:
                _rate_limits[ip] = []
            
            # 清理过期记录
            _rate_limits[ip] = [t for t in _rate_limits[ip] if now - t < window_seconds]
            
            if len(_rate_limits[ip]) >= max_requests:
                return jsonify({"error": "请求过于频繁，请稍后再试"}), 429
            
            _rate_limits[ip].append(now)
            return f(*args, **kwargs)
        return wrapper
    return decorator


# ═══════════════════════════════════════
# 请求日志
# ═══════════════════════════════════════

def log_api_request(response):
    """记录 API 请求到数据库"""
    from server.models.database import execute
    try:
        cid = getattr(g, "customer_id", None)
        # 脱敏请求体
        body = ""
        if request.method in ("POST", "PUT", "PATCH") and request.is_json:
            try:
                raw = request.get_json(silent=True) or {}
                # 脱敏：密码字段打码
                if "password" in raw:
                    raw["password"] = "***"
                body = json.dumps(raw, ensure_ascii=False)[:500]
            except:
                body = ""
        
        execute(
            "INSERT INTO api_logs (customer_id, endpoint, method, status_code, ip_address, request_body) VALUES (?,?,?,?,?,?)",
            (cid, request.path, request.method, response.status_code, request.remote_addr, body)
        )
    except:
        pass  # 日志记录不阻塞业务
    return response
