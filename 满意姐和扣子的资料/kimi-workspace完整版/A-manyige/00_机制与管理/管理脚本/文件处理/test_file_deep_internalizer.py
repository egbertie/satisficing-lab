"""
test_file_deep_internalizer.py
pytest for file_deep_internalizer.
"""
import json
from pathlib import Path

import file_deep_internalizer as fdi


def test_classify_domain_decision_science():
    text = "This book is about decision making, cognitive bias, and behavioral economics."
    assert fdi._classify_domain(text) == "decision_science"


def test_classify_domain_confucian():
    text = "黎红雷教授阐述了儒商伦理与企业治理中的仁义礼智信。"
    assert fdi._classify_domain(text) == "confucian_philosophy"


def test_classify_domain_general():
    text = "Random text about nothing specific at all."
    assert fdi._classify_domain(text) == "general"


def test_structure_record():
    record = {
        "source_dir": "/tmp/test",
        "source_name": "test_doc",
        "extracted_text": "This is a decision science document about satisficing and bias.",
        "meta": {"word_count": 12, "paragraph_count": 1},
    }
    structured = fdi.structure_record(record)
    assert structured["domain"] == "decision_science"
    assert structured["title"] == "test_doc"
    assert structured["exec_target"] == "decision_science_kb.md"
    assert structured["linked_asset"] == "satisficing_decision_engine.py"


def test_store_to_master_db(tmp_path: Path, monkeypatch):
    db_path = tmp_path / "master.json"
    monkeypatch.setattr(fdi, "MASTER_DB", db_path)
    items = [
        {"id": "doc-a", "domain": "general", "title": "Doc A"},
        {"id": "doc-b", "domain": "general", "title": "Doc B"},
    ]
    fdi.store_to_master_db(items)
    assert db_path.exists()
    data = json.loads(db_path.read_text(encoding="utf-8"))
    assert len(data["items"]) == 2

    # Idempotent: re-insert same ids should not duplicate
    fdi.store_to_master_db(items)
    data = json.loads(db_path.read_text(encoding="utf-8"))
    assert len(data["items"]) == 2


def test_store_to_domain_md(tmp_path: Path, monkeypatch):
    kb_base = tmp_path / "domains"
    monkeypatch.setattr(fdi, "KB_BASE", kb_base)
    items = [
        {"id": "doc-1", "domain": "general", "title": "General Doc", "word_count": 10, "paragraph_count": 1, "summary": "Summary", "source_path": "/tmp", "linked_asset": None, "timestamp": "2026-04-09T12:00:00"},
    ]
    fdi.store_to_domain_md(items)
    md_path = kb_base / "general_kb.md"
    assert md_path.exists()
    content = md_path.read_text(encoding="utf-8")
    assert "General Doc" in content
    assert "Summary" in content


def test_run_internalization(tmp_path: Path, monkeypatch):
    extraction_base = tmp_path / "internalization_output" / "2026-04-08"
    subdir = extraction_base / "test_file"
    subdir.mkdir(parents=True)
    (subdir / "extracted.txt").write_text(
        " This is about decision making and cognitive bias. ", encoding="utf-8"
    )
    (subdir / "meta.json").write_text(
        json.dumps({"word_count": 8, "paragraph_count": 1}), encoding="utf-8"
    )

    monkeypatch.setattr(fdi, "EXTRACTION_BASE", extraction_base.parent)
    monkeypatch.setattr(fdi, "MASTER_DB", tmp_path / "master.json")
    monkeypatch.setattr(fdi, "KB_BASE", tmp_path / "domains")

    result = fdi.run_internalization("2026-04-08")
    assert result["total_scanned"] == 1
    assert result["domain_distribution"]["decision_science"] == 1
    assert "satisficing_decision_engine.py" in result["execution_closure"]["linked_assets"]
