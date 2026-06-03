"""
test_v16_new_assets.py
V1.6 底稿队列缺失 3 个文件的代码资产测试

测试目标:
- hardtech_partner_conflict_window.py
- lizexiang_human_factor_analyzer.py
- lizexiang_synergy_strategy_v1.py
"""

import pytest
from hardtech_partner_conflict_window import (
    HardtechPartnerConflictWindow,
    ConflictStage,
    RiskLevel,
)
from lizexiang_human_factor_analyzer import (
    LizexiangHumanFactorAnalyzer,
    FounderProfile,
    TeamArchetype,
    Outcome,
)
from lizexiang_synergy_strategy_v1 import (
    LizexiangSynergyStrategyV1,
    PartnerProfile,
    SynergyDomain,
)


class TestHardtechPartnerConflictWindow:
    def test_stage_determination(self):
        w = HardtechPartnerConflictWindow()
        assert w.determine_stage(6) == ConflictStage.LATENCY
        assert w.determine_stage(18) == ConflictStage.MANIFESTATION
        assert w.determine_stage(30) == ConflictStage.OUTBREAK

    def test_assess_low_risk(self):
        w = HardtechPartnerConflictWindow()
        result = w.assess("TestCo", 6, 0.2, 3.0, 0, 0.05)
        assert result.overall_risk == RiskLevel.GREEN
        assert result.stage == ConflictStage.LATENCY

    def test_assess_high_risk_manifestation(self):
        w = HardtechPartnerConflictWindow()
        result = w.assess("RiskCo", 18, 3.5, 0.5, 3, 0.45)
        assert result.stage == ConflictStage.MANIFESTATION
        assert result.overall_risk == RiskLevel.RED
        assert any("导师" in a for a in result.recommended_actions)

    def test_did_effect(self):
        w = HardtechPartnerConflictWindow()
        effect = w.did_effect(True, "seed_stage")
        assert effect["risk_reduction"] == 0.65
        assert "p<0.05" in effect["effect_significance"]

    def test_export_checklist(self):
        w = HardtechPartnerConflictWindow()
        result = w.assess("ExportCo", 20, 2.0, 1.0, 1, 0.20)
        checklist = w.export_checklist(result)
        assert "company" in checklist
        assert "signals" in checklist
        assert len(checklist["signals"]) == 4


class TestLizexiangHumanFactorAnalyzer:
    def test_classify_archetype(self):
        a = LizexiangHumanFactorAnalyzer()
        founders = [
            FounderProfile("A", 80, 40, 70, 80),
            FounderProfile("B", 30, 85, 65, 75),
        ]
        archetype = a.classify_archetype(founders)
        assert archetype == TeamArchetype.TECH_BUSINESS

    def test_predict_success(self):
        a = LizexiangHumanFactorAnalyzer()
        founders = [
            FounderProfile("Tech1", 85, 20, 60, 70),
            FounderProfile("Tech2", 80, 25, 55, 65),
        ]
        match = a.predict_success(founders, mentor_involved=True, pressure_test_passed=False)
        assert match.archetype == TeamArchetype.MULTI_TECH
        assert 0 < match.success_probability <= 1.0
        assert len(match.risk_factors) > 0
        assert any("压力测试" in r for r in match.mentor_recommendations)

    def test_case_stats(self):
        a = LizexiangHumanFactorAnalyzer()
        stats = a.get_case_stats()
        assert stats["total_cases"] == 270
        assert stats["unicorns"] == 12

    def test_batch_evaluate(self):
        a = LizexiangHumanFactorAnalyzer()
        cases = [
            {
                "founders": [
                    {"name": "A", "technical_depth": 80, "business_acumen": 40, "resilience_score": 70, "motivation_clarity": 80},
                    {"name": "B", "technical_depth": 30, "business_acumen": 85, "resilience_score": 65, "motivation_clarity": 75},
                ],
                "mentor_involved": True,
            }
        ]
        results = a.batch_evaluate(cases)
        assert len(results) == 1
        assert results[0].archetype == TeamArchetype.TECH_BUSINESS


class TestLizexiangSynergyStrategyV1:
    def test_assess_partner_fit_university(self):
        s = LizexiangSynergyStrategyV1()
        assessments = s.assess_partner_fit(PartnerProfile.UNIVERSITY, has_talent_pool=True)
        domains = [a.domain for a in assessments]
        assert SynergyDomain.TALENT_PIPELINE in domains

    def test_generate_entry_strategy(self):
        s = LizexiangSynergyStrategyV1()
        strategy = s.generate_entry_strategy(PartnerProfile.STARTUP, "深圳科创学院")
        assert strategy["partner_type"] == PartnerProfile.STARTUP.value
        assert strategy["region"] == "深圳科创学院"
        assert strategy["weighted_readiness_score"] > 0
        assert any(a["domain"] == SynergyDomain.REGIONAL_EXPANSION.value for a in strategy["domain_assessments"])

    def test_xbotpark_stats(self):
        s = LizexiangSynergyStrategyV1()
        stats = s.get_xbotpark_stats()
        assert stats["unicorns"] == 12
        assert "东莞松山湖" in stats["regional_bases"]

    def test_regional_focus(self):
        s = LizexiangSynergyStrategyV1()
        focus = s.get_regional_focus("宁波基地")
        assert "工业" in focus

    def test_benchmark_concentration(self):
        s = LizexiangSynergyStrategyV1()
        assert s.benchmark_concentration("MIT_Stanford") == 0.01
        assert s.benchmark_concentration("重庆大学明月班") == 0.20


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
