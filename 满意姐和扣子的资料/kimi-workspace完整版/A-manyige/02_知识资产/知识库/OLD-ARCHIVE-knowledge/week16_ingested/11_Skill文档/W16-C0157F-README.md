---
# 知识元数据 (5标准化)
knowledge_id: W16-C0157F
title: React Email Agent Skill
category: 11_Skill文档
source: skills/react-email/README.md
ingested_at: 2026-03-27 17:59:30
word_count: 1672
week: 16
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# React Email Agent Skill

> **知识ID**: W16-C0157F  
> **分类**: 11_Skill文档  
> **来源**: `skills/react-email/README.md`  
> **入库时间**: 2026-03-27

---

## 正文

# React Email Agent Skill

This directory contains an Agent Skill for building HTML emails with React Email components.

## Structure

```
react-email/
├── SKILL.md                  # Main skill instructions
└── references/
    ├── COMPONENTS.md         # Complete component reference
    ├── I18N.md              # Internationalization guide
    └── PATTERNS.md          # Common email patterns and examples
```

## What is an Agent Skill?

Agent Skills are a standardized format for giving AI agents specialized knowledge and workflows. This skill teaches agents how to:

- Build HTML email templates using React Email components
- Send emails through Resend and other providers
- Implement internationalization for multi-language support
- Follow email development best practices

## Using This Skill

AI agents can load this skill to gain expertise in React Email development. The skill follows the [Agent Skills specification](https://agentskills.io) with:

- **SKILL.md**: Core instructions loaded when the skill is activated (< 350 lines)
- **references/**: Detailed documentation loaded on-demand for specific topics

## Progressive Disclosure

The skill is structured for efficient context usage:

1. **Metadata** (~100 tokens): Name and description in frontmatter
2. **Core Instructions** (~3K tokens): Main SKILL.md content
3. **Detailed References** (as needed): Component docs, i18n guides, patterns

Agents load only what they need for each task.

## Learn More

- [React Email Documentation](https://react.email/docs/llms.txt)
- [Agent Skills Specification](https://agentskills.io/specification.md)
- [Resend Documentation](https://resend.com/docs/llms.txt)