#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_confucian_business_wisdom.py
pytest 单元测试 —— 儒家商道智慧工具箱
"""

import pytest
from confucian_business_wisdom import (
    query_way,
    get_core_message,
    RuShangAuditor,
    get_case_principle,
    KNOWLEDGE_BASE,
)


class TestKnowledgeBase:
    def test_eight_ways_count(self):
        assert len(KNOWLEDGE_BASE["eight_ways"]) == 8

    def test_core_message_count(self):
        assert len(KNOWLEDGE_BASE["core_message"]) == 3


class TestQueryFunctions:
    def test_query_way(self):
        result = query_way("经营之道")
        assert any("经营之道" in k for k in result)

    def test_query_way_not_found(self):
        result = query_way("不存在")
        assert "error" in result

    def test_query_way_all(self):
        result = query_way()
        assert len(result["ways"]) == 8

    def test_get_core_message(self):
        result = get_core_message()
        assert "儒商精神" in result


class TestRuShangAuditor:
    def test_evaluate(self):
        auditor = RuShangAuditor()
        result = auditor.evaluate([7, 6, 6, 7, 5, 6, 7, 6])
        assert result["total_score"] == 50
        assert len(result["weaknesses"]) == 1

    def test_evaluate_length_error(self):
        auditor = RuShangAuditor()
        result = auditor.evaluate([1, 2, 3])
        assert "error" in result

    def test_level_benchmark(self):
        auditor = RuShangAuditor()
        result = auditor.evaluate([9] * 8)
        assert "儒商标杆" in result["maturity_level"]


class TestCasePrinciple:
    def test_case_found(self):
        result = get_case_principle("合伙人信任")
        assert any("合伙人信任" in k for k in result)

    def test_case_not_found(self):
        result = get_case_principle("不存在")
        assert "note" in result
