#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_honeybee_democracy_toolkit.py
pytest 单元测试 —— 蜜蜂民主工具箱
"""

import pytest
from honeybee_democracy_toolkit import (
    query_nest_criteria,
    query_decision_process,
    query_lesson,
    query_mechanism,
    SwarmDecisionHealthChecker,
    ScoutBeeSimulator,
    get_cross_book_mapping,
    KNOWLEDGE_BASE,
)


class TestKnowledgeBase:
    def test_criteria_count(self):
        assert len(KNOWLEDGE_BASE["nest_site_criteria"]) == 6

    def test_process_count(self):
        assert len(KNOWLEDGE_BASE["decision_process"]) == 8

    def test_lessons_count(self):
        assert len(KNOWLEDGE_BASE["human_lessons"]) == 5


class TestQueryFunctions:
    def test_query_nest_criteria(self):
        result = query_nest_criteria("空洞容量")
        assert "足够宽敞" in str(result)

    def test_query_nest_criteria_not_found(self):
        result = query_nest_criteria("不存在")
        assert "error" in result

    def test_query_decision_process(self):
        result = query_decision_process()
        assert "步骤8_引导迁移" in result

    def test_query_lesson(self):
        result = query_lesson("领导者")
        assert any("领导者的影响" in k for k in result)

    def test_query_mechanism(self):
        result = query_mechanism("摇摆舞")
        assert any("Waggle Dance" in k for k in result)


class TestSwarmDecisionHealthChecker:
    def test_evaluate_perfect(self):
        checker = SwarmDecisionHealthChecker()
        answers = [True] * 7
        result = checker.evaluate(answers)
        assert result["percentage"] == 100.0
        assert result["level"] == "优秀"

    def test_evaluate_with_negative_item(self):
        checker = SwarmDecisionHealthChecker()
        # 最后一项是negative: 有人强行统一意见？True=不存在该问题
        answers = [True, True, True, True, True, True, False]
        result = checker.evaluate(answers)
        assert result["score"] == 15  # 17-2
        assert len(result["advice"]) > 0
        assert any("看来大家都同意" in a for a in result["advice"])

    def test_evaluate_length_mismatch(self):
        checker = SwarmDecisionHealthChecker()
        result = checker.evaluate([True, True])
        assert "error" in result


class TestScoutBeeSimulator:
    def test_perfect_site(self):
        sim = ScoutBeeSimulator()
        result = sim.evaluate_site(
            entrance_size_cm2=12.5,
            entrance_direction="南",
            entrance_height_m=6.5,
            entrance_position="底部",
            cavity_volume_liters=40,
            has_old_comb=True
        )
        assert result["score"] == 10.0
        assert result["dance_recommendation"] == "强烈舞蹈"

    def test_poor_site(self):
        sim = ScoutBeeSimulator()
        result = sim.evaluate_site(
            entrance_size_cm2=100,
            entrance_direction="北",
            entrance_height_m=0.5,
            entrance_position="顶部",
            cavity_volume_liters=5,
            has_old_comb=False
        )
        assert result["score"] < 5.0
        assert result["quorum_likelihood"] == "低"


class TestCrossBookMapping:
    def test_mapping_conflict(self):
        result = get_cross_book_mapping("适当的冲突")
        assert "法庭辩论" in result["slow_think_fast_decide"]

    def test_mapping_not_found(self):
        result = get_cross_book_mapping("不存在")
        assert "note" in result
