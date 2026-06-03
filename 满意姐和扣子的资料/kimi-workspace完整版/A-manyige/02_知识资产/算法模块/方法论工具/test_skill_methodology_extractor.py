"""
test_skill_methodology_extractor.py
pytest for skill_methodology_extractor.
"""
import json
import tempfile
from pathlib import Path

import skill_methodology_extractor as sme


def test_slugify():
    assert sme._slugify("Hello World") == "hello-world"
    assert sme._slugify("foo_bar") == "foo-bar"


def test_parse_yaml_frontmatter():
    text = "---\nname: test\ndescription: A test skill\n---\n# Body"
    fm = sme._parse_yaml_frontmatter(text)
    assert fm["name"] == "test"
    assert fm["description"] == "A test skill"


def test_parse_yaml_frontmatter_missing():
    text = "# No frontmatter\nSome body"
    assert sme._parse_yaml_frontmatter(text) == {}


def test_extract_description_yaml():
    text = "---\ndescription: YAML desc\n---\n# Title\nbody"
    assert sme._extract_description(text) == "YAML desc"


def test_extract_description_xml():
    text = "<description>XML desc</description>\n# Title"
    assert sme._extract_description(text) == "XML desc"


def test_extract_description_fallback():
    text = "First paragraph.\n\nSecond paragraph.\n# Header"
    assert sme._extract_description(text) == "First paragraph."


def test_extract_triggers_yaml():
    text = "---\ntriggers:\n  - weather query\n  - forecast\n---\n# Body"
    triggers = sme._extract_triggers(text)
    assert "weather query" in triggers
    assert "forecast" in triggers


def test_extract_triggers_inline():
    text = "Use when the user asks about rain.\n# Title"
    triggers = sme._extract_triggers(text)
    assert any("user asks about rain" in t for t in triggers)


def test_extract_methodology():
    text = "## Methodology\n- Model A\n- Framework B"
    methods = sme._extract_methodology(text)
    assert "Model A" in methods


def test_extract_best_practices():
    text = "## Best Practices\n- Do something X\n- Avoid running Y"
    practices = sme._extract_best_practices(text)
    assert "Do something X" in practices
    assert "Avoid running Y" in practices


def test_extract_anti_patterns():
    text = "- Don't run rm without backup\n- Avoid loops"
    patterns = sme._extract_anti_patterns(text)
    assert any("rm without backup" in p for p in patterns)


def test_extract_workflow():
    text = "## Workflow\nStep 1\nStep 2\n## End"
    wf = sme._extract_workflow(text)
    assert "Step 1" in wf


def test_extract_input_output():
    text = "## Input\nfoo\n## Output\nbar"
    io = sme._extract_input_output(text)
    assert io["inputs"] == "foo"
    assert io["outputs"] == "bar"


def test_extract_skill(tmp_path: Path):
    skill_dir = tmp_path / "test-skill"
    skill_dir.mkdir()
    skill_md = skill_dir / "SKILL.md"
    skill_md.write_text(
        "---\n"
        "name: test-skill\n"
        "description: A sample skill for testing\n"
        "triggers:\n"
        "  - unit test\n"
        "---\n"
        "# Test Skill\n\n"
        "## Methodology\n"
        "- Pattern match\n"
        "## Best Practices\n"
        "- Keep it simple\n",
        encoding="utf-8",
    )
    organ_mapping = {"test-skill": "思维器官"}
    record = sme.extract_skill(skill_dir, organ_mapping, {})
    assert record["skill_name"] == "test-skill"
    assert record["description"] == "A sample skill for testing"
    assert "unit test" in record["trigger_keywords"]
    assert "Pattern match" in record["core_methodology"]
    assert record["organ"] == "思维器官"


def test_run_extraction(tmp_path: Path, monkeypatch):
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()
    (skills_dir / "skill-a").mkdir()
    (skills_dir / "skill-a" / "SKILL.md").write_text(
        "---\ndescription: Skill A\n---\n# A", encoding="utf-8"
    )
    (skills_dir / "skill-b").mkdir()
    (skills_dir / "skill-b" / "SKILL.md").write_text(
        "---\ndescription: Skill B\n---\n# B", encoding="utf-8"
    )
    output_path = tmp_path / "kb.json"

    monkeypatch.setattr(sme, "SKILLS_DIR", skills_dir)
    monkeypatch.setattr(sme, "OUTPUT_PATH", output_path)

    kb = sme.run_extraction()
    assert kb["meta"]["total_skills"] == 2
    assert "skill-a" in kb["skills"]
    assert "skill-b" in kb["skills"]
    assert output_path.exists()
