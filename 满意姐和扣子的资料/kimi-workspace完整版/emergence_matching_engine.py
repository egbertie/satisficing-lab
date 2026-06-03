#!/usr/bin/env python3
"""
emergence_matching_engine.py
涌现匹配算法引擎 V1.0

基于《涌现匹配算法实施手册 V1.0》构建的可运行评估系统。
功能：
- 三模块数据采集与评分（数据挖掘 / 社交图谱 / 互动观察）
- 场景化权重动态分配
- 结构化评估报告生成（Markdown）
- 候选人档案持久化（JSON）

作者: 满意姐 + 蓝军Skeptor-7
日期: 2026-04-04
"""

import json
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

# ─────────────────────────────────────────────
# 配置
# ─────────────────────────────────────────────
WORKSPACE = Path("/root/.openclaw/workspace")
DATA_DIR = WORKSPACE / "data" / "emergence_matching"
REPORTS_DIR = WORKSPACE / "A-manyige" / "汇报"
DATA_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


class StartupType(Enum):
    TECH = "技术驱动型"
    RESOURCE = "资源驱动型"
    RELATIONSHIP = "关系驱动型"


# ─────────────────────────────────────────────
# 数据模型
# ─────────────────────────────────────────────

@dataclass
class DataMiningScores:
    # 职业平台 (0-5)
    career_trajectory: float = 0.0
    skill_match: float = 0.0
    promotion_pattern: float = 0.0
    risk_signals: float = 0.0
    # 学术/技术 (0-5)
    academic_depth: float = 0.0
    patent_quality: float = 0.0
    tech_transfer: float = 0.0
    # 社交媒体 (0-5)
    value_signals: float = 0.0
    expression_style: float = 0.0
    risk_content: float = 0.0
    # 公开演讲 (0-5)
    structured_thinking: float = 0.0
    ad_hoc_reaction: float = 0.0
    audience_adaptation: float = 0.0

    def weighted_score(self) -> float:
        # 职业平台40% + 学术技术30% + 社交媒体20% + 公开演讲10%
        career = (self.career_trajectory + self.skill_match + self.promotion_pattern + self.risk_signals) / 4
        academic = (self.academic_depth + self.patent_quality + self.tech_transfer) / 3
        social = (self.value_signals + self.expression_style + self.risk_content) / 3
        speech = (self.structured_thinking + self.ad_hoc_reaction + self.audience_adaptation) / 3
        return career * 0.40 + academic * 0.30 + social * 0.20 + speech * 0.10


@dataclass
class SocialGraphScores:
    # 共同联系人 (0-5)
    common_contacts_quality: float = 0.0
    side_info_credibility: float = 0.0
    # 社交圈结构 (0-5)
    network_diversity: float = 0.0
    network_core_quality: float = 0.0
    # 网络关联 (0-5)
    overlap_density: float = 0.0
    complementarity: float = 0.0
    conflict_risk: float = 0.0

    def weighted_score(self) -> float:
        common = (self.common_contacts_quality + self.side_info_credibility) / 2
        structure = (self.network_diversity + self.network_core_quality) / 2
        relation = (self.overlap_density + self.complementarity - self.conflict_risk + 5) / 3
        return common * 0.40 + structure * 0.35 + relation * 0.25


@dataclass
class InteractionObservationScores:
    # 社交场景 (0-5)
    industry_event_performance: float = 0.0
    social_gathering_behavior: float = 0.0
    work_scene_collaboration: float = 0.0
    # 行为清单 (0-5)
    service_attitude: float = 0.0
    time_consciousness: float = 0.0
    objection_handling: float = 0.0
    stress_performance: float = 0.0
    # 长期跟踪 (0-5)
    consistency_score: float = 0.0

    def weighted_score(self) -> float:
        scene = (self.industry_event_performance + self.social_gathering_behavior + self.work_scene_collaboration) / 3
        behavior = (self.service_attitude + self.time_consciousness + self.objection_handling + self.stress_performance) / 4
        tracking = self.consistency_score
        return scene * 0.35 + behavior * 0.45 + tracking * 0.20


