---
# 知识元数据 (5标准化)
knowledge_id: W10-88FADD
title: ffmpeg-video-editor Scripts
category: 11_Skill文档
source: skills/.archive_ffmpeg-video-editor/scripts/README.md
ingested_at: 2026-03-27 17:59:30
word_count: 567
week: 10
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# ffmpeg-video-editor Scripts

> **知识ID**: W10-88FADD  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_ffmpeg-video-editor/scripts/README.md`  
> **入库时间**: 2026-03-27

---

## 正文

# ffmpeg-video-editor Scripts

## Overview

FFmpeg video editor for video processing

## Files

- `ffmpeg-video-editor-runner.py` - Main execution script

## Usage

```bash
# Check status
python3 scripts/ffmpeg-video-editor-runner.py status

# Run the skill
python3 scripts/ffmpeg-video-editor-runner.py run

# Generate report
python3 scripts/ffmpeg-video-editor-runner.py report
```

## Options

- `--mode` - Execution mode (default: standard)
- `--verbose, -v` - Enable verbose output

## Generated

- Date: 2026-03-20
- Batch: Batch 1 (30 skills)
- Version: 1.0.0
