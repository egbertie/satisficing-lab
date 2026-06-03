#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_confucian_business_philosophy_core.py
pytest 单元测试 —— 儒商哲学核心资产
"""

import pytest
from confucian_business_philosophy_core import (
    query_ten_views,
    query_eight_ways,
    query_ten_theories,
    query_concept,
    ConfucianBusinessAssessor,
    recommend_wisdom,
    KNOWLEDGE_BASE,
)


class TestTenViews:
    def test_list_all_views(self):
        result = query_ten_views()
        assert "available_views" in result
        assert len(result["available_views"]) == 10
        assert "導德齊禮的治理觀" in result["available_views"]
        assert "兼善天下的責任觀" in result["available_views"]

    def test_query_specific_view(self):
        result = query_ten_views("身正令行的領導觀")
        assert result["classic"].startswith("《論語·子路》")
        assert any("正己正人" in item for item in result["core"])

    def test_query_missing_view_returns_error(self):
        result = query_ten_views("不存在的觀念")
        assert "error" in result

    def test_stub_view_removed(self):
        result = query_ten_views("敬天法祖愛人的信仰觀")
        assert result.get("stub") is None
        assert "稻盛和夫" in result["practice"]["愛人"]
        assert "西鄉隆盛" in result["classic"]


class TestEightWays:
    def test_list_all_ways(self):
        result = query_eight_ways()
        assert len(result["available_ways"]) == 8

    def test_query_specific_way(self):
        result = query_eight_ways("經營之道")
        assert "阿里巴巴" in result["case"]


class TestTenTheories:
    def test_list_all_theories(self):
        result = query_ten_theories()
        assert len(result["available_theories"]) == 10

    def test_query_specific_theory(self):
        result = query_ten_theories("修己安人的管理目標觀")
        assert "安人" in result["summary"]


class TestConceptSearch:
    def test_search_hits_multiple_sources(self):
        results = query_concept("誠信")
        sources = [r[0] for r in results]
        assert "十大觀念" in sources or "八大道" in sources

    def test_search_no_match_returns_empty(self):
        results = query_concept("量子力學")
        assert results == []


class TestAssessor:
    def test_evaluate_basic(self):
        a = ConfucianBusinessAssessor()
        a.input_scores(9, 9, 9, 9, 9)
        result = a.evaluate()
        assert result["total"] == 45
        assert result["average"] == 9.0
        assert "典範儒商" in result["level"]

    def test_evaluate_clamps_scores(self):
        a = ConfucianBusinessAssessor()
        a.input_scores(ren=0, yi=15, li=5, zhi=5, xin=5)
        result = a.evaluate()
        assert result["scores"]["仁"] == 1
        assert result["scores"]["義"] == 10

    def test_evaluate_without_input(self):
        a = ConfucianBusinessAssessor()
        result = a.evaluate()
        assert "error" in result

    def test_weak_advice(self):
        a = ConfucianBusinessAssessor()
        a.input_scores(ren=9, yi=9, li=3, zhi=9, xin=9)
        result = a.evaluate()
        assert result["weakest"][0] == "禮"
        assert "制度" in result["primary_advice"]


class TestRecommendWisdom:
    def test_partner_scenario(self):
        results = recommend_wisdom("合伙人股权分配")
        sources = [r["source"] for r in results]
        assert "價值論" in sources
        assert "組織論" in sources

    def test_leadership_scenario(self):
        results = recommend_wisdom("CEO以身作则")
        sources = [r["source"] for r in results]
        assert "領導之道" in sources

    def test_esg_scenario(self):
        results = recommend_wisdom("企业公益和环保")
        sources = [r["source"] for r in results]
        assert "責任觀" in sources

    def test_unknown_scenario_fallback(self):
        results = recommend_wisdom("量子計算機研發")
        assert results[0]["source"] == "通用建議"


class TestKnowledgeIntegrity:
    def test_core_values_keys(self):
        cv = KNOWLEDGE_BASE["core_values"]
        assert "五常" in cv
        assert "新儒商六標準" in cv
        assert len(cv["新儒商六標準"]) == 6

    def test_ten_views_complete(self):
        views = KNOWLEDGE_BASE["ten_views"]["views"]
        complete_views = [k for k, v in views.items() if not v.get("stub")]
        assert len(complete_views) == 10  # 10 complete, 0 stub
