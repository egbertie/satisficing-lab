---
# 知识元数据 (5标准化)
knowledge_id: W9-85A07E
title: cron-merge-optimizer Scripts
category: 11_Skill文档
source: skills/.archive_cron-merge-optimizer/scripts/README.md
ingested_at: 2026-03-27 17:59:30
word_count: 582
week: 9
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# cron-merge-optimizer Scripts

> **知识ID**: W9-85A07E  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_cron-merge-optimizer/scripts/README.md`  
> **入库时间**: 2026-03-27

---

## 正文

# cron-merge-optimizer Scripts

## Overview

Cron job merge optimizer for scheduling efficiency

## Files

- `cron-merge-optimizer-runner.py` - Main execution script

## Usage

```bash
# Check status
python3 scripts/cron-merge-optimizer-runner.py status

# Run the skill
python3 scripts/cron-merge-optimizer-runner.py run

# Generate report
python3 scripts/cron-merge-optimizer-runner.py report
```

## Options

- `--mode` - Execution mode (default: standard)
- `--verbose, -v` - Enable verbose output

## Generated

- Date: 2026-03-20
- Batch: Batch 1 (30 skills)
- Version: 1.0.0
