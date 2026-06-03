---
# 知识元数据 (5标准化)
knowledge_id: W9-716F8D
title: 持续改进 Scripts
category: 11_Skill文档
source: skills/.archive_continuous-improvement/scripts/README.md
ingested_at: 2026-03-27 17:59:30
word_count: 313
week: 9
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# 持续改进 Scripts

> **知识ID**: W9-716F8D  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_continuous-improvement/scripts/README.md`  
> **入库时间**: 2026-03-27

---

## 正文

# 持续改进 Scripts

## 脚本说明

### continuous-improvement-runner.py
持续改进主执行脚本。

## 功能

- analyze
- suggest
- track

## 使用方法

```bash
# 执行功能
python3 continuous-improvement-runner.py run --feature analyze

# 查看状态
python3 continuous-improvement-runner.py status

# 生成报告
python3 continuous-improvement-runner.py report
```
