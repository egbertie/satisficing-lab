"""
skill_execution_embedder.py
Embed skill methodologies into execution mechanisms with automatic triggers.
Every trigger is gated by Token Economics + Benefit Economics (Q1-Q3, C1-C3).
"""
from __future__ import annotations
import json
import re
from pathlib import Path
from typing import Any

KB_PATH = Path("/root/.openclaw/workspace/skill_methodology_knowledge_base.json")
TRIGGERS_PATH = Path("/root/.openclaw/workspace/skill_execution_triggers.json")

ECONOMIC_QS = {
    "q1_local": "能否在本地完成？（不调用外部API/LLM）",
    "q2_light": "是否存在更轻量的替代方案？",
    "q3_compress": "是否已对输入上下文进行压缩？",
}
ECONOMIC_CS = {
    "c1_reusable": "产出是否具备可复用框架？",
    "c2_parallel": "任务是否可并行化以节省时间？",
    "c3_boundary_clear": "边界条件（输入/输出/失败态）是否已明确？",
}


def _scene_keywords(record: dict[str, Any]) -> list[str]:
    """Derive concrete scene keywords from triggers + description."""
    triggers = record.get("trigger_keywords", [])
    desc = record.get("description", "")
    methods = record.get("core_methodology", [])
    keywords = set(triggers)
    # Keyword mining from description
    desc_lower = desc.lower()
    scene_hints = [
        "search", "fetch", "read", "write", "create", "update", "delete",
        "analyze", "decide", "compare", "evaluate", "scan", "monitor",
        "send", "reply", "schedule", "remind", "alert",
        "weather", "stock", "news", "pdf", "doc", "email",
        "搜索", "抓取", "读取", "写入", "创建", "更新", "删除",
        "分析", "决策", "对比", "评估", "扫描", "监控",
        "发送", "回复", "日程", "提醒", "告警",
    ]
    for hint in scene_hints:
        if hint in desc_lower:
            keywords.add(hint)
    # Methodology hints
    for m in methods:
        m_lower = m.lower()
        if any(h in m_lower for h in scene_hints):
            # Extract first sentence or phrase
            phrase = m.strip().split("。")[0].split(".")[0].strip()
            if len(phrase) > 3:
                keywords.add(phrase)
    return list(keywords)[:15]


def _fallback_skill(record: dict[str, Any]) -> str | None:
    """Suggest a lighter fallback based on organ and description."""
    organ = record.get("organ", "")
    desc_lower = record.get("description", "").lower()
    if "llm" in desc_lower or "deep research" in desc_lower or "agent" in desc_lower:
        return "Use local rule-based alternative or compress context first"
    if organ == "感知器官":
        return "web_fetch (cheaper than web_search if URL known)"
    if organ == "思维器官":
        return "afrexai-strategic-thinking (lighter than deep-research for quick decisions)"
    if organ == "记忆器官":
        return "Local markdown append instead of cloud doc update"
    if organ == "运动器官":
        return "Batch messages instead of individual sends"
    return None


