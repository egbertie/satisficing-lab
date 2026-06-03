---
# 知识元数据 (5标准化)
knowledge_id: W9-49E6A6
title: Decision Frameworks
category: 11_Skill文档
source: skills/.archive_decision-frameworks/README.md
ingested_at: 2026-03-27 17:59:30
word_count: 2010
week: 9
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# Decision Frameworks

> **知识ID**: W9-49E6A6  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_decision-frameworks/README.md`  
> **入库时间**: 2026-03-27

---

## 正文

# Decision Frameworks

Structured decision-making patterns for common engineering choices — library selection, architecture, build vs buy, prioritization, reversibility analysis, and ADRs.

## What's Inside

- Decision matrix template with weighted scoring
- Build vs buy framework (decision tree + factor comparison)
- Library and framework selection criteria
- Architecture decision tables (monolith vs microservices, SQL vs NoSQL, REST vs GraphQL, SSR vs CSR vs SSG, monorepo vs polyrepo)
- Priority matrices — RICE scoring and MoSCoW method
- Reversibility check (one-way vs two-way doors)
- ADR (Architecture Decision Record) template
- Anti-patterns (analysis paralysis, HiPPO, sunk cost fallacy, bandwagon effect)

## When to Use

- Choosing between libraries, frameworks, or tools
- Facing a build-vs-buy decision
- Selecting an architecture pattern (monolith vs microservices, SQL vs NoSQL, etc.)
- Multiple valid options exist and the team needs alignment
- Prioritizing a backlog or technical roadmap
- Documenting a significant technical decision for future reference

## Installation

```bash
npx add https://github.com/wpank/ai/tree/main/skills/meta/decision-frameworks
```

### OpenClaw / Moltbot / Clawbot

```bash
npx clawhub@latest install decision-frameworks
```

### Manual Installation

#### Cursor (per-project)

From your project root:

```bash
mkdir -p .cursor/skills
cp -r ~/.ai-skills/skills/meta/decision-frameworks .cursor/skills/decision-frameworks
```

#### Cursor (global)

```bash
mkdir -p ~/.cursor/skills
cp -r ~/.ai-skills/skills/meta/decision-frameworks ~/.cursor/skills/decision-frameworks
```

#### Claude Code (per-project)

From your project root:

```bash
mkdir -p .claude/skills
cp -r ~/.ai-skills/skills/meta/decision-frameworks .claude/skills/decision-frameworks
```

#### Claude Code (global)

```bash
mkdir -p ~/.claude/skills
cp -r ~/.ai-skills/skills/meta/decision-frameworks ~/.claude/skills/decision-frameworks
```

---

Part of the [Meta](..) skill category.
