---
# 知识元数据 (5标准化)
knowledge_id: W9-ABFE7E
title: 内容分发引擎 Scripts
category: 11_Skill文档
source: skills/.archive_content-distribution-engine/scripts/README.md
ingested_at: 2026-03-27 17:59:30
word_count: 344
week: 9
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# 内容分发引擎 Scripts

> **知识ID**: W9-ABFE7E  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_content-distribution-engine/scripts/README.md`  
> **入库时间**: 2026-03-27

---

## 正文

# 内容分发引擎 Scripts

## 脚本说明

### content-distribution-engine-runner.py
内容分发引擎主执行脚本。

## 功能

- distribute
- schedule
- track

## 使用方法

```bash
# 执行功能
python3 content-distribution-engine-runner.py run --feature distribute

# 查看状态
python3 content-distribution-engine-runner.py status

# 生成报告
python3 content-distribution-engine-runner.py report
```
