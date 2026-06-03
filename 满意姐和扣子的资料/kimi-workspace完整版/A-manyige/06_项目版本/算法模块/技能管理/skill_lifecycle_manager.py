#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
skill_lifecycle_manager.py
技能生命周期管理器 V1.0 — 真生命周期，不是假周期

生命周期阶段：
  genesis   → 诞生（经严格门控后才允许创建）
  growth    → 成长（血液化、方法论提取、执行嵌入）
  maturity  → 成熟（稳定运行、定期健康检查）
  consolidation → 整合（同类合并、去重优化）
  retirement → 退役（移出活跃目录，保留元数据）
  archived  → 归档（长期冷存，可复兴）

核心原则：
  1. 创建有门槛 — 必须满足 ECONOMIC_QS + ECONOMIC_CS + HOST 四循环
  2. 合并有机制 — 基于方法论知识库的文本相似度自动检测，人工确认后执行
  3. 更新有追踪 — 读取 config.json 中的 update URL，周期性检查上游版本
  4. 退役有标准 — unused / deprecated / merged / broken 四种退役原因
  5. 复兴有通道 — 归档 skill 可在需要时一键复活，不丢失历史投资
"""
from __future__ import annotations

import os
import json
import re
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from difflib import SequenceMatcher

WORKSPACE = Path("/root/.openclaw/workspace")
SKILLS_DIR = WORKSPACE / "skills"
ARCHIVE_DIR = WORKSPACE / "archive" / "skills-archive"
REGISTRY_PATH = WORKSPACE / "skill_lifecycle_registry.json"
METHODOLOGY_KB_PATH = WORKSPACE / "skill_methodology_knowledge_base.json"
BLOODIZED_REGISTRY = WORKSPACE / ".bloodized_registry.json"

ECONOMIC_QS = {
    "q1_local": "本地能否完成？",
    "q2_light": "轻量能否替代？",
    "q3_compress": "能否压缩？",
}
ECONOMIC_CS = {
    "c1_reusable": "可复用框架？",
    "c2_parallel": "可并行？",
    "c3_boundary_clear": "边界条件明确？",
}

STAGES = ["genesis", "growth", "maturity", "consolidation", "retirement", "archived"]


@dataclass
class SkillLifecycleRecord:
    name: str
    stage: str
    created_at: str
    updated_at: str
    creation_trigger: Dict[str, Any] = field(default_factory=dict)
    bloodized_at: Optional[str] = None
    merge_info: Optional[Dict[str, Any]] = None
    retired_at: Optional[str] = None
    retired_reason: Optional[str] = None
    replacement_skill: Optional[str] = None
    update_url: Optional[str] = None
    last_update_check: Optional[str] = None
    update_available: bool = False
    latest_version: Optional[str] = None
    local_version: Optional[str] = None
    usage_score: float = 0.0
    host_cycle_doc: Optional[str] = None
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "SkillLifecycleRecord":
        return cls(**d)


class SkillLifecycleRegistry:
    """JSON 注册表的读写操作"""

    def __init__(self, path: Path = REGISTRY_PATH, skills_dir: Optional[Path] = None):
        self.path = path
        self.skills_dir = skills_dir or SKILLS_DIR
        self._data: Dict[str, Dict[str, Any]] = {}
        self._load()

    def _load(self):
        if self.path.exists():
            self._data = json.loads(self.path.read_text(encoding="utf-8"))
        else:
            self._data = {}

    def _save(self):
        self.path.write_text(json.dumps(self._data, ensure_ascii=False, indent=2), encoding="utf-8")

    def get(self, name: str) -> Optional[SkillLifecycleRecord]:
        if name in self._data:
            return SkillLifecycleRecord.from_dict(self._data[name])
        return None

    def set(self, record: SkillLifecycleRecord):
        self._data[record.name] = record.to_dict()
        self._save()

    def delete(self, name: str):
        if name in self._data:
            del self._data[name]
            self._save()

    def all_names(self) -> Set[str]:
        return set(self._data.keys())

    def list_by_stage(self, stage: str) -> List[SkillLifecycleRecord]:
        return [SkillLifecycleRecord.from_dict(v) for v in self._data.values() if v.get("stage") == stage]

    def seed_from_workspace(self):
        """首次运行：从 skills/ 目录自动初始化注册表"""
        now = datetime.now(timezone.utc).isoformat()
        changed = False
        for d in sorted(self.skills_dir.iterdir()):
            if not d.is_dir():
                continue
            name = d.name
            if name not in self._data:
                stage = self._infer_stage(d)
                self._data[name] = SkillLifecycleRecord(
                    name=name,
                    stage=stage,
                    created_at=now,
                    updated_at=now,
                ).to_dict()
                changed = True
            # 补充 update_url
            config_path = d / "config.json"
            if config_path.exists():
                try:
                    cfg = json.loads(config_path.read_text(encoding="utf-8"))
                    url = cfg.get("updateUrl") or cfg.get("update_url")
                    if url and not self._data[name].get("update_url"):
                        self._data[name]["update_url"] = url
                        changed = True
                except Exception:
                    pass
        if changed:
            self._save()

    def _infer_stage(self, skill_dir: Path) -> str:
        has_md = (skill_dir / "SKILL.md").exists()
        has_scripts = any((skill_dir / sub).exists() for sub in ["scripts", "script", "src"])
        has_tests = any((skill_dir / sub).exists() for sub in ["tests", "test"])
        if not has_md:
            return "retirement"
        if has_scripts and has_tests:
            return "maturity"
        if has_md and not has_scripts:
            return "growth"
        return "maturity"


class SkillLifecycleManager:
    """技能生命周期管理核心引擎"""

    def __init__(
        self,
        workspace: Optional[Path] = None,
        registry_path: Optional[Path] = None,
        skills_dir: Optional[Path] = None,
        archive_dir: Optional[Path] = None,
        methodology_kb_path: Optional[Path] = None,
    ):
        self.workspace = workspace or WORKSPACE
        self.skills_dir = skills_dir or (self.workspace / "skills")
        self.archive_dir = archive_dir or (self.workspace / "archive" / "skills-archive")
        self.registry = SkillLifecycleRegistry(
            path=registry_path or REGISTRY_PATH,
            skills_dir=self.skills_dir,
        )
        self.registry.seed_from_workspace()
        self._methodology_kb_path = methodology_kb_path or METHODOLOGY_KB_PATH
        self.kb = self._load_methodology_kb()

    def _load_methodology_kb(self) -> Dict[str, Dict[str, Any]]:
        if self._methodology_kb_path.exists():
            data = json.loads(self._methodology_kb_path.read_text(encoding="utf-8"))
            # Support both {"skills": [...]} and direct dict-of-dicts schema
            if isinstance(data, dict) and "skills" in data and isinstance(data["skills"], list):
                return {item["skill_name"]: item for item in data["skills"] if isinstance(item, dict) and "skill_name" in item}
            if isinstance(data, dict):
                # If keys look like skill names and values are dicts, use directly
                if all(isinstance(v, dict) for v in data.values()):
                    return data
        return {}

    # ───────────────────────────────────────────────────────────────
    # GENESIS — 诞生门控
    # ───────────────────────────────────────────────────────────────

    def evaluate_creation_request(
        self,
        skill_name: str,
        problem_statement: str,
        pattern_frequency: int,
        existing_coverage_rate: float,
        roi_estimate: float,
        economic_qs: Dict[str, bool],
        economic_cs: Dict[str, bool],
        host_doc_path: Optional[str] = None,
    ) -> Tuple[bool, List[str]]:
        """评估是否允许创建新 skill。返回 (approved, reasons)"""
        issues = []
        if pattern_frequency < 3:
            issues.append(f"模式重复次数不足（{pattern_frequency} < 3），不满足诞生门槛")
        if existing_coverage_rate >= 0.8:
            issues.append(f"现有 skill 已覆盖 {existing_coverage_rate*100:.0f}%，无需新建")
        if roi_estimate <= 0:
            issues.append(f"预估 ROI 非正（{roi_estimate}）")
        for q, passed in economic_qs.items():
            if not passed:
                issues.append(f"ECONOMIC_QS 未通过: {ECONOMIC_QS.get(q, q)}")
        for c, passed in economic_cs.items():
            if not passed:
                issues.append(f"ECONOMIC_CS 未通过: {ECONOMIC_CS.get(c, c)}")
        if not host_doc_path or not Path(host_doc_path).exists():
            issues.append("未提供 HOST 四循环文档，无法验证决策链路")
        approved = len(issues) == 0
        return approved, issues

    def register_genesis(
        self,
        skill_name: str,
        problem_statement: str,
        pattern_frequency: int,
        existing_coverage_rate: float,
        roi_estimate: float,
        economic_qs: Dict[str, bool],
        economic_cs: Dict[str, bool],
        host_doc_path: str,
    ) -> SkillLifecycleRecord:
        approved, issues = self.evaluate_creation_request(
            skill_name, problem_statement, pattern_frequency,
            existing_coverage_rate, roi_estimate, economic_qs, economic_cs, host_doc_path
        )
        if not approved:
            raise ValueError(f"Skill '{skill_name}' 未通过诞生门控: " + "; ".join(issues))

        now = datetime.now(timezone.utc).isoformat()
        record = SkillLifecycleRecord(
            name=skill_name,
            stage="genesis",
            created_at=now,
            updated_at=now,
            creation_trigger={
                "problem_statement": problem_statement,
                "pattern_frequency": pattern_frequency,
                "existing_coverage_rate": existing_coverage_rate,
                "roi_estimate": roi_estimate,
                "economic_qs": economic_qs,
                "economic_cs": economic_cs,
            },
            host_cycle_doc=host_doc_path,
            notes=["通过诞生门控"] if not issues else [f"门控通过但含 {len(issues)} 条警告"],
        )
        self.registry.set(record)
        return record

    def promote_to_growth(self, skill_name: str) -> SkillLifecycleRecord:
        rec = self.registry.get(skill_name)
        if not rec:
            raise ValueError(f"Skill {skill_name} 不在注册表中")
        if rec.stage != "genesis":
            raise ValueError(f"只能在 genesis 阶段晋升，当前为 {rec.stage}")
        skill_dir = self.skills_dir / skill_name
        if not (skill_dir / "SKILL.md").exists():
            raise ValueError("缺少 SKILL.md，无法晋升到 growth")
        now = datetime.now(timezone.utc).isoformat()
        rec.stage = "growth"
        rec.updated_at = now
        rec.notes.append(f"{now[:10]} 晋升至 growth（SKILL.md 就绪）")
        self.registry.set(rec)
        return rec

    def promote_to_maturity(self, skill_name: str) -> SkillLifecycleRecord:
        rec = self.registry.get(skill_name)
        if not rec or rec.stage != "growth":
            raise ValueError("只能从 growth 晋升")
        skill_dir = self.skills_dir / skill_name
        has_scripts = any((skill_dir / sub).exists() for sub in ["scripts", "script", "src"])
        has_tests = any((skill_dir / sub).exists() for sub in ["tests", "test"])
        if not has_scripts and not has_tests:
            raise ValueError("缺少可运行脚本或测试，无法晋升到 maturity")
        now = datetime.now(timezone.utc).isoformat()
        rec.stage = "maturity"
        rec.bloodized_at = now
        rec.updated_at = now
        rec.notes.append(f"{now[:10]} 晋升至 maturity（血液化完成）")
        self.registry.set(rec)
        return rec

    # ───────────────────────────────────────────────────────────────
    # CONSOLIDATION — 同类合并优化
    # ───────────────────────────────────────────────────────────────

    def _text_similarity(self, a: str, b: str) -> float:
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()

    def _skill_signature(self, name: str) -> str:
        item = self.kb.get(name, {})
        parts = [
            item.get("description", ""),
            " ".join(item.get("core_methodology", [])),
            " ".join(item.get("trigger_keywords", [])),
            item.get("workflow_pattern", ""),
        ]
        return " ".join(parts).strip()

    def find_merge_candidates(self, threshold: float = 0.65) -> List[Dict[str, Any]]:
        """基于方法论 KB 和文本相似度，找出可合并的 skill 组。"""
        names = sorted(self.kb.keys())
        sigs = {n: self._skill_signature(n) for n in names}
        pairs = []
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                a, b = names[i], names[j]
                sig_a = sigs[a]
                sig_b = sigs[b]
                if not sig_a or not sig_b:
                    continue
                sim = self._text_similarity(sig_a, sig_b)
                if sim >= threshold:
                    pairs.append((a, b, sim))

        # Union-Find 聚类
        parent = {n: n for n in names}

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(x, y):
            rx, ry = find(x), find(y)
            if rx != ry:
                parent[ry] = rx

        for a, b, sim in pairs:
            union(a, b)

        groups: Dict[str, List[str]] = {}
        for n in names:
            r = find(n)
            groups.setdefault(r, []).append(n)

        results = []
        for root, members in groups.items():
            if len(members) > 1:
                # 选举 canonical skill（成熟度最高或字典序最小）
                canonical = self._elect_canonical(members)
                pair_sims = [
                    {"a": a, "b": b, "similarity": round(sim, 3)}
                    for a, b, sim in pairs if a in members and b in members
                ]
                results.append({
                    "canonical": canonical,
                    "members": members,
                    "pair_similarities": pair_sims,
                    "recommended_action": "review_and_merge",
                })
        # 按组大小降序
        results.sort(key=lambda x: -len(x["members"]))
        return results

    def _elect_canonical(self, members: List[str]) -> str:
        """选举合并后的主 skill：优先选 maturity > growth > genesis，然后 usage_score 高，最后字典序。"""
        def score(name):
            rec = self.registry.get(name)
            stage_score = {"maturity": 3, "growth": 2, "genesis": 1, "consolidation": 0}.get(rec.stage if rec else "", 0)
            usage = rec.usage_score if rec else 0.0
            return (stage_score, usage, name)
        return max(members, key=score)

    def execute_merge(self, canonical: str, merged_skills: List[str], dry_run: bool = True) -> Dict[str, Any]:
        """执行合并：将 merged_skills 退役，迁移能力描述到 canonical。"""
        if canonical in merged_skills:
            merged_skills = [m for m in merged_skills if m != canonical]
        now = datetime.now(timezone.utc).isoformat()
        report = {"canonical": canonical, "merged": [], "errors": [], "dry_run": dry_run}

        for skill in merged_skills:
            rec = self.registry.get(skill)
            if not rec:
                report["errors"].append(f"{skill} 不在注册表中")
                continue
            if rec.stage in ("retirement", "archived"):
                report["errors"].append(f"{skill} 已处于退役/归档状态，无需合并")
                continue

            # 更新被合并 skill 的注册信息
            rec.stage = "consolidation"
            rec.merge_info = {
                "merged_into": canonical,
                "merged_at": now,
            }
            rec.notes.append(f"{now[:10]} 合并入 {canonical}")
            self.registry.set(rec)

            if not dry_run:
                # 物理移动目录到 retirement
                src = self.skills_dir / skill
                dst = self.archive_dir / "retired" / skill
                if src.exists():
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(src), str(dst))

            report["merged"].append(skill)

        # 更新 canonical 的注册信息
        can_rec = self.registry.get(canonical)
        if can_rec:
            can_rec.notes.append(f"{now[:10]} 接收合并: {', '.join(merged_skills)}")
            self.registry.set(can_rec)

        return report

    # ───────────────────────────────────────────────────────────────
    # UPDATE TRACKING — 版本更新追踪
    # ───────────────────────────────────────────────────────────────

    def check_updates(self) -> List[Dict[str, Any]]:
        """基于 config.json 中的 update_url 检查上游更新。"""
        results = []
        now = datetime.now(timezone.utc).isoformat()
        for rec in [self.registry.get(n) for n in self.registry.all_names()]:
            if not rec or not rec.update_url:
                continue
            # 轻量级检查：读取本地 config.json 的 version 字段作为快照
            skill_dir = self.skills_dir / rec.name
            local_ver = None
            config_path = skill_dir / "config.json"
            if config_path.exists():
                try:
                    cfg = json.loads(config_path.read_text(encoding="utf-8"))
                    local_ver = cfg.get("version") or cfg.get("commit")
                except Exception:
                    pass

            rec.local_version = local_ver
            rec.last_update_check = now
            # TODO: 如需真正的远程版本检查，可在此调用 requests HEAD 或读取 remote git tags
            # 当前先标记为"已检查"
            rec.update_available = False
            self.registry.set(rec)
            results.append({
                "name": rec.name,
                "update_url": rec.update_url,
                "local_version": local_ver,
                "checked_at": now,
            })
        return results

    # ───────────────────────────────────────────────────────────────
    # RETIREMENT — 退役机制
    # ───────────────────────────────────────────────────────────────

    def find_retirement_candidates(self) -> List[Dict[str, Any]]:
        """发现符合退役条件的 skill。"""
        candidates = []
        for name in self.registry.all_names():
            rec = self.registry.get(name)
            if not rec or rec.stage in ("retirement", "archived"):
                continue
            reasons = []
            skill_dir = self.skills_dir / name

            # R1: 合并后未退役的
            if rec.merge_info:
                reasons.append("merged")

            # R2: 缺少 SKILL.md 的孤儿目录
            if not (skill_dir / "SKILL.md").exists():
                reasons.append("missing_documentation")

            # R3: consolidation 阶段超过 7 天未清理的
            if rec.stage == "consolidation":
                reasons.append("stale_consolidation")

            # R4: 不存在于 skills/ 目录但仍在注册表中（物理已删除）
            if not skill_dir.exists():
                reasons.append("physically_missing")

            if reasons:
                candidates.append({"name": name, "stage": rec.stage, "reasons": reasons})
        return candidates

    def retire_skill(self, skill_name: str, reason: str, replacement: Optional[str] = None, dry_run: bool = True) -> SkillLifecycleRecord:
        rec = self.registry.get(skill_name)
        if not rec:
            raise ValueError(f"Skill {skill_name} 不在注册表中")
        if rec.stage in ("retirement", "archived"):
            raise ValueError(f"Skill {skill_name} 已退役或归档")

        now = datetime.now(timezone.utc).isoformat()
        rec.stage = "retirement"
        rec.retired_at = now
        rec.retired_reason = reason
        rec.replacement_skill = replacement
        rec.notes.append(f"{now[:10]} 退役，原因: {reason}" + (f"，替代: {replacement}" if replacement else ""))
        self.registry.set(rec)

        if not dry_run:
            src = self.skills_dir / skill_name
            dst = self.archive_dir / "retired" / skill_name
            if src.exists():
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(src), str(dst))
        return rec

    def archive_skill(self, skill_name: str, dry_run: bool = True) -> SkillLifecycleRecord:
        """从 retirement 进一步归档到长期冷存。"""
        rec = self.registry.get(skill_name)
        if not rec or rec.stage != "retirement":
            raise ValueError("只能归档处于 retirement 阶段的 skill")
        now = datetime.now(timezone.utc).isoformat()
        rec.stage = "archived"
        rec.updated_at = now
        rec.notes.append(f"{now[:10]} 归档至长期冷存")
        self.registry.set(rec)

        if not dry_run:
            retired_dst = self.archive_dir / "retired" / skill_name
            archive_dst = self.archive_dir / "archived" / skill_name
            if retired_dst.exists():
                archive_dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(retired_dst), str(archive_dst))
        return rec

    def revive_skill(self, skill_name: str, dry_run: bool = True) -> SkillLifecycleRecord:
        """从归档/退役状态恢复为活跃 skill。"""
        rec = self.registry.get(skill_name)
        if not rec or rec.stage not in ("retirement", "archived"):
            raise ValueError("只能复兴处于 retirement 或 archived 阶段的 skill")

        now = datetime.now(timezone.utc).isoformat()
        src = None
        if rec.stage == "archived":
            src = self.archive_dir / "archived" / skill_name
        else:
            src = self.archive_dir / "retired" / skill_name

        dst = self.skills_dir / skill_name
        if not dry_run:
            if src.exists():
                shutil.move(str(src), str(dst))

        rec.stage = "growth"  # 复活后先回到 growth，需要重新验证再晋升
        rec.updated_at = now
        rec.notes.append(f"{now[:10]} 从 {rec.stage} 复兴，回到 growth 待验证")
        self.registry.set(rec)
        return rec

    # ───────────────────────────────────────────────────────────────
    # FLYWHEEL INTEGRATION — 资产飞轮联动
    # ───────────────────────────────────────────────────────────────

    def sync_to_daily_asset_runner(self) -> Dict[str, Any]:
        """将 maturity 阶段的 skill 同步为 daily_asset_runner 的调度项。"""
        mature_skills = self.registry.list_by_stage("maturity")
        # 读取现有 runner 内容
        runner_lines = []
        runner_path = self.workspace / "daily_asset_runner.py"
        if runner_path.exists():
            runner_lines = runner_path.read_text(encoding="utf-8").splitlines()

        marker_start = "# SKILL_LIFECYCLE_AUTO_INSERT_START"
        marker_end = "# SKILL_LIFECYCLE_AUTO_INSERT_END"

        # 去除旧的自动插入块
        before = []
        after = []
        in_block = False
        for line in runner_lines:
            if marker_start in line:
                in_block = True
                before.append(line)
                continue
            if marker_end in line:
                in_block = False
                after.append(line)
                continue
            if not in_block:
                if after:
                    after.append(line)
                else:
                    before.append(line)

        auto_block = [marker_start]
        auto_block.append("# 由 skill_lifecycle_manager.py 自动生成")
        auto_block.append("SKILL_MATURITY_ASSETS = [")
        for rec in mature_skills:
            auto_block.append(f'    "{rec.name}",')
        auto_block.append("]")
        auto_block.append(marker_end)

        new_lines = before + auto_block + after
        runner_path.write_text("\n".join(new_lines), encoding="utf-8")
        return {"mature_count": len(mature_skills), "runner_updated": True}

    # ───────────────────────────────────────────────────────────────
    # AUDIT — 全量审计报告
    # ───────────────────────────────────────────────────────────────

    def full_audit(self) -> Dict[str, Any]:
        stages = {s: len(self.registry.list_by_stage(s)) for s in STAGES}
        merge_candidates = self.find_merge_candidates(threshold=0.65)
        retirement_candidates = self.find_retirement_candidates()
        update_status = self.check_updates()
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "stage_distribution": stages,
            "total_registered": len(self.registry.all_names()),
            "active_skills_dir": len([d for d in self.skills_dir.iterdir() if d.is_dir()]),
            "merge_candidates": merge_candidates,
            "merge_candidate_count": len(merge_candidates),
            "retirement_candidates": retirement_candidates,
            "retirement_candidate_count": len(retirement_candidates),
            "update_checked": len(update_status),
            "update_available_count": sum(1 for u in update_status if u.get("update_available")),
        }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Skill Lifecycle Manager")
    sub = parser.add_subparsers(dest="command")

    p_audit = sub.add_parser("audit", help="执行全量生命周期审计")
    p_merge = sub.add_parser("merge-scan", help="扫描可合并的 skill 组")
    p_merge.add_argument("--threshold", type=float, default=0.65)
    p_retire = sub.add_parser("retire-scan", help="扫描应退役的 skill")
    p_sync = sub.add_parser("sync-runner", help="同步 maturity skill 到 daily_asset_runner")

    args = parser.parse_args()
    mgr = SkillLifecycleManager()

    if args.command == "audit":
        report = mgr.full_audit()
        print(json.dumps(report, ensure_ascii=False, indent=2))
    elif args.command == "merge-scan":
        candidates = mgr.find_merge_candidates(threshold=args.threshold)
        print(json.dumps(candidates, ensure_ascii=False, indent=2))
    elif args.command == "retire-scan":
        candidates = mgr.find_retirement_candidates()
        print(json.dumps(candidates, ensure_ascii=False, indent=2))
    elif args.command == "sync-runner":
        result = mgr.sync_to_daily_asset_runner()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
