---
# 知识元数据 (5标准化)
knowledge_id: W9-4E7774
title: 决策矩阵计算器 Scripts
category: 11_Skill文档
source: skills/.archive_decision-matrix-calculator/scripts/README.md
ingested_at: 2026-03-27 17:59:30
word_count: 338
week: 9
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# 决策矩阵计算器 Scripts

> **知识ID**: W9-4E7774  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_decision-matrix-calculator/scripts/README.md`  
> **入库时间**: 2026-03-27

---

## 正文

# 决策矩阵计算器 Scripts

## 脚本说明

### decision-matrix-calculator-runner.py
决策矩阵计算器主执行脚本。

## 功能

- calculate
- compare
- rank

## 使用方法

```bash
# 执行功能
python3 decision-matrix-calculator-runner.py run --feature calculate

# 查看状态
python3 decision-matrix-calculator-runner.py status

# 生成报告
python3 decision-matrix-calculator-runner.py report
```
