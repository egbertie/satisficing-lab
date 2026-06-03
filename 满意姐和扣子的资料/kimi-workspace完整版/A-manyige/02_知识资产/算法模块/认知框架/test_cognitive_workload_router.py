"""
test_cognitive_workload_router.py
pytest for cognitive_workload_router.
"""
import json
from pathlib import Path

import cognitive_workload_router as cwr


def test_classify_local():
    router = cwr.CognitiveWorkloadRouter(ledger_path=Path("/tmp/test_router_1.json"))
    route, conf = router.classify("批量提取这100个docx文件的内容并分类")
    assert route == "local"
    assert conf > 0.5


def test_classify_hybrid():
    router = cwr.CognitiveWorkloadRouter(ledger_path=Path("/tmp/test_router_2.json"))
    route, conf = router.classify("帮我总结这三篇文章的核心观点")
    assert route == "hybrid"
    assert conf > 0.3


def test_classify_llm():
    router = cwr.CognitiveWorkloadRouter(ledger_path=Path("/tmp/test_router_3.json"))
    route, conf = router.classify("基于儒商哲学设计一个全新的战略框架")
    assert route == "llm"
    assert conf > 0.3


def test_estimate_tokens():
    router = cwr.CognitiveWorkloadRouter(ledger_path=Path("/tmp/test_router_4.json"))
    assert router.estimate_tokens("local", "some text") == 0
    assert router.estimate_tokens("hybrid", "a b c d e") >= 200
    assert router.estimate_tokens("llm", "a b c d e") >= 800


def test_gate_check():
    router = cwr.CognitiveWorkloadRouter(ledger_path=Path("/tmp/test_router_5.json"))
    gates = router.gate_check("local")
    assert gates["q1_local"] is True
    assert gates["q2_light"] is True
    assert gates["c2_parallel"] is True

    gates_llm = router.gate_check("llm")
    assert gates_llm["q1_local"] is False
    assert gates_llm["c2_parallel"] is False


def test_route_downgrades_low_confidence_local(tmp_path: Path):
    ledger = tmp_path / "ledger.json"
    router = cwr.CognitiveWorkloadRouter(ledger_path=ledger)
    # "list files" should be local but confidence might be borderline
    result = router.route("list files in directory")
    if result.route == "local":
        assert result.confidence >= 0.5
    else:
        assert result.route == "hybrid"


def test_route_barbell_override(tmp_path: Path):
    ledger = tmp_path / "ledger.json"
    # Pre-seed ledger with 20 LLM routes
    fake_routes = [{"route": "llm"} for _ in range(20)]
    ledger.write_text(json.dumps({"routes": fake_routes, "weekly_summary": {}}), encoding="utf-8")

    router = cwr.CognitiveWorkloadRouter(ledger_path=ledger)
    # Even an LLM task should be downgraded if cap exceeded
    result = router.route("generate a creative story about AI")
    assert result.route == "hybrid"


def test_route_savings_calculation(tmp_path: Path):
    ledger = tmp_path / "ledger.json"
    router = cwr.CognitiveWorkloadRouter(ledger_path=ledger)
    result = router.route("parse all xml files", input_text="word1 word2 word3")
    if result.route == "local":
        assert result.savings_vs_llm == 1.0
    elif result.route == "hybrid":
        assert 0 < result.savings_vs_llm < 1.0


def test_weekly_audit(tmp_path: Path):
    ledger = tmp_path / "ledger.json"
    router = cwr.CognitiveWorkloadRouter(ledger_path=ledger)
    router.route("提取文件")
    router.route("总结文章")
    audit = router.weekly_audit(window=10)
    assert "local_ratio" in audit
    assert "barbell_health" in audit
