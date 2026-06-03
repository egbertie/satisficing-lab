#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_kahneman_tversky_decision_archive.py
pytest 单元测试 —— 卡尼曼-特沃斯基决策档案
"""

import pytest
from kahneman_tversky_decision_archive import (
    query_person,
    query_theory,
    query_experiment,
    query_domain,
    get_heuristic_bias,
    ExpertVsAlgorithmEvaluator,
    DecisionBiasDetectorV2,
    get_cross_book_bias_lookup,
    KNOWLEDGE_BASE,
)


class TestKnowledgeBase:
    def test_people_count(self):
        assert len(KNOWLEDGE_BASE["people"]) == 2

    def test_theories_count(self):
        assert len(KNOWLEDGE_BASE["theory_evolution"]) == 4

    def test_experiments_count(self):
        assert len(KNOWLEDGE_BASE["experiments"]) == 5


class TestQueryFunctions:
    def test_query_person_by_partial_name(self):
        result = query_person("卡尼曼")
        assert any("丹尼尔·卡尼曼" in k for k in result)

    def test_query_person_not_found(self):
        result = query_person("爱因斯坦")
        assert "error" in result

    def test_query_theory_prospect(self):
        result = query_theory("前景理论")
        assert any("前景理论" in k for k in result)

    def test_query_experiment_linda(self):
        result = query_experiment("琳达")
        assert any("琳达问题" in k for k in result)

    def test_query_domain_medical(self):
        result = query_domain("医学")
        assert "医生诊断一致性研究" in list(result.values())[0]["cases"]

    def test_get_heuristic_bias(self):
        result = get_heuristic_bias("代表性")
        assert "代表性启发法" in result["heuristic"]


class TestExpertVsAlgorithmEvaluator:
    def test_evaluate_default(self):
        evaluator = ExpertVsAlgorithmEvaluator()
        result = evaluator.evaluate("医生需要根据多条线索做重复诊断")
        assert "verdict" in result


class TestDecisionBiasDetectorV2:
    def test_detect_representativeness(self):
        detector = DecisionBiasDetectorV2()
        result = detector.detect("这个候选人看起来就是一个典型的成功者")
        biases = [r["bias"] for r in result]
        assert "代表性启发法" in biases

    def test_detect_availability(self):
        detector = DecisionBiasDetectorV2()
        result = detector.detect("最近媒体上都在报道这件事")
        biases = [r["bias"] for r in result]
        assert "可得性启发法" in biases

    def test_detect_fallback(self):
        detector = DecisionBiasDetectorV2()
        result = detector.detect("今天天气不错")
        assert result[0]["bias"] == "未识别明显偏见"


class TestCrossBookMapping:
    def test_mapping_loss_aversion(self):
        result = get_cross_book_bias_lookup("损失厌恶")
        assert result["speed_category"] == "安全性偏見 (Safety)"

    def test_mapping_not_found(self):
        result = get_cross_book_bias_lookup("不存在")
        assert "note" in result
