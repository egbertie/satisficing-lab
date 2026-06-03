---
# 知识元数据 (5标准化)
knowledge_id: W8-2E306A
title: Claude Code集成 Scripts
category: 11_Skill文档
source: skills/.archive_claude-code/scripts/README.md
ingested_at: 2026-03-27 17:59:30
word_count: 283
week: 8
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# Claude Code集成 Scripts

> **知识ID**: W8-2E306A  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_claude-code/scripts/README.md`  
> **入库时间**: 2026-03-27

---

## 正文

# Claude Code集成 Scripts

## 脚本说明

### claude-code-runner.py
Claude Code集成主执行脚本。

## 功能

- code
- review
- refactor

## 使用方法

```bash
# 执行功能
python3 claude-code-runner.py run --feature code

# 查看状态
python3 claude-code-runner.py status

# 生成报告
python3 claude-code-runner.py report
```
