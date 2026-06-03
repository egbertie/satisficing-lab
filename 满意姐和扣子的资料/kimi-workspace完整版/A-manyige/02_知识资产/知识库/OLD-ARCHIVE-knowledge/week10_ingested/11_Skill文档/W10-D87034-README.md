---
# 知识元数据 (5标准化)
knowledge_id: W10-D87034
title: email-daily-summary Scripts
category: 11_Skill文档
source: skills/.archive_email-daily-summary/scripts/README.md
ingested_at: 2026-03-27 17:59:30
word_count: 577
week: 10
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# email-daily-summary Scripts

> **知识ID**: W10-D87034  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_email-daily-summary/scripts/README.md`  
> **入库时间**: 2026-03-27

---

## 正文

# email-daily-summary Scripts

## Overview

Email daily summary generator for inbox management

## Files

- `email-daily-summary-runner.py` - Main execution script

## Usage

```bash
# Check status
python3 scripts/email-daily-summary-runner.py status

# Run the skill
python3 scripts/email-daily-summary-runner.py run

# Generate report
python3 scripts/email-daily-summary-runner.py report
```

## Options

- `--mode` - Execution mode (default: standard)
- `--verbose, -v` - Enable verbose output

## Generated

- Date: 2026-03-20
- Batch: Batch 1 (30 skills)
- Version: 1.0.0
