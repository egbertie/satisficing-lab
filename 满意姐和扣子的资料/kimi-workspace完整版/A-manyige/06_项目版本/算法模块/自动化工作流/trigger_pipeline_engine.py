#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
trigger_pipeline_engine.py
事件触发器 + 自动化流水线引擎 V1.0

把 L4（固化层）的知识资产推进到 L5（自动化层）。
将 12 场景条件反射矩阵中的每个场景绑定为可执行的触发器流水线。

执行模式:
  - python3 trigger_pipeline_engine.py run <scene_id> [--dry-run]
  - python3 trigger_pipeline_engine.py list
  - python3 trigger_pipeline_engine.py audit
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

WORKSPACE = Path("/root/.openclaw/workspace")
SCENE_MODULE = "cognitive_organ_reflex_matrix"
PIPELINE_REGISTRY = WORKSPACE / "trigger_pipeline_registry.json"
EXECUTION_LOG = WORKSPACE / "trigger_pipeline_execution_log.jsonl"

# 场景到可执行脚本的映射（渐进式填充）
SCENE_PIPELINE_MAP = {
    "scene_01_file_received": {
        "steps": [
            {"name": "file_extraction", "cmd": "python3 file_internalization_orchestrator.py batch --input {{input}}", "fallback": "ollie-file-processor"},
            {"name": "duplicate_check", "cmd": "python3 skill_bloodization_guardian.py drift", "optional": True},
            {"name": "memory_update", "cmd": "python3 daily_asset_runner.py --category management", "optional": True},
        ]
    },
    "scene_02_open_question": {
        "steps": [
            {"name": "local_search", "cmd": "python3 -m memory.tiered_semantic_index query '{{query}}'", "fallback": "raglite"},
            {"name": "web_search", "cmd": "python3 -c \"import subprocess; subprocess.run(['python3', '-c', 'print(web_search not available)'])\"", "optional": True},
        ]
    },
    "scene_07_research_report": {
        "steps": [
            {"name": "research", "cmd": "python3 academic_deep_research.py run --topic '{{topic}}'", "fallback": "kimi_search"},
            {"name": "report_generation", "cmd": "python3 md-to-pdf --input report.md", "optional": True},
        ]
    },
    "scene_10_heartbeat": {
        "steps": [
            {"name": "baseline_check", "cmd": "python3 skills/baseline-checker/scripts/baseline-checker-runner.py check"},
            {"name": "asset_runner", "cmd": "python3 daily_asset_runner.py", "optional": True},
        ]
    },
}


def load_scene_matrix() -> Dict[str, Dict[str, Any]]:
    """动态导入 cognitive_organ_reflex_matrix 的 SCENARIO_MATRIX"""
    sys.path.insert(0, str(WORKSPACE))
    try:
        mod = __import__(SCENE_MODULE)
        return getattr(mod, "SCENARIO_MATRIX", {})
    except Exception as e:
        return {"_error": str(e)}


def list_scenes() -> None:
    matrix = load_scene_matrix()
    print("=" * 60)
    print("Trigger Pipeline Engine — 可用场景列表")
    print("=" * 60)
    for sid, data in matrix.items():
        has_pipeline = "✅" if sid in SCENE_PIPELINE_MAP else "📝"
        print(f"{has_pipeline} {sid}: {data.get('name', 'N/A')}")
    print("\n说明: ✅ 表示已绑定可执行流水线; 📝 表示仅有矩阵定义, 流水线待补充")


def run_pipeline(scene_id: str, dry_run: bool = False, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    matrix = load_scene_matrix()
    if scene_id not in matrix:
        return {"ok": False, "error": f"未知场景: {scene_id}"}

    scene_def = matrix[scene_id]
    pipeline_def = SCENE_PIPELINE_MAP.get(scene_id, {"steps": []})

    result = {
        "scene_id": scene_id,
        "scene_name": scene_def.get("name"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "dry_run": dry_run,
        "steps": [],
        "ok": True,
    }

    for step in pipeline_def["steps"]:
        step_result = {
            "name": step["name"],
            "cmd": step["cmd"],
            "status": "skipped" if dry_run else "pending",
            "stdout": "",
            "stderr": "",
            "returncode": None,
        }

        if not dry_run:
            try:
                cmd = step["cmd"]
                if context:
                    for k, v in context.items():
                        cmd = cmd.replace(f"{{{{{k}}}}}", str(v))
                proc = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=120)
                step_result["status"] = "success" if proc.returncode == 0 else "failed"
                step_result["returncode"] = proc.returncode
                step_result["stdout"] = proc.stdout[:500]  # trunc for log size
                step_result["stderr"] = proc.stderr[:500]
            except Exception as e:
                step_result["status"] = "error"
                step_result["stderr"] = str(e)

        result["steps"].append(step_result)
        if step_result["status"] in ("failed", "error") and not step.get("optional"):
            result["ok"] = False

    # Append to execution log
    with EXECUTION_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(result, ensure_ascii=False) + "\n")

    return result


def audit() -> None:
    matrix = load_scene_matrix()
    mapped = set(SCENE_PIPELINE_MAP.keys())
    total = len(matrix)
    covered = len(mapped & set(matrix.keys()))
    print(f"矩阵覆盖率: {covered}/{total} = {covered/total*100:.1f}%")
    for sid in matrix:
        status = "✅ 已映射" if sid in mapped else "❌ 未映射"
        print(f"  {status} {sid}")


def main():
    parser = argparse.ArgumentParser(description="Trigger + Pipeline Engine V1.0")
    sub = parser.add_subparsers(dest="command")

    list_cmd = sub.add_parser("list", help="列出所有场景及其流水线绑定状态")

    run_cmd = sub.add_parser("run", help="执行指定场景的流水线")
    run_cmd.add_argument("scene_id")
    run_cmd.add_argument("--dry-run", action="store_true")

    audit_cmd = sub.add_parser("audit", help="审计矩阵到流水线的映射覆盖率")

    args = parser.parse_args()

    if args.command == "list":
        list_scenes()
    elif args.command == "run":
        res = run_pipeline(args.scene_id, dry_run=args.dry_run)
        print(json.dumps(res, ensure_ascii=False, indent=2))
    elif args.command == "audit":
        audit()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
