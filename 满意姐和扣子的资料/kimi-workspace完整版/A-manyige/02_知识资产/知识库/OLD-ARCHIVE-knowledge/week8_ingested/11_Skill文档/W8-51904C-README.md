---
# 知识元数据 (5标准化)
knowledge_id: W8-51904C
title: 合同分析工具 Scripts
category: 11_Skill文档
source: skills/.archive_afrexai-contract-review/scripts/README.md
ingested_at: 2026-03-27 17:59:30
word_count: 326
week: 8
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# 合同分析工具 Scripts

> **知识ID**: W8-51904C  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_afrexai-contract-review/scripts/README.md`  
> **入库时间**: 2026-03-27

---

## 正文

# 合同分析工具 Scripts

## 脚本说明

### afrexai-contract-review-runner.py
合同分析工具主执行脚本。

## 功能

- analyze
- risk-check
- summary

## 使用方法

```bash
# 执行功能
python3 afrexai-contract-review-runner.py run --feature analyze

# 查看状态
python3 afrexai-contract-review-runner.py status

# 生成报告
python3 afrexai-contract-review-runner.py report
```
