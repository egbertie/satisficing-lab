#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for skill_lifecycle_manager.py
"""
import json
import os
import tempfile
import shutil
from pathlib import Path

import pytest

from skill_lifecycle_manager import (
    SkillLifecycleRecord,
    SkillLifecycleRegistry,
    SkillLifecycleManager,
    ECONOMIC_QS,
    ECONOMIC_CS,
)


@pytest.fixture
def temp_workspace(tmp_path):
    """Create a temporary workspace with skills/ and archive/ structure."""
    ws = tmp_path / "workspace"
    skills = ws / "skills"
    archive = ws / "archive" / "skills-archive"
    skills.mkdir(parents=True)
    archive.mkdir(parents=True)
    return ws


@pytest.fixture
def registry(temp_workspace):
    path = temp_workspace / "registry.json"
    return SkillLifecycleRegistry(path, skills_dir=temp_workspace / "skills")


class TestSkillLifecycleRecord:
    def test_to_dict_and_from_dict(self):
        rec = SkillLifecycleRecord(name="test-skill", stage="genesis", created_at="2026-01-01T00:00:00+00:00", updated_at="2026-01-01T00:00:00+00:00")
        d = rec.to_dict()
        assert d["name"] == "test-skill"
        restored = SkillLifecycleRecord.from_dict(d)
        assert restored.name == "test-skill"
        assert restored.stage == "genesis"


class TestSkillLifecycleRegistry:
    def test_seed_from_workspace(self, temp_workspace, registry):
        # Create some fake skills
        (temp_workspace / "skills" / "alpha").mkdir()
        (temp_workspace / "skills" / "alpha" / "SKILL.md").write_text("# Alpha")
        (temp_workspace / "skills" / "beta").mkdir()
        (temp_workspace / "skills" / "beta" / "SKILL.md").write_text("# Beta")
        (temp_workspace / "skills" / "beta" / "scripts").mkdir()
        (temp_workspace / "skills" / "beta" / "tests").mkdir()

        registry.seed_from_workspace()
        assert "alpha" in registry.all_names()
        assert "beta" in registry.all_names()
        assert registry.get("alpha").stage == "growth"
        assert registry.get("beta").stage == "maturity"

    def test_list_by_stage(self, temp_workspace, registry):
        (temp_workspace / "skills" / "gamma").mkdir()
        (temp_workspace / "skills" / "gamma" / "SKILL.md").write_text("# G")
        registry.seed_from_workspace()
        growth_items = registry.list_by_stage("growth")
        assert len(growth_items) == 1
        assert growth_items[0].name == "gamma"


class TestSkillLifecycleManager:
    def test_creation_gate_approves_valid_request(self, temp_workspace):
        mgr = SkillLifecycleManager(
            workspace=temp_workspace,
            registry_path=temp_workspace / "registry.json",
        )
        host_doc = temp_workspace / "host_doc.md"
        host_doc.write_text("HOST cycle")

        approved, issues = mgr.evaluate_creation_request(
            skill_name="new-skill",
            problem_statement="Automate partner matching",
            pattern_frequency=5,
            existing_coverage_rate=0.5,
            roi_estimate=10.0,
            economic_qs={"q1_local": True, "q2_light": True, "q3_compress": True},
            economic_cs={"c1_reusable": True, "c2_parallel": True, "c3_boundary_clear": True},
            host_doc_path=str(host_doc),
        )
        assert approved is True
        assert len(issues) == 0

    def test_creation_gate_rejects_low_frequency(self, temp_workspace):
        mgr = SkillLifecycleManager(
            workspace=temp_workspace,
            registry_path=temp_workspace / "registry.json",
        )
        host_doc = temp_workspace / "host_doc.md"
        host_doc.write_text("HOST cycle")

        approved, issues = mgr.evaluate_creation_request(
            skill_name="new-skill",
            problem_statement="Automate partner matching",
            pattern_frequency=1,
            existing_coverage_rate=0.5,
            roi_estimate=10.0,
            economic_qs={"q1_local": True, "q2_light": True, "q3_compress": True},
            economic_cs={"c1_reusable": True, "c2_parallel": True, "c3_boundary_clear": True},
            host_doc_path=str(host_doc),
        )
        assert approved is False
        assert any("3" in i for i in issues)

    def test_register_genesis_and_promote(self, temp_workspace):
        mgr = SkillLifecycleManager(
            workspace=temp_workspace,
            registry_path=temp_workspace / "registry.json",
        )
        host_doc = temp_workspace / "host_doc.md"
        host_doc.write_text("HOST cycle")

        rec = mgr.register_genesis(
            skill_name="test-create",
            problem_statement="Pattern automation",
            pattern_frequency=5,
            existing_coverage_rate=0.3,
            roi_estimate=20.0,
            economic_qs={"q1_local": True, "q2_light": True, "q3_compress": True},
            economic_cs={"c1_reusable": True, "c2_parallel": True, "c3_boundary_clear": True},
            host_doc_path=str(host_doc),
        )
        assert rec.stage == "genesis"

        # Promote to growth
        skill_dir = temp_workspace / "skills" / "test-create"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("# Test Create")
        grec = mgr.promote_to_growth("test-create")
        assert grec.stage == "growth"

        # Promote to maturity
        (skill_dir / "scripts").mkdir()
        (skill_dir / "tests").mkdir()
        mrec = mgr.promote_to_maturity("test-create")
        assert mrec.stage == "maturity"

    def test_find_merge_candidates(self, temp_workspace):
        mgr = SkillLifecycleManager(
            workspace=temp_workspace,
            registry_path=temp_workspace / "registry.json",
        )
        # Inject a fake methodology KB
        mgr.kb = {
            "skill-a": {
                "skill_name": "skill-a",
                "description": "Search the web and fetch news articles",
                "core_methodology": ["query parsing", "web search", "result ranking"],
                "trigger_keywords": ["search", "news"],
                "workflow_pattern": "search-fetch-summarize",
            },
            "skill-b": {
                "skill_name": "skill-b",
                "description": "Fetch web pages and search for information",
                "core_methodology": ["web search", "fetching", "ranking"],
                "trigger_keywords": ["search", "fetch"],
                "workflow_pattern": "search-fetch-summarize",
            },
            "skill-c": {
                "skill_name": "skill-c",
                "description": "Completely different: cook pasta",
                "core_methodology": ["boil water", "add pasta"],
                "trigger_keywords": ["cook"],
                "workflow_pattern": "cook-serve",
            },
        }
        # Seed registry
        for name in ["skill-a", "skill-b", "skill-c"]:
            (temp_workspace / "skills" / name).mkdir()
            (temp_workspace / "skills" / name / "SKILL.md").write_text(f"# {name}")
        mgr.registry.seed_from_workspace()

        candidates = mgr.find_merge_candidates(threshold=0.5)
        # skill-a and skill-b should be grouped
        names_in_groups = set()
        for c in candidates:
            names_in_groups.update(c["members"])
        assert "skill-a" in names_in_groups
        assert "skill-b" in names_in_groups
        assert "skill-c" not in names_in_groups

    def test_elect_canonical_prefers_maturity(self, temp_workspace):
        mgr = SkillLifecycleManager(
            workspace=temp_workspace,
            registry_path=temp_workspace / "registry.json",
        )
        now = "2026-01-01T00:00:00+00:00"
        mgr.registry.set(SkillLifecycleRecord(name="mature-skill", stage="maturity", created_at=now, updated_at=now))
        mgr.registry.set(SkillLifecycleRecord(name="growth-skill", stage="growth", created_at=now, updated_at=now))
        canonical = mgr._elect_canonical(["growth-skill", "mature-skill"])
        assert canonical == "mature-skill"

    def test_retire_and_archive_and_revive(self, temp_workspace):
        mgr = SkillLifecycleManager(
            workspace=temp_workspace,
            registry_path=temp_workspace / "registry.json",
        )
        now = "2026-01-01T00:00:00+00:00"
        mgr.registry.set(SkillLifecycleRecord(name="old-skill", stage="maturity", created_at=now, updated_at=now))
        skill_dir = temp_workspace / "skills" / "old-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("# Old")

        rec = mgr.retire_skill("old-skill", reason="unused", replacement="new-skill", dry_run=False)
        assert rec.stage == "retirement"
        assert not (temp_workspace / "skills" / "old-skill").exists()
        assert (temp_workspace / "archive" / "skills-archive" / "retired" / "old-skill").exists()

        rec2 = mgr.archive_skill("old-skill", dry_run=False)
        assert rec2.stage == "archived"

        rec3 = mgr.revive_skill("old-skill", dry_run=False)
        assert rec3.stage == "growth"
        assert (temp_workspace / "skills" / "old-skill").exists()

    def test_sync_to_daily_asset_runner(self, temp_workspace):
        mgr = SkillLifecycleManager(
            workspace=temp_workspace,
            registry_path=temp_workspace / "registry.json",
        )
        now = "2026-01-01T00:00:00+00:00"
        mgr.registry.set(SkillLifecycleRecord(name="mature-a", stage="maturity", created_at=now, updated_at=now))
        mgr.registry.set(SkillLifecycleRecord(name="growth-b", stage="growth", created_at=now, updated_at=now))

        runner = temp_workspace / "daily_asset_runner.py"
        runner.write_text("# existing content\nprint('hello')\n", encoding="utf-8")

        result = mgr.sync_to_daily_asset_runner()
        assert result["mature_count"] == 1
        text = runner.read_text(encoding="utf-8")
        assert "mature-a" in text
        assert "growth-b" not in text
        assert "SKILL_LIFECYCLE_AUTO_INSERT_START" in text


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
