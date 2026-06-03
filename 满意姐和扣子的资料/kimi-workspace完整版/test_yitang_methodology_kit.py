"""
test_yitang_methodology_kit.py
一堂方法论数字资产测试（V1.1 扩展版）
"""

import pytest
from yitang_methodology_kit import (
    YitangMethodologyKit,
    LeanStartupSpectrum,
    ProductKernelMetrics,
    KeyMethodologyImageArchive,
    YitangPersonalRoadmap,
)


class TestCaseCatalog:
    def test_total_cases(self):
        kit = YitangMethodologyKit()
        stats = kit.case_stats()
        assert stats["total_unique_cases"] == 128

    def test_search_cases(self):
        kit = YitangMethodologyKit()
        results = kit.search_cases("SaaS")
        assert len(results) >= 3
        assert any("SaaS" in r["case"] for r in results)

    def test_chapter_retrieval(self):
        kit = YitangMethodologyKit()
        chapter1 = kit.get_chapter_cases("第一章：关键假设相关")
        assert len(chapter1) == 46
        assert "餐饮调味料平台" in chapter1

    def test_locked_registry_exists(self):
        kit = YitangMethodologyKit()
        report = kit.export_report()
        assert report["locked_resources"]["total"] == 4
        assert any("微信扫码" in item["barrier"] for item in report["locked_resources"]["items"])

    def test_ai_acceleration_structure(self):
        kit = YitangMethodologyKit()
        pack = kit.AI_ACCELERATION_PACK
        assert pack["title"] == "一堂AI加速包"
        assert len(pack["components"]) == 2
        assert pack["components"][1]["lecturer"] == "于陆"


class TestLeanStartupSpectrum:
    def test_spectrum_stage_count(self):
        assert len(LeanStartupSpectrum.SPECTRUM_STAGES) == 6

    def test_get_stage(self):
        stage = LeanStartupSpectrum.get_stage("direct_test")
        assert stage is not None
        assert stage["name"] == "直接测试"
        assert "假产品" in stage["tactics"]

    def test_low_cost_principles(self):
        assert "尽早发布" in LeanStartupSpectrum.LOW_COST_PRINCIPLES
        assert len(LeanStartupSpectrum.LOW_COST_PRINCIPLES) == 4

    def test_fatal_wastes_count(self):
        assert len(LeanStartupSpectrum.FATAL_WASTES) == 6
        waste_names = [w["name"] for w in LeanStartupSpectrum.FATAL_WASTES]
        assert "问题找错" in waste_names
        assert "盲目坚持" in waste_names

    def test_sri_adaptation(self):
        report = LeanStartupSpectrum.sri_adaptation_report()
        assert report["advice"]
        assert "direct_test" in report["current_stage_recommendation"]
        assert "full_dev" in report["avoid_stages"]


class TestProductKernelMetrics:
    def test_metrics_tree_structure(self):
        assert len(ProductKernelMetrics.METRICS_TREE["获客环节"]) == 3
        assert len(ProductKernelMetrics.METRICS_TREE["服务环节"]) == 4
        assert len(ProductKernelMetrics.METRICS_TREE["复购环节"]) == 3

    def test_get_metrics_by_stage(self):
        acquisition = ProductKernelMetrics.get_metrics_by_stage("获客环节")
        assert any(m["metric"] == "销转率" for m in acquisition)

    def test_sri_funnel_report(self):
        report = ProductKernelMetrics.sri_funnel_report()
        assert report["business_name"] == "满意解研究所合伙人匹配服务"
        assert "销转率" in report["funnel_stages"]["获客"]
        assert "完课率_<70%" in report["health_check_rules"]


class TestYitangPersonalRoadmap:
    def test_layers_count(self):
        assert len(YitangPersonalRoadmap.LAYERS) == 3

    def test_competencies_count(self):
        comps = YitangPersonalRoadmap.LAYERS["leading"]["competencies"]
        assert len(comps) == 6

    def test_get_decision_competency(self):
        c = YitangPersonalRoadmap.get_competency("decision")
        assert c is not None
        assert c["name"] == "决策力"
        assert c["sri_status"] == "核心竞争力"

    def test_growth_rings(self):
        assert len(YitangPersonalRoadmap.GROWTH_RINGS) == 3
        assert YitangPersonalRoadmap.GROWTH_RINGS[0]["name"] == "有驱动"

    def test_sri_assessment(self):
        assessment = YitangPersonalRoadmap.sri_assessment()
        assert "strengths" in assessment
        assert "build_zones" in assessment
        assert "产品力" in assessment["next_6_month_focus"]

    def test_roadmap_trilogy(self):
        trilogy = YitangPersonalRoadmap.roadmap_trilogy()
        assert "创业地图" in trilogy
        assert "管理地图" in trilogy
        assert "个人地图" in trilogy
        assert trilogy["个人地图"]["goal"] == "天花板"


class TestKeyMethodologyImageArchive:
    def test_archived_images_count(self):
        archived = KeyMethodologyImageArchive.list_archived()
        assert len(archived) == 5

    def test_pending_images_count(self):
        pending = KeyMethodologyImageArchive.list_pending()
        assert len(pending) == 4

    def test_get_by_id(self):
        img = KeyMethodologyImageArchive.get_by_id("IMG-20260409-001")
        assert img is not None
        assert img["title"] == "一堂低成本创业全景图谱·超级小抄"


class TestKitIntegration:
    def test_export_report_v12(self):
        kit = YitangMethodologyKit()
        report = kit.export_report()
        assert report["version"] == "V1.2"
        assert "lean_startup_spectrum" in report
        assert "product_kernel_metrics" in report
        assert "personal_roadmap" in report
        assert "image_archive" in report

    def test_sri_adaptation_integration(self):
        adaptation = YitangMethodologyKit.get_sri_adaptation()
        assert "cost_spectrum" in adaptation
        assert "metrics" in adaptation
        assert "personal_growth" in adaptation
        assert len(adaptation["fatal_wastes_to_watch"]) == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
