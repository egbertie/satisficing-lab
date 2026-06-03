#!/usr/bin/env python3
"""
Skill 瘦身批量退役脚本 - Phase 1
目标：将 skills/ 目录从 511 降至 250 以下
策略：基于命名规则和用户历史决策，批量标记并物理移动重复/非核心 skill
"""
import json
import shutil
from pathlib import Path
from datetime import datetime, timezone

WORKSPACE = Path("/root/.openclaw/workspace")
SKILLS_DIR = WORKSPACE / "skills"
ARCHIVE_DIR = WORKSPACE / "archive" / "skills-archive" / "retired"
REGISTRY_PATH = WORKSPACE / "skill_lifecycle_registry.json"

ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

# 读取注册表
registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8")) if REGISTRY_PATH.exists() else {}

# 退役规则分组：每组保留 canonical，其余退役
RETIREMENT_RULES = {
    "deep-research": {
        "keep": ["deep-research", "academic-deep-research", "agent-reach"],
        "pattern": ["deep-research", "deepresearch", "researcher", "research-orchestrator", "research-cli"],
    },
    "agent-browser": {
        "keep": ["agent-browser-clawdbot"],
        "pattern": ["agent-browser"],
    },
    "advisor-board": {
        "keep": ["board-meeting", "virtual-board-of-advisors", "boardroom-advisor"],
        "pattern": ["advisor", "board", "c-level", "ceo", "cto", "cmo", "founder-coach"],
    },
    "interview": {
        "keep": ["interview-simulator"],
        "pattern": ["interview"],
    },
    "writing-content": {
        "keep": ["react-email", "marketing-designer"],
        "pattern": ["writing-assistant", "content-creator", "copywriter", "blog-writer"],
    },
    "game-duplicate": {
        "keep": ["game", "defipoly", "1001night-stories"],
        "pattern": ["game-designer", "moltimon", "game-cog"],
    },
    "health-check-duplicate": {
        "keep": ["healthcheck"],
        "pattern": ["health-check", "security-audit", "vulnerability-scan"],
    },
    "news-info-redundant": {
        "keep": ["tencent-news", "ai-news-zh"],
        "pattern": ["news-collector", "news-aggregator", "daily-news"],
    },
    "email-redundant": {
        "keep": ["react-email"],
        "pattern": ["email-sender", "outreach-assistant", "cold-email"],
    },
    "self-improving-redundant": {
        "keep": ["self-improving-agent"],
        "pattern": ["self-improving", "auto-updater", "agent-optimizer"],
    },
}

# 明确退役黑名单（用户未使用且功能重复）
BLACKLIST_KEYWORDS = [
    # 纯外语/地区不可用
    "pesquisa-profunda", "deling-knowledge", "ai-meeting-room",
    # 概念性/非当前阶段
    "achurch", "agentarxiv", "ai-familiar", "ai-proposal-generator",
    # 外围工具
    "yahoo-finance", "youtube-full", "youtube-watcher",
    # 法律和税务重复
    "zhang-trade-secret", "zhang-trade-compliance", "zhang-intl-tax-law",
    "zhang-gdpr-compliance", "zhang-customs-law", "zhang-civil-litigation",
    "zhang-doc-automation",
    # WPS 重复
    "wps-office-automation-skill",
    # 其他已知功能重复
    "worry-list-manager", "worker-swarm-tracker", "worker-orchestrator",
    "zero-vacancy-executor", "zero-idle-enforcer",
    # 决策引擎重复（保留 adi-decision-engine 和 satisficing_decision_engine）
    "decision-support-system", "decision-engine-pro",
    # PDF/文档处理重复
    "pdf-summarizer", "docx-processor", "markdown-converter-skill",
]

all_skills = {p.name for p in SKILLS_DIR.iterdir() if p.is_dir()}
retire_candidates = set()
retire_reasons = {}

now = datetime.now(timezone.utc).isoformat()

# 规则1：按组退役
for group_name, rule in RETIREMENT_RULES.items():
    keep_set = set(rule["keep"])
    matched = set()
    for skill in all_skills:
        if skill in keep_set:
            continue
        for pat in rule["pattern"]:
            if pat.lower() in skill.lower():
                matched.add(skill)
                break
    for skill in matched:
        if skill not in retire_candidates:
            retire_candidates.add(skill)
            retire_reasons[skill] = f"grouped_retirement:{group_name}"

# 规则2：黑名单
for skill in all_skills:
    for kw in BLACKLIST_KEYWORDS:
        if kw.lower() in skill.lower():
            if skill not in retire_candidates:
                retire_candidates.add(skill)
                retire_reasons[skill] = "blacklist_keyword"

# 规则3：孤儿目录（无 SKILL.md）
for skill in all_skills:
    if not (SKILLS_DIR / skill / "SKILL.md").exists():
        retire_candidates.add(skill)
        retire_reasons[skill] = "missing_skill_md"

# 规则4：备份/旧版本目录
backup_patterns = ["-bak-", "-backup-", "-old-", "-v0-", "-test-"]
for skill in all_skills:
    for pat in backup_patterns:
        if pat in skill.lower():
            retire_candidates.add(skill)
            retire_reasons[skill] = "backup_or_old_version"

# 排除已被退役的
already_retired = {k for k, v in registry.items() if v.get("stage") in ("retirement", "archived")}
retire_candidates = retire_candidates - already_retired

# 确保 canonical skill 不被误伤
all_canonical = set()
for rule in RETIREMENT_RULES.values():
    all_canonical.update(rule["keep"])
retire_candidates = retire_candidates - all_canonical

print(f"Total skills: {len(all_skills)}")
print(f"Already retired: {len(already_retired)}")
print(f"New retirement candidates: {len(retire_candidates)}")
print(f"Projected active after retirement: {len(all_skills) - len(retire_candidates)}")
print("\nTop 20 candidates:")
for s in sorted(retire_candidates)[:20]:
    print(f"  - {s} ({retire_reasons[s]})")

# 写入退役候选清单
report = {
    "timestamp": now,
    "total_skills": len(all_skills),
    "already_retired": len(already_retired),
    "candidates_count": len(retire_candidates),
    "projected_active": len(all_skills) - len(retire_candidates),
    "candidates": [{"name": s, "reason": retire_reasons[s]} for s in sorted(retire_candidates)],
}
report_path = WORKSPACE / "tmp" / "skill_retirement_candidates_phase1.json"
report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\nReport saved to: {report_path}")

# 物理执行退役（dry_run=False）
moved = 0
errors = []
for skill in sorted(retire_candidates):
    src = SKILLS_DIR / skill
    dst = ARCHIVE_DIR / skill
    if src.exists():
        try:
            if dst.exists():
                shutil.rmtree(dst)
            shutil.move(str(src), str(dst))
            moved += 1
            # 更新注册表
            if skill in registry:
                registry[skill]["stage"] = "retirement"
                registry[skill]["retired_at"] = now
                registry[skill]["retired_reason"] = retire_reasons[skill]
        except Exception as e:
            errors.append(f"{skill}: {e}")

if registry:
    REGISTRY_PATH.write_text(json.dumps(registry, ensure_ascii=False, indent=2), encoding="utf-8")

print(f"\nPhysically moved: {moved}")
print(f"Errors: {len(errors)}")
if errors[:5]:
    for e in errors[:5]:
        print(f"  ERROR: {e}")

# 最终统计
final_active = len([p for p in SKILLS_DIR.iterdir() if p.is_dir()])
print(f"\nFinal active skills directory count: {final_active}")
print(f"Target < 250: {'✅ MET' if final_active < 250 else '❌ NOT MET'}")
