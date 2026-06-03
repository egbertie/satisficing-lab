"""
session_startup_guardian.py
Wraps Every Session startup sequence with embedder + router gates.
Call this at the top of the main session to validate pre-flight conditions.
"""
from __future__ import annotations
from pathlib import Path
from typing import Any

from cognitive_workload_router import CognitiveWorkloadRouter, RouteDecision
from egbertie_management_philosophy_embedder import EgbertieManagementPhilosophyEmbedder, PhilosophyGateResult


class SessionStartupGuardian:
    def __init__(self) -> None:
        self.router = CognitiveWorkloadRouter()
        self.embedder = EgbertieManagementPhilosophyEmbedder()

    def inspect_task(
        self,
        task_description: str,
        *,
        has_goal: bool,
        has_expected_result: bool,
        has_timeline: bool,
        is_project_before_product: bool,
        is_immediate_not_later: bool,
        respects_token_economics: bool,
        respects_benefit_economics: bool,
        is_satisficing_not_perfectionist: bool,
        input_text: str = "",
    ) -> dict[str, Any]:
        # Step 1: Philosophy gate
        philosophy = self.embedder.preflight_check(
            task_id=f"session-{hash(task_description) & 0xFFFFFFFF:08x}",
            task_summary=task_description[:200],
            has_goal=has_goal,
            has_expected_result=has_expected_result,
            has_timeline=has_timeline,
            is_project_before_product=is_project_before_product,
            follows_three_layer_architecture=True,
            is_immediate_not_later=is_immediate_not_later,
            respects_token_economics=respects_token_economics,
            respects_benefit_economics=respects_benefit_economics,
            is_satisficing_not_perfectionist=is_satisficing_not_perfectionist,
        )

        # Step 2: Router gate
        route = self.router.route(task_description, input_text=input_text)

        # Step 3: Barbell override check
        llm_ratio = self.router._recent_llm_ratio(window=20)
        barbell_ok = llm_ratio <= 0.15

        all_pass = philosophy.passed and barbell_ok and route.gate_check.get("q3_compress", False)

        return {
            "all_pass": all_pass,
            "philosophy": {
                "passed": philosophy.passed,
                "score": philosophy.score,
                "violations": philosophy.violations,
            },
            "router": {
                "route": route.route,
                "confidence": route.confidence,
                "savings_vs_llm": route.savings_vs_llm,
                "gate_check": route.gate_check,
                "llm_ratio_20": round(llm_ratio, 2),
                "barbell_ok": barbell_ok,
            },
            "timestamp": route.timestamp,
        }

    def close_session(
        self,
        task_description: str,
        *,
        c1_memory_written: bool,
        c2_memory_synced: bool,
        c3_task_master_updated: bool,
        c4_code_exists_and_runnable: bool,
        c5_git_snapshot: bool,
        c6_restart_recovery_passed: bool,
        c7_token_preaudit_passed: bool,
        c8_benefit_postaudit_archived: bool,
        no_rework_occurred: bool,
        is_honest_not_cosmetic: bool,
    ) -> dict[str, Any]:
        post = self.embedder.postflight_check(
            task_id=f"session-{hash(task_description) & 0xFFFFFFFF:08x}",
            task_summary=task_description[:200],
            c1_memory_written=c1_memory_written,
            c2_memory_synced=c2_memory_synced,
            c3_task_master_updated=c3_task_master_updated,
            c4_code_exists_and_runnable=c4_code_exists_and_runnable,
            c5_git_snapshot=c5_git_snapshot,
            c6_restart_recovery_passed=c6_restart_recovery_passed,
            c7_token_preaudit_passed=c7_token_preaudit_passed,
            c8_benefit_postaudit_archived=c8_benefit_postaudit_archived,
            no_rework_occurred=no_rework_occurred,
            is_honest_not_cosmetic=is_honest_not_cosmetic,
        )
        return {
            "all_pass": post.passed,
            "score": post.score,
            "violations": post.violations,
            "timestamp": post.timestamp,
        }


def demo() -> None:
    guardian = SessionStartupGuardian()
    report = guardian.inspect_task(
        task_description="将三层认知架构嵌入主工作流",
        has_goal=True,
        has_expected_result=True,
        has_timeline=True,
        is_project_before_product=True,
        is_immediate_not_later=True,
        respects_token_economics=True,
        respects_benefit_economics=True,
        is_satisficing_not_perfectionist=True,
    )
    print("Startup Inspection:", report)

    close = guardian.close_session(
        task_description="将三层认知架构嵌入主工作流",
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
    print("Session Close:", close)


if __name__ == "__main__":
    demo()
