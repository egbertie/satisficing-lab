"""
test_skill_execution_embedder.py
pytest for skill_execution_embedder.
"""
import json
from pathlib import Path

import skill_execution_embedder as see


def test_scene_keywords():
    record = {
        "trigger_keywords": ["weather query"],
        "description": "Get current weather and forecasts via wttr.in.",
        "core_methodology": ["Fetch remote data", "Pattern matching for locations"],
    }
    keywords = see._scene_keywords(record)
    assert "weather query" in keywords
    assert "weather" in keywords or any("weather" in k for k in keywords)


def test_fallback_skill_external():
    record = {"description": "Uses LLM deep research", "organ": "思维器官"}
    assert "compress context" in (see._fallback_skill(record) or "")


def test_fallback_skill_perception():
    record = {"description": "Search the web", "organ": "感知器官"}
    assert "web_fetch" in (see._fallback_skill(record) or "")


def test_embed_skill_structure(tmp_path: Path):
    record = {
        "skill_name": "test-skill",
        "description": "A test skill for demo.",
        "trigger_keywords": ["demo"],
        "core_methodology": ["Example methodology"],
        "organ": "思维器官",
        "value_density": "high",
    }
    trigger = see.embed_skill("test-skill", record)
    assert trigger["skill"] == "test-skill"
    assert trigger["organ"] == "思维器官"
    assert "economics_gate" in trigger
    assert "composition_partners" in trigger
    assert "embedded_workflow" in trigger


def test_embed_all(tmp_path: Path, monkeypatch):
    kb = {
        "meta": {"total_skills": 2},
        "skills": {
            "skill-a": {
                "description": "Skill A",
                "trigger_keywords": ["a"],
                "core_methodology": [],
                "organ": "感知器官",
            },
            "skill-b": {
                "description": "Skill B",
                "trigger_keywords": ["b"],
                "core_methodology": [],
                "organ": "记忆器官",
            },
        },
    }
    kb_path = tmp_path / "kb.json"
    kb_path.write_text(json.dumps(kb), encoding="utf-8")
    out_path = tmp_path / "triggers.json"

    monkeypatch.setattr(see, "KB_PATH", kb_path)
    monkeypatch.setattr(see, "TRIGGERS_PATH", out_path)

    result = see.embed_all(kb_path, out_path)
    assert result["meta"]["total_skills"] == 2
    assert "skill-a" in result["triggers"]
    assert out_path.exists()


def test_check_trigger(tmp_path: Path, monkeypatch):
    triggers_db = {
        "meta": {"version": "1.0"},
        "triggers": {
            "search-skill": {
                "scene_keywords": ["search", "look up"],
                "economics_gate": {
                    "auto_eval_rules": {"q3_compress": "context_tokens < 40000"},
                },
                "fallback_strategy": None,
            }
        },
    }
    out_path = tmp_path / "triggers.json"
    out_path.write_text(json.dumps(triggers_db), encoding="utf-8")
    monkeypatch.setattr(see, "TRIGGERS_PATH", out_path)

    result = see.check_trigger("search-skill", "I want to search for something", context_tokens=10000)
    assert result["should_trigger"] is True
    assert "search" in result["keyword_hits"]

    result2 = see.check_trigger("search-skill", "Hello world", context_tokens=10000)
    assert result2["should_trigger"] is False
    assert result2["next_step"] == "SKIP"
