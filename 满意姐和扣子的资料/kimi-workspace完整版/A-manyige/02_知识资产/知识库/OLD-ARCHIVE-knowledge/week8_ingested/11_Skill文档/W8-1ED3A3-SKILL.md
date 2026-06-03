---
# 知识元数据 (5标准化)
knowledge_id: W8-1ED3A3
title: Agentic Workflow Automation
category: 11_Skill文档
source: skills/.archive_agentic-workflow-automation/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 900
week: 8
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# Agentic Workflow Automation

> **知识ID**: W8-1ED3A3  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_agentic-workflow-automation/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

---
name: agentic-workflow-automation
description: Generate reusable multi-step agent workflow blueprints. Use for trigger/action orchestration, deterministic workflow definitions, and automation handoff artifacts.
---

# Agentic Workflow Automation

## Overview

Build workflow blueprints that can be translated into automation platforms such as n8n or internal orchestrators.

## Workflow

1. Define workflow name, trigger, and ordered steps.
2. Normalize each step into a simple execution contract.
3. Build a blueprint with dependencies and execution order.
4. Export JSON/markdown artifacts for implementation.

## Use Bundled Resources

- Run `scripts/generate_workflow_blueprint.py` for deterministic workflow output.
- Read `references/workflow-blueprint-guide.md` for step design guidance.

## Guardrails

- Keep each step single-purpose.
- Include clear fallback behavior for failed steps.
