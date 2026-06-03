#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_slow_think_fast_decide_toolkit.py
pytest 单元测试 —— 慢思考快决策工具箱
"""

import pytest
from slow_think_fast_decide_toolkit import (
    query_speed_bias,
    query_scenario,
    query_strategy,
    DecisionBiasDetector,
    DecisionScenarioClassifier,
    BiasMitigationAdvisor,
    decision_quality_checklist,
    KNOWLEDGE_BASE,
)


class TestKnowledgeBase:
    def test_speed_categories(self):
        cats = list(KNOWLEDGE_BASE["speed_biases"].keys())
        assert len(cats) == 5
        assert "安全性偏見 (Safety)" in cats

    def test_scenarios(self):
        scenes = list(KNOWLEDGE_BASE["scenarios"].keys())
        assert len(scenes) == 4
        assert "棋手(形勢評估)" in scenes

    def test_strategies(self):
        strats = list(KNOWLEDGE_BASE["strategies"].keys())
        assert len(strats) == 4
        assert "以小博大" in strats


class TestQueryFunctions:
    def test_query_speed_bias_category(self):
        result = query_speed_bias("安全性偏見 (Safety)")
        assert "負面偏見" in result["biases"]

    def test_query_speed_bias_specific(self):
        result = query_speed_bias("便利性偏見 (Expedience)", "錨定效應")
        assert "聚焦效應" in result["alias"]

    def test_query_scenario(self):
        result = query_scenario("偵探(原因分析)")
        assert "發生問題的原因" in result["core"]

    def test_query_strategy(self):
        result = query_strategy("旁觀者清")
        assert any("互審程序" in k for k in result["techniques"])


class TestBiasDetector:
    def test_detect_politics(self):
        d = DecisionBiasDetector()
        result = d.detect("大家都這麼說應該不會錯")
        categories = [r["category"] for r in result]
        assert "政治性偏見 (Politics)" in categories

    def test_detect_experience(self):
        d = DecisionBiasDetector()
        result = d.detect("我經驗豐富肯定沒問題")
        categories = [r["category"] for r in result]
        assert "經驗性偏見 (Experience)" in categories

    def test_detect_fallback(self):
        d = DecisionBiasDetector()
        result = d.detect("今天天氣很好")
        assert result[0]["category"] == "暫無明顯匹配"


class TestScenarioClassifier:
    def test_classify_purchasing(self):
        c = DecisionScenarioClassifier()
        result = c.classify("應該選擇哪一個方案")
        assert result["scene"] == "採購(方案選擇)"
        assert result["confidence"] == 1.0

    def test_classify_judge(self):
        c = DecisionScenarioClassifier()
        result = c.classify("是否應該進入新市場")
        assert result["scene"] == "裁判(採取行動)"


class TestAdvisor:
    def test_advise_safety(self):
        a = BiasMitigationAdvisor()
        result = a.advise(["安全性偏見 (Safety)"])
        assert any(item["technique"] == "檢查清單" for item in result)

    def test_advise_fallback(self):
        a = BiasMitigationAdvisor()
        result = a.advise(["未知偏見"])
        assert result[0]["technique"] == "慢思考流程"


class TestChecklist:
    def test_checklist_length(self):
        result = decision_quality_checklist()
        assert len(result) == 6
        assert all("item" in item and "question" in item for item in result)
