---
# 知识元数据 (5标准化)
knowledge_id: W10-27767D
title: expert-profile-manager Scripts
category: 11_Skill文档
source: skills/.archive_expert-profile-manager/scripts/README.md
ingested_at: 2026-03-27 17:59:30
word_count: 589
week: 10
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# expert-profile-manager Scripts

> **知识ID**: W10-27767D  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_expert-profile-manager/scripts/README.md`  
> **入库时间**: 2026-03-27

---

## 正文

# expert-profile-manager Scripts

## Overview

Expert profile manager for consultant portfolio

## Files

- `expert-profile-manager-runner.py` - Main execution script

## Usage

```bash
# Check status
python3 scripts/expert-profile-manager-runner.py status

# Run the skill
python3 scripts/expert-profile-manager-runner.py run

# Generate report
python3 scripts/expert-profile-manager-runner.py report
```

## Options

- `--mode` - Execution mode (default: standard)
- `--verbose, -v` - Enable verbose output

## Generated

- Date: 2026-03-20
- Batch: Batch 1 (30 skills)
- Version: 1.0.0
