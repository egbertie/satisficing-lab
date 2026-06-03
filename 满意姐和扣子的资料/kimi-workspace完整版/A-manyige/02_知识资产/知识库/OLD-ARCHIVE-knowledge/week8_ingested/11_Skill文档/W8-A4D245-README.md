---
# 知识元数据 (5标准化)
knowledge_id: W8-A4D245
title: 音频处理器 Scripts
category: 11_Skill文档
source: skills/.archive_audio-handler/scripts/README.md
ingested_at: 2026-03-27 17:59:30
word_count: 286
week: 8
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# 音频处理器 Scripts

> **知识ID**: W8-A4D245  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_audio-handler/scripts/README.md`  
> **入库时间**: 2026-03-27

---

## 正文

# 音频处理器 Scripts

## 脚本说明

### audio-handler-runner.py
音频处理器主执行脚本。

## 功能

- convert
- trim
- merge
- extract

## 使用方法

```bash
# 执行功能
python3 audio-handler-runner.py run --feature convert

# 查看状态
python3 audio-handler-runner.py status

# 生成报告
python3 audio-handler-runner.py report
```
