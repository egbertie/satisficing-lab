---
# 知识元数据 (5标准化)
knowledge_id: W9-BA316A
title: 决策治理 Scripts
category: 11_Skill文档
source: skills/.archive_decision-governance/scripts/README.md
ingested_at: 2026-03-27 17:59:30
word_count: 296
week: 9
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# 决策治理 Scripts

> **知识ID**: W9-BA316A  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_decision-governance/scripts/README.md`  
> **入库时间**: 2026-03-27

---

## 正文

# 决策治理 Scripts

## 脚本说明

### decision-governance-runner.py
决策治理主执行脚本。

## 功能

- track
- audit
- report

## 使用方法

```bash
# 执行功能
python3 decision-governance-runner.py run --feature track

# 查看状态
python3 decision-governance-runner.py status

# 生成报告
python3 decision-governance-runner.py report
```
