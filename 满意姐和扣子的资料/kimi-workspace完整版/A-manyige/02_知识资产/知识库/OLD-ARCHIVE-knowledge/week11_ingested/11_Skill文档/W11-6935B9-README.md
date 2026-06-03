---
# 知识元数据 (5标准化)
knowledge_id: W11-6935B9
title: growth-path-monitor Scripts
category: 11_Skill文档
source: skills/.archive_growth-path-monitor/scripts/README.md
ingested_at: 2026-03-27 17:59:30
word_count: 568
week: 11
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# growth-path-monitor Scripts

> **知识ID**: W11-6935B9  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_growth-path-monitor/scripts/README.md`  
> **入库时间**: 2026-03-27

---

## 正文

# growth-path-monitor Scripts

## Overview

Growth path monitor for progress tracking

## Files

- `growth-path-monitor-runner.py` - Main execution script

## Usage

```bash
# Check status
python3 scripts/growth-path-monitor-runner.py status

# Run the skill
python3 scripts/growth-path-monitor-runner.py run

# Generate report
python3 scripts/growth-path-monitor-runner.py report
```

## Options

- `--mode` - Execution mode (default: standard)
- `--verbose, -v` - Enable verbose output

## Generated

- Date: 2026-03-20
- Batch: Batch 1 (30 skills)
- Version: 1.0.0
