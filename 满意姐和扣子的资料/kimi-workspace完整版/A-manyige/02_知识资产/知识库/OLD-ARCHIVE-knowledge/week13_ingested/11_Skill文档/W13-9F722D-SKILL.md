---
# 知识元数据 (5标准化)
knowledge_id: W13-9F722D
title: SKILL
category: 11_Skill文档
source: skills/.archive_sql-query-templates/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 2031
week: 13
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# SKILL

> **知识ID**: W13-9F722D  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_sql-query-templates/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

---
name: sql-query-templates
version: 1.0.0
description: |
  SQL查询模板库 - 常用数据分析查询模板：
  1. 全局考虑：覆盖探索、时间分析、队列分析、漏斗分析等场景
  2. 系统考虑：场景选择→模板加载→参数填充→查询生成闭环
  3. 迭代机制：根据使用频率优化模板库
  4. Skill化：标准接口，可扩展新模板
  5. 流程自动化：自动生成可执行SQL
author: Satisficing Institute
tags:
  - sql
  - query
  - template
  - data-analysis
requires:
  - model: "kimi-coding/k2p5"
---

# SQL查询模板库标准Skill V1.0.0

## 标准1: 全局考虑（Global Coverage）

### 1.1 模板类型

| 类型 | 用途 | 示例 |
|------|------|------|
| **数据探索** | 基础统计 | COUNT, MIN, MAX, DISTINCT |
| **时间分析** | 日/月聚合 | DATE_TRUNC, LAG, 增长率 |
| **队列分析** | 留存/流失 | Cohort分析 |
| **漏斗分析** | 转化 | 多步骤转化 |
| **数据清洗** | 去重/空值 | Deduplication, NULL处理 |

### 1.2 输出格式

| 格式 | 说明 |
|------|------|
| SQL文件 | 可直接执行 |
| 参数化模板 | 可复用 |
| 解释文档 | 用法说明 |

---

## 标准2: 系统考虑（Systematic）

### 2.1 使用流程

```
场景识别 → 模板选择 → 参数输入 → 生成SQL → 解释说明
```

---

## 标准3: 迭代机制（Iterative）

根据使用频率和需求扩展模板库。

---

## 标准4: Skill化（Skill-ified）

### 4.1 目录结构

```
sql-query-templates/
├── SKILL.md                    # 本文件
├── _meta.json                  # 元数据
├── scripts/
│   ├── list_templates.py       # 模板列表
│   ├── generate_query.py       # 查询生成
│   └── explain_template.py     # 模板解释
└── templates/
    ├── exploration.sql
    ├── time_analysis.sql
    ├── cohort_analysis.sql
    └── funnel_analysis.sql
```

### 4.2 调用接口

```python
from sql_query_templates import QueryTemplates

templates = QueryTemplates()

# 获取模板
query = templates.get(
    template="time_analysis",
    table="orders",
    date_column="created_at"
)
```

---

## 标准5: 流程自动化（Fully Automated）

### 5.1 使用方法

```bash
# 列出模板
openclaw skill run sql-query-templates list

# 生成查询
openclaw skill run sql-query-templates generate \
  --template time_analysis \
  --table orders \
  --date-column created_at
```

---

## 5标准验证清单

| 标准 | 验证项 | 状态 |
|------|--------|------|
| **1. 全局** | 多分析场景覆盖 | ✅ |
| **2. 系统** | 选择→生成→解释闭环 | ✅ |
| **3. 迭代** | 模板库扩展机制 | ✅ |
| **4. Skill化** | 标准目录 + 调用接口 | ✅ |
| **5. 自动化** | 自动生成SQL | ✅ |

---

*版本: v1.0.0*  
*来源: data-analyst散落机制提取*  
*创建: 2026-03-20*
