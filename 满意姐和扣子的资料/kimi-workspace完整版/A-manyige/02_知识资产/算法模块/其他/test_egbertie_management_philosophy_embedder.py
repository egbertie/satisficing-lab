"""
test_egbertie_management_philosophy_embedder.py
pytest for egbertie_management_philosophy_embedder.
"""
from pathlib import Path

import egbertie_management_philosophy_embedder as empe


def test_preflight_all_pass(tmp_path: Path):
    db = tmp_path / "philosophy.json"
    embedder = empe.EgbertieManagementPhilosophyEmbedder(db_path=db)
    result = embedder.preflight_check(
        task_id="t1",
        task_summary="test",
        has_goal=True,
        has_expected_result=True,
        has_timeline=True,
        is_project_before_product=True,
        follows_three_layer_architecture=True,
        is_immediate_not_later=True,
        respects_token_economics=True,
        respects_benefit_economics=True,
        is_satisficing_not_perfectionist=True,
    )
    assert result.passed is True
    assert result.score == 100
    assert len(result.violations) == 0


def test_preflight_multiple_failures(tmp_path: Path):
    db = tmp_path / "philosophy.json"
    embedder = empe.EgbertieManagementPhilosophyEmbedder(db_path=db)
    result = embedder.preflight_check(
        task_id="t2",
        task_summary="test",
        has_goal=False,
        has_expected_result=False,
        has_timeline=False,
        is_project_before_product=False,
        follows_three_layer_architecture=False,
        is_immediate_not_later=False,
        respects_token_economics=False,
        respects_benefit_economics=False,
        is_satisficing_not_perfectionist=False,
    )
    assert result.passed is False
    assert len(result.violations) == 9
    assert result.score == 1


def test_postflight_all_pass(tmp_path: Path):
    db = tmp_path / "philosophy.json"
    embedder = empe.EgbertieManagementPhilosophyEmbedder(db_path=db)
    result = embedder.postflight_check(
        task_id="t3",
        task_summary="test",
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
    assert result.passed is True
    assert result.score == 100


def test_postflight_rework_and_dishonesty(tmp_path: Path):
    db = tmp_path / "philosophy.json"
    embedder = empe.EgbertieManagementPhilosophyEmbedder(db_path=db)
    result = embedder.postflight_check(
        task_id="t4",
        task_summary="test",
        c1_memory_written=True,
        c2_memory_synced=True,
        c3_task_master_updated=True,
        c4_code_exists_and_runnable=True,
        c5_git_snapshot=True,
        c6_restart_recovery_passed=True,
        c7_token_preaudit_passed=True,
        c8_benefit_postaudit_archived=True,
        no_rework_occurred=False,
        is_honest_not_cosmetic=False,
    )
    assert result.passed is False
    assert len(result.violations) == 2
    assert "返工" in result.violations[0]
    assert "诚实" in result.violations[1]


def test_violation_aggregation(tmp_path: Path):
    db = tmp_path / "philosophy.json"
    embedder = empe.EgbertieManagementPhilosophyEmbedder(db_path=db)
    embedder.preflight_check(
        task_id="t5",
        task_summary="test",
        has_goal=False,
        has_expected_result=True,
        has_timeline=True,
        is_project_before_product=False,
        follows_three_layer_architecture=True,
        is_immediate_not_later=True,
        respects_token_economics=True,
        respects_benefit_economics=True,
        is_satisficing_not_perfectionist=True,
    )
    report = embedder.health_report(n=10)
    assert report["sample_size"] == 1
    assert report["pass_rate"] == 0.0
    assert len(report["top_violations"]) == 2


def test_get_latest_audit(tmp_path: Path):
    db = tmp_path / "philosophy.json"
    embedder = empe.EgbertieManagementPhilosophyEmbedder(db_path=db)
    embedder.preflight_check(
        task_id="t6",
        task_summary="first",
        has_goal=True,
        has_expected_result=True,
        has_timeline=True,
        is_project_before_product=True,
        follows_three_layer_architecture=True,
        is_immediate_not_later=True,
        respects_token_economics=True,
        respects_benefit_economics=True,
        is_satisficing_not_perfectionist=True,
    )
    latest = embedder.get_latest_audit("t6")
    assert latest is not None
    assert latest["task_summary"] == "first"
    assert latest["passed"] is True
