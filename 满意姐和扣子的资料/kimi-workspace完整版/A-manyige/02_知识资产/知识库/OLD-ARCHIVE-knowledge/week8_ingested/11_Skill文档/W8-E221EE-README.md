---
# 知识元数据 (5标准化)
knowledge_id: W8-E221EE
title: 图表生成器 Scripts
category: 11_Skill文档
source: skills/.archive_chart-generator/scripts/README.md
ingested_at: 2026-03-27 17:59:30
word_count: 295
week: 8
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# 图表生成器 Scripts

> **知识ID**: W8-E221EE  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_chart-generator/scripts/README.md`  
> **入库时间**: 2026-03-27

---

## 正文

# 图表生成器 Scripts

## 脚本说明

### chart-generator-runner.py
图表生成器主执行脚本。

## 功能

- create
- bar
- line
- pie
- export

## 使用方法

```bash
# 执行功能
python3 chart-generator-runner.py run --feature create

# 查看状态
python3 chart-generator-runner.py status

# 生成报告
python3 chart-generator-runner.py report
```
