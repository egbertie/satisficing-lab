#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_partner_match_consultation_kit.py
合伙人匹配咨询工具箱测试
"""

import pytest
from partner_match_consultation_kit import PartnerMatchConsultationKit


class TestPartnerMatchConsultationKit:
    def test_kit_initialization(self):
        kit = PartnerMatchConsultationKit(startup_name="测试科技")
        assert kit.startup_name == "测试科技"

    def test_run_returns_markdown_report(self):
        kit = PartnerMatchConsultationKit(startup_name="深芯科技")
        founder = {"name": "张明", "industry": "半导体", "stage": "Pre-A"}
        candidate = {
            "name": "李明辉",
            "confucian_scores": {"仁": 7, "義": 6, "禮": 5, "智": 8, "信": 6},
            "maturity_scores": [7, 6, 6, 7, 5, 6, 7, 6],
            "tech_stake": 0.35,
            "has_veto": False,
            "resource_commitments": [
                {"item": "引入产线资源", "milestone": "Q3 完成首条产线打通", "penalty": "未达成则股权稀释 5%"}
            ],
            "has_exit_agreement": False,
            "has_stop_loss": False,
            "has_vesting": True,
            "vesting_stages": ["实验室", "工程化", "商业化"],
            "mcda_context": {"准则间可补偿": True, "需明确权衡": True, "决策者偏好清晰": True},
            "risk_evidence": ["股权讨论寸步不让"],
            "tech_score": 75,
            "comm_score": 60,
            "value_score": 55,
            "tech_complement": 8,
            "value_fit": 5,
            "commitment_credibility": 6,
            "risk_appetite": 5,
            "exit_flexibility": 4,
        }
        report = kit.run(founder, candidate)
        assert isinstance(report, str)
        assert "合伙人匹配决策咨询报告" in report
        assert "决策信号灯" in report
        assert "儒商伦理匹配度" in report
        assert "风险扫描结果" in report
        assert "下一步行动清单" in report

    def test_demo_runs_without_exception(self, capsys):
        from partner_match_consultation_kit import demo
        demo()
        captured = capsys.readouterr()
        assert "模拟案例实测完成" in captured.out

    def test_mcda_recommendation_included(self):
        kit = PartnerMatchConsultationKit()
        candidate = {
            "name": "测试候选人",
            "confucian_scores": {"仁": 6, "義": 6, "禮": 6, "智": 6, "信": 6},
            "maturity_scores": [6, 6, 6, 6, 6, 6, 6, 6],
            "tech_stake": 0.50,
            "has_veto": True,
            "resource_commitments": [],
            "has_exit_agreement": True,
            "has_stop_loss": True,
            "has_vesting": True,
            "vesting_stages": ["实验室", "工程化", "商业化"],
            "mcda_context": {"准则间可补偿": True},
            "risk_evidence": [],
            "tech_score": 70,
            "comm_score": 70,
            "value_score": 70,
            "tech_complement": 7,
            "value_fit": 7,
            "commitment_credibility": 7,
            "risk_appetite": 7,
            "exit_flexibility": 7,
        }
        report = kit.run({"name": "创始人"}, candidate)
        assert "决策方法推荐" in report
        assert "儒商智慧锦囊" in report
        assert "合伙人信任专题建议" in report
