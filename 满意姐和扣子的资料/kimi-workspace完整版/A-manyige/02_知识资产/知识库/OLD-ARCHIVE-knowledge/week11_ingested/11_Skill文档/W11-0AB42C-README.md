---
# 知识元数据 (5标准化)
knowledge_id: W11-0AB42C
title: global-file-governance Scripts
category: 11_Skill文档
source: skills/.archive_global-file-governance/scripts/README.md
ingested_at: 2026-03-27 17:59:30
word_count: 589
week: 11
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# global-file-governance Scripts

> **知识ID**: W11-0AB42C  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_global-file-governance/scripts/README.md`  
> **入库时间**: 2026-03-27

---

## 正文

# global-file-governance Scripts

## Overview

Global file governance for workspace management

## Files

- `global-file-governance-runner.py` - Main execution script

## Usage

```bash
# Check status
python3 scripts/global-file-governance-runner.py status

# Run the skill
python3 scripts/global-file-governance-runner.py run

# Generate report
python3 scripts/global-file-governance-runner.py report
```

## Options

- `--mode` - Execution mode (default: standard)
- `--verbose, -v` - Enable verbose output

## Generated

- Date: 2026-03-20
- Batch: Batch 1 (30 skills)
- Version: 1.0.0
