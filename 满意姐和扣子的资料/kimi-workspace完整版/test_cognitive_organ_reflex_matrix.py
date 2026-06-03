#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_cognitive_organ_reflex_matrix.py
12场景条件反射矩阵实测基座测试
"""

import pytest
from cognitive_organ_reflex_matrix import CognitiveOrganReflexMatrix


class TestCognitiveOrganReflexMatrix:
    def test_init(self):
        matrix = CognitiveOrganReflexMatrix()
        assert len(matrix.list_scenarios()) == 12

    def test_all_scenarios_triggerable(self):
        matrix = CognitiveOrganReflexMatrix()
        for scene_id in matrix.matrix.keys():
            result = matrix.trigger(scene_id)
            assert result["status"] == "reflex_ready"
            assert "activated_organs" in result
            assert "skill_allocation" in result
            assert "execution_flow" in result

    def test_reflex_report_contains_all_scenes(self):
        matrix = CognitiveOrganReflexMatrix()
        report = matrix.reflex_report()
        assert "# 12场景条件反射矩阵实测基座报告" in report
        for scene_name in matrix.list_scenarios():
            assert scene_name in report

    def test_stat(self):
        matrix = CognitiveOrganReflexMatrix()
        stat = matrix.stat()
        assert stat["场景总数"] == 12
        assert len(stat["覆盖器官"]) >= 7
        assert stat["去重技能数"] >= 40

    def test_demo_runs(self, capsys):
        from cognitive_organ_reflex_matrix import demo
        demo()
        captured = capsys.readouterr()
        assert "12场景条件反射矩阵" in captured.out
