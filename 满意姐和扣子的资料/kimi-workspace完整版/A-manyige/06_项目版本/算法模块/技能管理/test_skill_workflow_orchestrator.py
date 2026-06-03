"""
test_skill_workflow_orchestrator.py
pytest for skill_workflow_orchestrator.
"""
from pathlib import Path

import skill_workflow_orchestrator as swo


def test_classify_deep_research():
    orch = swo.SkillWorkflowOrchestrator()
    assert orch.classify_task("帮我深度研究一下硬科技合伙人匹配") == swo.WorkflowType.DEEP_RESEARCH
    assert orch.classify_task("做一份行业文献综述") == swo.WorkflowType.DEEP_RESEARCH


def test_classify_landscape_scanning():
    orch = swo.SkillWorkflowOrchestrator()
    assert orch.classify_task("扫描一下竞争格局") == swo.WorkflowType.LANDSCAPE_SCANNING
    assert orch.classify_task("这个 ecosystem 有哪些玩家") == swo.WorkflowType.LANDSCAPE_SCANNING


def test_classify_comparative_evaluation():
    orch = swo.SkillWorkflowOrchestrator()
    assert orch.classify_task("对比三个方案择优") == swo.WorkflowType.COMPARATIVE_EVALUATION
    assert orch.classify_task("用 MCDA 评估选项") == swo.WorkflowType.COMPARATIVE_EVALUATION


def test_classify_risk_audit():
    orch = swo.SkillWorkflowOrchestrator()
    assert orch.classify_task("蓝军审计一下这份报告") == swo.WorkflowType.RISK_AUDIT
    assert orch.classify_task("风险评估") == swo.WorkflowType.RISK_AUDIT


def test_classify_execution_and_closure():
    orch = swo.SkillWorkflowOrchestrator()
    assert orch.classify_task("把这个功能闭环并 pytest 测试") == swo.WorkflowType.EXECUTION_AND_CLOSURE
    assert orch.classify_task("提交并登记") == swo.WorkflowType.EXECUTION_AND_CLOSURE


def test_plan_returns_valid_workflow(tmp_path: Path):
    orch = swo.SkillWorkflowOrchestrator()
    orch.ledger_path = tmp_path / "ledger.json"
    orch.ledger = {"workflow_runs": [], "workflow_stats": {}}

    plan = orch.plan("帮我深度研究一下硬科技合伙人匹配")
    assert plan.workflow_type == swo.WorkflowType.DEEP_RESEARCH
    assert len(plan.steps) > 0
    assert plan.estimated_llm_ratio <= 0.15
    assert "杠铃" in plan.barbell_rule or "barbell" in plan.barbell_rule.lower()


def test_health_barbell_alarm(tmp_path: Path):
    orch = swo.SkillWorkflowOrchestrator()
    orch.ledger_path = tmp_path / "ledger.json"
    # Fake a history of high-llm runs
    orch.ledger = {
        "workflow_runs": [
            {"workflow": "creative_generation", "llm_ratio": 0.45, "timestamp": "2026-04-09T13:00:00"}
            for _ in range(20)
        ],
        "workflow_stats": {},
    }
    health = orch.health(n=20)
    assert health["barbell_alarm"] is True
    assert health["avg_llm_ratio"] == 0.45


def test_default_structured_analysis():
    orch = swo.SkillWorkflowOrchestrator()
    # A vague task that doesn't match any specific keyword
    assert orch.classify_task("随便分析一下") == swo.WorkflowType.STRUCTURED_ANALYSIS


def test_all_workflows_have_steps():
    for wf in swo.WorkflowType:
        pattern = swo.WORKFLOW_PATTERNS[wf]
        assert "description" in pattern
        assert "steps" in pattern
        assert len(pattern["steps"]) > 0
        assert "barbell_rule" in pattern
