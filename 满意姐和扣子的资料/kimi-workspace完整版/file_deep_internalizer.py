"""
file_deep_internalizer.py
Deeply internalize extracted files into a structured knowledge base with execution closure.
Every file must complete: extract → classify → structure → store → link_to_execution.
"""
from __future__ import annotations
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

EXTRACTION_BASE = Path("/root/.openclaw/workspace/tmp/internalization_output")
KB_BASE = Path("/root/.openclaw/workspace/knowledge_base/domains")
MASTER_DB = Path("/root/.openclaw/workspace/file_structured_knowledge_base.json")

DOMAIN_RULES = {
    "decision_science": {
        "keywords": ["决策", "decision", "thinking", "cognitive", "bias", "系统思考", "博弈论", "game theory", "behavioral", "nudge", "prospect theory", "满意解", "satisficing"],
        "exec_target": "decision_science_kb.md",
        "linked_asset": "satisficing_decision_engine.py",
    },
    "confucian_philosophy": {
        "keywords": ["儒学", "儒商", "孔子", "儒家", "黎红雷", "伦理", "virtue", "商道", "敬天", "义利", "礼治", "修身"],
        "exec_target": "confucian_philosophy_kb.md",
        "linked_asset": "confucian_business_philosophy_core.py",
    },
    "business_model": {
        "keywords": ["商业模式", "business model", "画布", "canvas", "value proposition", "revenue", "盈利模式"],
        "exec_target": "business_model_kb.md",
        "linked_asset": None,
    },
    "ai_product": {
        "keywords": ["AI", "做课", "提示词", "prompt", "知识创作者", "变现", " content ", "课程", "教學"],
        "exec_target": "ai_product_kb.md",
        "linked_asset": None,
    },
    "partner_matching": {
        "keywords": ["合伙人", "partner", "硬科技", "matching", "合伙", "股权", "co-founder", "founder"],
        "exec_target": "partner_matching_kb.md",
        "linked_asset": "hardtech_partner_risk_scanner.py",
    },
    "system_optimization": {
        "keywords": ["系统优化", "容錯", "自动化", "skill", "认知生态", "knowledge graph", "pipeline", "memory"],
        "exec_target": "system_optimization_kb.md",
        "linked_asset": "skill_bloodization_guardian.py",
    },
    "general": {
        "keywords": [],
        "exec_target": "general_kb.md",
        "linked_asset": None,
    },
}


def _classify_domain(text: str) -> str:
    text_lower = text.lower()
    scores = {}
    for domain, rules in DOMAIN_RULES.items():
        if domain == "general":
            continue
        score = sum(1 for kw in rules["keywords"] if kw.lower() in text_lower)
        if score:
            scores[domain] = score
    if not scores:
        return "general"
    return max(scores, key=scores.get)


def _sanitize_filename(name: str) -> str:
    return re.sub(r"[^\w\-_.]", "_", name)[:120]


def scan_extractions(date_str: str = "2026-04-08") -> list[dict[str, Any]]:
    date_dir = EXTRACTION_BASE / date_str
    if not date_dir.exists():
        return []
    records = []
    for subdir in sorted(date_dir.iterdir()):
        if not subdir.is_dir():
            continue
        extracted_file = subdir / "extracted.txt"
        meta_file = subdir / "meta.json"
        if not extracted_file.exists():
            continue
        record = {
            "source_dir": str(subdir),
            "source_name": subdir.name,
            "extracted_text": extracted_file.read_text(encoding="utf-8"),
            "meta": json.loads(meta_file.read_text(encoding="utf-8")) if meta_file.exists() else {},
        }
        records.append(record)
    return records


def structure_record(record: dict[str, Any]) -> dict[str, Any]:
    text = record["extracted_text"]
    meta = record.get("meta", {})
    domain = _classify_domain(text)

    # Generate a concise summary (first substantial paragraph or first 400 chars)
    summary = text[:400].strip().replace("\n", " ")
    for para in text.split("\n\n"):
        p = para.strip()
        if len(p) > 20:
            summary = p[:500]
            break

    structured = {
        "id": _sanitize_filename(record["source_name"]),
        "domain": domain,
        "title": record["source_name"][:100],
        "word_count": meta.get("word_count", len(text.split())),
        "paragraph_count": meta.get("paragraph_count", text.count("\n\n") + 1),
        "summary": summary,
        "source_path": record["source_dir"],
        "routed_to": meta.get("routed_to", "WEP"),
        "exec_target": DOMAIN_RULES[domain]["exec_target"],
        "linked_asset": DOMAIN_RULES[domain]["linked_asset"],
        "timestamp": datetime.now().isoformat(),
    }
    return structured


def store_to_master_db(structured_items: list[dict[str, Any]]) -> None:
    if MASTER_DB.exists():
        master = json.loads(MASTER_DB.read_text(encoding="utf-8"))
    else:
        master = {"version": "1.0", "items": []}

    existing_ids = {item["id"] for item in master["items"]}
    new_count = 0
    for item in structured_items:
        if item["id"] not in existing_ids:
            master["items"].append(item)
            existing_ids.add(item["id"])
            new_count += 1

    MASTER_DB.write_text(json.dumps(master, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Master DB updated: +{new_count} new items, total {len(master['items'])}")


def store_to_domain_md(structured_items: list[dict[str, Any]]) -> None:
    KB_BASE.mkdir(parents=True, exist_ok=True)
    domain_groups: dict[str, list[dict[str, Any]]] = {}
    for item in structured_items:
        domain_groups.setdefault(item["domain"], []).append(item)

    for domain, items in domain_groups.items():
        md_path = KB_BASE / DOMAIN_RULES[domain]["exec_target"]
        lines = []
        if md_path.exists():
            lines.append(md_path.read_text(encoding="utf-8"))
        else:
            lines.append(f"# {domain.replace('_', ' ').title()} Knowledge Base\n")
            lines.append(f"> Auto-generated by file_deep_internalizer.py\n")

        for item in items:
            lines.append(f"\n---\n")
            lines.append(f"## {item['title']}\n")
            lines.append(f"- **Domain**: {item['domain']}\n")
            lines.append(f"- **Words**: {item['word_count']} | **Paragraphs**: {item['paragraph_count']}\n")
            lines.append(f"- **Source**: `{item['source_path']}`\n")
            lines.append(f"- **Linked Asset**: {item['linked_asset'] or 'None'}\n")
            lines.append(f"- **Ingested At**: {item['timestamp']}\n")
            lines.append(f"\n**Summary**:\n\n{item['summary']}\n")

        md_path.write_text("\n".join(lines), encoding="utf-8")
        print(f"Domain MD written: {md_path} ({len(items)} items)")


def run_internalization(date_str: str = "2026-04-08") -> dict[str, Any]:
    records = scan_extractions(date_str)
    structured_items = [structure_record(r) for r in records]
    store_to_master_db(structured_items)
    store_to_domain_md(structured_items)

    summary = {
        "total_scanned": len(records),
        "domain_distribution": {},
        "execution_closure": {
            "master_db": str(MASTER_DB),
            "domain_md_dir": str(KB_BASE),
            "linked_assets": list({item["linked_asset"] for item in structured_items if item["linked_asset"]}),
        },
    }
    for item in structured_items:
        summary["domain_distribution"][item["domain"]] = summary["domain_distribution"].get(item["domain"], 0) + 1

    return summary


if __name__ == "__main__":
    result = run_internalization()
    print("\n=== File Deep Internalization Summary ===")
    print(json.dumps(result, ensure_ascii=False, indent=2))
