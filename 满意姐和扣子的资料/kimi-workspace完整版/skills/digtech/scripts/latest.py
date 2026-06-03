#!/usr/bin/env python3
from __future__ import annotations

import datetime as _dt
import json
import os
import sys
from pathlib import Path
from typing import Any

import httpx


ALLOWED_CATEGORIES = {
    "信息通信",
    "集成电路",
    "人工智能",
    "工业软件",
    "生物医药",
    "元宇宙",
    "具身智能",
    "人形机器人",
    "量子计算",
    "脑机接口",
    "先进材料",
    "先进能源",
    "空天海洋",
    "工业母机",
    "智慧医疗",
    "生命科学",
    "类脑计算",
    "科学智能",
    "其他类别",
}


def _normalize_categories(raw: Any) -> list[str]:
    if raw is None:
        return []
    if isinstance(raw, str):
        items = [c.strip() for c in raw.split(",") if c.strip()]
    elif isinstance(raw, list):
        items = []
        for x in raw:
            if x is None:
                continue
            s = str(x).strip()
            if s:
                items.append(s)
    else:
        items = [str(raw).strip()] if str(raw).strip() else []

    # de-dup while preserving order
    seen = set()
    out = []
    for c in items:
        if c in seen:
            continue
        seen.add(c)
        out.append(c)
    return out


def _validate_categories(categories: list[str]) -> None:
    if not categories:
        return  # allow empty
    bad = [c for c in categories if c not in ALLOWED_CATEGORIES]
    if bad:
        allowed = "、".join(sorted(ALLOWED_CATEGORIES))
        raise ValueError(f"category 不支持: {bad}. 仅允许: {allowed}。也可以不填 category。")


def _skill_dir() -> Path:
    # .../skills/digtech/scripts/latest.py -> .../skills/digtech
    return Path(__file__).resolve().parents[1]


def _load_config() -> dict[str, Any]:
    cfg_path = _skill_dir() / "config.json"
    if not cfg_path.exists():
        return {}
    try:
        return json.loads(cfg_path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _iso_date(d: _dt.date) -> str:
    return d.strftime("%Y-%m-%d")


def _default_payload(user: dict[str, Any]) -> dict[str, Any]:
    today = _dt.date.today()
    start = today - _dt.timedelta(days=7)

    page = int(user.get("page", 1))
    size = int(user.get("size", 50))

    category = _normalize_categories(user.get("category"))
    _validate_categories(category)

    language = user.get("language", ["zh-cn", "en"])
    if isinstance(language, str):
        language = [x.strip() for x in language.split(",") if x.strip()]

    pub_start_date = user.get("pub_start_date") or _iso_date(start)
    pub_end_date = user.get("pub_end_date") or _iso_date(today)

    # API expects comma-joined for language, category can be comma-joined too
    return {
        "page_info": {"page": page, "size": size},
        "filter_info": {
            "title": user.get("title", ""),
            "summary": user.get("summary", ""),
            "content": user.get("content", ""),
            "author": user.get("author", ""),
            "source": user.get("source", ""),
            "category": ",".join(category) if category else "",
            "score": 0,
            "type": user.get("type", ""),
            "language": ",".join(language) if language else "",
            "region": user.get("region", ""),
            "pub_start_date": pub_start_date,
            "pub_end_date": pub_end_date,
            "sort_by": user.get("sort_by", "pub_date"),
            "publication": user.get("publication", ""),
            "order": user.get("order", "desc"),
        },
    }


def fetch_latest(*, api_base: str, token: str, payload: dict[str, Any]) -> dict[str, Any]:
    url = f"{api_base.rstrip('/')}/api/article/list?token={token}"
    with httpx.Client(timeout=30) as client:
        resp = client.post(url, json=payload)
        resp.raise_for_status()
        return resp.json()


def _md_escape(s: str) -> str:
    return (s or "").replace("\n", " ").strip()


def render_markdown(result: dict[str, Any], *, max_items: int | None = None) -> str:
    page_info = result.get("page_info") or {}
    records = result.get("records") or []
    if max_items is not None:
        records = records[: max_items]

    lines: list[str] = []
    lines.append(f"## DigTech 最新资讯")
    lines.append("")
    lines.append(f"- 本页: {page_info.get('page')} / size={page_info.get('size')} / total={page_info.get('total')}")
    lines.append("")

    if not records:
        lines.append("（无记录）")
        lines.append("")
        lines.append("---")
        lines.append("来源：DigTech")
        return "\n".join(lines).rstrip() + "\n"

    for r in records:
        title = _md_escape(r.get("ai_title") or r.get("title") or "")
        url = r.get("url") or ""
        source = _md_escape(r.get("source") or "")
        pub_date = _md_escape(r.get("pub_date") or "")
        category = _md_escape(r.get("category") or "")
        region = _md_escape(r.get("ai_region") or "")
        ai_summary = _md_escape(r.get("ai_summary") or r.get("summary") or "")

        lines.append(f"### {title}")
        meta_bits = [b for b in [pub_date, source, category, region] if b]
        if meta_bits:
            lines.append("- " + " | ".join(meta_bits))
        if ai_summary:
            lines.append(f"- 摘要: {ai_summary}")
        if url:
            lines.append(f"- 链接: {url}")
        lines.append("")

    lines.append("---")
    lines.append("来源：DigTech")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    if len(sys.argv) < 2:
        print('Usage: python3 skills/digtech/scripts/latest.py \'<JSON>\'')
        print('Example: python3 skills/digtech/scripts/latest.py \'{"page":1,"size":30,"category":["脑机接口","具身智能"]}\'')
        return 2

    try:
        user_req = json.loads(sys.argv[1])
    except Exception as e:
        print(f"Error: invalid JSON: {e}")
        return 2

    cfg = _load_config()
    api_base = (user_req.get("apiBase") or cfg.get("apiBase") or "https://digtech.com.cn").strip()
    token = (user_req.get("token") or cfg.get("token") or os.getenv("DIGTECH_TOKEN") or "").strip()
    if not token or token == "REPLACE_ME":
        print("Error: missing token. Set skills/digtech/config.json token or env DIGTECH_TOKEN.")
        return 1

    try:
        payload = _default_payload(user_req)
    except Exception as e:
        print(f"Error: invalid request: {e}")
        return 2
    try:
        result = fetch_latest(api_base=api_base, token=token, payload=payload)
    except Exception as e:
        print(f"Error: request failed: {e}")
        return 1

    fmt = (user_req.get("format") or "md").lower()
    if fmt in ("json",):
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(render_markdown(result, max_items=user_req.get("max_items")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

