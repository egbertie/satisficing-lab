---
# 知识元数据 (5标准化)
knowledge_id: W9-A6E99A
title: SKILL
category: 11_Skill文档
source: skills/.archive_cron-merge-optimizer/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 2030
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

> **知识ID**: W9-A6E99A  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_cron-merge-optimizer/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

---
name: cron-merge-optimizer
version: 1.0.0
description: |
  Cron合并优化器 - 智能合并定时任务减少调度开销：
  1. 全局考虑：覆盖分析→合并→优化→回滚全流程
  2. 系统考虑：扫描→分析→生成方案→执行→验证闭环
  3. 迭代机制：根据执行效果优化合并策略
  4. Skill化：标准接口，可安全回滚
  5. 流程自动化：自动分析和执行合并
author: Satisficing Institute
tags:
  - cron
  - optimization
  - merge
  - scheduler
requires:
  - model: "kimi-coding/k2p5"
  - cron: true
---

# Cron合并优化器标准Skill V1.0.0

## 标准1: 全局考虑（Global Coverage）

### 1.1 优化维度

| 维度 | 说明 |
|------|------|
| **时间亲和性** | 同时间段任务合并 |
| **性质亲和性** | 同类型任务合并 |
| **依赖关系** | 保持任务间依赖 |
| **关键任务** | 保持关键任务时间准确 |

### 1.2 双Cron架构

| Cron | 时间 | 合并任务 |
|------|------|----------|
| 晨间统一Cron | 09:00 | 6个检查/采集任务 |
| 晚间统一Cron | 22:00 | 4个报告/审计任务 |

---

## 标准2: 系统考虑（Systematic）

### 2.1 优化流程

```
扫描现有Cron → 分析亲和性 → 生成合并方案 → 执行合并 → 验证效果 → 监控
```

### 2.2 安全机制

| 机制 | 说明 |
|------|------|
| 备份原配置 | 合并前自动备份 |
| 回滚支持 | 可一键回滚 |
| 验证检查 | 合并后验证执行 |

---

## 标准3: 迭代机制（Iterative）

根据执行效果优化合并策略。

---

## 标准4: Skill化（Skill-ified）

### 4.1 目录结构

```
cron-merge-optimizer/
├── SKILL.md                    # 本文件
├── _meta.json                  # 元数据
├── scripts/
│   ├── analyze_cron.py         # Cron分析
│   ├── generate_plan.py        # 方案生成
│   ├── execute_merge.py        # 执行合并
│   └── rollback.py             # 回滚
└── rules/
    └── merge_rules.yaml
```

### 4.2 调用接口

```python
from cron_merge_optimizer import CronOptimizer

optimizer = CronOptimizer()

# 分析当前Cron
analysis = optimizer.analyze()

# 执行合并
optimizer.execute_merge(plan)

# 回滚
optimizer.rollback()
```

---

## 标准5: 流程自动化（Fully Automated）

### 5.1 使用方法

```bash
# 分析当前Cron
openclaw skill run cron-merge-optimizer analyze

# 执行合并
openclaw skill run cron-merge-optimizer execute

# 回滚
openclaw skill run cron-merge-optimizer rollback
```

---

## 5标准验证清单

| 标准 | 验证项 | 状态 |
|------|--------|------|
| **1. 全局** | 多维度优化覆盖 | ✅ |
| **2. 系统** | 分析→合并→验证闭环 | ✅ |
| **3. 迭代** | 策略优化机制 | ✅ |
| **4. Skill化** | 标准目录 + 调用接口 | ✅ |
| **5. 自动化** | 自动分析+合并 | ✅ |

---

*版本: v1.0.0*  
*来源: cron-optimization-manager散落机制提取*  
*创建: 2026-03-20*
