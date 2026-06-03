"""
token_benefit_auditor.py
Audits every completed task against Token Economics + Benefit Economics.
Runs at task completion to close the loop.
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any
from dataclasses import dataclass, asdict

DEFAULT_DB = Path("/root/.openclaw/workspace/token_benefit_audit.json")


@dataclass
class AuditRecord:
    task_id: str
    actual_tokens: int
    output_reused: bool
    output_quality_score: int  # 0-10
    economics_score: int  # 0-100
    notes: str = ""


class TokenBenefitAuditor:
    def __init__(self, db_path: Path | None = None) -> None:
        self.db_path = db_path or DEFAULT_DB
        self.db: dict[str, Any] = self._load()

    def _load(self) -> dict[str, Any]:
        if self.db_path.exists():
            return json.loads(self.db_path.read_text(encoding="utf-8"))
        return {"audits": [], "summary": {}}

    def _save(self) -> None:
        self.db_path.write_text(json.dumps(self.db, ensure_ascii=False, indent=2), encoding="utf-8")

    def _calc_score(self, tokens: int, reused: bool, quality: int) -> int:
        score = 100
        if tokens > 8000:
            score -= 30
        elif tokens > 4000:
            score -= 20
        elif tokens > 2000:
            score -= 10
        if not reused:
            score -= 15
        if quality < 5:
            score -= 25
        elif quality < 7:
            score -= 10
        return max(0, score)

    def audit(
        self,
        task_id: str,
        actual_tokens: int,
        output_reused: bool,
        output_quality_score: int,
        notes: str = "",
    ) -> AuditRecord:
        score = self._calc_score(actual_tokens, output_reused, output_quality_score)
        record = AuditRecord(
            task_id=task_id,
            actual_tokens=actual_tokens,
            output_reused=output_reused,
            output_quality_score=output_quality_score,
            economics_score=score,
            notes=notes,
        )
        self.db["audits"].append(asdict(record))
        self._save()
        return record

    def get_summary(self, n: int = 50) -> dict[str, Any]:
        audits = self.db.get("audits", [])
        recent = audits[-n:] if n < len(audits) else audits
        if not recent:
            return {"error": "No audits yet."}
        avg_score = sum(a["economics_score"] for a in recent) / len(recent)
        high_token = [a for a in recent if a["actual_tokens"] > 5000]
        low_quality = [a for a in recent if a["output_quality_score"] < 7]
        wasted = [a for a in recent if a["economics_score"] < 60]
        return {
            "sample_size": len(recent),
            "avg_economics_score": round(avg_score, 1),
            "high_token_count": len(high_token),
            "low_quality_count": len(low_quality),
            "wasted_task_count": len(wasted),
            "health": "✅" if avg_score >= 80 else ("⚠️" if avg_score >= 60 else "🔴"),
        }

    def close_loop(self, n: int = 50) -> dict[str, Any]:
        summary = self.get_summary(n)
        self.db.setdefault("summary", {})[str(Path.cwd())] = summary
        self._save()
        return summary


if __name__ == "__main__":
    auditor = TokenBenefitAuditor()
    auditor.audit("task-001", 1200, True, 8, "local file parse")
    auditor.audit("task-002", 3500, True, 9, "hybrid research synthesis")
    auditor.audit("task-003", 9000, False, 5, "llm overuse, low reuse")
    print(auditor.close_loop())
