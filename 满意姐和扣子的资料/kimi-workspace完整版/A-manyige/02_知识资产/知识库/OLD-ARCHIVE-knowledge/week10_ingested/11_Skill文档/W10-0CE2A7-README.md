---
# 知识元数据 (5标准化)
knowledge_id: W10-0CE2A7
title: feishu-messaging Scripts
category: 11_Skill文档
source: skills/.archive_feishu-messaging/scripts/README.md
ingested_at: 2026-03-27 17:59:30
word_count: 558
week: 10
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# feishu-messaging Scripts

> **知识ID**: W10-0CE2A7  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_feishu-messaging/scripts/README.md`  
> **入库时间**: 2026-03-27

---

## 正文

# feishu-messaging Scripts

## Overview

Feishu messaging integration for notifications

## Files

- `feishu-messaging-runner.py` - Main execution script

## Usage

```bash
# Check status
python3 scripts/feishu-messaging-runner.py status

# Run the skill
python3 scripts/feishu-messaging-runner.py run

# Generate report
python3 scripts/feishu-messaging-runner.py report
```

## Options

- `--mode` - Execution mode (default: standard)
- `--verbose, -v` - Enable verbose output

## Generated

- Date: 2026-03-20
- Batch: Batch 1 (30 skills)
- Version: 1.0.0
