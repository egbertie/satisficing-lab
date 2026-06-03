"""
满意解研究所 · 数据模型
====================
SQLite + SQLAlchemy 风格的纯 SQL 实现
精简可靠，零额外依赖
"""
import sqlite3
import os
from datetime import datetime
from server.config import DATABASE_PATH

os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)


def get_db():
    """获取数据库连接"""
    conn = sqlite3.connect(str(DATABASE_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """初始化所有数据表"""
    conn = get_db()
    conn.executescript("""
        -- 客户账号表
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            name TEXT NOT NULL DEFAULT '',
            phone TEXT DEFAULT '',
            company TEXT DEFAULT '',
            position TEXT DEFAULT '',
            industry TEXT DEFAULT '',
            stage TEXT DEFAULT '',
            role TEXT DEFAULT 'trial',
            source TEXT DEFAULT '',
            interests TEXT DEFAULT '',
            avatar_url TEXT DEFAULT '',
            email_verified INTEGER DEFAULT 0,
            is_active INTEGER DEFAULT 1,
            last_login_at TEXT,
            created_at TEXT DEFAULT (datetime('now', 'localtime')),
            updated_at TEXT DEFAULT (datetime('now', 'localtime'))
        );

        -- 登录会话（JWT 黑名单/刷新控制）
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            token_hash TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now', 'localtime')),
            FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
        );

        -- 客户留言/咨询
        CREATE TABLE IF NOT EXISTS inquiries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            name TEXT NOT NULL,
            email TEXT DEFAULT '',
            company TEXT DEFAULT '',
            message TEXT NOT NULL,
            category TEXT DEFAULT 'general',
            status TEXT DEFAULT 'new',
            replied_at TEXT,
            replied_by TEXT,
            created_at TEXT DEFAULT (datetime('now', 'localtime')),
            FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE SET NULL
        );

        -- 产品交付记录
        CREATE TABLE IF NOT EXISTS deliveries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            product_id TEXT NOT NULL,
            product_name TEXT NOT NULL,
            status TEXT DEFAULT 'active',
            granted_at TEXT DEFAULT (datetime('now', 'localtime')),
            expires_at TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
        );

        -- API 调用日志
        CREATE TABLE IF NOT EXISTS api_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            endpoint TEXT NOT NULL,
            method TEXT NOT NULL,
            ip_address TEXT,
            status_code INTEGER,
            created_at TEXT DEFAULT (datetime('now', 'localtime'))
        );

        -- 验证码（邮箱验证/密码重置）
        CREATE TABLE IF NOT EXISTS verification_codes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            code TEXT NOT NULL,
            purpose TEXT DEFAULT 'email_verify',
            used INTEGER DEFAULT 0,
            expires_at TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now', 'localtime'))
        );

        -- 索引
        CREATE INDEX IF NOT EXISTS idx_customers_email ON customers(email);
        CREATE INDEX IF NOT EXISTS idx_inquiries_customer ON inquiries(customer_id);
        CREATE INDEX IF NOT EXISTS idx_deliveries_customer ON deliveries(customer_id);
        CREATE INDEX IF NOT EXISTS idx_sessions_customer ON sessions(customer_id);
    """)
    conn.commit()
    conn.close()
    print("✅ 数据库初始化完成")


def migrate():
    """运行数据库迁移"""
    conn = get_db()
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    existing_tables = {r[0] for r in cursor.fetchall()}

    if 'customers' not in existing_tables:
        print("🆕 首次初始化，创建所有表...")
        init_db()
        return

    # 后续版本迁移在此添加
    # 例如：ALTER TABLE customers ADD COLUMN new_field TEXT DEFAULT '';
    conn.close()
    print("✅ 数据库已是最新版本")
