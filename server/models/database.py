"""
满意解研究所 · 数据库 v2.0
=========================
统一的数据库初始化和迁移管理
"""
import sqlite3
import os
from datetime import datetime
from server.config import DATABASE_PATH
from server.models.schema_v2 import CREATE_TABLES, SEED_CONFIG


def get_db():
    """获取数据库连接（WAL模式，高并发读）"""
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    conn = sqlite3.connect(str(DATABASE_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA busy_timeout=5000")
    return conn


def init_db():
    """初始化所有 v2.0 表结构"""
    conn = get_db()
    conn.executescript(CREATE_TABLES)
    
    # 预置系统配置
    for key, value, desc in SEED_CONFIG:
        conn.execute(
            "INSERT OR IGNORE INTO system_config (key, value, description) VALUES (?, ?, ?)",
            (key, value, desc)
        )
    
    conn.commit()
    conn.close()
    print("✅ 数据库 v2.0 初始化完成")


def migrate(db_path: str = None):
    """自动迁移：从 v1.x → v2.0"""
    path = db_path or str(DATABASE_PATH)
    
    if not os.path.exists(path):
        print("🆕 全新数据库，初始化 v2.0...")
        init_db()
        return
    
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    
    # 检查当前版本
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    existing = {r[0] for r in cursor.fetchall()}
    
    if 'events' not in existing:
        print("📦 升级到 v2.0：添加事件/会话/转介绍/邮件等表...")
        conn.executescript(CREATE_TABLES)
        
        # 预置系统配置
        for key, value, desc in SEED_CONFIG:
            conn.execute(
                "INSERT OR IGNORE INTO system_config (key, value, description) VALUES (?, ?, ?)",
                (key, value, desc)
            )
        
        conn.commit()
        print("✅ 迁移到 v2.0 完成")
    else:
        print("✅ 数据库已是 v2.0 最新版本")
    
    conn.close()


def query(sql: str, params: tuple = None) -> list:
    """安全查询"""
    conn = get_db()
    try:
        rows = conn.execute(sql, params or ()).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def execute(sql: str, params: tuple = None) -> int:
    """执行写操作，返回 lastrowid"""
    conn = get_db()
    try:
        cursor = conn.execute(sql, params or ())
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def execute_many(sql: str, params_list: list) -> None:
    """批量执行"""
    conn = get_db()
    try:
        conn.executemany(sql, params_list)
        conn.commit()
    finally:
        conn.close()
