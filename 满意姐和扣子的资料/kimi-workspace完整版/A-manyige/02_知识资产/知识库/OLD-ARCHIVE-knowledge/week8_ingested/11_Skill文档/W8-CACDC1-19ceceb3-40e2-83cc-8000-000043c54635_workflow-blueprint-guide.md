---
# 知识元数据 (5标准化)
knowledge_id: W8-CACDC1
title: Workflow Blueprint Guide
category: 11_Skill文档
source: skills/.archive_agentic-workflow-automation/19ceceb3-40e2-83cc-8000-000043c54635_workflow-blueprint-guide.md
ingested_at: 2026-03-27 17:59:30
word_count: 421
week: 8
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# Workflow Blueprint Guide

> **知识ID**: W8-CACDC1  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_agentic-workflow-automation/19ceceb3-40e2-83cc-8000-000043c54635_workflow-blueprint-guide.md`  
> **入库时间**: 2026-03-27

---

## 正文

# Workflow Blueprint Guide

## Input Fields

- `workflow_name`
- `trigger`
- `steps[]`

## Step Design Rules

- Keep each step focused on one action.
- Declare step type (`http`, `llm`, `db`, `task`, etc.).
- Define fallback action per step (`retry`, `skip`, `stop`).
- Keep ordering explicit.

## Output Expectations

- Ordered step list
- Trigger metadata
- Portable blueprint structure suitable for automation tooling
