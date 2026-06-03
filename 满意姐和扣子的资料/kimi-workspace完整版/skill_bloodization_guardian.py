#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
skill_bloodization_guardian.py
技能血液化监控守护器 V1.0

机制目标：
  1. 让 195 个 eligible skill 的血液化状态成为可查询、可监控的事实。
  2. 在 skill 增加/删除/升级时自动检测漂移。
  3. 强制触发血液化检查，防止掉链子。

运行方式：
  - python3 skill_bloodization_guardian.py check       # 全面体检
  - python3 skill_bloodization_guardian.py drift       # 检测当前 workspace 相对 manifest 的漂移
  - python3 skill_bloodization_guardian.py inspect <skill_name>  # 单个 skill 血液化评估
"""

import os
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

WORKSPACE = Path("/root/.openclaw/workspace")
SKILLS_DIR = WORKSPACE / "skills"
MANIFEST_PATH = WORKSPACE / "A-manyige" / "对话" / "2026-04-09" / "195个eligible_skill血液化宣言手册-V1.0-20260409-1115.md"
CLASSIFICATION_PATH = Path("/tmp/skills_by_organ.json")
BLOODIZED_REGISTRY = WORKSPACE / ".bloodized_registry.json"

ORGAN_TARGET_COUNTS = {
    "思维器官": 25,
    "感知器官": 34,
    "记忆器官": 54,
    "运动器官": 39,
    "构造器官": 13,
    "代谢器官": 9,
    "特化器官": 18,
    "干细胞池": 31,
}


def load_manifest_skills() -> set:
    """从宣言手册中提取 skill 名称"""
    if not MANIFEST_PATH.exists():
        return set()
    text = MANIFEST_PATH.read_text(encoding="utf-8")
    # 匹配 `- `skill_name`: 当...` 的格式
    pattern = re.compile(r"-\s+`([^`]+)`:\s+当")
    return set(pattern.findall(text))


def load_classification() -> Dict[str, List[Dict]]:
    """加载八大认知器官分类数据"""
    if CLASSIFICATION_PATH.exists():
        data = json.loads(CLASSIFICATION_PATH.read_text(encoding="utf-8"))
        return data.get("organs", {})
    return {}


def get_installed_skills() -> set:
    """扫描 skills/ 目录获取已安装的 skill 名称"""
    if not SKILLS_DIR.exists():
        return set()
    return {d.name for d in SKILLS_DIR.iterdir() if d.is_dir() and (d / "SKILL.md").exists() or (d / "_meta.json").exists()}


def get_skill_trigger_text(skill_name: str) -> Optional[str]:
    """读取 skill 的 SKILL.md，尝试提取触发条件"""
    skill_dir = SKILLS_DIR / skill_name
    for filename in ["SKILL.md", "SKILL_zh.md", "README.md"]:
        fpath = skill_dir / filename
        if fpath.exists():
            text = fpath.read_text(encoding="utf-8")
            # 优先查找 "触发" / "Use when" / "当用户" 等关键词
            for keyword in ["Use when", "触发", "当用户", "适用场景"]:
                idx = text.find(keyword)
                if idx != -1:
                    snippet = text[idx:idx+300].replace("\n", " ")
                    return snippet[:250]
            return text[:250] + "..."
    return None


def assess_bloodization_level(skill_name: str) -> Tuple[str, List[str]]:
    """
    评估单个 skill 的血液化程度。
    返回 (level, issues)
    """
    issues = []
    skill_dir = SKILLS_DIR / skill_name

    if not skill_dir.exists():
        return "missing", ["Skill 目录不存在"]

    # 检查 SKILL.md 或等效文档
    has_doc = any((skill_dir / fn).exists() for fn in ["SKILL.md", "SKILL_zh.md", "README.md"])
    if not has_doc:
        issues.append("缺少 SKILL.md / README.md，无法判断触发条件")

    trigger_text = get_skill_trigger_text(skill_name)
    if trigger_text is None:
        issues.append("无法提取触发条件文本")
    else:
        # 检查是否是模板化的无意义触发
        template_phrases = ["当遇到对应场景时，我是", "Automatically triggered", "当用户提到"]
        meaningful = False
        if any(p in trigger_text for p in template_phrases):
            # 如果只有模板短语而没有具体内容，标记为低血液化
            pass
        # 检查触发文本长度，过短说明 insufficient
        if len(trigger_text) < 20:
            issues.append("触发条件描述过短，血液化不足")
            meaningful = False
        else:
            meaningful = True

        if not meaningful and len(trigger_text) < 50:
            issues.append("触发条件尚未真正内化（可能为模板填充）")

    # 检查是否有可运行脚本/代码（可选加分项）
    has_scripts = any((skill_dir / sub).exists() for sub in ["scripts", "script", "src"])

    if issues:
        if any("无法" in i or "不存在" in i for i in issues):
            return "unhealthy", issues
        return "candidate", issues  # 有文档但未真正血液化

    return "bloodized", ["触发条件明确，文档完整" + ("，含可运行脚本" if has_scripts else "")]


class SkillBloodizationGuardian:
    """技能血液化监控守护器"""

    def __init__(self, workspace: Path = WORKSPACE):
        self.workspace = workspace
        self.installed = get_installed_skills()
        self.manifest = load_manifest_skills()
        self.classification = load_classification()

    def detect_drift(self) -> Dict:
        """检测宣言、分类、实际安装之间的漂移"""
        manifest_only = self.manifest - self.installed
        installed_only = self.installed - self.manifest
        classified = set()
        for organ, skills in self.classification.items():
            for s in skills:
                classified.add(s["name"])

        classified_only = classified - self.installed
        unclassified = self.installed - classified

        return {
            "installed_count": len(self.installed),
            "manifest_count": len(self.manifest),
            "classified_count": len(classified),
            "manifest_only": sorted(manifest_only),
            "installed_only": sorted(installed_only),
            "classified_only": sorted(classified_only),
            "unclassified": sorted(unclassified),
            "drift_detected": bool(manifest_only or installed_only or classified_only or unclassified),
        }

    def health_check(self, sample_limit: Optional[int] = None) -> Dict:
        """对全部或抽样 skill 执行血液化健康检查"""
        skills_to_check = sorted(self.installed)
        if sample_limit and len(skills_to_check) > sample_limit:
            # 按字母序取前 N 个作为样本（可改为随机）
            skills_to_check = skills_to_check[:sample_limit]

        results = {}
        summary = {"bloodized": 0, "candidate": 0, "unhealthy": 0, "missing": 0}

        for name in skills_to_check:
            level, issues = assess_bloodization_level(name)
            results[name] = {"level": level, "issues": issues}
            summary[level] = summary.get(level, 0) + 1

        return {
            "checked": len(skills_to_check),
            "summary": summary,
            "details": results,
        }

    def inspect(self, skill_name: str) -> Dict:
        """单个 skill 详细检查"""
        if skill_name not in self.installed:
            return {"error": f"{skill_name} 未在 workspace 中安装"}
        level, issues = assess_bloodization_level(skill_name)
        trigger = get_skill_trigger_text(skill_name)
        # 查找所属器官
        organs = []
        for organ, skills in self.classification.items():
            if any(s["name"] == skill_name for s in skills):
                organs.append(organ)
        return {
            "name": skill_name,
            "level": level,
            "issues": issues,
            "trigger_snippet": trigger,
            "organs": organs,
        }

    def check_manifest_integrity(self) -> Dict:
        """检查宣言手册的完整性（数量是否对得上8大器官目标）"""
        report = {}
        total_in_manifest = 0
        for organ, target in ORGAN_TARGET_COUNTS.items():
            actual = len(self.classification.get(organ, []))
            total_in_manifest += actual
            report[organ] = {
                "target": target,
                "actual": actual,
                "delta": actual - target,
                "status": "ok" if actual == target else "mismatch",
            }
        report["total"] = {"target": 195, "actual": total_in_manifest}
        return report

    def full_report(self) -> str:
        drift = self.detect_drift()
        health = self.health_check(sample_limit=20)
        manifest_integrity = self.check_manifest_integrity()

        lines = [
            "# 技能血液化 Guardian 报告",
            "",
            f"**已安装 skill**: {drift['installed_count']}",
            f"**宣言覆盖 skill**: {drift['manifest_count']}",
            f"**分类覆盖 skill**: {manifest_integrity['total']['actual']}",
            "",
        ]

        if drift["drift_detected"]:
            lines.append("## ⚠️ 漂移检测")
            if drift["manifest_only"]:
                lines.append(f"- 宣言中有但实际未安装: {len(drift['manifest_only'])} 个")
            if drift["installed_only"]:
                lines.append(f"- 已安装但宣言未覆盖: {len(drift['installed_only'])} 个")
            if drift["unclassified"]:
                lines.append(f"- 已安装但未分类到八大器官: {len(drift['unclassified'])} 个")
            lines.append("")
        else:
            lines.append("## ✅ 无漂移")
            lines.append("")

        lines.append("## 健康抽查（前 20 个 skill）")
        for level, count in health["summary"].items():
            lines.append(f"- {level}: {count}")
        lines.append("")

        lines.append("## 宣言完整性")
        for organ, info in manifest_integrity.items():
            if organ == "total":
                continue
            icon = "✅" if info["status"] == "ok" else "⚠️"
            lines.append(f"- {icon} {organ}: {info['actual']} / {info['target']} (差 {info['delta']})")
        lines.append("")

        return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 skill_bloodization_guardian.py [check|drift|inspect <skill_name>]")
        sys.exit(0)

    cmd = sys.argv[1]
    guardian = SkillBloodizationGuardian()

    if cmd == "check":
        print(guardian.full_report())
    elif cmd == "drift":
        drift = guardian.detect_drift()
        print(json.dumps(drift, ensure_ascii=False, indent=2))
    elif cmd == "inspect" and len(sys.argv) >= 3:
        result = guardian.inspect(sys.argv[2])
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("Unknown command")


if __name__ == "__main__":
    main()
