"""
test_session_startup_guardian.py
pytest for session_startup_guardian.
"""
from pathlib import Path
import json

import session_startup_guardian as ssg


def test_inspect_task_all_pass(tmp_path: Path):
    # Use isolated ledger/db paths
    router_ledger = tmp_path / "router_ledger.json"
    phil_db = tmp_path / "phil_db.json"
    g = ssg.SessionStartupGuardian()
    g.router.ledger_path = router_ledger
    g.router.ledger = {"routes": [], "weekly_summary": {}}
    g.embedder.db_path = phil_db
    g.embedder.db = {"audits": [], "violations_by_rule": {}}

    report = g.inspect_task(
        task_description=" test task",
        has_goal=True,
        has_expected_result=True,
        has_timeline=True,
        is_project_before_product=True,
        is_immediate_not_later=True,
        respects_token_economics=True,
        respects_benefit_economics=True,
        is_satisficing_not_perfectionist=True,
    )
    assert report["all_pass"] is True
    assert report["philosophy"]["passed"] is True
    assert report["router"]["barbell_ok"] is True


def test_inspect_task_philosophy_fail(tmp_path: Path):
    router_ledger = tmp_path / "router_ledger.json"
    phil_db = tmp_path / "phil_db.json"
    g = ssg.SessionStartupGuardian()
    g.router.ledger_path = router_ledger
    g.router.ledger = {"routes": [], "weekly_summary": {}}
    g.embedder.db_path = phil_db
    g.embedder.db = {"audits": [], "violations_by_rule": {}}

    report = g.inspect_task(
        task_description="test task with violations",
        has_goal=False,
        has_expected_result=False,
        has_timeline=False,
        is_project_before_product=False,
        is_immediate_not_later=False,
        respects_token_economics=False,
        respects_benefit_economics=False,
        is_satisficing_not_perfectionist=False,
    )
    assert report["all_pass"] is False
    assert report["philosophy"]["passed"] is False
    assert len(report["philosophy"]["violations"]) > 0


def test_barbell_override_blocks(tmp_path: Path):
    router_ledger = tmp_path / "router_ledger.json"
    phil_db = tmp_path / "phil_db.json"
    g = ssg.SessionStartupGuardian()
    g.router.ledger_path = router_ledger
    # Seed ledger with 20 LLM routes to trigger barbell violation
    g.router.ledger = {"routes": [{"route": "llm"} for _ in range(20)], "weekly_summary": {}}
    g.embedder.db_path = phil_db
    g.embedder.db = {"audits": [], "violations_by_rule": {}}

    report = g.inspect_task(
        task_description="creative high level synthesis",
        has_goal=True,
        has_expected_result=True,
        has_timeline=True,
        is_project_before_product=True,
        is_immediate_not_later=True,
        respects_token_economics=True,
        respects_benefit_economics=True,
        is_satisficing_not_perfectionist=True,
    )
    # Even if philosophy passes, barbell should not be ok (llm_ratio > 0.15)
    assert report["router"]["barbell_ok"] is False
    assert report["all_pass"] is False


def test_close_session_pass(tmp_path: Path):
    phil_db = tmp_path / "phil_db.json"
    g = ssg.SessionStartupGuardian()
    g.embedder.db_path = phil_db
    g.embedder.db = {"audits": [], "violations_by_rule": {}}

    close = g.close_session(
        task_description="test close",
        c1_memory_written=True,
        c2_memory_synced=True,
        c3_task_master_updated=True,
        c4_code_exists_and_runnable=True,
        c5_git_snapshot=True,
        c6_restart_recovery_passed=True,
        c7_token_preaudit_passed=True,
        c8_benefit_postaudit_archived=True,
        no_rework_occurred=True,
        is_honest_not_cosmetic=True,
    )
    assert close["all_pass"] is True
    assert close["score"] == 100


def test_close_session_rework_and_memory_fail(tmp_path: Path):
    phil_db = tmp_path / "phil_db.json"
    g = ssg.SessionStartupGuardian()
    g.embedder.db_path = phil_db
    g.embedder.db = {"audits": [], "violations_by_rule": {}}

    close = g.close_session(
        task_description="test close fail",
        c1_memory_written=False,
        c2_memory_synced=False,
        c3_task_master_updated=True,
        c4_code_exists_and_runnable=True,
        c5_git_snapshot=True,
        c6_restart_recovery_passed=True,
        c7_token_preaudit_passed=True,
        c8_benefit_postaudit_archived=True,
        no_rework_occurred=False,
        is_honest_not_cosmetic=True,
    )
    assert close["all_pass"] is False
    assert any("memory" in v for v in close["violations"])
    assert any("返工" in v for v in close["violations"])
