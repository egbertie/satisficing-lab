---
# 知识元数据 (5标准化)
knowledge_id: W9-2C9F9F
title: Dashboard Widgets
category: 11_Skill文档
source: skills/.archive_dashboard/widgets.md
ingested_at: 2026-03-27 17:59:30
word_count: 977
week: 9
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# Dashboard Widgets

> **知识ID**: W9-2C9F9F  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_dashboard/widgets.md`  
> **入库时间**: 2026-03-27

---

## 正文

# Dashboard Widgets

## KPI Card

```html
<div class="kpi-card">
  <span class="value">$12,450</span>
  <span class="label">Monthly Revenue</span>
  <span class="delta positive">+12%</span>
</div>
```

## Line Chart

Best for: Trends over time
```json
{
  "type": "line",
  "data": "data.json#revenue",
  "xAxis": "date",
  "yAxis": "amount"
}
```

## Bar Chart

Best for: Comparisons
```json
{
  "type": "bar",
  "data": "data.json#categories",
  "xAxis": "name",
  "yAxis": "value"
}
```

## Status Indicator

```html
<div class="status">
  <span class="dot green"></span>
  <span class="label">API Healthy</span>
  <span class="time">Updated 2m ago</span>
</div>
```

## Table

Best for: Detailed data
```json
{
  "type": "table",
  "data": "data.json#transactions",
  "columns": ["date", "description", "amount"]
}
```

## Widget Sizing

| Size | Width | Use for |
|------|-------|---------|
| Small | 1/4 | KPIs |
| Medium | 1/2 | Charts |
| Large | Full | Tables, maps |
