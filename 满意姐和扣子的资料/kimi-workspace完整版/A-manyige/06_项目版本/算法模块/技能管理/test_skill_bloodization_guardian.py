#!/usr/bin/env python3
"""
test_skill_bloodization_guardian.py
技能血液化监控守护器测试
"""

import json
import pytest
from skill_bloodization_guardian import (
    SkillBloodizationGuardian,
    load_manifest_skills,
    get_installed_skills,
    assess_bloodization_level,
    ORGAN_TARGET_COUNTS,
)


class TestManifestLoading:
    def test_manifest_has_skills(self):
        skills = load_manifest_skills()
        assert len(skills) > 0
        # 只要有一个在已安装列表中即可
        installed = get_installed_skills()
        assert any(s in installed for s in skills)


class TestInstalledSkills:
    def test_installed_not_empty(self):
        skills = get_installed_skills()
        assert len(skills) > 100  # workspace 应该有不少于 100 个 skill


class TestBloodizationAssessment:
    def test_assess_existing_skill(self):
        level, issues = assess_bloodization_level("feishu-bitable")
        assert level in {"bloodized", "candidate", "unhealthy", "missing"}
        assert isinstance(issues, list)

    def test_assess_missing_skill(self):
        level, issues = assess_bloodization_level("definitely_nonexistent_skill_12345")
        assert level == "missing"
        assert "不存在" in issues[0]


class TestGuardianDrift:
    def test_drift_structure(self):
        g = SkillBloodizationGuardian()
        drift = g.detect_drift()
        assert "installed_count" in drift
        assert "manifest_count" in drift
        assert "drift_detected" in drift
        assert isinstance(drift["installed_only"], list)


class TestGuardianHealth:
    def test_health_sample(self):
        g = SkillBloodizationGuardian()
        health = g.health_check(sample_limit=10)
        assert health["checked"] == 10
        assert "summary" in health
        assert "details" in health

    def test_health_full(self):
        g = SkillBloodizationGuardian()
        health = g.health_check()
        assert health["checked"] > 100


class TestGuardianInspect:
    def test_inspect_existing(self):
        g = SkillBloodizationGuardian()
        result = g.inspect("feishu-bitable")
        assert "error" not in result
        assert "level" in result
        assert "trigger_snippet" in result

    def test_inspect_missing(self):
        g = SkillBloodizationGuardian()
        result = g.inspect("nonexistent_xyz")
        assert "error" in result


class TestManifestIntegrity:
    def test_integrity_totals(self):
        g = SkillBloodizationGuardian()
        integrity = g.check_manifest_integrity()
        assert "total" in integrity
        assert integrity["total"]["target"] == 195
        for organ in ORGAN_TARGET_COUNTS:
            assert organ in integrity

    def test_organ_counts_match(self):
        g = SkillBloodizationGuardian()
        integrity = g.check_manifest_integrity()
        total_actual = sum(v["actual"] for k, v in integrity.items() if k != "total")
        assert total_actual == integrity["total"]["actual"]


class TestReportGeneration:
    def test_report_contains_sections(self):
        g = SkillBloodizationGuardian()
        report = g.full_report()
        assert "# 技能血液化 Guardian 报告" in report
        assert "漂移检测" in report or "无漂移" in report
        assert "健康抽查" in report
