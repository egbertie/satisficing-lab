"""
egbertie_management_philosophy_embedder.py
Executable codification of Egbertie's management philosophy.
Every task must pass these gates before execution and after completion.
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any
from dataclasses import dataclass, asdict

DEFAULT_DB = Path("/root/.openclaw/workspace/egbertie_philosophy_audit.json")


@dataclass
class PhilosophyGateResult:
    task_id: str
    task_summary: str
    passed: bool
    violations: list[str]
    score: int  # 0-100
    timestamp: str


class EgbertieManagementPhilosophyEmbedder:
    """
    Codifies Egbertie's management philosophy into an executable pre-flight and post-flight checklist.
    """

    def __init__(self, db_path: Path | None = None) -> None:
        self.db_path = db_path or DEFAULT_DB
        self.db: dict[str, Any] = self._load()

    def _load(self) -> dict[str, Any]:
        if self.db_path.exists():
            return json.loads(self.db_path.read_text(encoding="utf-8"))
        return {"audits": [], "violations_by_rule": {}}

    def _save(self) -> None:
        self.db_path.write_text(json.dumps(self.db, ensure_ascii=False, indent=2), encoding="utf-8")

    # ── Pre-flight gates (must pass before execution) ──
    def preflight_check(
        self,
        task_id: str,
        task_summary: str,
        *,
        has_goal: bool,
        has_expected_result: bool,
        has_timeline: bool,
        is_project_before_product: bool,
        follows_three_layer_architecture: bool,
        is_immediate_not_later: bool,
        respects_token_economics: bool,
        respects_benefit_economics: bool,
        is_satisficing_not_perfectionist: bool,
    ) -> PhilosophyGateResult:
        violations: list[str] = []
        if not has_goal:
            violations.append("[P0] 每个产出必须有明确目标")
        if not has_expected_result:
            violations.append("[P0] 每个产出必须有结果预期")
        if not has_timeline:
            violations.append("[P0] 每个产出必须有时间节点")
        if not is_project_before_product:
            violations.append("[P0] 必须先项目升级，后产品研发")
        if not follows_three_layer_architecture:
            violations.append("[P0] 必须遵循三层认知架构（Local≥70% / Hybrid~15% / LLM≤15%）")
        if not is_immediate_not_later:
            violations.append("[P0] 禁止用'本周/稍后/明天'替代'立即执行'")
        if not respects_token_economics:
            violations.append("[P0] 必须通过Token经济学安检（Q1-Q3）")
        if not respects_benefit_economics:
            violations.append("[P0] 必须通过效益经济学安检（C1-C3）")
        if not is_satisficing_not_perfectionist:
            violations.append("[P1] 必须遵循满意解原则，拒绝完美主义")

        score = max(0, 100 - len(violations) * 11)
        passed = len(violations) == 0

        import datetime as _dt
        result = PhilosophyGateResult(
            task_id=task_id,
            task_summary=task_summary,
            passed=passed,
            violations=violations,
            score=score,
            timestamp=_dt.datetime.now().isoformat(),
        )
        self._record(result)
        return result

    # ── Post-flight gates (must pass before marking FIN) ──
    def postflight_check(
        self,
        task_id: str,
        task_summary: str,
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
    ) -> PhilosophyGateResult:
        violations: list[str] = []
        if not c1_memory_written:
            violations.append("[C1] memory/YYYY-MM-DD.md 未追加")
        if not c2_memory_synced:
            violations.append("[C2] MEMORY.md 指针未同步")
        if not c3_task_master_updated:
            violations.append("[C3] TASK_MASTER.md 未更新")
        if not c4_code_exists_and_runnable:
            violations.append("[C4] 当日代码/产出物不存在或不可运行")
        if not c5_git_snapshot:
            violations.append("[C5] Git 状态未快照")
        if not c6_restart_recovery_passed:
            violations.append("[C6] 重启恢复自检未通过")
        if not c7_token_preaudit_passed:
            violations.append("[C7] Token经济学预审未通过")
        if not c8_benefit_postaudit_archived:
            violations.append("[C8] 效益经济学后审未归档")
        if not no_rework_occurred:
            violations.append("[P0] 发生了返工——必须一次做对")
        if not is_honest_not_cosmetic:
            violations.append("[P0] 产出存在粉饰或隐瞒——诚实至上")

        score = max(0, 100 - len(violations) * 10)
        passed = len(violations) == 0

        import datetime as _dt
        result = PhilosophyGateResult(
            task_id=task_id,
            task_summary=task_summary,
            passed=passed,
            violations=violations,
            score=score,
            timestamp=_dt.datetime.now().isoformat(),
        )
        self._record(result)
        return result

    def _record(self, result: PhilosophyGateResult) -> None:
        self.db["audits"].append(asdict(result))
        for v in result.violations:
            self.db.setdefault("violations_by_rule", {}).setdefault(v, 0)
            self.db["violations_by_rule"][v] += 1
        self._save()

    def get_latest_audit(self, task_id: str) -> dict[str, Any] | None:
        audits = self.db.get("audits", [])
        for a in reversed(audits):
            if a.get("task_id") == task_id:
                return a
        return None

    def health_report(self, n: int = 50) -> dict[str, Any]:
        audits = self.db.get("audits", [])[-n:]
        if not audits:
            return {"error": "No audits yet."}
        passed = sum(1 for a in audits if a.get("passed"))
        total = len(audits)
        return {
            "sample_size": total,
            "pass_rate": round(passed / total, 2),
            "avg_score": round(sum(a.get("score", 0) for a in audits) / total, 1),
            "top_violations": sorted(
                self.db.get("violations_by_rule", {}).items(),
                key=lambda x: x[1],
                reverse=True,
            )[:5],
            "health": "✅" if passed / total >= 0.95 else ("⚠️" if passed / total >= 0.80 else "🔴"),
        }


def demo() -> None:
    embedder = EgbertieManagementPhilosophyEmbedder()

    # Example of a task that is about to execute correctly
    pre = embedder.preflight_check(
        task_id="phase2-router-embed-001",
        task_summary="将cognitive_workload_router嵌入主工作流",
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
    print(f"[Pre-flight] Passed={pre.passed}, Score={pre.score}, Violations={pre.violations}")

    # Example of post-flight after completion
    post = embedder.postflight_check(
        task_id="phase2-router-embed-001",
        task_summary="将cognitive_workload_router嵌入主工作流",
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
    print(f"[Post-flight] Passed={post.passed}, Score={post.score}, Violations={post.violations}")

    print("Health Report:", embedder.health_report())


if __name__ == "__main__":
    demo()
