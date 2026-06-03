"""
OpenSpec与满意姐认知生态整合管理器
实现契约驱动开发(SDD)与认知晶体的双向同步
"""

import os
import shutil
import yaml
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

try:
    from cognitive_ecosystem.base.crystal_models import CognitiveCrystal, TemporalCrystal
except ImportError:
    CognitiveCrystal = None
    TemporalCrystal = None


class OpenSpecManager:
    """
    OpenSpec管理器
    核心职责：强制工作流执行 + Bridge Rule维护 + Spec-Crystal同步
    """

    def __init__(self, project_root: str, temporal_store=None):
        self.root = Path(project_root)
        self.store = temporal_store
        self.openspec_dir = self.root / "openspec"
        self.specs_dir = self.openspec_dir / "specs"
        self.changes_dir = self.openspec_dir / "changes"
        self._ensure_structure()

    def _ensure_structure(self):
        """强制OpenSpec目录结构，缺失则创建"""
        required_dirs = [
            self.openspec_dir,
            self.specs_dir,
            self.changes_dir,
            self.openspec_dir / "archive"
        ]
        for d in required_dirs:
            d.mkdir(parents=True, exist_ok=True)

        config_file = self.openspec_dir / "config.yaml"
        if not config_file.exists():
            self._create_default_config(config_file)

    def _create_default_config(self, path: Path):
        default_config = {
            "project": {
                "name": "satisfying-ecosystem",
                "tech_stack": ["python"],
                "architecture": "cognitive_ecosystem"
            },
            "rules": {
                "max_tasks_per_change": 15,
                "require_tests": True,
                "coding_standards": "strict"
            }
        }
        with open(path, 'w', encoding="utf-8") as f:
            yaml.dump(default_config, f)
        print(f"✅ 创建默认OpenSpec配置: {path}")

    def propose_change(self, change_name: str, description: str) -> Dict:
        """
        /opsx:propose 实现
        生成三阶契约文件，并转化为满意姐认知晶体
        """
        change_dir = self.changes_dir / change_name
        change_dir.mkdir(exist_ok=True)

        proposal = self._generate_proposal(change_name, description)
        self._write_file(change_dir / "proposal.md", proposal)

        design = self._generate_design(change_name, description)
        self._write_file(change_dir / "design.md", design)

        tasks = self._generate_tasks(change_name)
        self._write_file(change_dir / "tasks.md", tasks)

        crystals = self._convert_to_crystals(change_name, proposal, design, tasks)

        return {
            "change_name": change_name,
            "location": str(change_dir),
            "files_created": ["proposal.md", "design.md", "tasks.md"],
            "crystal_ids": [c.crystal_id for c in crystals] if CognitiveCrystal else [],
            "next_step": "议会审计（蓝军+五路图腾）"
        }

    def _generate_proposal(self, name: str, desc: str) -> str:
        return f"""# Proposal: {name}

## 背景与动机（为什么做）
{desc}

## 预期收益
- ROI分析：
- 风险：

## 备选方案（至少3个）
1.
2.
3.

## 建议方案
<!-- 司马贺满意解评估后选择 -->

## 相关晶体
- 关联意图晶体：
- 关联架构约束：
"""

    def _generate_design(self, name: str, desc: str) -> str:
        return f"""# Design: {name}

## 技术方案

## 架构决策（ADR）

## 接口契约

## 风险与缓解
<!-- 观自在风险扫描 -->

## 检查清单（7项专业检查）
- [ ] 1. 单元测试覆盖
- [ ] 2. 集成测试覆盖
- [ ] 3. 文档更新
- [ ] 4. 性能影响评估
- [ ] 5. 安全审计
- [ ] 6. 向后兼容
- [ ] 7. 监控告警
"""

    def _generate_tasks(self, name: str) -> str:
        return f"""# Tasks: {name}

## 实施清单（每项必须有验收标准）
- [ ] 1.
- [ ] 2.
- [ ] 3.

## 阻塞条件
<!-- 明确什么情况下禁止继续 -->

## 验收标准
<!-- 什么算完成 -->
"""

    def _write_file(self, path: Path, content: str):
        with open(path, 'w', encoding="utf-8") as f:
            f.write(content)

    def _convert_to_crystals(self, change_name: str, proposal: str, design: str, tasks: str) -> List:
        if CognitiveCrystal is None or self.store is None:
            return []
        crystals = []
        intention_crystal = CognitiveCrystal(
            source_uris=[str(self.changes_dir / change_name / "proposal.md")],
            compression_ratio=0.3,
            primary_entities=[change_name, "proposal"],
            key_relations=[{"subject": change_name, "predicate": "intends_to", "object": "implement_feature"}],
            decision_patterns=[proposal[:200]],
            totem_affinity={"simon": 0.9},
            activation_triggers=[change_name, "propose", "planning"],
            confidence_score=0.9
        )
        crystals.append(intention_crystal)
        if hasattr(self.store, "store_event"):
            self.store.store_event(TemporalCrystal(
                semantic_time="OpenSpec-Propose",
                event_type="perception",
                content=f"提案: {change_name}",
                crystal_refs=[intention_crystal.crystal_id],
                narrative_cluster="openspec_workflow"
            ))
        return crystals

    def apply_change(self, change_name: str, p8_executor=None) -> Dict:
        """
        /opsx:apply 实现
        使用P8引擎执行tasks.md，带压力升级机制
        """
        change_dir = self.changes_dir / change_name
        tasks_file = change_dir / "tasks.md"

        if not tasks_file.exists():
            raise FileNotFoundError(f"Tasks文件不存在: {tasks_file}")

        tasks = self._read_tasks(tasks_file)

        if len(tasks) > 15:
            raise ValueError(f"任务数{len(tasks)}超过15，拒绝执行（防止幻觉）")

        results = []
        for i, task in enumerate(tasks):
            print(f"🔄 执行任务 {i+1}/{len(tasks)}: {task[:50]}...")
            task_def = {
                "id": f"{change_name}-task-{i}",
                "description": task,
                "type": "code_generation"
            }

            if p8_executor:
                result = p8_executor.execute_with_pressure(task_def)
            else:
                result = {"success": True, "result": "模拟执行", "attempts": 1, "final_pressure": "L0"}
            results.append(result)

            if not result.get("success"):
                print(f"❌ 任务{i+1}失败，P8引擎已尽力")
                break

        return {
            "change_name": change_name,
            "tasks_total": len(tasks),
            "tasks_completed": len([r for r in results if r.get("success")]),
            "results": results,
            "next_step": "测试验证" if all(r.get("success") for r in results) else "修复或归档失败"
        }

    def _read_tasks(self, path: Path) -> List[str]:
        with open(path, 'r', encoding="utf-8") as f:
            content = f.read()
        tasks = []
        for line in content.split('\n'):
            if line.strip().startswith('- [ ]'):
                tasks.append(line.strip()[5:].strip())
        return tasks

    def archive_change(self, change_name: str) -> Dict:
        """
        /opsx:archive 实现
        """
        change_dir = self.changes_dir / change_name
        archive_dir = self.openspec_dir / "archive" / change_name

        if not change_dir.exists():
            return {"error": f"变更目录不存在: {change_dir}"}

        if archive_dir.exists():
            shutil.rmtree(archive_dir)
        shutil.move(str(change_dir), str(archive_dir))

        spec_increment = f"# Spec: {change_name}\n\nArchived from {change_name}\n"
        spec_file = self.specs_dir / f"{change_name}.md"
        with open(spec_file, 'w', encoding="utf-8") as f:
            f.write(spec_increment)

        if TemporalCrystal is not None and self.store and hasattr(self.store, "store_event"):
            self.store.store_event(TemporalCrystal(
                semantic_time="OpenSpec归档",
                event_type="archive",
                content=f"变更{change_name}已归档并入specs/",
                narrative_cluster="openspec_workflow"
            ))

        return {
            "change_name": change_name,
            "archived_to": str(archive_dir),
            "spec_created": str(spec_file)
        }

    def load_config(self) -> Dict:
        config_file = self.openspec_dir / "config.yaml"
        if not config_file.exists():
            return {}
        with open(config_file, 'r', encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    def get_specs(self) -> List[Path]:
        return list(self.specs_dir.glob("*.md"))
