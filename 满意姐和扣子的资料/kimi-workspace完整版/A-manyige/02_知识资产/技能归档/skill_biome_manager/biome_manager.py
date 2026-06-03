"""
Biome Manager - Skill生态系统工程化管理
健康度扫描、依赖隔离、退休机制
"""

import os
import re
import json
import sqlite3
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class SkillHealth:
    skill_name: str
    has_skill_md: bool
    has_tests: bool
    has_demo: bool
    hard_dependency_count: int
    last_modified_days: float
    import_risk: List[str]
    score: float
    status: str  # healthy | warning | critical | zombie


class BiomeManager:
    """Skill生物群落管理器"""

    def __init__(self, workspace: str = "/root/.openclaw/workspace"):
        self.workspace = Path(workspace)
        self.skills_dir = self.workspace / "skills"
        self.db_path = self.workspace / "skill_biome.db"
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS skill_organisms (
                skill_name TEXT PRIMARY KEY,
                report_json TEXT,
                scanned_at TEXT
            )
        """)
        conn.commit()
        conn.close()

    def scan_all(self) -> List[SkillHealth]:
        results = []
        if not self.skills_dir.exists():
            return results

        for skill_dir in self.skills_dir.iterdir():
            if not skill_dir.is_dir() or skill_dir.name.startswith("."):
                continue
            health = self._scan_single(skill_dir)
            results.append(health)
            self._persist(health)
        return results

    def _scan_single(self, skill_dir: Path) -> SkillHealth:
        name = skill_dir.name
        has_md = (skill_dir / "SKILL.md").exists()
        has_tests = any((skill_dir / d).exists() and any((skill_dir / d).rglob("test*.py"))
                        for d in ["tests", "test"])
        has_demo = any((skill_dir / f).exists() for f in ["demo.py", "demo_unified.py"])

        # 硬依赖扫描
        hard_deps = 0
        import_risks = []
        for py_file in skill_dir.rglob("*.py"):
            try:
                text = py_file.read_text()
                # 检查是否有外部API硬编码密钥或高风险import
                if re.search(r'api[_-]?key\s*=\s*["\'][^"\']+["\']', text, re.I):
                    hard_deps += 1
                risky = ["requests.get", "urllib.request", "subprocess.run", "eval(", "exec("]
                for r in risky:
                    if r in text:
                        import_risks.append(f"{py_file.name}:{r}")
            except:
                pass

        # 最后修改时间
        try:
            import subprocess
            result = subprocess.run(
                ["git", "log", "-1", "--format=%ct", "--", str(skill_dir)],
                capture_output=True, text=True, cwd=str(self.workspace)
            )
            last_modified_days = float("inf")
            if result.returncode == 0 and result.stdout.strip():
                from time import time
                last_commit = float(result.stdout.strip())
                last_modified_days = (time() - last_commit) / 86400
        except:
            last_modified_days = float("inf")

        # 评分
        score = 0.0
        if has_md:
            score += 25
        if has_tests:
            score += 25
        if has_demo:
            score += 20
        score += max(0, 20 - hard_deps * 5)
        score += max(0, 10 - min(last_modified_days / 30, 10))
        score = min(100, score)

        if score >= 70:
            status = "healthy"
        elif score >= 50:
            status = "warning"
        elif last_modified_days < 180:
            status = "critical"
        else:
            status = "zombie"

        return SkillHealth(
            skill_name=name,
            has_skill_md=has_md,
            has_tests=has_tests,
            has_demo=has_demo,
            hard_dependency_count=hard_deps,
            last_modified_days=last_modified_days,
            import_risk=import_risks[:5],
            score=round(score, 1),
            status=status
        )

    def _persist(self, health: SkillHealth):
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            INSERT OR REPLACE INTO skill_organisms (skill_name, report_json, scanned_at)
            VALUES (?, ?, datetime('now'))
        """, (health.skill_name, json.dumps(health.__dict__)))
        conn.commit()
        conn.close()

    def generate_report(self) -> Dict:
        healths = self.scan_all()
        counts = {"healthy": 0, "warning": 0, "critical": 0, "zombie": 0}
        for h in healths:
            counts[h.status] = counts.get(h.status, 0) + 1
        zombies = [h.skill_name for h in healths if h.status == "zombie"]
        criticals = [h.skill_name for h in healths if h.status == "critical"]
        return {
            "total_skills": len(healths),
            "status_distribution": counts,
            "average_score": round(sum(h.score for h in healths) / len(healths), 1) if healths else 0,
            "zombie_candidates": zombies,
            "critical_skills": criticals,
            "recommendations": [
                f"有{len(zombies)}个僵尸Skill建议清理" if zombies else "无僵尸Skill",
                f"有{len(criticals)}个危急Skill需要优先修复" if criticals else "无危急Skill",
            ]
        }
