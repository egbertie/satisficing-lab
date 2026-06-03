---
# 知识元数据 (5标准化)
knowledge_id: W11-7741BF
title: Meeting to Action
category: 11_Skill文档
source: skills/.archive_meeting-to-action/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 2056
week: 11
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# Meeting to Action

> **知识ID**: W11-7741BF  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_meeting-to-action/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

---
name: meeting-to-action
description: Convert meeting notes or transcripts into clear summaries, decisions, and action items with owners and due dates. Use when a user asks to turn a meeting recording, transcript, or notes into a follow-up plan.
---

# Meeting to Action

## Goal
Transform meeting content into an actionable follow-up package with clear ownership and deadlines.

## Best fit
- Use when the user provides a transcript or detailed notes.
- Use when the user needs action items, decisions, and next steps.
- Use when a concise recap email or message is required.

## Not fit
- Avoid when the user wants tasks or calendar invites created automatically.
- Avoid when the transcript is missing and cannot be summarized reliably.
- Avoid when sensitive content should not be shared.

## Quick orientation
- `references/overview.md` for workflow and quality bar.
- `references/auth.md` for access and token handling.
- `references/endpoints.md` for optional integrations and templates.
- `references/webhooks.md` for async event handling.
- `references/ux.md` for intake questions and output formats.
- `references/troubleshooting.md` for common issues.
- `references/safety.md` for safety and privacy guardrails.

## Required inputs
- Transcript or notes.
- Participant list and roles (if available).
- Preferred due date format and timezone.
- Audience for the recap (internal or external).

## Expected output
- Short summary and key decisions.
- Action items with owners, due dates, and status.
- Open questions or risks.
- Draft follow-up message or email.

## Operational notes
- Mark any inferred owners or due dates as tentative.
- Use clear, consistent action verbs.
- Deliver drafts only; do not send or update systems.

## Security notes
- Treat meeting content as confidential.
- Avoid sharing outputs outside the user context.

## Safe mode
- Summarize and draft action items only.
- Do not create tasks, invites, or messages automatically.

## Sensitive ops
- Creating tasks, calendar events, or sending messages is out of scope.
