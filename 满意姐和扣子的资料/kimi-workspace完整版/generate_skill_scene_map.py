#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
195 eligible skills → 12-scene reflex matrix 实战映射生成器

读取:
  - /tmp/skills_by_organ.json (195 skills 分类)
  - cognitive_organ_reflex_matrix.py 中的 SCENARIO_MATRIX

输出:
  - /tmp/skill_scene_practical_map.json (结构化映射)
  - A-manyige/项目版本/V1.6/中间产出/195技能-12场景实战映射-V1.0-20260409.md

映射逻辑 (规则引擎, 零 LLM 调用):
  1. 按器官匹配: skill 所属器官 = 场景激活器官 → 基础关联
  2. 按关键词匹配: skill description 中的 trigger 关键词与场景 trigger 信号重叠 → 增强关联
  3. 每个场景选取 top-10 高频/高相关 skills 作为"核心武器库"
"""

import json
import re
import sys
from pathlib import Path
from collections import defaultdict

WORKSPACE = Path("/root/.openclaw/workspace")
OUTPUT_MD = WORKSPACE / "A-manyige" / "项目版本" / "V1.6" / "中间产出" / "195技能-12场景实战映射-V1.0-20260409.md"
OUTPUT_JSON = Path("/tmp/skill_scene_practical_map.json")

SCENE_KEYWORDS = {
    "scene_01_file_received": ["file", "docx", "pdf", "md", "image", "extract", "parse", "batch", "process"],
    "scene_02_open_question": ["search", "research", "find", "query", "answer", "explain"],
    "scene_03_review_idea": ["review", "decision", "strategy", "risk", "analyze", "evaluate", "critique"],
    "scene_04_schedule": ["calendar", "schedule", "meeting", "time", "event", "busy", "free"],
    "scene_05_task_todo": ["task", "todo", "okr", "goal", "track", "remind", "deadline"],
    "scene_06_send_message": ["message", "send", "notify", "chat", "im", "communication"],
    "scene_07_research_report": ["research", "report", "pdf", "daily", "intelligence", "academic"],
    "scene_08_finance": ["stock", "finance", "invest", "fundamental", "competitor", "market"],
    "scene_09_create_skill": ["skill", "create", "build", "tool", "architecture", "design", "code"],
    "scene_10_heartbeat": ["baseline", "health", "check", "monitor", "system", "cron", "heartbeat"],
    "scene_11_emotion": ["emotion", "memory", "familiar", "meditation", "spiritual", "personal"],
    "scene_12_decision_help": ["decision", "choose", "select", "rank", "mcda", "satisficing", "uncertainty"],
}

sys.path.insert(0, str(WORKSPACE))
mod = __import__("cognitive_organ_reflex_matrix")
SCENARIO_MATRIX = getattr(mod, "SCENARIO_MATRIX", {})

skills_data = json.loads(Path("/tmp/skills_by_organ.json").read_text(encoding="utf-8"))
organs = skills_data.get("organs", {})

# 扁平化 skill 列表
all_skills = []
for organ_name, skill_list in organs.items():
    for skill in skill_list:
        skill["organ"] = organ_name
        all_skills.append(skill)

# 计算每个 skill 与每个场景的关联度
def score_skill_scene(skill, scene_id):
    score = 0
    organ = skill.get("organ", "")
    desc = (skill.get("description", "") + " " + skill.get("name", "")).lower()

    # 1. 器官匹配
    scene_organs = SCENARIO_MATRIX.get(scene_id, {}).get("organs", [])
    if organ in scene_organs:
        score += 2.0

    # 2. 关键词匹配
    keywords = SCENE_KEYWORDS.get(scene_id, [])
    matched = sum(1 for kw in keywords if kw.lower() in desc)
    score += matched * 1.5

    # 3. 名称直接包含场景关键词加分
    name = skill.get("name", "").lower()
    if scene_id == "scene_08_finance" and any(x in name for x in ["finance", "stock", "fundamental", "competitor"]):
        score += 3
    if scene_id == "scene_12_decision_help" and any(x in name for x in ["decision", "satisfic", "mcda"]):
        score += 3
    if scene_id == "scene_10_heartbeat" and any(x in name for x in ["healthcheck", "baseline", "monitor"]):
        score += 3
    if scene_id == "scene_04_schedule" and any(x in name for x in ["calendar", "schedule", "meeting"]):
        score += 3
    if scene_id == "scene_05_task_todo" and any(x in name for x in ["task", "todo", "okr"]):
        score += 3

    return score

# 构建映射
scene_map = {}
for scene_id in SCENARIO_MATRIX:
    scored = []
    for skill in all_skills:
        s = score_skill_scene(skill, scene_id)
        if s > 0:
            scored.append({
                "name": skill["name"],
                "organ": skill["organ"],
                "score": round(s, 1),
            })
    scored.sort(key=lambda x: -x["score"])
    scene_map[scene_id] = {
        "scene_name": SCENARIO_MATRIX[scene_id]["name"],
        "core_skills": scored[:10],
        "extended_skills": scored[10:20],
        "total_matched": len(scored),
    }

# 反向映射: skill -> 哪些场景最相关
skill_scene_reverse = defaultdict(list)
for scene_id, data in scene_map.items():
    for sk in data["core_skills"]:
        skill_scene_reverse[sk["name"]].append({"scene_id": scene_id, "scene_name": data["scene_name"], "score": sk["score"]})
    for sk in data["extended_skills"]:
        skill_scene_reverse[sk["name"]].append({"scene_id": scene_id, "scene_name": data["scene_name"], "score": sk["score"]})

# 输出 JSON
OUTPUT_JSON.write_text(json.dumps({
    "generated_at": "2026-04-09T18:15:00+08:00",
    "total_skills": len(all_skills),
    "scene_coverage": {k: v["total_matched"] for k, v in scene_map.items()},
    "scene_map": scene_map,
    "skill_scene_reverse": {k: sorted(v, key=lambda x: -x["score"])[:5] for k, v in skill_scene_reverse.items()},
}, ensure_ascii=False, indent=2), encoding="utf-8")

# 输出 Markdown
lines = [
    "---",
    "title: 195 eligible skills · 12场景条件反射矩阵 实战映射",
    "version: V1.0",
    "date: 2026-04-09",
    "source: /tmp/skills_by_organ.json + cognitive_organ_reflex_matrix.py",
    "generated_by: 规则引擎（零 LLM 调用）",
    "---",
    "",
    "# 195 eligible skills → 12场景实战映射",
    "",
    "> 本文件将 195 个 eligible skill 按规则引擎映射到 12 个核心触发场景，",
    "> 实现从'认知器官分类'到'实战条件反射'的跃迁。",
    "",
]

for scene_id, data in scene_map.items():
    lines.append(f"## {data['scene_name']} (`{scene_id}`)")
    lines.append(f"")
    lines.append(f"**场景触发信号**: {', '.join(SCENARIO_MATRIX[scene_id]['trigger'])}")
    lines.append(f"")
    lines.append(f"**核心武器库** (Top 10):")
    for sk in data["core_skills"]:
        lines.append(f"- `{sk['name']}` ({sk['organ']}) — 关联度 {sk['score']}")
    if data["extended_skills"]:
        lines.append(f"")
        lines.append(f"**扩展武器库** (Top 11-20):")
        for sk in data["extended_skills"]:
            lines.append(f"- `{sk['name']}` ({sk['organ']}) — 关联度 {sk['score']}")
    lines.append(f"")
    lines.append(f"*本场景共匹配 {data['total_matched']} 个 skill*")
    lines.append(f"")

lines.append("---")
lines.append("")
lines.append("# 附录：常用 skill 的推荐激活场景速查")
lines.append("")

# 选取比较有代表性的 skills 做反向速查
showcase = [
    "thinking-mentor", "adi-decision-engine", "feishu-calendar", "feishu-task",
    "kimi-search", "agent-reach", "stock-assistant", "skill-creator",
    "baseline-checker", "healthcheck", "ai-familiar", "satisficing_decision_engine",
]
for name in showcase:
    if name in skill_scene_reverse:
        scenes = skill_scene_reverse[name]
        lines.append(f"- `{name}` → " + ", ".join([f"{s['scene_name']}({s['score']})" for s in scenes[:3]]))

lines.append("")
lines.append("---")
lines.append("*映射逻辑：器官匹配(2.0) + 关键词匹配(1.5×词数) + 名称硬匹配(+3)*")

OUTPUT_MD.write_text("\n".join(lines), encoding="utf-8")

print(f"✅ JSON 输出: {OUTPUT_JSON}")
print(f"✅ Markdown 输出: {OUTPUT_MD}")
print(f"\n场景覆盖率统计:")
for scene_id, data in scene_map.items():
    print(f"  {scene_id}: {data['total_matched']} skills matched")
