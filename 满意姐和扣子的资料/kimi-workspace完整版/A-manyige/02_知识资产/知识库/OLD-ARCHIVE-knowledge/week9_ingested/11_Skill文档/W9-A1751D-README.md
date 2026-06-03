---
# 知识元数据 (5标准化)
knowledge_id: W9-A1751D
title: 决策框架 Scripts
category: 11_Skill文档
source: skills/.archive_decision-frameworks/scripts/README.md
ingested_at: 2026-03-27 17:59:30
word_count: 305
week: 9
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# 决策框架 Scripts

> **知识ID**: W9-A1751D  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_decision-frameworks/scripts/README.md`  
> **入库时间**: 2026-03-27

---

## 正文

# 决策框架 Scripts

## 脚本说明

### decision-frameworks-runner.py
决策框架主执行脚本。

## 功能

- evaluate
- score
- recommend

## 使用方法

```bash
# 执行功能
python3 decision-frameworks-runner.py run --feature evaluate

# 查看状态
python3 decision-frameworks-runner.py status

# 生成报告
python3 decision-frameworks-runner.py report
```
