#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_systems_thinking_primer.py
pytest 单元测试 —— 系统之美入门工具箱
"""

import pytest
from systems_thinking_primer import (
    query_component,
    query_trap,
    query_leverage_point,
    query_feedback_loop,
    SystemTrapDiagnoser,
    LeveragePointAdvisor,
    KNOWLEDGE_BASE,
)


class TestKnowledgeBase:
    def test_traps_count(self):
        assert len(KNOWLEDGE_BASE["traps"]) == 8

    def test_leverage_points_count(self):
        assert len(KNOWLEDGE_BASE["leverage_points"]) == 12

    def test_feedback_loops_count(self):
        assert len(KNOWLEDGE_BASE["feedback_loops"]) == 2


class TestQueryFunctions:
    def test_query_component(self):
        result = query_component("存量")
        assert len(result) > 0

    def test_query_trap(self):
        result = query_trap("公地悲剧")
        assert any("公地悲剧" in k for k in result)

    def test_query_trap_not_found(self):
        result = query_trap("不存在")
        assert "error" in result

    def test_query_leverage_point(self):
        result = query_leverage_point(1)
        assert "1_超越范式" in result or "超越范式" in str(result)

    def test_query_feedback_loop(self):
        result = query_feedback_loop("调节")
        assert any("调节" in k for k in result)


class TestSystemTrapDiagnoser:
    def test_diagnose_policy_resistance(self):
        d = SystemTrapDiagnoser()
        result = d.diagnose("各个部门利益冲突，措施遇到很大阻力")
        traps = [r["trap"] for r in result]
        assert "政策阻力" in traps

    def test_diagnose_target_erosion(self):
        d = SystemTrapDiagnoser()
        result = d.diagnose("业绩越来越差，所以把标准一再调低")
        traps = [r["trap"] for r in result]
        assert "目标侵蚀" in traps

    def test_diagnose_fallback(self):
        d = SystemTrapDiagnoser()
        result = d.diagnose("今天天气不错")
        assert result[0]["trap"] == "暂无明确匹配"


class TestLeveragePointAdvisor:
    def test_recommend_oscillation(self):
        a = LeveragePointAdvisor()
        result = a.recommend("业绩忽上忽下")
        assert result["primary"] == "9_时间延迟"

    def test_recommend_growth(self):
        a = LeveragePointAdvisor()
        result = a.recommend("指数增长")
        assert result["primary"] == "7_增强回路"

    def test_recommend_default(self):
        a = LeveragePointAdvisor()
        result = a.recommend("不知道")
        assert result["primary"] == "12_常数和参数"
