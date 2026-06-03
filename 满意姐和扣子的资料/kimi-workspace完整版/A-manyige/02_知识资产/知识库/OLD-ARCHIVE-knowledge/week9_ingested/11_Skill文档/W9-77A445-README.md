---
# 知识元数据 (5标准化)
knowledge_id: W9-77A445
title: 公司搜索Kimi Scripts
category: 11_Skill文档
source: skills/.archive_company-search-kimi/scripts/README.md
ingested_at: 2026-03-27 17:59:30
word_count: 308
week: 9
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# 公司搜索Kimi Scripts

> **知识ID**: W9-77A445  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_company-search-kimi/scripts/README.md`  
> **入库时间**: 2026-03-27

---

## 正文

# 公司搜索Kimi Scripts

## 脚本说明

### company-search-kimi-runner.py
公司搜索Kimi主执行脚本。

## 功能

- search
- analyze
- report

## 使用方法

```bash
# 执行功能
python3 company-search-kimi-runner.py run --feature search

# 查看状态
python3 company-search-kimi-runner.py status

# 生成报告
python3 company-search-kimi-runner.py report
```
