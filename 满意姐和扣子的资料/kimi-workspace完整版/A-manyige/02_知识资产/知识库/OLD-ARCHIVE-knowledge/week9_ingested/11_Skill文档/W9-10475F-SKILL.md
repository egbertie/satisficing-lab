---
# 知识元数据 (5标准化)
knowledge_id: W9-10475F
title: SKILL
category: 11_Skill文档
source: skills/.archive_data-visualization-engine/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 2105
week: 9
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# SKILL

> **知识ID**: W9-10475F  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_data-visualization-engine/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

---
name: data-visualization-engine
version: 1.0.0
description: |
  数据可视化引擎 - 多格式图表生成与仪表板创建：
  1. 全局考虑：覆盖柱状图、折线图、饼图、表格、热力图等多类型
  2. 系统考虑：数据输入→图表选择→生成→输出闭环
  3. 迭代机制：根据使用反馈优化图表样式
  4. Skill化：标准接口，支持多种输出格式
  5. 流程自动化：一键生成多种格式图表
author: Satisficing Institute
tags:
  - data-visualization
  - chart
  - dashboard
  - svg
requires:
  - model: "kimi-coding/k2p5"
---

# 数据可视化引擎标准Skill V1.0.0

## 标准1: 全局考虑（Global Coverage）

### 1.1 图表类型

| 类型 | 用途 | 输出格式 |
|------|------|----------|
| 柱状图 | 分类比较 | ASCII/HTML/SVG |
| 折线图 | 趋势展示 | ASCII/HTML/SVG |
| 饼图 | 占比展示 | ASCII/HTML/SVG |
| 表格 | 数据展示 | 格式化文本 |
| 热力图 | 矩阵数据 | ASCII/SVG |
| 仪表盘 | 综合展示 | HTML |

### 1.2 输出格式

| 格式 | 适用场景 |
|------|----------|
| ASCII | 终端查看 |
| HTML | 网页嵌入 |
| SVG | 矢量图形 |
| Markdown | 文档嵌入 |

---

## 标准2: 系统考虑（Systematic）

### 2.1 生成流程

```
数据输入 → 图表类型选择 → 样式配置 → 生成 → 输出
```

---

## 标准3: 迭代机制（Iterative）

根据使用反馈优化默认样式和配色。

---

## 标准4: Skill化（Skill-ified）

### 4.1 目录结构

```
data-visualization-engine/
├── SKILL.md                    # 本文件
├── _meta.json                  # 元数据
├── scripts/
│   ├── chart.sh                # 主脚本
│   ├── generate_bar.py         # 柱状图
│   ├── generate_line.py        # 折线图
│   ├── generate_pie.py         # 饼图
│   └── generate_dashboard.py   # 仪表盘
└── templates/
    └── chart_styles.yaml
```

### 4.2 调用接口

```python
from data_visualization_engine import ChartEngine

engine = ChartEngine()

# 生成柱状图
chart = engine.bar(data={"A": 30, "B": 50}, format="svg")

# 生成仪表盘
dashboard = engine.dashboard(title="数据概览", charts=[...])
```

---

## 标准5: 流程自动化（Fully Automated）

### 5.1 使用方法

```bash
# ASCII柱状图
openclaw skill run data-visualization-engine bar \
  --data "A:30,B:50" \
  --format ascii

# SVG饼图
openclaw skill run data-visualization-engine pie \
  --data "A:30,B:50,C:20" \
  --format svg \
  --output chart.svg
```

---

## 5标准验证清单

| 标准 | 验证项 | 状态 |
|------|--------|------|
| **1. 全局** | 多图表类型覆盖 | ✅ |
| **2. 系统** | 数据→生成→输出闭环 | ✅ |
| **3. 迭代** | 样式优化机制 | ✅ |
| **4. Skill化** | 标准目录 + 调用接口 | ✅ |
| **5. 自动化** | 一键生成多格式 | ✅ |

---

*版本: v1.0.0*  
*来源: chart-generator散落机制提取*  
*创建: 2026-03-20*
