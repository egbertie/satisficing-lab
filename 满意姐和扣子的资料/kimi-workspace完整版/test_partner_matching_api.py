#!/usr/bin/env python3
"""
test_partner_matching_api.py
Partner Matching API 测试套件 V1.0

运行方式:
  pytest test_partner_matching_api.py -v
"""

import sys
import os

sys.path.insert(0, "/root/.openclaw/workspace")
os.environ["PARTNER_MATCHING_API_KEY"] = "test-key"

from fastapi.testclient import TestClient
from partner_matching_api import app, API_KEY

client = TestClient(app)

DEMO_PAYLOAD = {
    "company_name": "Test硬科技",
    "founded_months": 10,
    "tech_founder_stake": 0.5,
    "has_veto": True,
    "resource_milestones": [{"item": "政府补贴", "milestone": "2026Q2", "penalty": "股权稀释"}],
    "has_exit_agreement": True,
    "has_stop_loss": True,
    "has_stage_vesting": True,
    "vesting_stages": ["实验室", "工程化", "商业化"],
    "tech_route_disputes_monthly": 0.5,
    "communication_frequency_weekly": 4.0,
    "equity_change_count": 0,
    "funding_deviation_rate": 0.05,
    "mentor_involved": True,
    "stage": "种子期",
    "actions_done": ["能力评估", "价值观测试", "压力测试"],
    "pattern_flags": {
        "has_tech_biz_complement": True,
        "value_aligned": True,
        "shared_stress_test": True,
        "dynamic_equity": True,
        "transparent_comm": True,
        "equity_imbalanced": False,
        "capability_overlap": False,
        "founder_dependent": False,
    },
}


class TestHealth:
    def test_health(self):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"


class TestAuthentication:
    def test_missing_key(self):
        response = client.post("/v1/assessments/sku-a", json=DEMO_PAYLOAD)
        assert response.status_code == 401

    def test_invalid_key(self):
        response = client.post(
            "/v1/assessments/sku-a",
            json=DEMO_PAYLOAD,
            headers={"X-API-Key": "wrong-key"},
        )
        assert response.status_code == 401


class TestSkuAAssessment:
    def test_create_assessment_happy_path(self):
        response = client.post(
            "/v1/assessments/sku-a",
            json=DEMO_PAYLOAD,
            headers={"X-API-Key": API_KEY},
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["company_name"] == "Test硬科技"
        assert data["sku_type"] == "SKU-A"
        assert "assessment_id" in data
        assert "overall_score" in data
        assert "overall_risk" in data
        assert len(data["dimensions"]) >= 4
        assert data["dimensions"][0]["name"] == "合伙人冲突窗口"
        # 保存ID供后续查询测试
        self.__class__._created_id = data["assessment_id"]

    def test_get_assessment(self):
        created_id = getattr(self.__class__, "_created_id", None)
        if not created_id:
            # 如果没有前置创建，先创建一个
            r = client.post(
                "/v1/assessments/sku-a",
                json=DEMO_PAYLOAD,
                headers={"X-API-Key": API_KEY},
            )
            created_id = r.json()["assessment_id"]
        response = client.get(
            f"/v1/assessments/{created_id}",
            headers={"X-API-Key": API_KEY},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["assessment_id"] == created_id
        assert "raw_json" in data
        assert "dimensions" in data

    def test_get_assessment_not_found(self):
        response = client.get(
            "/v1/assessments/Assessment-NOTEXIST",
            headers={"X-API-Key": API_KEY},
        )
        assert response.status_code == 404

    def test_list_assessments(self):
        response = client.get(
            "/v1/assessments?limit=5",
            headers={"X-API-Key": API_KEY},
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "count" in data
        assert isinstance(data["items"], list)

    def test_validation_error(self):
        bad_payload = dict(DEMO_PAYLOAD)
        bad_payload["tech_founder_stake"] = 1.5  # 超出范围
        response = client.post(
            "/v1/assessments/sku-a",
            json=bad_payload,
            headers={"X-API-Key": API_KEY},
        )
        assert response.status_code == 422


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
