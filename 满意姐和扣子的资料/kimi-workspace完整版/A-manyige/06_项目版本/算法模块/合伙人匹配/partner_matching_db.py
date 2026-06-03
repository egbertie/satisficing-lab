#!/usr/bin/env python3
"""
partner_matching_db.py
合伙人匹配服务 - SQLite 数据层 V1.0

基于外援方案的数据库设计思想，降级为 SQLite 实现（零安装成本）。
"""

import sqlite3
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

WORKSPACE = Path("/root/.openclaw/workspace")
DB_PATH = WORKSPACE / "memory" / "partner_matching.db"


def _get_conn() -> sqlite3.Connection:
    db_path = DB_PATH if isinstance(DB_PATH, Path) else Path(DB_PATH)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """初始化数据库表结构。"""
    conn = _get_conn()
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS assessment_results (
            assessment_id TEXT PRIMARY KEY,
            sku_type TEXT NOT NULL,
            company_name TEXT NOT NULL,
            created_at TEXT NOT NULL,
            overall_risk TEXT,
            overall_score INTEGER,
            markdown_report_path TEXT,
            raw_json TEXT NOT NULL,
            duration_seconds REAL
        );

        CREATE TABLE IF NOT EXISTS assessment_dimensions (
            dimension_id INTEGER PRIMARY KEY AUTOINCREMENT,
            assessment_id TEXT NOT NULL,
            dimension_name TEXT NOT NULL,
            dimension_value TEXT,
            dimension_json TEXT,
            FOREIGN KEY (assessment_id) REFERENCES assessment_results(assessment_id)
        );

        CREATE TABLE IF NOT EXISTS case_studies (
            case_id INTEGER PRIMARY KEY AUTOINCREMENT,
            assessment_id TEXT,
            company_name TEXT NOT NULL,
            industry_tag TEXT,
            stage TEXT,
            key_insights TEXT,
            anonymized_json TEXT NOT NULL,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS sri_assets (
            asset_id TEXT PRIMARY KEY,
            asset_type TEXT NOT NULL,
            name TEXT NOT NULL,
            version TEXT,
            role TEXT,
            content_summary TEXT,
            status TEXT DEFAULT 'active',
            usage_count INTEGER DEFAULT 0,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS sri_metrics_snapshots (
            snapshot_id INTEGER PRIMARY KEY AUTOINCREMENT,
            snapshot_at TEXT NOT NULL,
            time_minutes REAL,
            quality_rate REAL,
            risk_count INTEGER,
            cost_yuan REAL,
            reuse_rate REAL,
            note TEXT
        );

        CREATE INDEX IF NOT EXISTS idx_dim_assessment
            ON assessment_dimensions(assessment_id);
        CREATE INDEX IF NOT EXISTS idx_asset_type
            ON sri_assets(asset_type);
        CREATE INDEX IF NOT EXISTS idx_metrics_snapshot_at
            ON sri_metrics_snapshots(snapshot_at);
        """
    )
    conn.commit()
    # 轻量迁移：为旧表补充 duration_seconds 列
    try:
        conn.execute("ALTER TABLE assessment_results ADD COLUMN duration_seconds REAL")
        conn.commit()
    except sqlite3.OperationalError:
        pass  # 列已存在
    conn.close()


def save_assessment(
    sku_type: str,
    company_name: str,
    overall_risk: str,
    overall_score: int,
    dimensions: List[Dict[str, Any]],
    raw_json: Dict[str, Any],
    markdown_report_path: Optional[str] = None,
    duration_seconds: Optional[float] = None,
) -> str:
    """保存一次评估结果，返回 assessment_id。"""
    init_db()
    assessment_id = f" Assessment-{uuid.uuid4().hex[:12].upper()}"
    created_at = datetime.now().isoformat()
    conn = _get_conn()
    conn.execute(
        """
        INSERT INTO assessment_results
        (assessment_id, sku_type, company_name, created_at, overall_risk, overall_score, markdown_report_path, raw_json, duration_seconds)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            assessment_id,
            sku_type,
            company_name,
            created_at,
            overall_risk,
            overall_score,
            markdown_report_path,
            json.dumps(raw_json, ensure_ascii=False),
            duration_seconds,
        ),
    )
    for dim in dimensions:
        conn.execute(
            """
            INSERT INTO assessment_dimensions
            (assessment_id, dimension_name, dimension_value, dimension_json)
            VALUES (?, ?, ?, ?)
            """,
            (
                assessment_id,
                dim.get("name", ""),
                str(dim.get("value", "")),
                json.dumps(dim.get("detail", {}), ensure_ascii=False),
            ),
        )
    conn.commit()
    conn.close()
    return assessment_id


