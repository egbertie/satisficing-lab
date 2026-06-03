"""
---
KIA-CODE: 知识入库代码级闭环
Asset: cognitive_workload_router.py
Status: ✅ 代码级KIA完成
Date: 2026-04-15
Batch: OM-03 Python资产25份代码级KIA-批次四

KIA-Loop:
  - 接收清点: 2026-04-15
  - 轻量提取: 2026-04-15 (代码结构识别)
  - 查重去冗: 2026-04-15 (无重复代码)
  - Tier分级: T1 (核心项目资产)
  - 深度洞察: 2026-04-15 (协作与认知系统)
  - 血液化: ✅ 完成 (五路图腾映射确认)
  - 归档锁定: 2026-04-15

功能定位:
  - 用途: 认知工作负载路由器
  - 关联: 任务分配
  - 维护者: 蓝军+满意姐

血液化映射:
  - 五路图腾关联: 负载均衡
  - 产品映射: 观自在-动态调度
  - 运营映射: 协作与认知优化

---
"""

"""
cognitive_workload_router.py
Hybrid 'Local Program + LLM' cognitive workload router.
Token Economic Principle: local-first, hybrid-second, LLM-only as last resort.
"""
from __future__ import annotations
import json
import hashlib
import re
from pathlib import Path
from typing import Any, Literal
from dataclasses import dataclass, asdict

TASK_COMPLEXITY_PATTERNS = {
    "local": [
        "extract", "parse", "batch", "list", "count", "sort",
        "提取", "解析", "批量", "列表", "统计", "排序", "分类",
        "read file", "search skill", "check status", "git status",
        "download", "upload", "move file", "copy file", "rename",
        "pytest", "run test", "lint", "format", "compress",
    ],
    "hybrid": [
        "summarize", "classify", "compare", "analyze",
        "总结", "分类", "对比", "分析", "extract key points",
        "结构化", "归纳", "评估", "评分", "outline",
        "categorize", "rank", "prioritize", "index",
    ],
    "llm": [
        "synthesize", "creative", "generate proposal", "write story",
        "deep research", "philosophy", "ethics", "strategy",
        "综合", "创造", "撰写方案", "深度研究", "哲学", "伦理",
        "战略", "洞察", "直觉", "debate", "brainstorm",
        "design from scratch", "novel", "invent", "imagine",
    ],
}

DEFAULT_BARBELL_LLM_CAP = 0.15


@dataclass
class RouteDecision:
    task_id: str
    task_summary: str
    route: Literal["local", "hybrid", "llm"]
    confidence: float
    estimated_tokens_local: int
    estimated_tokens_hybrid: int
    estimated_tokens_llm: int
    savings_vs_llm: float
    gate_check: dict[str, bool]
    fallback: str | None
    timestamp: str


