---
# 知识元数据 (5标准化)
knowledge_id: W10-57E642
title: Troubleshooting (Feishu Docx PowerWrite)
category: 11_Skill文档
source: skills/.archive_feishu-docx-powerwrite/troubleshooting.md
ingested_at: 2026-03-27 17:59:30
word_count: 708
week: 10
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# Troubleshooting (Feishu Docx PowerWrite)

> **知识ID**: W10-57E642  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_feishu-docx-powerwrite/troubleshooting.md`  
> **入库时间**: 2026-03-27

---

## 正文

# Troubleshooting (Feishu Docx PowerWrite)

## 1) Permission / 403 / no access
Typical causes:
- Feishu app scopes missing docx/drive permissions
- The bot/app isn’t added as a collaborator to the target doc

Fix:
- Re-check Feishu app scopes
- Share the doc to the bot/app (or make it accessible via org policy)

## 2) Content not rendered as expected
Common causes:
- Markdown too dense (giant paragraphs)
- Incorrect list indentation

Fix:
- Keep paragraphs short
- Use consistent 2-space indentation for nested lists

## 3) Replace mode didn’t overwrite
- Replace requires `confirm: true` (destructive)

## 4) Large docs
- Prefer chunked appends
- Append section-by-section (e.g., 1k–3k chars per chunk)