def get_assessment(assessment_id: str) -> Optional[Dict[str, Any]]:
    """根据 ID 获取完整评估结果（含维度详情）。"""
    init_db()
    conn = _get_conn()
    row = conn.execute(
        "SELECT * FROM assessment_results WHERE assessment_id = ?", (assessment_id,)
    ).fetchone()
    if row is None:
        conn.close()
        return None
    dims = conn.execute(
        "SELECT dimension_name, dimension_value, dimension_json FROM assessment_dimensions WHERE assessment_id = ?",
        (assessment_id,),
    ).fetchall()
    conn.close()
    result = dict(row)
    result["dimensions"] = [dict(d) for d in dims]
    result["raw_json"] = json.loads(result["raw_json"])
    for d in result["dimensions"]:
        d["detail"] = json.loads(d["dimension_json"])
        del d["dimension_json"]
    return result


def save_case_study(
    company_name: str,
    industry_tag: str,
    stage: str,
    key_insights: str,
    anonymized_json: Dict[str, Any],
    assessment_id: Optional[str] = None,
) -> int:
    """保存一个案例到案例库，返回 case_id。"""
    init_db()
    conn = _get_conn()
    cur = conn.execute(
        """
        INSERT INTO case_studies
        (assessment_id, company_name, industry_tag, stage, key_insights, anonymized_json, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            assessment_id,
            company_name,
            industry_tag,
            stage,
            key_insights,
            json.dumps(anonymized_json, ensure_ascii=False),
            datetime.now().isoformat(),
        ),
    )
    conn.commit()
    case_id = cur.lastrowid
    conn.close()
    return case_id


def list_recent_assessments(limit: int = 20) -> List[Dict[str, Any]]:
    init_db()
    conn = _get_conn()
    rows = conn.execute(
        """
        SELECT assessment_id, sku_type, company_name, created_at, overall_risk, overall_score, duration_seconds
        FROM assessment_results
        ORDER BY created_at DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── SRI 资产飞轮与经营指标辅助函数 ───────────────────────────────


def save_asset(
    asset_id: str,
    asset_type: str,
    name: str,
    version: Optional[str] = None,
    role: Optional[str] = None,
    content_summary: Optional[str] = None,
    status: str = "active",
) -> str:
    """注册或更新企业资产。"""
    init_db()
    now = datetime.now().isoformat()
    conn = _get_conn()
    conn.execute(
        """
        INSERT INTO sri_assets (asset_id, asset_type, name, version, role, content_summary, status, usage_count, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(asset_id) DO UPDATE SET
            version=excluded.version,
            role=excluded.role,
            content_summary=excluded.content_summary,
            status=excluded.status,
            updated_at=excluded.updated_at
        """,
        (asset_id, asset_type, name, version, role, content_summary, status, 0, now, now),
    )
    conn.commit()
    conn.close()
    return asset_id


def increment_asset_usage(asset_id: str) -> bool:
    """记录资产被复用一次。"""
    init_db()
    now = datetime.now().isoformat()
    conn = _get_conn()
    cur = conn.execute(
        "UPDATE sri_assets SET usage_count = usage_count + 1, updated_at = ? WHERE asset_id = ?",
        (now, asset_id),
    )
    conn.commit()
    conn.close()
    return cur.rowcount > 0


def list_assets(asset_type: Optional[str] = None, limit: int = 200) -> List[Dict[str, Any]]:
    """列出资产。"""
    init_db()
    conn = _get_conn()
    if asset_type:
        rows = conn.execute(
            "SELECT * FROM sri_assets WHERE asset_type = ? ORDER BY updated_at DESC LIMIT ?",
            (asset_type, limit),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM sri_assets ORDER BY updated_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_asset(asset_id: str) -> Optional[Dict[str, Any]]:
    """获取单个资产。"""
    init_db()
    conn = _get_conn()
    row = conn.execute("SELECT * FROM sri_assets WHERE asset_id = ?", (asset_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def delete_asset(asset_id: str) -> bool:
    """软删除资产。"""
    init_db()
    now = datetime.now().isoformat()
    conn = _get_conn()
    cur = conn.execute(
        "UPDATE sri_assets SET status = 'deprecated', updated_at = ? WHERE asset_id = ?",
        (now, asset_id),
    )
    conn.commit()
    conn.close()
    return cur.rowcount > 0


def save_metrics_snapshot(
    time_minutes: Optional[float],
    quality_rate: Optional[float],
    risk_count: Optional[int],
    cost_yuan: Optional[float],
    reuse_rate: Optional[float],
    note: Optional[str] = None,
) -> int:
    """保存经营指标快照，返回 snapshot_id。"""
    init_db()
    now = datetime.now().isoformat()
    conn = _get_conn()
    cur = conn.execute(
        """
        INSERT INTO sri_metrics_snapshots (snapshot_at, time_minutes, quality_rate, risk_count, cost_yuan, reuse_rate, note)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (now, time_minutes, quality_rate, risk_count, cost_yuan, reuse_rate, note),
    )
    conn.commit()
    snapshot_id = cur.lastrowid
    conn.close()
    return snapshot_id


def get_latest_metrics_snapshot() -> Optional[Dict[str, Any]]:
    """获取最新指标快照。"""
    init_db()
    conn = _get_conn()
    row = conn.execute(
        "SELECT * FROM sri_metrics_snapshots ORDER BY snapshot_at DESC LIMIT 1"
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def list_metrics_snapshots(limit: int = 30) -> List[Dict[str, Any]]:
    """列出近期指标快照。"""
    init_db()
    conn = _get_conn()
    rows = conn.execute(
        "SELECT * FROM sri_metrics_snapshots ORDER BY snapshot_at DESC LIMIT ?",
        (limit,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_assessment_stats(days: int = 30) -> Dict[str, Any]:
    """获取近期评估统计，用于经营指标计算。"""
    init_db()
    since = (datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)).isoformat()
    conn = _get_conn()
    total = conn.execute(
        "SELECT COUNT(*) as cnt FROM assessment_results WHERE created_at >= ?",
        (since,),
    ).fetchone()["cnt"]
    avg_score_row = conn.execute(
        "SELECT AVG(overall_score) as avg_score FROM assessment_results WHERE created_at >= ?",
        (since,),
    ).fetchone()
    avg_duration_row = conn.execute(
        "SELECT AVG(duration_seconds) as avg_duration FROM assessment_results WHERE created_at >= ? AND duration_seconds IS NOT NULL",
        (since,),
    ).fetchone()
    risk_rows = conn.execute(
        "SELECT overall_risk, COUNT(*) as cnt FROM assessment_results WHERE created_at >= ? GROUP BY overall_risk",
        (since,),
    ).fetchall()
    sku_rows = conn.execute(
        "SELECT sku_type, COUNT(*) as cnt FROM assessment_results WHERE created_at >= ? GROUP BY sku_type",
        (since,),
    ).fetchall()
    conn.close()
    return {
        "total_assessments": total,
        "avg_score": avg_score_row["avg_score"] or 0.0,
        "avg_duration_seconds": avg_duration_row["avg_duration"] or 0.0,
        "risk_distribution": {r["overall_risk"]: r["cnt"] for r in risk_rows},
        "sku_distribution": {r["sku_type"]: r["cnt"] for r in sku_rows},
    }


if __name__ == "__main__":
    init_db()
    print(f"Database initialized at {DB_PATH}")
