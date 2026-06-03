"""
skill_methodology_extractor.py
Extract methodology, thought frameworks, and workflow patterns from SKILL.md files.
Token-economic: rule-based extraction, no LLM calls per skill.
"""
from __future__ import annotations
import json
import os
import re
from pathlib import Path
from typing import Any

SKILLS_DIR = Path("/root/.openclaw/workspace/skills")
OUTPUT_PATH = Path("/root/.openclaw/workspace/skill_methodology_knowledge_base.json")

METHOD_SCHEMA = {
    "skill_name": "",
    "skill_path": "",
    "description": "",
    "core_methodology": [],
    "thought_framework": "",
    "workflow_pattern": "",
    "input_output_spec": {},
    "best_practices": [],
    "anti_patterns": [],
    "trigger_keywords": [],
    "organ": "unclassified",
    "value_density": "pending",
    "bloodized_status": "unknown",
}


def _slugify(name: str) -> str:
    return name.strip().lower().replace(" ", "-").replace("_", "-")


def _find_skills() -> list[Path]:
    if not SKILLS_DIR.exists():
        return []
    skills = []
    for entry in sorted(SKILLS_DIR.iterdir()):
        if entry.is_dir():
            skill_md = entry / "SKILL.md"
            if skill_md.exists():
                skills.append(entry)
    return skills


