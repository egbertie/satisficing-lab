#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_integrative_decision_toolkit.py
pytest 单元测试 —— 整合决策工具箱
"""

import pytest
from integrative_decision_toolkit import (
    query_mind_model_characteristic,
    query_principle,
    query_stage,
    query_creative_path,
    OpposingModelsAnalyzer,
    IntegrativeSolutionAdvisor,
    integrative_thinking_checklist,
    get_cross_book_mapping,
    KNOWLEDGE_BASE,
)


class TestKnowledgeBase:
    def test_mind_model_count(self):
        assert len(KNOWLEDGE_BASE["mind_model_characteristics"]) == 5

    def test_principles_count(self):
        assert len(KNOWLEDGE_BASE["decision_principles"]) == 3

    def test_stages_count(self):
        assert len(KNOWLEDGE_BASE["four_stages"]) == 4


class TestQueryFunctions:
    def test_query_mind_model(self):
        result = query_mind_model_characteristic("顽固")
        assert any("顽固" in k for k in result)

    def test_query_principle(self):
        result = query_principle("同理心")
        assert any("同理心" in k for k in result)

    def test_query_stage(self):
        result = query_stage("阶段1")
        assert any("阶段1" in k for k in result)

    def test_query_creative_path(self):
        result = query_creative_path("隐藏的宝石")
        assert any("隐藏的宝石" in k for k in result)


class TestOpposingModelsAnalyzer:
    def test_analyze(self):
        analyzer = OpposingModelsAnalyzer()
        result = analyzer.analyze("A模式", "逻辑A", "B模式", "逻辑B")
        assert result["stage1_呈现对立模式"]["model_a"]["name"] == "A模式"
        assert "A模式 与 B模式" in result["stage1_呈现对立模式"]["core_tension"]


class TestIntegrativeSolutionAdvisor:
    def test_recommend_resource(self):
        advisor = IntegrativeSolutionAdvisor()
        result = advisor.recommend_path("直营", "控制力", "加盟", "扩张速度", "资源竞争")
        assert "路径1_隐藏的宝石" in result["recommended_path"]

    def test_recommend_deconstruction(self):
        advisor = IntegrativeSolutionAdvisor()
        result = advisor.recommend_path("线上", "效率", "线下", "体验", "假设对立")
        assert "路径3_解构" in result["recommended_path"]

    def test_recommend_default(self):
        advisor = IntegrativeSolutionAdvisor()
        result = advisor.recommend_path("X", "a", "Y", "b", "未知")
        assert "依次尝试3条路径" in result["recommended_path"]


class TestCrossBookMapping:
    def test_mapping_empathy(self):
        result = get_cross_book_mapping("同理心")
        assert "后入为主" in result["slow_think_fast_decide"]

    def test_mapping_not_found(self):
        result = get_cross_book_mapping("不存在")
        assert "note" in result
