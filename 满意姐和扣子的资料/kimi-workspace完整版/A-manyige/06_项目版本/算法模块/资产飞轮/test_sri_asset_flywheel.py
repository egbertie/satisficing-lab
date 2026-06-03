#!/usr/bin/env python3
"""
test_sri_asset_flywheel.py
满意解资产飞轮与经营指标测试套件
"""

import os
import pytest
import sys

sys.path.insert(0, "/root/.openclaw/workspace")

from sri_asset_flywheel import EnterpriseAssetFlywheel, ManagementIndicators
import partner_matching_db as db

# 使用独立测试数据库，避免污染主库
TEST_DB = "/root/.openclaw/workspace/memory/test_partner_matching.db"


@pytest.fixture(autouse=True)
def isolate_test_db(monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", TEST_DB)
    # 清理旧库
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    db.init_db()
    yield
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)


class TestEnterpriseAssetFlywheel:
    def test_register_and_get_asset(self):
        fw = EnterpriseAssetFlywheel()
        aid = fw.register_asset("prompt", "测试Prompt", "1.0", "测试", "这是一个测试")
        assert aid.startswith("prompt_")
        asset = fw.get_asset(aid)
        assert asset is not None
        assert asset["name"] == "测试Prompt"
        assert asset["asset_type"] == "prompt"
        assert asset["status"] == "active"

    def test_invalid_asset_type(self):
        fw = EnterpriseAssetFlywheel()
        with pytest.raises(ValueError):
            fw.register_asset("invalid_type", "非法资产")

    def test_record_usage(self):
        fw = EnterpriseAssetFlywheel()
        aid = fw.register_asset("skill", "测试技能")
        ok = fw.record_usage(aid)
        assert ok is True
        asset = fw.get_asset(aid)
        assert asset["usage_count"] == 1

    def test_reuse_rate(self):
        fw = EnterpriseAssetFlywheel()
        fw.register_asset("prompt", "P1")
        fw.register_asset("prompt", "P2")
        fw.register_asset("skill", "S1")
        # 只用 P1
        fw.record_usage(fw.list_assets("prompt")[0]["asset_id"])
        reuse = fw.get_reuse_rate()
        assert reuse["total_active"] == 3
        assert reuse["used_assets"] == 1
        assert reuse["reuse_rate"] == pytest.approx(33.33, abs=0.1)

    def test_seed_default_assets_idempotent(self):
        fw = EnterpriseAssetFlywheel()
        ids1 = fw.seed_default_assets()
        ids2 = fw.seed_default_assets()
        assert len(ids2) == 0  # 幂等，第二次无新增
        all_assets = fw.list_assets()
        assert len(all_assets) == len(ids1)

    def test_export_dashboard(self):
        fw = EnterpriseAssetFlywheel()
        fw.seed_default_assets()
        dash = fw.export_dashboard()
        assert "assets_by_type" in dash
        assert "reuse_summary" in dash


class TestManagementIndicators:
    def test_compute_time_no_data(self):
        mi = ManagementIndicators()
        result = mi.compute_time_efficiency({"total_assessments": 0, "avg_duration_seconds": 0.0})
        assert result["time_minutes"] == 15.0
        assert result["source"] == "estimated"

    def test_compute_time_with_data(self):
        mi = ManagementIndicators()
        result = mi.compute_time_efficiency(
            {"total_assessments": 2, "avg_duration_seconds": 900.0}
        )
        assert result["time_minutes"] == 15.0
        assert result["source"] == "measured"

    def test_compute_quality_no_data(self):
        mi = ManagementIndicators()
        result = mi.compute_quality_rate({"total_assessments": 0, "avg_score": 0.0})
        assert result["quality_rate"] == 0.0
        assert result["source"] == "none"

    def test_compute_quality_with_data(self):
        mi = ManagementIndicators()
        result = mi.compute_quality_rate(
            {"total_assessments": 3, "avg_score": 82.5}
        )
        assert result["quality_rate"] == 82.5
        assert result["source"] == "score_avg"

    def test_compute_risk_exposure(self):
        mi = ManagementIndicators()
        result = mi.compute_risk_exposure(
            {
                "total_assessments": 5,
                "risk_distribution": {"高风险": 2, "中风险": 3},
            }
        )
        assert result["risk_count"] == 2
        assert result["risk_rate"] == 40.0

    def test_compute_unit_cost(self):
        mi = ManagementIndicators()
        result = mi.compute_unit_cost(
            {
                "total_assessments": 3,
                "sku_distribution": {"SKU-A": 2, "SKU-B": 1},
            }
        )
        expected = (500 * 2 + 2000 * 1) / 3
        assert result["cost_yuan"] == pytest.approx(expected, abs=0.01)

    def test_capture_snapshot(self):
        mi = ManagementIndicators()
        snap = mi.capture_snapshot(note="test")
        assert snap["snapshot_id"] > 0
        assert "time" in snap
        assert "quality" in snap
        assert "risk" in snap
        assert "cost" in snap
        assert "reuse" in snap
        assert snap["timestamp"]

    def test_dashboard_reads_snapshot(self):
        mi = ManagementIndicators()
        snap = mi.capture_snapshot()
        dash = mi.dashboard()
        assert dash["source"] == "latest_snapshot"
        assert dash["time_minutes"] == snap["time"]["time_minutes"]

    def test_markdown_report(self):
        mi = ManagementIndicators()
        report = mi.markdown_report()
        assert "# SRI 经营指标看板" in report
        assert "时间 (Time)" in report
        assert "质量 (Quality)" in report
        assert "风险 (Risk)" in report
        assert "成本 (Cost)" in report
        assert "复用率 (Reuse)" in report

    def test_seed_demo_data(self):
        mi = ManagementIndicators()
        snap = mi.seed_demo_data()
        # 验证资产已注册
        assets = mi.flywheel.list_assets()
        assert len(assets) >= 1
        # 验证评估数据已写入
        stats = db.get_assessment_stats()
        assert stats["total_assessments"] >= 1
        # 验证有复用记录
        reuse = mi.flywheel.get_reuse_rate()
        assert reuse["used_assets"] >= 1
        # 验证快照生成
        assert snap["snapshot_id"] > 0


class TestIntegrationWithPartnerMatchingDB:
    def test_save_assessment_with_duration(self):
        db.init_db()
        aid = db.save_assessment(
            sku_type="SKU-A",
            company_name="集成测试公司",
            overall_risk="低风险",
            overall_score=88,
            dimensions=[{"name": "测试维度", "value": 88, "detail": {}}],
            raw_json={"test": True},
            duration_seconds=12.5 * 60,
        )
        row = db.get_assessment(aid)
        assert row is not None
        assert row["company_name"] == "集成测试公司"

    def test_asset_lifecycle(self):
        db.init_db()
        aid = db.save_asset("skill", "生命周期测试技能", "1.0")
        assert db.get_asset(aid) is not None
        db.increment_asset_usage(aid)
        asset = db.get_asset(aid)
        assert asset["usage_count"] == 1
        db.delete_asset(aid)
        asset = db.get_asset(aid)
        assert asset["status"] == "deprecated"

    def test_metrics_snapshot_crud(self):
        db.init_db()
        sid = db.save_metrics_snapshot(
            time_minutes=14.5,
            quality_rate=88.0,
            risk_count=0,
            cost_yuan=500.0,
            reuse_rate=75.0,
            note="crud_test",
        )
        assert sid > 0
        latest = db.get_latest_metrics_snapshot()
        assert latest["note"] == "crud_test"
        history = db.list_metrics_snapshots(limit=10)
        assert any(h["snapshot_id"] == sid for h in history)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
