---
# 知识元数据 (5标准化)
knowledge_id: W13-252EE6
title: SKILL
category: 11_Skill文档
source: skills/.archive_touchpoint-designer/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 2206
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

> **知识ID**: W13-252EE6  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_touchpoint-designer/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

---
name: touchpoint-designer
version: 1.0.0
description: |
  触点体验设计师 - 客户触点行为设计与仪式感生成：
  1. 全局考虑：覆盖首次/深度/长期接触全流程
  2. 系统考虑：需求→设计→输出→验证闭环
  3. 迭代机制：根据效果反馈优化触点设计
  4. Skill化：标准接口，可按触点类型独立调用
  5. 流程自动化：自动生成触点设计方案
author: Satisficing Institute
tags:
  - touchpoint
  - experience-design
  - behavioral-design
  - customer-journey
requires:
  - model: "kimi-coding/k2p5"
---

# 触点体验设计师标准Skill V1.0.0

## 标准1: 全局考虑（Global Coverage）

### 1.1 触点类型

| 类型 | 目标 | 关键原则 |
|------|------|----------|
| **首次接触** | 建立信任 | 3秒/15秒/60秒原则 |
| **深度接触** | 展示专业 | 可视化/故事化/可执行化 |
| **长期接触** | 维护关系 | 定期价值/关键时刻/社交货币 |

### 1.2 设计要素

| 要素 | 说明 |
|------|------|
| 触点场景 | 网站/电话/面谈/活动 |
| 时间窗口 | 3秒/15秒/60秒/全程 |
| 关键信息 | 价值主张+信任背书+CTA |
| 视觉规范 | 布局/配色/字体 |
| 仪式感 | 启动/交付/里程碑 |

---

## 标准2: 系统考虑（Systematic）

### 2.1 设计流程

```
触点类型 → 场景描述 → 目标设定 → 结构设计 → 内容生成 → 视觉规范 → 仪式感设计
```

### 2.2 输出内容

| 输出 | 说明 |
|------|------|
| 触点地图 | 完整接触流程 |
| 内容框架 | 各阶段关键信息 |
| 视觉规范 | 设计标准 |
| 仪式感文案 | 启动/交付仪式 |

---

## 标准3: 迭代机制（Iterative）

根据转化率数据持续优化触点设计。

---

## 标准4: Skill化（Skill-ified）

### 4.1 目录结构

```
touchpoint-designer/
├── SKILL.md                    # 本文件
├── _meta.json                  # 元数据
├── scripts/
│   ├── design_touchpoint.py    # 触点设计
│   ├── generate_ritual.py      # 仪式感生成
│   └── create_visual_guide.py  # 视觉规范
└── templates/
    └── touchpoint_templates.yaml
```

### 4.2 调用接口

```python
from touchpoint_designer import TouchpointDesigner

designer = TouchpointDesigner()

# 设计首次接触
design = designer.design(
    touchpoint_type="first_contact",
    channel="web",
    goal="建立信任"
)

# 生成仪式感
ritual = designer.generate_ritual(
    ritual_type="kickoff",
    customer="XX公司"
)
```

---

## 标准5: 流程自动化（Fully Automated）

### 5.1 使用方法

```bash
# 设计触点
openclaw skill run touchpoint-designer design \
  --type first_contact \
  --channel web

# 生成仪式感
openclaw skill run touchpoint-designer ritual \
  --type kickoff \
  --customer "XX公司"
```

---

## 5标准验证清单

| 标准 | 验证项 | 状态 |
|------|--------|------|
| **1. 全局** | 触点类型全覆盖 | ✅ |
| **2. 系统** | 需求→设计→输出闭环 | ✅ |
| **3. 迭代** | 效果优化机制 | ✅ |
| **4. Skill化** | 标准目录 + 调用接口 | ✅ |
| **5. 自动化** | 自动生成设计方案 | ✅ |

---

*版本: v1.0.0*  
*来源: behavioral-design散落机制提取*  
*创建: 2026-03-20*