def _parse_yaml_frontmatter(text: str) -> dict[str, Any]:
    if not text.startswith("---"):
        return {}
    m = re.search(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not m:
        return {}
    try:
        import yaml
        data = yaml.safe_load(m.group(1))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _extract_description(text: str) -> str:
    fm = _parse_yaml_frontmatter(text)
    if fm.get("description"):
        return str(fm["description"]).strip()
    # Try XML-style description tags
    m = re.search(r"<description>(.*?)</description>", text, re.DOTALL | re.IGNORECASE)
    if m:
        return m.group(1).strip()
    # Then markdown headers
    m = re.search(r"#{1,3}\s*description\s*\n(.*?)(?=\n#{1,3}\s|\Z)", text, re.DOTALL | re.IGNORECASE)
    if m:
        return m.group(1).strip()
    # Fallback: first non-empty paragraph before first header / after frontmatter
    body = text
    if text.startswith("---"):
        m2 = re.search(r"\n---\s*\n(.*)", text, re.DOTALL)
        if m2:
            body = m2.group(1)
    lines = body.splitlines()
    paras = []
    for line in lines:
        if line.strip().startswith("#") and paras:
            break
        if line.strip():
            paras.append(line.strip())
        elif paras:
            break
    return " ".join(paras).strip()


def _extract_triggers(text: str) -> list[str]:
    triggers = set()
    fm = _parse_yaml_frontmatter(text)
    for key in ["triggers", "trigger", "use_when"]:
        val = fm.get(key)
        if val:
            if isinstance(val, list):
                for item in val:
                    triggers.add(str(item).strip())
            else:
                triggers.add(str(val).strip())
    # Trigger sections
    for pattern in [
        r"#{1,3}\s*(?:trigger|triggers|触发|触发条件|use when|usage)\s*\n(.*?)(?=\n#{1,3}\s|\Z)",
    ]:
        m = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if m:
            section = m.group(1)
            for line in section.splitlines():
                line = line.strip().lstrip("*-").strip()
                if line and len(line) > 3:
                    triggers.add(line)
    # Inline trigger phrases
    for phrase in re.findall(r"(?:Use when|Trigg(?:er|ers) on|触发|适用场景)([^.\n]{5,120})", text, re.IGNORECASE):
        triggers.add(phrase.strip().lstrip(":").strip())
    return list(triggers)[:20]


def _extract_methodology(text: str) -> list[str]:
    methods = []
    fm = _parse_yaml_frontmatter(text)
    for key in ["methodology", "framework", "core", "approach", "workflow"]:
        val = fm.get(key)
        if val:
            if isinstance(val, list):
                methods.extend(str(v).strip() for v in val if len(str(v).strip()) > 5)
            else:
                methods.append(str(val).strip())
    # Markdown sections
    for pattern in [
        r"#{1,3}\s*(?:methodology|framework|core|核心方法论|方法论|工作模式|workflow|方法|模式)\s*\n(.*?)(?=\n#{1,3}\s|\Z)",
    ]:
        m = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if m:
            section = m.group(1)
            for line in section.splitlines():
                line = line.strip().lstrip("*-1234567890.").strip()
                if line and len(line) > 5:
                    methods.append(line)
    # Collect bullet points with strong methodology keywords
    keywords = ["framework", "methodology", "model", "principle", "heuristic", "pattern", "workflow", "system", "theory", "approach", "决策", "分析", "思考", "模型"]
    for line in text.splitlines():
        line_stripped = line.strip().lstrip("*-").strip()
        if any(kw in line_stripped.lower() for kw in keywords) and len(line_stripped) > 10:
            methods.append(line_stripped)
    return list(dict.fromkeys(methods))[:30]


def _extract_best_practices(text: str) -> list[str]:
    practices = []
    fm = _parse_yaml_frontmatter(text)
    for key in ["best_practices", "practices", "guidelines", "recommendations"]:
        val = fm.get(key)
        if val:
            if isinstance(val, list):
                practices.extend(str(v).strip() for v in val if len(str(v).strip()) > 5)
            else:
                practices.append(str(val).strip())
    for pattern in [
        r"#{1,3}\s*(?:best practices?|practices|good practice|推荐用法|最佳实践|guidelines)\s*\n(.*?)(?=\n#{1,3}\s|\Z)",
    ]:
        m = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if m:
            section = m.group(1)
            for line in section.splitlines():
                line = line.strip().lstrip("*-1234567890.").strip()
                if line and len(line) > 5:
                    practices.append(line)
    return list(dict.fromkeys(practices))[:20]


def _extract_anti_patterns(text: str) -> list[str]:
    patterns = []
    for keyword in ["anti-pattern", "avoid", "don't", "do not", "禁止", "切忌", " pitfalls", "not for", "不适合", "❌"]:
        for line in text.splitlines():
            if keyword in line.lower():
                line_stripped = line.strip().lstrip("*-").strip()
                if len(line_stripped) > 5:
                    patterns.append(line_stripped)
    return list(dict.fromkeys(patterns))[:15]


def _extract_workflow(text: str) -> str:
    for pattern in [
        r"#{1,3}\s*(?:workflow|process|steps|execution|使用流程|工作流程|步骤)\s*\n(.*?)(?=\n#{1,3}\s|\Z)",
    ]:
        m = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if m:
            return m.group(1).strip()[:800]
    return ""


def _extract_input_output(text: str) -> dict[str, Any]:
    io = {}
    fm = _parse_yaml_frontmatter(text)
    if fm.get("parameters"):
        io["inputs"] = json.dumps(fm["parameters"], ensure_ascii=False)
    for pattern in [
        r"#{1,3}\s*(?:input|parameters|args|arguments|输入)\s*\n(.*?)(?=\n#{1,3}\s|\Z)",
    ]:
        m = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if m:
            io["inputs"] = m.group(1).strip()[:600]
    for pattern in [
        r"#{1,3}\s*(?:output|returns|result|输出)\s*\n(.*?)(?=\n#{1,3}\s|\Z)",
    ]:
        m = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if m:
            io["outputs"] = m.group(1).strip()[:600]
    return io


def _load_organ_mapping() -> dict[str, str]:
    """Load organ mapping from /tmp/skills_by_organ.json (generated by V3.0 charter)."""
    json_path = Path("/tmp/skills_by_organ.json")
    mapping = {}
    if not json_path.exists():
        return mapping
    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
        organs = data.get("organs", {})
        for organ_name, skills in organs.items():
            for skill in skills:
                name = skill.get("name", "")
                if name:
                    mapping[_slugify(name)] = organ_name
    except Exception:
        pass
    return mapping


def _load_bloodized_status() -> dict[str, str]:
    # Guardian state not available as JSON; infer from installed presence for now.
    return {}


def extract_skill(skill_dir: Path, organ_mapping: dict[str, str], bloodized: dict[str, str]) -> dict[str, Any]:
    skill_md = skill_dir / "SKILL.md"
    text = skill_md.read_text(encoding="utf-8")
    skill_name = skill_dir.name
    record = dict(METHOD_SCHEMA)
    record["skill_name"] = skill_name
    record["skill_path"] = str(skill_md)
    record["description"] = _extract_description(text)
    record["core_methodology"] = _extract_methodology(text)
    record["thought_framework"] = _extract_description(text)[:400]
    record["workflow_pattern"] = _extract_workflow(text)
    record["input_output_spec"] = _extract_input_output(text)
    record["best_practices"] = _extract_best_practices(text)
    record["anti_patterns"] = _extract_anti_patterns(text)
    record["trigger_keywords"] = _extract_triggers(text)
    record["organ"] = organ_mapping.get(_slugify(skill_name), "unclassified")
    record["bloodized_status"] = bloodized.get(_slugify(skill_name), "unknown")
    return record


def run_extraction() -> dict[str, Any]:
    skill_dirs = _find_skills()
    organ_mapping = _load_organ_mapping()
    bloodized = _load_bloodized_status()
    knowledge_base = {
        "meta": {
            "version": "1.0",
            "total_skills": len(skill_dirs),
            "extraction_engine": "rule-based+yaml-aware",
            "note": "Token-economic extraction without per-skill LLM calls",
        },
        "skills": {},
        "organs": {},
    }
    for skill_dir in skill_dirs:
        record = extract_skill(skill_dir, organ_mapping, bloodized)
        knowledge_base["skills"][record["skill_name"]] = record
        organ = record["organ"]
        knowledge_base["organs"].setdefault(organ, []).append(record["skill_name"])

    OUTPUT_PATH.write_text(json.dumps(knowledge_base, ensure_ascii=False, indent=2), encoding="utf-8")
    return knowledge_base


if __name__ == "__main__":
    kb = run_extraction()
    print(f"Extracted {kb['meta']['total_skills']} skills into {OUTPUT_PATH}")
    for organ, skills in sorted(kb["organs"].items(), key=lambda x: -len(x[1])):
        print(f"  {organ}: {len(skills)} skills")
