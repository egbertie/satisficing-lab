#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_confucian_management_philosophy.py
pytest 单元测试 —— 儒家管理哲学工具箱
"""

import pytest
from confucian_management_philosophy import (
    query_chapter,
    query_concept,
    query_core_spirit,
    ConfucianManagementAuditor,
    get_modern_mapping,
    KNOWLEDGE_BASE,
)


class TestKnowledgeBase:
    def test_chapters_count(self):
        assert len(KNOWLEDGE_BASE["ten_chapters"]) == 10

    def test_concepts_count(self):
        assert len(KNOWLEDGE_BASE["key_concepts"]) == 7

    def test_core_spirit_count(self):
        assert len(KNOWLEDGE_BASE["core_spirit"]) == 3


class TestQueryFunctions:
    def test_query_chapter(self):
        result = query_chapter("无为而治")
        assert any("无为而治" in k for k in result)

    def test_query_chapter_not_found(self):
        result = query_chapter("不存在")
        assert "error" in result

    def test_query_concept(self):
        result = query_concept("义利合一")
        assert any("义利合一" in k for k in result)

    def test_query_concept_not_found(self):
        result = query_concept("不存在")
        assert "error" in result

    def test_query_core_spirit(self):
        result = query_core_spirit()
        assert "以人为中心" in result


class TestConfucianManagementAuditor:
    def test_evaluate(self):
        auditor = ConfucianManagementAuditor()
        result = auditor.evaluate([8, 7, 6, 5, 7, 8, 6, 5, 6, 7])
        assert result["total_score"] == 65
        assert len(result["weaknesses"]) == 2

    def test_evaluate_length_mismatch(self):
        auditor = ConfucianManagementAuditor()
        result = auditor.evaluate([1, 2, 3])
        assert "error" in result

    def test_level_excellent(self):
        auditor = ConfucianManagementAuditor()
        result = auditor.evaluate([9] * 10)
        assert "卓越" in result["maturity_level"]

    def test_level_poor(self):
        auditor = ConfucianManagementAuditor()
        result = auditor.evaluate([4] * 10)
        assert "待改进" in result["maturity_level"]


class TestModernMapping:
    def test_mapping_leadership(self):
        result = get_modern_mapping("领导力")
        assert any("领导力" in k for k in result)

    def test_mapping_not_found(self):
        result = get_modern_mapping("不存在")
        assert "note" in result
