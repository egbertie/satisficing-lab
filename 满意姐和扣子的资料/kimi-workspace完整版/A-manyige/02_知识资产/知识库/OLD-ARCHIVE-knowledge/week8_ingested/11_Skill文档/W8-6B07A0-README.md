---
# 知识元数据 (5标准化)
knowledge_id: W8-6B07A0
title: bmc-consistency-checker Scripts
category: 11_Skill文档
source: skills/.archive_bmc-consistency-checker/scripts/README.md
ingested_at: 2026-03-27 17:59:30
word_count: 616
week: 8
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# bmc-consistency-checker Scripts

> **知识ID**: W8-6B07A0  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_bmc-consistency-checker/scripts/README.md`  
> **入库时间**: 2026-03-27

---

## 正文

# bmc-consistency-checker Scripts

## Overview

Business Model Canvas consistency checker for cross-module validation

## Files

- `bmc-consistency-checker-runner.py` - Main execution script

## Usage

```bash
# Check status
python3 scripts/bmc-consistency-checker-runner.py status

# Run the skill
python3 scripts/bmc-consistency-checker-runner.py run

# Generate report
python3 scripts/bmc-consistency-checker-runner.py report
```

## Options

- `--mode` - Execution mode (default: standard)
- `--verbose, -v` - Enable verbose output

## Generated

- Date: 2026-03-20
- Batch: Batch 1 (30 skills)
- Version: 1.0.0
