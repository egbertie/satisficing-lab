---
# 知识元数据 (5标准化)
knowledge_id: W10-A0CAC0
title: Firecrawl
category: 11_Skill文档
source: skills/.archive_firecrawl-search/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 997
week: 10
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# Firecrawl

> **知识ID**: W10-A0CAC0  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_firecrawl-search/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

---
name: firecrawl
description: Web search and scraping via Firecrawl API. Use when you need to search the web, scrape websites (including JS-heavy pages), crawl entire sites, or extract structured data from web pages. Requires FIRECRAWL_API_KEY environment variable.
---

# Firecrawl

Web search and scraping via Firecrawl API.

## Prerequisites

Set `FIRECRAWL_API_KEY` in your environment or `.env` file:
```bash
export FIRECRAWL_API_KEY=fc-xxxxxxxxxx
```

## Quick Start

### Search the web
```bash
firecrawl_search "your search query" --limit 10
```

### Scrape a single page
```bash
firecrawl_scrape "https://example.com"
```

### Crawl an entire site
```bash
firecrawl_crawl "https://example.com" --max-pages 50
```

## API Reference

See [references/api.md](references/api.md) for detailed API documentation and advanced options.

## Scripts

- `scripts/search.py` - Search the web with Firecrawl
- `scripts/scrape.py` - Scrape a single URL
- `scripts/crawl.py` - Crawl an entire website
