"""
test_token_benefit_auditor.py
pytest for token_benefit_auditor.
"""
import json
from pathlib import Path

import token_benefit_auditor as tba


def test_calc_score_perfect():
    auditor = tba.TokenBenefitAuditor(db_path=Path("/tmp/test_auditor_1.json"))
    assert auditor._calc_score(500, True, 10) == 100


def test_calc_score_high_tokens():
    auditor = tba.TokenBenefitAuditor(db_path=Path("/tmp/test_auditor_2.json"))
    # 9000 tokens -> -30, not reused -> -15, quality 5 -> -10 (<7) = 45
    assert auditor._calc_score(9000, False, 5) == 45


def test_calc_score_moderate():
    auditor = tba.TokenBenefitAuditor(db_path=Path("/tmp/test_auditor_3.json"))
    # 3000 tokens -> -10, reused, quality 8 = 90
    assert auditor._calc_score(3000, True, 8) == 90


def test_audit_record(tmp_path: Path):
    db = tmp_path / "audit.json"
    auditor = tba.TokenBenefitAuditor(db_path=db)
    record = auditor.audit("task-001", 1500, True, 9, "note")
    assert record.task_id == "task-001"
    assert record.economics_score == 100
    assert db.exists()


def test_get_summary(tmp_path: Path):
    db = tmp_path / "audit.json"
    auditor = tba.TokenBenefitAuditor(db_path=db)
    auditor.audit("t1", 1000, True, 8)
    auditor.audit("t2", 2000, True, 9)
    auditor.audit("t3", 10000, False, 4)
    summary = auditor.get_summary(n=10)
    assert summary["sample_size"] == 3
    assert summary["high_token_count"] == 1
    assert summary["low_quality_count"] == 1
    assert summary["wasted_task_count"] == 1
    assert summary["health"] in ("✅", "⚠️", "🔴")


def test_close_loop(tmp_path: Path):
    db = tmp_path / "audit.json"
    auditor = tba.TokenBenefitAuditor(db_path=db)
    auditor.audit("t1", 1200, True, 8)
    result = auditor.close_loop(n=10)
    assert "avg_economics_score" in result
    data = json.loads(db.read_text(encoding="utf-8"))
    assert "summary" in data