@dataclass
class CandidateProfile:
    candidate_id: str
    name: str
    startup_type: StartupType
    data_mining: DataMiningScores = field(default_factory=DataMiningScores)
    social_graph: SocialGraphScores = field(default_factory=SocialGraphScores)
    interaction: InteractionObservationScores = field(default_factory=InteractionObservationScores)
    notes: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def calculate_match_score(self) -> Dict:
        """三模块整合评分"""
        dm_score = self.data_mining.weighted_score()
        sg_score = self.social_graph.weighted_score()
        io_score = self.interaction.weighted_score()

        if self.startup_type == StartupType.TECH:
            weights = {"data_mining": 0.50, "social_graph": 0.25, "interaction": 0.25}
        elif self.startup_type == StartupType.RESOURCE:
            weights = {"data_mining": 0.25, "social_graph": 0.50, "interaction": 0.25}
        else:
            weights = {"data_mining": 0.25, "social_graph": 0.25, "interaction": 0.50}

        total = (
            dm_score * weights["data_mining"]
            + sg_score * weights["social_graph"]
            + io_score * weights["interaction"]
        )

        return {
            "data_mining": round(dm_score, 2),
            "social_graph": round(sg_score, 2),
            "interaction": round(io_score, 2),
            "weights": weights,
            "total_score": round(total, 2),
            "max_possible": 5.0,
            "match_rate": round(total / 5.0 * 100, 1),
        }

    def to_dict(self) -> Dict:
        d = asdict(self)
        d["startup_type"] = self.startup_type.value
        return d

    @classmethod
    def from_dict(cls, data: Dict) -> "CandidateProfile":
        data["startup_type"] = StartupType(data["startup_type"])
        data["data_mining"] = DataMiningScores(**data["data_mining"])
        data["social_graph"] = SocialGraphScores(**data["social_graph"])
        data["interaction"] = InteractionObservationScores(**data["interaction"])
        return cls(**{k: v for k, v in data.items() if k in {f.name for f in cls.__dataclass_fields__.values()}})


# ─────────────────────────────────────────────
# 引擎主类
# ─────────────────────────────────────────────

