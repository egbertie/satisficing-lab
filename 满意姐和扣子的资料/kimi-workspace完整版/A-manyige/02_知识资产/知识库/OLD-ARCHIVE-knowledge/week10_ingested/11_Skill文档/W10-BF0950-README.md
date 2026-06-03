---
# 知识元数据 (5标准化)
knowledge_id: W10-BF0950
title: evolution-experiment-lab Scripts
category: 11_Skill文档
source: skills/.archive_evolution-experiment-lab/scripts/README.md
ingested_at: 2026-03-27 17:59:30
word_count: 611
week: 10
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# evolution-experiment-lab Scripts

> **知识ID**: W10-BF0950  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_evolution-experiment-lab/scripts/README.md`  
> **入库时间**: 2026-03-27

---

## 正文

# evolution-experiment-lab Scripts

## Overview

Evolution experiment lab for continuous improvement testing

## Files

- `evolution-experiment-lab-runner.py` - Main execution script

## Usage

```bash
# Check status
python3 scripts/evolution-experiment-lab-runner.py status

# Run the skill
python3 scripts/evolution-experiment-lab-runner.py run

# Generate report
python3 scripts/evolution-experiment-lab-runner.py report
```

## Options

- `--mode` - Execution mode (default: standard)
- `--verbose, -v` - Enable verbose output

## Generated

- Date: 2026-03-20
- Batch: Batch 1 (30 skills)
- Version: 1.0.0
