#!/usr/bin/env python3
"""
sri_asset_flywheel.py
满意解研究所底层操作系统：资产飞轮 + 经营指标 V1.0

生产层: EnterpriseAssetFlywheel — 管理 Prompt/Skill/Memory/Workflow/Case Library
经营层: ManagementIndicators — 计算 时间/质量/风险/成本/复用率

核心映射（来自两张方法论原图）:
- Prompt/Skill/Memory  → 复用率 (Reuse)
- Workflow 效率        → 时间 (Time)
- Case 质量            → 质量 (Quality)
- 执行过程             → 风险 (Risk)
- 投入产出             → 成本 (Cost)
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

import sys
sys.path.insert(0, "/root/.openclaw/workspace")

from defense_base_components import BaseComponent
import partner_matching_db as db


class EnterpriseAssetFlywheel(BaseComponent):
    """
    企业资产飞轮（生产层）
    将 Prompt、Skill、Memory、Workflow、Case Library 沉淀为可复用资产。
    """

    ASSET_TYPES = ["prompt", "skill", "memory", "workflow", "case_library"]

    def __init__(self):
        super().__init__("enterprise_asset_flywheel")
        self.db = db

    def register_asset(
        self,
        asset_type: str,
        name: str,
        version: str = "1.0.0",
        role: str = "通用",
        content_summary: str = "",
    ) -> str:
        if asset_type not in self.ASSET_TYPES:
            raise ValueError(f"不支持的资产类型: {asset_type}，仅支持 {self.ASSET_TYPES}")
        safe_name = name.replace(" ", "_").replace("/", "_")
        asset_id = f"{asset_type.lower()}_{safe_name}_{uuid.uuid4().hex[:8]}"
        self.db.save_asset(
            asset_id=asset_id,
            asset_type=asset_type,
            name=name,
            version=version,
            role=role,
            content_summary=content_summary,
            status="active",
        )
        return asset_id

    def record_usage(self, asset_id: str) -> bool:
        return self.db.increment_asset_usage(asset_id)

    def get_asset(self, asset_id: str) -> Optional[Dict[str, Any]]:
        return self.db.get_asset(asset_id)

    def list_assets(self, asset_type: Optional[str] = None) -> List[Dict[str, Any]]:
        return self.db.list_assets(asset_type=asset_type)

    def get_reuse_rate(self) -> Dict[str, Any]:
        assets = self.list_assets()
        if not assets:
            return {
                "reuse_rate": 0.0,
                "total_active": 0,
                "used_assets": 0,
                "avg_usage_count": 0.0,
            }
        active = [a for a in assets if a.get("status") == "active"]
        used = [a for a in active if a.get("usage_count", 0) > 0]
        total = len(active)
        reuse_rate = (len(used) / total * 100) if total else 0.0
        avg_usage = sum(a.get("usage_count", 0) for a in active) / total if total else 0.0
        return {
            "reuse_rate": round(reuse_rate, 2),
            "total_active": total,
            "used_assets": len(used),
            "avg_usage_count": round(avg_usage, 2),
        }

    def export_dashboard(self) -> Dict[str, Any]:
        assets = self.list_assets()
        by_type: Dict[str, List[Dict]] = {}
        for a in assets:
            by_type.setdefault(a["asset_type"], []).append(a)
        reuse = self.get_reuse_rate()
        return {
            "timestamp": self.get_timestamp(),
            "assets_by_type": {k: len(v) for k, v in by_type.items()},
            "top_reused": sorted(
                assets, key=lambda x: x.get("usage_count", 0), reverse=True
            )[:5],
            "reuse_summary": reuse,
        }

    def seed_default_assets(self) -> List[str]:
        """注册一组默认的 SRI 核心资产（幂等：先检查是否已存在同类型同名资产）"""
        defaults = [
            ("prompt", "SKU-A诊断对话开场白", "1.0", "诊断顾问", "标准化客户首次沟通开场Prompt"),
            ("prompt", "风险扫描结果解释Prompt", "1.0", "诊断顾问", "将风险扫描结果转译为创始人语言"),
            ("skill", "hardtech_partner_conflict_window", "1.0", "系统", "冲突窗口期分析技能"),
            ("skill", "hardtech_partner_risk_scanner", "1.0", "系统", "股权/资源/退出/Vesting风险扫描"),
            ("skill", "sku_a_assessment_orchestrator", "1.0", "系统", "SKU-A编排器"),
            ("memory", "partner_matching_casebook_v1", "1.0", "知识库", "128个一堂案例+SRI精选案例"),
            ("memory", "yitang_methodology_kit", "1.0", "知识库", "一堂低成本创业与指标体系资产"),
            ("workflow", "sku_a_light_consulting_workflow", "1.0", "运营", "从信息采集到报告交付的SKU-A工作流"),
            ("case_library", "硬科技合伙人冲突案例集", "1.0", "案例", "股权纠纷、技术路线分歧等真实脱敏案例"),
        ]
        ids = []
        for asset_type, name, version, role, summary in defaults:
            existing = self.list_assets(asset_type=asset_type)
            if any(e.get("name") == name for e in existing):
                continue
            aid = self.register_asset(asset_type, name, version, role, summary)
            ids.append(aid)
        return ids


class ManagementIndicators(BaseComponent):
    """
    经营指标体系（经营层）
    最终回到管理层关心的五类指标：时间、质量、风险、成本、复用率。
    """

    SKU_COST_MAP: Dict[str, float] = {
        "SKU-A": 500.0,
        "SKU-B": 2000.0,
        "SKU-C": 8000.0,
    }

    def __init__(self):
        super().__init__("management_indicators")
        self.flywheel = EnterpriseAssetFlywheel()

    def compute_time_efficiency(
        self, stats: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        if stats is None:
            stats = db.get_assessment_stats()
        avg_sec = stats.get("avg_duration_seconds") or 0.0
        if avg_sec <= 0:
            return {
                "time_minutes": 15.0,
                "source": "estimated",
                "note": "尚无足够实测数据，采用SKU-A标称处理时长15分钟",
            }
        return {
            "time_minutes": round(avg_sec / 60.0, 2),
            "source": "measured",
            "note": f"基于最近{stats.get('total_assessments', 0)}次评估的平均耗时",
        }

    def compute_quality_rate(
        self, stats: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        if stats is None:
            stats = db.get_assessment_stats()
        avg_score = stats.get("avg_score") or 0.0
        if stats.get("total_assessments", 0) == 0:
            return {
                "quality_rate": 0.0,
                "source": "none",
                "note": "尚无评估数据",
            }
        return {
            "quality_rate": round(avg_score, 2),
            "source": "score_avg",
            "note": f"基于最近{stats['total_assessments']}次评估的平均得分",
        }

    def compute_risk_exposure(
        self, stats: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        if stats is None:
            stats = db.get_assessment_stats()
        risk_dist = stats.get("risk_distribution", {})
        high_risk = risk_dist.get("高风险", 0) + risk_dist.get("极高风险", 0)
        total = stats.get("total_assessments", 0)
        return {
            "risk_count": high_risk,
            "risk_rate": round((high_risk / total * 100), 2) if total else 0.0,
            "distribution": risk_dist,
            "note": f"最近{total}次评估中高风险/极高风险出现{high_risk}次",
        }

    def compute_unit_cost(
        self, stats: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        if stats is None:
            stats = db.get_assessment_stats()
        sku_dist = stats.get("sku_distribution", {})
        total = stats.get("total_assessments", 0)
        if total == 0:
            return {
                "cost_yuan": 0.0,
                "source": "none",
                "note": "尚无评估数据",
            }
        total_cost = sum(
            self.SKU_COST_MAP.get(sku, 500.0) * cnt for sku, cnt in sku_dist.items()
        )
        avg_cost = total_cost / total
        return {
            "cost_yuan": round(avg_cost, 2),
            "source": "sku_model",
            "note": f"按SKU单价模型加权平均：{sku_dist}",
        }

    def compute_asset_reuse(self) -> Dict[str, Any]:
        return self.flywheel.get_reuse_rate()

    def capture_snapshot(self, note: str = "") -> Dict[str, Any]:
        stats = db.get_assessment_stats()
        time_info = self.compute_time_efficiency(stats)
        quality_info = self.compute_quality_rate(stats)
        risk_info = self.compute_risk_exposure(stats)
        cost_info = self.compute_unit_cost(stats)
        reuse_info = self.compute_asset_reuse()

        snapshot_id = db.save_metrics_snapshot(
            time_minutes=time_info["time_minutes"],
            quality_rate=quality_info["quality_rate"],
            risk_count=risk_info["risk_count"],
            cost_yuan=cost_info["cost_yuan"],
            reuse_rate=reuse_info["reuse_rate"],
            note=note,
        )

        return {
            "snapshot_id": snapshot_id,
            "timestamp": self.get_timestamp(),
            "time": time_info,
            "quality": quality_info,
            "risk": risk_info,
            "cost": cost_info,
            "reuse": reuse_info,
        }

    def dashboard(self) -> Dict[str, Any]:
        latest = db.get_latest_metrics_snapshot()
        if latest:
            return {
                "timestamp": latest["snapshot_at"],
                "time_minutes": latest["time_minutes"],
                "quality_rate": latest["quality_rate"],
                "risk_count": latest["risk_count"],
                "cost_yuan": latest["cost_yuan"],
                "reuse_rate": latest["reuse_rate"],
                "source": "latest_snapshot",
            }
        return self.capture_snapshot(note="首次自动采集")

    def markdown_report(self) -> str:
        dash = self.dashboard()
        lines = [
            "# SRI 经营指标看板",
            f"**更新时间**: {dash.get('timestamp', self.get_timestamp())}",
            "",
            "## 五类核心指标",
            "",
            "| 指标 | 当前值 | 说明 |",
            "|------|--------|------|",
            f"| 时间 (Time) | {dash.get('time_minutes', 'N/A')} 分钟 | 平均处理时长 |",
            f"| 质量 (Quality) | {dash.get('quality_rate', 'N/A')}% | 评估平均得分 |",
            f"| 风险 (Risk) | {dash.get('risk_count', 'N/A')} 件 | 高风险事件数 |",
            f"| 成本 (Cost) | ¥{dash.get('cost_yuan', 'N/A')} | 单位任务成本 |",
            f"| 复用率 (Reuse) | {dash.get('reuse_rate', 'N/A')}% | 资产复用率 |",
            "",
            "## 解读",
            "- **时间**：目标 ≤15 分钟。若超过，需优化 Workflow 效率。",
            "- **质量**：目标 ≥80%。反映 Case Library 与诊断流程的准确性。",
            "- **风险**：红线条线为 1 件。≥1 件时触发复核机制。",
            "- **成本**：SKU-A/B/C 分别按 ¥500/¥2000/¥8000 模型计算。",
            "- **复用率**：Prompt/Skill/Memory 等资产被复用的比例。越高说明沉淀越厚。",
            "",
            "*本报告由 ManagementIndicators 自动生成。*",
        ]
        return "\n".join(lines)

    def seed_demo_data(self) -> Dict[str, Any]:
        """初始化资产并模拟若干评估数据，用于演示指标效果（典型硬科技困境画像）"""
        # 1. 注册默认资产（幂等）
        self.flywheel.seed_default_assets()

        # 2. 模拟多次评估（典型硬科技困境画像）
        demo_cases = [
            ("Demo硬科技", "SKU-A", 72, "中风险", 12.5),
            ("Test硬科技", "SKU-A", 68, "中风险", 18.0),
            ("Pre-A硬科技C", "SKU-A", 85, "低风险", 14.2),
        ]
        for company, sku, score, risk, duration in demo_cases:
            db.save_assessment(
                sku_type=sku,
                company_name=company,
                overall_risk=risk,
                overall_score=score,
                dimensions=[{"name": "综合", "value": score, "detail": {}}],
                raw_json={"demo": True, "company": company},
                duration_seconds=duration * 60,
            )

        # 3. 模拟资产复用
        assets = self.flywheel.list_assets()
        for a in assets[:4]:
            for _ in range(3):
                self.flywheel.record_usage(a["asset_id"])

        # 4. 捕获快照
        return self.capture_snapshot(note="Demo数据初始化快照（典型硬科技困境）")


def main():
    """日常资产激活入口：初始化并打印看板"""
    flywheel = EnterpriseAssetFlywheel()
    indicators = ManagementIndicators()

    existing = flywheel.list_assets()
    if not existing:
        flywheel.seed_default_assets()

    snapshot = indicators.capture_snapshot()
    print(json.dumps(snapshot, ensure_ascii=False, indent=2))
    print("\n--- Markdown 看板 ---\n")
    print(indicators.markdown_report())


if __name__ == "__main__":
    main()
