---
# 知识元数据 (5标准化)
knowledge_id: W8-8AA20E
title: 客户价值系统 Scripts
category: 11_Skill文档
source: skills/.archive_client-value-system/scripts/README.md
ingested_at: 2026-03-27 17:59:30
word_count: 312
week: 8
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# 客户价值系统 Scripts

> **知识ID**: W8-8AA20E  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_client-value-system/scripts/README.md`  
> **入库时间**: 2026-03-27

---

## 正文

# 客户价值系统 Scripts

## 脚本说明

### client-value-system-runner.py
客户价值系统主执行脚本。

## 功能

- evaluate
- segment
- prioritize

## 使用方法

```bash
# 执行功能
python3 client-value-system-runner.py run --feature evaluate

# 查看状态
python3 client-value-system-runner.py status

# 生成报告
python3 client-value-system-runner.py report
```
