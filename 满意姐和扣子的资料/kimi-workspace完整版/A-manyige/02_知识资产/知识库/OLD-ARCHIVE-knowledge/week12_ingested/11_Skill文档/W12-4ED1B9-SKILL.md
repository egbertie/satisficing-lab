---
# 知识元数据 (5标准化)
knowledge_id: W12-4ED1B9
title: notion-api (generic)
category: 11_Skill文档
source: skills/.archive_notion-api/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 1384
week: 12
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# notion-api (generic)

> **知识ID**: W12-4ED1B9  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_notion-api/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

---
name: notion-api
description: Generic Notion API CLI (Node) for search, querying data sources (databases), and creating pages. Configure with NOTION_KEY (or ~/.config/notion/api_key).
---

# notion-api (generic)

This skill provides a small Node-based CLI for the Notion API. It’s designed to be shareable: **no hard-coded database IDs and no secrets in the repo**.

## Auth

Provide a Notion integration token via either:

- `NOTION_KEY` env var, or
- `~/.config/notion/api_key` (first line)

Also make sure the target pages/databases are shared with your integration in Notion.

## Commands (CLI)

Run via:

- `node scripts/notion-api.mjs <command> ...`

### Search

```bash
node scripts/notion-api.mjs search "query" --page-size 10
```

### Query a data source (database query)

```bash
node scripts/notion-api.mjs query --data-source-id <DATA_SOURCE_ID> --page-size 10
# optionally pass raw JSON body:
node scripts/notion-api.mjs query --data-source-id <ID> --body '{"filter": {...}, "sorts": [...], "page_size": 10}'
```

### Create a page in a database

```bash
node scripts/notion-api.mjs create-page --database-id <DATABASE_ID> --title "My item" --title-prop Name
```

## Output

All commands print JSON to stdout.

## Notes

- Notion API version header defaults to `2025-09-03` (override with `NOTION_VERSION`).
- Rate limits apply; prefer `page_size` and minimal calls.