class EmergenceMatchingEngine:
    def __init__(self):
        self.profiles: Dict[str, CandidateProfile] = {}
        self._load_all()

    def _profile_path(self, candidate_id: str) -> Path:
        return DATA_DIR / f"{candidate_id}.json"

    def _load_all(self):
        for f in DATA_DIR.glob("*.json"):
            with open(f, "r", encoding="utf-8") as fp:
                self.profiles[f.stem] = CandidateProfile.from_dict(json.load(fp))

    def save_profile(self, profile: CandidateProfile):
        profile.updated_at = datetime.now().isoformat()
        path = self._profile_path(profile.candidate_id)
        with open(path, "w", encoding="utf-8") as fp:
            json.dump(profile.to_dict(), fp, ensure_ascii=False, indent=2)
        self.profiles[profile.candidate_id] = profile
        print(f"💾 档案已保存: {path}")

    def get_profile(self, candidate_id: str) -> Optional[CandidateProfile]:
        return self.profiles.get(candidate_id)

    def generate_report(self, candidate_id: str) -> str:
        profile = self.get_profile(candidate_id)
        if not profile:
            raise ValueError(f"未找到候选人: {candidate_id}")

        scores = profile.calculate_match_score()

        # 风险判定
        risk_level = "🟢 低风险"
        if scores["total_score"] < 2.5:
            risk_level = "🔴 高风险 / 不建议合作"
        elif scores["total_score"] < 3.5:
            risk_level = "🟡 中等风险 / 需深入验证"

        lines = []
        lines.append(f"# 涌现匹配算法评估报告")
        lines.append(f"")
        lines.append(f"**候选人**: {profile.name}")
        lines.append(f"**档案ID**: {profile.candidate_id}")
        lines.append(f"**创业类型**: {profile.startup_type.value}")
        lines.append(f"**评估时间**: {profile.updated_at}")
        lines.append(f"")
        lines.append(f"---")
        lines.append(f"")
        lines.append(f"## 综合评分")
        lines.append(f"")
        lines.append(f"| 模块 | 得分(0-5) | 权重 | 加权贡献 |")
        lines.append(f"|------|-----------|------|----------|")
        for k, v in scores["weights"].items():
            module_name = {"data_mining": "数据挖掘", "social_graph": "社交图谱", "interaction": "互动观察"}[k]
            lines.append(f"| {module_name} | {scores[k]} | {v*100:.0f}% | {scores[k] * v:.2f} |")
        lines.append(f"| **总分** | **{scores['total_score']}** | - | - |")
        lines.append(f"")
        lines.append(f"**匹配率**: {scores['match_rate']}%  {risk_level}")
        lines.append(f"")
        lines.append(f"---")
        lines.append(f"")
        lines.append(f"## 模块一：数据挖掘")
        lines.append(f"")
        dm = profile.data_mining
        lines.append(f"- 职业轨迹: {dm.career_trajectory}/5 | 技能匹配: {dm.skill_match}/5 | 晋升模式: {dm.promotion_pattern}/5 | 风险信号: {dm.risk_signals}/5")
        lines.append(f"- 学术深度: {dm.academic_depth}/5 | 专利质量: {dm.patent_quality}/5 | 技术转化: {dm.tech_transfer}/5")
        lines.append(f"- 价值观信号: {dm.value_signals}/5 | 表达风格: {dm.expression_style}/5 | 风险内容: {dm.risk_content}/5")
        lines.append(f"- 结构化思维: {dm.structured_thinking}/5 | 临场反应: {dm.ad_hoc_reaction}/5 | 受众适配: {dm.audience_adaptation}/5")
        lines.append(f"")
        lines.append(f"---")
        lines.append(f"")
        lines.append(f"## 模块二：社交图谱")
        lines.append(f"")
        sg = profile.social_graph
        lines.append(f"- 共同联系人质量: {sg.common_contacts_quality}/5 | 侧面信息可信度: {sg.side_info_credibility}/5")
        lines.append(f"- 网络多样性: {sg.network_diversity}/5 | 核心圈质量: {sg.network_core_quality}/5")
        lines.append(f"- 网络重叠度: {sg.overlap_density}/5 | 互补性: {sg.complementarity}/5 | 冲突风险: {sg.conflict_risk}/5")
        lines.append(f"")
        lines.append(f"---")
        lines.append(f"")
        lines.append(f"## 模块三：互动观察")
        lines.append(f"")
        io = profile.interaction
        lines.append(f"- 行业活动表现: {io.industry_event_performance}/5 | 社交聚会行为: {io.social_gathering_behavior}/5 | 工作场景协作: {io.work_scene_collaboration}/5")
        lines.append(f"- 服务态度: {io.service_attitude}/5 | 时间观念: {io.time_consciousness}/5 | 异议处理: {io.objection_handling}/5 | 压力下表现: {io.stress_performance}/5")
        lines.append(f"- 长期一致性: {io.consistency_score}/5")
        lines.append(f"")
        lines.append(f"---")
        lines.append(f"")
        lines.append(f"## 评估备注")
        lines.append(f"")
        lines.append(profile.notes or "（无备注）")
        lines.append(f"")
        lines.append(f"---")
        lines.append(f"")
        lines.append(f"*报告生成于 {datetime.now().isoformat()} | 涌现匹配算法引擎 V1.0*")

        report_text = "\n".join(lines)
        report_path = REPORTS_DIR / f"涌现匹配算法评估报告-{profile.candidate_id}.md"
        with open(report_path, "w", encoding="utf-8") as fp:
            fp.write(report_text)
        print(f"📄 报告已保存: {report_path}")
        return report_text

    def list_profiles(self) -> List[str]:
        return list(self.profiles.keys())


# ─────────────────────────────────────────────
# CLI / 快速测试
# ─────────────────────────────────────────────

def quick_demo():
    engine = EmergenceMatchingEngine()

    profile = CandidateProfile(
        candidate_id="demo_001",
        name="张三（示例候选人）",
        startup_type=StartupType.TECH,
        data_mining=DataMiningScores(
            career_trajectory=4.0, skill_match=3.5, promotion_pattern=3.0, risk_signals=4.0,
            academic_depth=2.5, patent_quality=2.0, tech_transfer=3.0,
            value_signals=4.0, expression_style=3.5, risk_content=4.0,
            structured_thinking=3.5, ad_hoc_reaction=3.0, audience_adaptation=4.0
        ),
        social_graph=SocialGraphScores(
            common_contacts_quality=3.5, side_info_credibility=4.0,
            network_diversity=3.0, network_core_quality=4.0,
            overlap_density=3.5, complementarity=4.0, conflict_risk=1.0
        ),
        interaction=InteractionObservationScores(
            industry_event_performance=4.0, social_gathering_behavior=3.5, work_scene_collaboration=3.0,
            service_attitude=4.5, time_consciousness=3.5, objection_handling=3.0, stress_performance=3.5,
            consistency_score=3.5
        ),
        notes="示例档案，用于验证引擎计算逻辑与报告格式。"
    )

    engine.save_profile(profile)
    report = engine.generate_report("demo_001")
    print("\n" + "=" * 60)
    print("演示完成。可用档案:", engine.list_profiles())
    print("=" * 60)
    return report


if __name__ == "__main__":
    quick_demo()
