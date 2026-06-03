---
# 知识元数据 (5标准化)
knowledge_id: W10-9A47B6
title: Feishu Docx PowerWrite
category: 11_Skill文档
source: skills/.archive_feishu-docx-powerwrite/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 1981
week: 10
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# Feishu Docx PowerWrite

> **知识ID**: W10-9A47B6  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_feishu-docx-powerwrite/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

---
name: feishu-docx-powerwrite
description: High-quality Feishu/Lark Docx writing via OpenClaw. Use when you want to turn Markdown into well-formatted Feishu Docx (headings, lists, nesting, code blocks) using feishu_docx_write_markdown; includes safe workflows, templates, and troubleshooting. Trigger on Feishu doc/docx links, “write to Feishu doc”, “generate a Feishu doc”, “append/replace docx”, “convert markdown to feishu doc”, or when users want consistently good doc formatting.
---

# Feishu Docx PowerWrite

This skill focuses on **reliably writing great-looking Feishu Docx** using OpenClaw’s Feishu OpenAPI tools.

Key idea: prefer **`feishu_docx_write_markdown`** (Markdown → Docx blocks) for structure-preserving output.

## Quick workflow

1) Get `document_id` (Docx token)
- From a Docx URL: `https://.../docx/<document_id>`

2) Decide write mode
- **Append**: add new content below existing content (most common)
- **Replace**: overwrite the entire document (use carefully)

3) Write markdown
- Use headings + lists + short paragraphs
- Avoid huge single paragraphs (harder to read)

## Recommended defaults

### Append mode (safe)
Use when adding sections, meeting notes, daily logs.

- `mode: append`
- Keep each append chunk <= ~300-600 lines if possible

### Replace mode (destructive)
Use when generating the full doc from scratch.

- `mode: replace`
- MUST set `confirm: true`

## Markdown patterns that render well

### Title + summary
```md
# <Title>

**Summary**
- Point 1
- Point 2

---
```

### Sections
```md
## Section

Short paragraph.

- Bullet
- Bullet

### Subsection

1) Step
2) Step
```

### Code
Use fenced blocks.

```md
```bash
openclaw skills check
```
```

## Templates & references

- Templates: `references/templates.md`
- Troubleshooting: `references/troubleshooting.md`

## Safety / privacy

- Never hardcode tokens, chat_id, open_id, or document links inside this skill.
- Always use the user’s own Feishu app credentials and scopes.