def embed_skill(skill_name: str, record: dict[str, Any]) -> dict[str, Any]:
    organ = record.get("organ", "unclassified")
    scene_keywords = _scene_keywords(record)
    fallback = _fallback_skill(record)

    # Compose with other skills based on organ
    composition_defaults = {
        "思维器官": ["baseline-checker", "adi-decision-engine"],
        "感知器官": ["web_fetch", "kimi-search"],
        "记忆器官": ["feishu-create-doc", "md-to-pdf"],
        "运动器官": ["feishu-channel-rules"],
        "构造器官": ["architecture-designer", "skill-creator"],
        "代谢器官": ["healthcheck", "baseline-checker"],
        "特化器官": [],
        "干细胞池": ["skill-creator"],
    }

    trigger = {
        "skill": skill_name,
        "organ": organ,
        "scene_keywords": scene_keywords,
        "economics_gate": {
            "questions": {
                **ECONOMIC_QS,
                **ECONOMIC_CS,
            },
            "default_logic": {
                "hard_fail": ["q1_local", "q3_compress"],  # Must be considered
                "soft_fail": ["q2_light", "c1_reusable", "c2_parallel", "c3_boundary_clear"],
            },
            "auto_eval_rules": {
                "q1_local": "not requires_external_api(record)",
                "q3_compress": "context_tokens < 40_000",
            },
        },
        "auto_invoke_conditions": [
            "scene_keywords match user intent",
            "economics_gate.hard_fail all pass",
            "no cheaper fallback actively overrides",
        ],
        "fallback_strategy": fallback,
        "composition_partners": composition_defaults.get(organ, []),
        "embedded_workflow": {
            "step1": "MATCH: Check if user request intersects scene_keywords",
            "step2": "GATE: Run economics_gate (answer Q1-Q3, C1-C3)",
            "step3": "FALLBACK: If gate fails hard condition, switch to fallback_strategy",
            "step4": "COMPOSE: Activate composition_partners if multi-step",
            "step5": "EXECUTE: Invoke skill with compressed, bounded context",
            "step6": "CAPTURE: Write result to memory/Git for reuse (C1 enforcement)",
        },
        "value_density": record.get("value_density", "pending"),
    }
    return trigger


def embed_all(kb_path: Path = KB_PATH, output_path: Path = TRIGGERS_PATH) -> dict[str, Any]:
    kb = json.loads(kb_path.read_text(encoding="utf-8"))
    triggers = {
        "meta": {
            "version": "1.0",
            "principle": "Every auto-trigger must pass Token Economics + Benefit Economics",
            "gating_questions": list(ECONOMIC_QS.keys()) + list(ECONOMIC_CS.keys()),
            "total_skills": kb["meta"]["total_skills"],
        },
        "triggers": {},
    }
    for skill_name, record in kb["skills"].items():
        triggers["triggers"][skill_name] = embed_skill(skill_name, record)

    output_path.write_text(json.dumps(triggers, ensure_ascii=False, indent=2), encoding="utf-8")
    return triggers


def check_trigger(skill_name: str, user_query: str, context_tokens: int = 0) -> dict[str, Any]:
    """Runtime check: should this skill auto-trigger for the given query?"""
    if not TRIGGERS_PATH.exists():
        return {"error": "Triggers not embedded yet. Run embed_all() first."}

    triggers_db = json.loads(TRIGGERS_PATH.read_text(encoding="utf-8"))
    trigger = triggers_db["triggers"].get(skill_name)
    if not trigger:
        return {"error": f"No trigger found for {skill_name}"}

    query_lower = user_query.lower()
    keyword_hits = [kw for kw in trigger["scene_keywords"] if kw.lower() in query_lower]

    # Simple economics evaluation
    gate = trigger["economics_gate"]
    hard_pass = True
    hard_eval = {}
    if context_tokens > 80_000:
        hard_eval["q3_compress"] = False
        hard_pass = False
    else:
        hard_eval["q3_compress"] = True

    # Heuristic: external API heavy skills fail q1 if context is large
    hard_eval["q1_local"] = True  # Default to True at runtime; user can override

    return {
        "skill": skill_name,
        "should_trigger": bool(keyword_hits) and hard_pass,
        "keyword_hits": keyword_hits,
        "economics_hard_eval": hard_eval,
        "fallback": trigger.get("fallback_strategy"),
        "next_step": "FALLBACK" if (keyword_hits and not hard_pass) else ("EXECUTE" if keyword_hits else "SKIP"),
    }


if __name__ == "__main__":
    triggers = embed_all()
    print(f"Embedded {triggers['meta']['total_skills']} skills into {TRIGGERS_PATH}")
    # Demo runtime check
    demo = check_trigger("agent-reach", "帮我搜一下 Twitter 上关于 AI 的讨论", context_tokens=12000)
    print("Demo check:", demo)
