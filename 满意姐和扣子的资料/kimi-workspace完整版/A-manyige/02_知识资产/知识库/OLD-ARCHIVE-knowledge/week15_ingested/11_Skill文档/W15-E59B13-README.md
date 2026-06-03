---
# 知识元数据 (5标准化)
knowledge_id: W15-E59B13
title: data-quality-auditor Scripts
category: 11_Skill文档
source: skills/data-quality-auditor/scripts/README.md
ingested_at: 2026-03-27 17:59:30
word_count: 581
week: 15
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# data-quality-auditor Scripts

> **知识ID**: W15-E59B13  
> **分类**: 11_Skill文档  
> **来源**: `skills/data-quality-auditor/scripts/README.md`  
> **入库时间**: 2026-03-27

---

## 正文

# data-quality-auditor Scripts

## Overview

Data quality auditor for validation and cleansing

## Files

- `data-quality-auditor-runner.py` - Main execution script

## Usage

```bash
# Check status
python3 scripts/data-quality-auditor-runner.py status

# Run the skill
python3 scripts/data-quality-auditor-runner.py run

# Generate report
python3 scripts/data-quality-auditor-runner.py report
```

## Options

- `--mode` - Execution mode (default: standard)
- `--verbose, -v` - Enable verbose output

## Generated

- Date: 2026-03-20
- Batch: Batch 1 (30 skills)
- Version: 1.0.0
