---
# 知识元数据 (5标准化)
knowledge_id: W7-E9EA38
title: ab-test-generator Scripts
category: 11_Skill文档
source: skills/.archive_ab-test-generator/scripts/README.md
ingested_at: 2026-03-27 17:59:30
word_count: 582
week: 7
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# ab-test-generator Scripts

> **知识ID**: W7-E9EA38  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_ab-test-generator/scripts/README.md`  
> **入库时间**: 2026-03-27

---

## 正文

# ab-test-generator Scripts

## Overview

A/B test generator for creating testable copy and design variants

## Files

- `ab-test-generator-runner.py` - Main execution script

## Usage

```bash
# Check status
python3 scripts/ab-test-generator-runner.py status

# Run the skill
python3 scripts/ab-test-generator-runner.py run

# Generate report
python3 scripts/ab-test-generator-runner.py report
```

## Options

- `--mode` - Execution mode (default: standard)
- `--verbose, -v` - Enable verbose output

## Generated

- Date: 2026-03-20
- Batch: Batch 1 (30 skills)
- Version: 1.0.0