class CognitiveWorkloadRouter:
    def __init__(self, ledger_path: Path | None = None) -> None:
        self.ledger_path = ledger_path or Path("/root/.openclaw/workspace/token_economic_ledger.json")
        self.ledger: dict[str, Any] = self._load_ledger()

    def _load_ledger(self) -> dict[str, Any]:
        if self.ledger_path.exists():
            return json.loads(self.ledger_path.read_text(encoding="utf-8"))
        return {"routes": [], "weekly_summary": {}}

    def _save_ledger(self) -> None:
        self.ledger_path.write_text(json.dumps(self.ledger, ensure_ascii=False, indent=2), encoding="utf-8")

    def classify(self, task_description: str) -> tuple[str, float]:
        text = task_description.lower()
        scores: dict[str, int] = {"local": 0, "hybrid": 0, "llm": 0}
        for route, patterns in TASK_COMPLEXITY_PATTERNS.items():
            for p in patterns:
                if re.search(rf"\b{re.escape(p.lower())}\b", text):
                    scores[route] += 2
                elif p.lower() in text:
                    scores[route] += 1
        total = sum(scores.values())
        if total == 0:
            return "hybrid", 0.5
        best = max(scores, key=scores.get)  # type: ignore[arg-type]
        confidence = scores[best] / total
        return best, confidence

    def estimate_tokens(self, route: str, input_text: str = "") -> int:
        base = len(input_text.split())
        multipliers = {
            "local": 0,
            "hybrid": max(200, base // 5),
            "llm": max(800, base // 2),
        }
        return multipliers.get(route, 0)

    def gate_check(self, route: str) -> dict[str, bool]:
        return {
            "q1_local": route in ("local", "hybrid"),
            "q2_light": route != "llm",
            "q3_compress": True,
            "c1_reusable": True,
            "c2_parallel": route == "local",
            "c3_boundary_clear": True,
        }

    def _recent_llm_ratio(self, window: int = 20) -> float:
        routes = self.ledger.get("routes", [])
        if not routes:
            return 0.0
        recent = routes[-window:]
        llm_count = sum(1 for r in recent if r.get("route") == "llm")
        return llm_count / len(recent)

    def route(self, task_description: str, input_text: str = "") -> RouteDecision:
        import datetime as _dt
        task_id = hashlib.sha256(task_description.encode()).hexdigest()[:12]
        route, confidence = self.classify(task_description)

        est_local = self.estimate_tokens("local", input_text)
        est_hybrid = self.estimate_tokens("hybrid", input_text)
        est_llm = self.estimate_tokens("llm", input_text)

        # Confidence override: low-confidence local bumps to hybrid
        if route == "local" and confidence < 0.5:
            route = "hybrid"
            confidence = 0.5

        # Barbell override: if LLM budget exceeded, downgrade to hybrid
        if route == "llm" and self._recent_llm_ratio() > DEFAULT_BARBELL_LLM_CAP:
            route = "hybrid"
            confidence = min(confidence, 0.6)

        gates = self.gate_check(route)
        savings = 0.0
        if route == "hybrid" and est_llm > 0:
            savings = (est_llm - est_hybrid) / est_llm
        elif route == "local" and est_llm > 0:
            savings = 1.0

        fallback = "hybrid" if route == "llm" else "llm"

        decision = RouteDecision(
            task_id=task_id,
            task_summary=task_description[:120],
            route=route,  # type: ignore[arg-type]
            confidence=round(confidence, 2),
            estimated_tokens_local=est_local,
            estimated_tokens_hybrid=est_hybrid,
            estimated_tokens_llm=est_llm,
            savings_vs_llm=round(savings, 2),
            gate_check=gates,
            fallback=fallback,
            timestamp=_dt.datetime.now().isoformat(),
        )

        self.ledger["routes"].append(asdict(decision))
        self._save_ledger()
        return decision

    def weekly_audit(self, window: int = 100) -> dict[str, Any]:
        routes = self.ledger.get("routes", [])[-window:]
        if not routes:
            return {"error": "No routes recorded yet."}

        total = len(routes)
        local_count = sum(1 for r in routes if r.get("route") == "local")
        hybrid_count = sum(1 for r in routes if r.get("route") == "hybrid")
        llm_count = sum(1 for r in routes if r.get("route") == "llm")
        avg_savings = sum(r.get("savings_vs_llm", 0.0) for r in routes) / total
        llm_ratio = llm_count / total

        import datetime as _dt
        key = _dt.date.today().isoformat()
        audit = {
            "audit_date": key,
            "period_routes": total,
            "local_ratio": round(local_count / total, 2),
            "hybrid_ratio": round(hybrid_count / total, 2),
            "llm_ratio": round(llm_ratio, 2),
            "avg_savings_vs_pure_llm": round(avg_savings, 2),
            "barbell_health": "✅" if llm_ratio <= DEFAULT_BARBELL_LLM_CAP else "⚠️ LLM overuse",
            "recommendation": (
                "Increase high-value LLM work (research/synthesis)"
                if llm_ratio <= DEFAULT_BARBELL_LLM_CAP
                else "Urgent: shift tasks to local/hybrid to restore barbell balance"
            ),
        }
        self.ledger.setdefault("weekly_summary", {})[key] = audit
        self._save_ledger()
        return audit


if __name__ == "__main__":
    router = CognitiveWorkloadRouter()
    demos = [
        "批量提取这100个docx文件的内容并分类",
        "帮我总结这三篇文章的核心观点",
        "基于儒商哲学和决策科学，为硬科技合伙人匹配设计一个全新的战略框架",
    ]
    for d in demos:
        result = router.route(d, input_text=d)
        print(f"[{result.route}] {result.task_summary} (confidence={result.confidence}, savings={result.savings_vs_llm})")
    print("\nWeekly Audit:", router.weekly_audit())
