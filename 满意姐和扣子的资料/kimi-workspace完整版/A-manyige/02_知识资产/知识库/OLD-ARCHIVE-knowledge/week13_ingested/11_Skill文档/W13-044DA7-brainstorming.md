---
# 知识元数据 (5标准化)
knowledge_id: W13-044DA7
title: Brainstorming Reference
category: 11_Skill文档
source: skills/.archive_satisficing-dev-workflow/references/brainstorming.md
ingested_at: 2026-03-27 17:59:30
word_count: 1454
week: 13
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# Brainstorming Reference

> **知识ID**: W13-044DA7  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_satisficing-dev-workflow/references/brainstorming.md`  
> **入库时间**: 2026-03-27

---

## 正文

# Brainstorming Reference

Source: satisficing-dev-workflow | obra/superpowers adaptation

---

## Checklist (in order)

1. **Explore project context** — check files, docs, recent commits
2. **Ask clarifying questions** — one at a time, understand purpose/constraints/success criteria
3. **Propose 2–3 approaches** — with trade-offs and recommendation
4. **Present design** — in sections scaled to complexity, get approval after each section
5. **Write design doc** — `docs/plans/YYYY-MM-DD-<topic>-design.md` → commit
6. **Transition** — invoke writing-plans phase

---

## Rules

- One question per message only
- Multiple choice preferred over open-ended
- Every project goes through this process — no exceptions for "simple" ones
- HARD GATE: Do NOT write code, scaffold, or implement anything until design is approved
- Propose 2–3 approaches before settling, lead with recommendation

---

## Questions to Ask

- What are you really trying to do? (purpose)
- What constraints exist? (time, tech stack, dependencies)
- What does success look like? (success criteria)
- What should this NOT do? (scope boundaries)

---

## Design Sections to Cover

- Architecture overview
- Components and their responsibilities
- Data flow
- Error handling approach
- Testing strategy

---

## After Design Approval

- Write design to `docs/plans/YYYY-MM-DD-<topic>-design.md`
- Commit the design doc
- Hand off to writing-plans — no other skill, no implementation
